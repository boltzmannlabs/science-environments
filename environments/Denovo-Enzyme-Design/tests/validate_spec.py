#!/usr/bin/env python3
"""Validate the local specification package, without running scientific tools."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import math
from pathlib import Path
import re
import sys

from jsonschema import Draft202012Validator, ValidationError
import yaml


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'tests/specification-validation.json'
checks: list[dict[str, str]] = []


def require(condition: bool, name: str) -> None:
    if not condition:
        raise AssertionError(name)
    checks.append({'check': name, 'status': 'PASS'})


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def finite_numbers(value: object) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(finite_numbers(v) for v in value.values())
    if isinstance(value, list):
        return all(finite_numbers(v) for v in value)
    return True


def validate_request(request: dict, schema: dict) -> None:
    """Documented request checks; this is not a scientific runtime resolver."""
    Draft202012Validator(schema).validate(request)
    limits = request['constraints']['length']
    execution = request['execution']
    if limits['min'] > limits['max']:
        raise ValueError('length range is reversed')
    if execution['final_count'] > execution['max_chemistry_candidates']:
        raise ValueError('requested count exceeds the chemistry cap')
    if execution['max_chemistry_candidates'] > execution['max_generated']:
        raise ValueError('chemistry cap exceeds generation cap')
    if not finite_numbers(request):
        raise ValueError('non-finite numeric input')


def expect_invalid(request: dict, schema: dict, name: str) -> None:
    try:
        validate_request(request, schema)
    except (ValidationError, ValueError):
        checks.append({'check': name, 'status': 'PASS'})
    else:
        raise AssertionError(name)


def main() -> None:
    required_files = [
        'README.md', 'ENVIRONMENT_SPEC.md',
        'config/environment.yaml', 'config/request.schema.json',
        'config/protocol.schema.json', 'tasks/denovo_enzyme_001.md',
        'tasks/request.example.json', 'tests/ACCEPTANCE.md',
        'tests/validate_spec.py',
        '../../research/Denovo-Enzyme-Design/research-notes.md',
        '../../research/Denovo-Enzyme-Design/references.md',
    ]
    require(all((ROOT / name).is_file() for name in required_files), 'required package files exist')

    schemas = {name: read_json(f'config/{name}.schema.json') for name in ['request', 'protocol']}
    for name, schema in schemas.items():
        Draft202012Validator.check_schema(schema)
        require(True, f'{name} JSON Schema is structurally valid')
        for pointer in re.findall(r'"\$ref":\s*"(#/[^"]+)"', json.dumps(schema)):
            target = schema
            for part in pointer[2:].split('/'):
                target = target[part.replace('~1', '/').replace('~0', '~')]
        require(True, f'{name} schema internal references resolve')

    request = read_json('tasks/request.example.json')
    validate_request(request, schemas['request'])
    require(True, 'example request passes structural and declared budget/range checks')
    cases = []
    bad = copy.deepcopy(request); del bad['reaction']; cases.append((bad, 'missing reaction rejected'))
    bad = copy.deepcopy(request); bad['execution']['final_count'] = 0; cases.append((bad, 'zero shortlist count rejected'))
    bad = copy.deepcopy(request); bad['execution']['budget']['gpu_hours'] = 0; cases.append((bad, 'zero required compute budget rejected'))
    bad = copy.deepcopy(request); bad['execution']['controller_mode'] = 'unrestricted'; cases.append((bad, 'unknown controller mode rejected'))
    bad = copy.deepcopy(request); bad['constraints']['length'] = {'min': 300, 'max': 150}; cases.append((bad, 'reversed length bounds rejected'))
    bad = copy.deepcopy(request); bad['execution']['final_count'] = 6; cases.append((bad, 'shortlist above chemistry cap rejected'))
    bad = copy.deepcopy(request); bad['execution']['max_chemistry_candidates'] = 101; cases.append((bad, 'chemistry cap above generation cap rejected'))
    bad = copy.deepcopy(request); bad['conditions']['pH'] = float('nan'); cases.append((bad, 'non-finite numeric input rejected'))
    for bad, name in cases:
        expect_invalid(bad, schemas['request'], name)

    config = yaml.safe_load((ROOT/'config/environment.yaml').read_text())
    require(config['maturity'] == 'Specification', 'maturity remains Specification')
    require(config['scientific_execution_included'] is False, 'no scientific implementation claimed')
    require(config['qualified_profiles_included'] is False, 'no qualified chemistry profile claimed')
    require(config['scope']['require_qualified_reaction_profile'] is True, 'qualified reaction profile required')
    stages = config['stages']
    expected = ['prepare', 'generate', 'sequence_screen', 'fold', 'aggregation', 'complex', 'catalytic_states', 'chemistry', 'evaluate']
    require([s['id'] for s in stages] == expected, 'complete cost-ordered stage sequence')
    seen = set()
    for stage in stages:
        require(set(stage['depends_on']).issubset(seen), f"dependencies precede {stage['id']}")
        seen.add(stage['id'])
    require(len({s['output'] for s in stages}) == len(stages), 'each stage has its own artifact location')
    require(stages[1]['capabilities'] == ['constrained_scaffold_and_sequence_generation'], 'scaffold and sequence generation precede sequence-property screening')
    require(all(stage.get('capabilities') and 'backends' not in stage for stage in stages), 'stages specify operations independently of software selection')

    rule_groups = set(schemas['protocol']['$defs']['rule']['properties']['group']['enum'])
    require(set(config['required_rule_groups']) == rule_groups and len(rule_groups) == 8, 'protocol and configuration agree on eight required rule groups')
    require({'solubility', 'aggregation', 'states_and_chemical_steps'}.issubset(rule_groups), 'solubility, aggregation and chemistry are separate mandatory groups')
    qualification = config['qualification']
    require(qualification['required_rule_combiner'] == 'all', 'qualification requires every mandatory rule')
    require(not qualification['unresolved_can_qualify'] and not qualification['fail_can_qualify'], 'failed and unresolved evidence cannot qualify')
    require(not qualification['score_compensation_across_hard_rules'], 'hard-rule failures cannot be compensated')
    require(not qualification['return_failed_to_fill_shortlist'], 'failed designs cannot fill a shortlist')
    require(qualification['missing_raw_value'] is None, 'missing raw measurements remain null')

    control = config['controller']
    reward = control['reward']
    require(reward['per_required_rule_positive_weight'] and reward['weight_sum'] == 1, 'every required rule has positive normalized reward weight')
    require(reward['score_range'] == [0, 1] and reward['gamma'] == 1, 'bounded potential with finite-episode discount')
    require(reward['maximum_total_normalized_episode_cost'] == 1, 'episode cost normalization is bounded')
    worst_success = reward['terminal_all_pass'] - reward['progress_coefficient'] - reward['cost_coefficient']
    best_incomplete = reward['terminal_incomplete'] + reward['progress_coefficient']
    best_failure = reward['terminal_verified_failure'] + reward['progress_coefficient']
    require(worst_success > best_incomplete > best_failure, 'configured reward bounds preserve terminal-outcome ordering')
    require(control['training_split'] == 'development_only' and control['held_out_policy'] == 'frozen', 'RL development and held-out evaluation are separated')
    require({'reaction', 'catalytic_groups', 'gates', 'reward_definition', 'required_stages', 'chemistry_reservation'}.issubset(control['immutable_to_policy']), 'scientific acceptance and chemistry reservation are immutable to policy')
    require(config['budgets']['reserve_finalist_chemistry'] and not config['budgets']['relax_gates_when_exhausted'], 'budgets reserve chemistry and cannot relax gates')
    require(config['benchmark']['equal_total_compute'] and config['benchmark']['independent_frozen_evaluator'], 'benchmark uses equal compute and a frozen evaluator')

    task = (ROOT/'tasks/denovo_enzyme_001.md').read_text()
    expected_sections = ['Description', 'Target', 'Design Constraints', 'Required Execution Steps', 'Expected Output', 'Constraints', 'Important Instructions']
    require(re.findall(r'^## (.+)$', task, re.M) == expected_sections, 'task preserves reference section order with execution steps replacing the software list')
    require('Execution is defined by required operations' in task, 'task specifies required operations rather than adapter names')
    specification = (ROOT/'ENVIRONMENT_SPEC.md').read_text()
    for name, text in [('agent task', task), ('environment specification', specification)]:
        step_numbers = [int(n) for n in re.findall(r'^\| (\d+)\. ', text, re.M)]
        require(step_numbers == list(range(1, 15)), f'{name} contains all fourteen ordered execution steps')

    local_links = 0
    research_root = ROOT.parents[1] / 'research' / ROOT.name
    documents = list(ROOT.rglob('*.md')) + list(research_root.rglob('*.md'))
    for document in documents:
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', document.read_text()):
            if link.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            target = (document.parent / link.split('#', 1)[0]).resolve()
            require(target.is_file() or target == REPORT.resolve(), f'local link resolves: {document.relative_to(ROOT.parents[1])} -> {link}')
            local_links += 1
    require(local_links > 0, 'package contains navigable local documentation links')

    report = {
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'environment_id': config['environment_id'],
        'maturity': 'Specification',
        'validation_scope': 'local specification consistency; no scientific execution',
        'status': 'PASS',
        'checks_passed': len(checks),
        'checks': checks,
        'dependencies': {'python': sys.version.split()[0], 'jsonschema': version('jsonschema'), 'PyYAML': version('PyYAML')},
        'file_sha256': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in required_files},
        'not_performed': [
            'qualification of a complete reaction profile',
            'scientific tool installation or execution',
            'chemical-structure validation of the example reaction',
            'RL training or inference',
            'computational or experimental enzyme benchmarking',
        ],
    }
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS: {len(checks)} specification checks; no scientific workflows executed.")
    print(f'Report: {REPORT}')


if __name__ == '__main__':
    main()
