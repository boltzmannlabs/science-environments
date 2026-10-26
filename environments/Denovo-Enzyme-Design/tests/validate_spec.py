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


def validate_protocol(protocol: dict, schema: dict, request: dict | None = None) -> None:
    """Check contract semantics only; do not certify artifacts or enzyme chemistry."""
    Draft202012Validator(schema).validate(protocol)
    if not finite_numbers(protocol):
        raise ValueError('non-finite protocol value')
    for key in ['pH_range', 'temperature_C_range']:
        lower, upper = protocol['scope'][key]
        if lower > upper:
            raise ValueError('reversed profile range')
    assembly = protocol['assembly']
    chains = set(assembly['sequence_groups'][0]['chain_ids'])
    if len(chains) != assembly['subunit_count']:
        raise ValueError('assembly chain count mismatch')
    if request is not None:
        mode = request.get('assembly', {}).get('mode', 'resolve_from_evidence')
        if mode != 'resolve_from_evidence' and mode != assembly['kind']:
            raise ValueError('requested assembly differs from profile')

    def indexed(items: list[dict], key: str) -> dict:
        result = {item[key]: item for item in items}
        if len(result) != len(items):
            raise ValueError(f'duplicate {key}')
        return result

    sites = indexed(assembly['active_sites'], 'site_id')
    states = indexed(protocol['states'], 'state_id')
    steps = indexed(protocol['steps'], 'step_id')
    indexed(protocol['rules'], 'rule_id')
    for site in sites.values():
        if not set(site['chain_ids']).issubset(chains):
            raise ValueError('site references unknown chain')
    for state in states.values():
        if not set(state['site_ids']).issubset(sites):
            raise ValueError('state references unknown site')
    for step in steps.values():
        if step['from_state'] not in states or step['to_state'] not in states:
            raise ValueError('step references unknown state')
        covered = set(step['site_ids'])
        if not covered.issubset(sites):
            raise ValueError('step references unknown site')
        if any(not covered.issubset(states[step[end]]['site_ids']) for end in ['from_state', 'to_state']):
            raise ValueError('step site missing from an endpoint state')
    if {site for step in steps.values() for site in step['site_ids']} != set(sites):
        raise ValueError('declared active site lacks chemical-step coverage')
    if {step[end] for step in steps.values() for end in ['from_state', 'to_state']} != set(states):
        raise ValueError('declared state lacks step coverage')

    required_rules = [rule for rule in protocol['rules'] if rule['required']]
    groups = set(schema['$defs']['rule']['properties']['group']['enum'])
    if {rule['group'] for rule in required_rules} != groups:
        raise ValueError('missing mandatory rule group')
    if not math.isclose(sum(rule['reward_weight'] for rule in protocol['rules']), 1.0, abs_tol=1e-9):
        raise ValueError('reward weights are not normalized')
    for rule in protocol['rules']:
        for key, known in [('chain_ids', chains), ('site_ids', sites), ('state_ids', states), ('step_ids', steps)]:
            if not set(rule[key]).issubset(known):
                raise ValueError(f'rule references unknown {key}')
    for group in ['fold_and_physical_integrity', 'assembly_and_interface']:
        covered = {chain for rule in required_rules if rule['group'] == group for chain in rule['chain_ids']}
        if covered != chains:
            raise ValueError(f'incomplete chain coverage in {group}')
    for group in ['reactive_geometry', 'protonation_and_stabilization', 'states_and_chemical_steps']:
        covered = {site for rule in required_rules if rule['group'] == group for site in rule['site_ids']}
        if covered != set(sites):
            raise ValueError(f'incomplete site coverage in {group}')
    chemical_rules = [rule for rule in required_rules if rule['group'] == 'states_and_chemical_steps']
    for key, items in [('state_ids', states), ('step_ids', steps)]:
        for identifier, item in items.items():
            covered = {site for rule in chemical_rules if identifier in rule[key] for site in rule['site_ids']}
            if not set(item['site_ids']).issubset(covered):
                raise ValueError('missing state/step-site chemistry rule')


def synthetic_protocol(schema: dict, kind: str) -> dict:
    """In-memory schema fixture. Dummy hashes/paths are NOT scientific evidence."""
    def artifact(name: str) -> dict:
        return {'path_or_uri': f'synthetic://not-scientific-evidence/{name}',
                'sha256': '0' * 64, 'description': 'SYNTHETIC contract fixture; no scientific calculation or artifact'}

    chains = ['A'] if kind == 'monomer' else ['A', 'B']
    sites = [f'site_{chain}' for chain in chains]
    assembly = {
        'kind': kind, 'subunit_count': len(chains), 'unique_sequence_count': 1,
        'sequence_groups': [{'sequence_id': 'shared_sequence', 'chain_ids': chains}],
        'reference_assembly': artifact('reference'), 'chain_map': artifact('chain_map'),
        'assembly_evidence': [artifact('assembly_evidence')],
        'design_symmetry': 'C1' if kind == 'monomer' else 'C2',
        'state_policy': artifact('state_policy'),
        'active_sites': [{'site_id': site, 'chain_ids': [chain], 'catalytic_map': artifact(site)}
                         for chain, site in zip(chains, sites)],
    }
    if kind == 'homodimer':
        assembly['interface_protocol'] = artifact('interface_protocol')
    groups = schema['$defs']['rule']['properties']['group']['enum']
    rules = [
        {'rule_id': f'rule_{group}', 'group': group, 'required': True,
         'metric': 'synthetic_boolean', 'units': 'boolean', 'chain_ids': chains, 'site_ids': sites,
         'state_ids': ['reactant', 'product'], 'step_ids': ['conversion'], 'reference_atoms': [],
         'acceptance': {'operator': 'eq', 'value': True},
         'applicability_and_uncertainty': artifact('applicability'),
         'reward_weight': 1 / len(groups), 'reward_transform': {'kind': 'binary'}}
        for group in groups
    ]
    return {
        'schema_version': '2.0', 'profile_id': f'synthetic_{kind}', 'version': 'fixture-only',
        'status': 'draft', 'scope': {'protein_form': 'soluble', 'cofactors': 'none',
            'supported_hosts': ['synthetic'], 'pH_range': [0, 14], 'temperature_C_range': [0, 100],
            'condition_domain': 'synthetic test only'},
        'assembly': assembly, 'reaction': artifact('reaction'), 'motif': artifact('motif'),
        'motif_map': artifact('motif_map'), 'generator_conditions': artifact('generator'),
        'states': [{'state_id': role, 'role': role, 'model': artifact(role),
                    'chemistry_definition': artifact(role + '_chemistry'), 'site_ids': sites}
                   for role in ['reactant', 'product']],
        'steps': [{'step_id': 'conversion', 'from_state': 'reactant', 'to_state': 'product',
                   'intended_bond_changes': artifact('bond_changes'), 'site_ids': sites}],
        'chemistry': {**{key: artifact(key) for key in [
            'parameterization', 'qm_region_and_boundaries', 'electronic_states', 'method_settings',
            'sampling_settings', 'path_search_settings', 'uncertainty_policy']},
            'controls': [artifact('control')], 'allowed_barrier_types': ['electronic_energy']},
        'rules': rules, 'tool_lock': [{'tool_id': 'synthetic_contract_fixture', 'code_commit': '0' * 40,
            'model_weights': [], 'dataset_snapshots': [], 'license_access_record': artifact('license')}],
        'qualification_evidence': [],
        'execution_policy': {key: artifact(key) for key in [
            'generation_presets', 'refinement_presets', 'cost_model', 'minimum_chemistry_reservation',
            'diversity_and_ranking', 'retry_policy', 'allowed_edit_regions']},
    }


def check_assembly_contracts(schemas: dict) -> None:
    request = read_json('tasks/homodimer.request.example.json')
    validate_request(request, schemas['request'])
    require(True, 'homodimer request is structurally valid; scientific inputs remain unqualified')
    implicit = copy.deepcopy(request)
    del implicit['assembly']
    validate_request(implicit, schemas['request'])
    require(True, 'request can leave assembly unspecified for subsequent evidence-based resolution')
    bad = copy.deepcopy(request)
    bad['assembly']['mode'] = 'heterodimer'
    expect_invalid(bad, schemas['request'], 'unsupported requested heterodimer rejected')
    bad = copy.deepcopy(request)
    del bad['assembly']['reference_structure']
    expect_invalid(bad, schemas['request'], 'assembly identifier without structure reference rejected')
    for kind in ['monomer', 'homodimer']:
        validate_protocol(synthetic_protocol(schemas['protocol'], kind), schemas['protocol'])
        require(True, f'synthetic {kind} profile passes structural and declared semantic checks')
    base = synthetic_protocol(schemas['protocol'], 'homodimer')
    asymmetric = copy.deepcopy(base)
    asymmetric['assembly']['design_symmetry'] = 'asymmetric'
    validate_protocol(asymmetric, schemas['protocol'])
    require(True, 'homodimer identity does not impose exact geometric symmetry')
    shared_site = copy.deepcopy(base)
    shared_site['assembly']['active_sites'] = [
        {**shared_site['assembly']['active_sites'][0], 'site_id': 'shared', 'chain_ids': ['A', 'B']}]
    for items in [shared_site['states'], shared_site['steps'], shared_site['rules']]:
        for item in items:
            item['site_ids'] = ['shared']
    validate_protocol(shared_site, schemas['protocol'])
    require(True, 'a homodimer may define an interface-spanning site instead of two independent sites')

    cases = []
    def bad_case(name, mutate):
        bad = copy.deepcopy(base)
        mutate(bad)
        cases.append((name, bad))
    bad_case('missing assembly block rejected', lambda p: p.pop('assembly'))
    bad_case('legacy profile version rejected', lambda p: p.update(schema_version='1.0'))
    bad_case('homodimer with one copy rejected', lambda p: p['assembly'].update(subunit_count=1))
    bad_case('homodimer with different unique sequences rejected', lambda p: p['assembly'].update(unique_sequence_count=2))
    bad_case('homodimer with duplicate chain identifiers rejected', lambda p: p['assembly']['sequence_groups'][0].update(chain_ids=['A', 'A']))
    bad_case('homodimer with three chains rejected', lambda p: p['assembly']['sequence_groups'][0].update(chain_ids=['A', 'B', 'C']))
    bad_case('homodimer missing interface protocol rejected', lambda p: p['assembly'].pop('interface_protocol'))
    bad_case('missing assembly evidence rejected', lambda p: p['assembly'].update(assembly_evidence=[]))
    bad_case('missing catalytic-state policy rejected', lambda p: p['assembly'].pop('state_policy'))
    bad_case('site referencing absent chain rejected', lambda p: p['assembly']['active_sites'][0].update(chain_ids=['C']))
    bad_case('duplicate site identity rejected', lambda p: p['assembly']['active_sites'][1].update(site_id='site_A'))
    bad_case('state referencing unknown site rejected', lambda p: p['states'][0].update(site_ids=['unknown']))
    bad_case('step referencing unknown endpoint rejected', lambda p: p['steps'][0].update(to_state='unknown'))
    bad_case('step site absent from endpoint rejected', lambda p: p['states'][0].update(site_ids=['site_A']))
    bad_case('missing second-site chemical-step coverage rejected', lambda p: p['steps'][0].update(site_ids=['site_A']))
    bad_case('required assembly gate cannot be made optional', lambda p: p['rules'][-1].update(required=False))
    bad_case('interface gate cannot omit partner chain', lambda p: p['rules'][-1].update(chain_ids=['A']))
    bad_case('required chemistry cannot omit second site', lambda p: p['rules'][3].update(site_ids=['site_A']))
    bad_case('required chemistry cannot omit step evidence', lambda p: p['rules'][3].update(step_ids=[]))
    bad_case('rule cannot refer to absent chain', lambda p: p['rules'][0].update(chain_ids=['C']))
    bad_case('unnormalized rewards rejected', lambda p: p['rules'][0].update(reward_weight=0.5))
    bad_case('non-finite profile values rejected', lambda p: p['scope'].update(pH_range=[0, float('nan')]))
    bad_case('qualified label without evidence rejected', lambda p: p.update(status='qualified'))
    for name, protocol in cases:
        try:
            validate_protocol(protocol, schemas['protocol'])
        except (ValidationError, ValueError):
            require(True, name)
        else:
            raise AssertionError(name)
    for protocol, req, name in [
        (base, read_json('tasks/request.example.json'), 'explicit monomer request cannot silently use a homodimer profile'),
        (synthetic_protocol(schemas['protocol'], 'monomer'), request, 'explicit homodimer request cannot silently use a monomer profile'),
    ]:
        try:
            validate_protocol(protocol, schemas['protocol'], req)
        except ValueError:
            require(True, name)
        else:
            raise AssertionError(name)


def main() -> None:
    required_files = [
        'README.md', 'ENVIRONMENT_SPEC.md',
        'config/environment.yaml', 'config/request.schema.json',
        'config/protocol.schema.json', 'tasks/denovo_enzyme_001.md',
        'tasks/request.example.json', 'tests/ACCEPTANCE.md',
        'tasks/homodimer.request.example.json',
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
    for basis in ['subunit_equivalents', 'assembled_complexes']:
        concentration_request = copy.deepcopy(request)
        concentration_request['conditions'].update(protein_concentration_uM=1.0, protein_concentration_basis=basis)
        validate_request(concentration_request, schemas['request'])
        require(True, f'paired concentration and {basis} basis accepted as syntax only')
    cases = []
    bad = copy.deepcopy(request); del bad['reaction']; cases.append((bad, 'missing reaction rejected'))
    bad = copy.deepcopy(request); bad['execution']['final_count'] = 0; cases.append((bad, 'zero shortlist count rejected'))
    bad = copy.deepcopy(request); bad['execution']['budget']['gpu_hours'] = 0; cases.append((bad, 'zero required compute budget rejected'))
    bad = copy.deepcopy(request); bad['execution']['controller_mode'] = 'unrestricted'; cases.append((bad, 'unknown controller mode rejected'))
    bad = copy.deepcopy(request); bad['constraints']['length'] = {'min': 300, 'max': 150}; cases.append((bad, 'reversed length bounds rejected'))
    bad = copy.deepcopy(request); bad['execution']['final_count'] = 6; cases.append((bad, 'shortlist above chemistry cap rejected'))
    bad = copy.deepcopy(request); bad['execution']['max_chemistry_candidates'] = 101; cases.append((bad, 'chemistry cap above generation cap rejected'))
    bad = copy.deepcopy(request); bad['conditions']['pH'] = float('nan'); cases.append((bad, 'non-finite numeric input rejected'))
    bad = copy.deepcopy(request); bad['conditions']['protein_concentration_uM'] = 1.0; cases.append((bad, 'concentration without normalization basis rejected'))
    bad = copy.deepcopy(request); bad['conditions']['protein_concentration_basis'] = 'subunit_equivalents'; cases.append((bad, 'normalization basis without concentration rejected'))
    for value in [0, -1, float('nan')]:
        bad = copy.deepcopy(request)
        bad['conditions'].update(protein_concentration_uM=value, protein_concentration_basis='subunit_equivalents')
        cases.append((bad, f'invalid protein concentration {value} rejected'))
    bad = copy.deepcopy(request); bad['conditions'].update(protein_concentration_uM=1.0, protein_concentration_basis='unspecified'); cases.append((bad, 'ambiguous concentration basis rejected'))
    for bad, name in cases:
        expect_invalid(bad, schemas['request'], name)
    check_assembly_contracts(schemas)

    config = yaml.safe_load((ROOT/'config/environment.yaml').read_text())
    require(config['maturity'] == 'Specification', 'maturity remains Specification')
    require(config['scientific_execution_included'] is False, 'no scientific implementation claimed')
    require(config['qualified_profiles_included'] is False, 'no qualified chemistry profile claimed')
    require(config['scope']['require_qualified_reaction_profile'] is True, 'qualified reaction profile required')
    require(config['schema_version'] == '2.0', 'configuration uses explicit assembly contract version')
    require(config['scope']['supported_assemblies'] == ['monomer', 'homodimer'], 'specified assembly scope is monomer and homodimer')
    require(config['scope']['request_assembly_fallback'] == 'resolve_from_evidence', 'unspecified assembly never defaults to monomer')
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
    require(set(config['required_rule_groups']) == rule_groups and len(rule_groups) == 9, 'protocol and configuration agree on nine required rule groups')
    require({'solubility', 'aggregation', 'states_and_chemical_steps'}.issubset(rule_groups), 'solubility, aggregation and chemistry are separate mandatory groups')
    qualification = config['qualification']
    require(qualification['required_rule_combiner'] == 'all', 'qualification requires every mandatory rule')
    require(not qualification['unresolved_can_qualify'] and not qualification['fail_can_qualify'], 'failed and unresolved evidence cannot qualify')
    require(not qualification['score_compensation_across_hard_rules'], 'hard-rule failures cannot be compensated')
    require(not qualification['return_failed_to_fill_shortlist'], 'failed designs cannot fill a shortlist')
    require(qualification['missing_raw_value'] is None, 'missing raw measurements remain null')
    require({'assembly', 'chain_mapping', 'site_coverage'}.issubset(config['controller']['immutable_to_policy']), 'policy cannot change assembly or site coverage')
    require(config['assembly_contract']['average_cannot_hide_required_site_failure'], 'site failures cannot be hidden by averages')
    require(config['assembly_contract']['homodimer_chain_sequences'] == 'identical', 'homodimer sequence copies must match')

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
            'coordinate-artifact validation, assembly reconstruction or scientific interface assessment',
            'execution or scientific qualification of either assembly route',
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
