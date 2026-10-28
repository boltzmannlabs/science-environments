"""Runtime evidence contracts. Structural checks do not certify enzyme activity."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {'reaction_identity', 'reactive_geometry', 'protonation_and_stabilization',
          'states_and_chemical_steps', 'fold_and_physical_integrity', 'solubility',
          'aggregation', 'operating_compatibility', 'assembly_and_interface'}
STAGES = ('prepare', 'generate', 'sequence_screen', 'fold', 'aggregation',
          'complex', 'catalytic_states', 'chemistry', 'evaluate')
EXPECTED = {'prepare': ['resolved_request', 'generation_profile', 'evaluation_plan'],
            'generate': ['candidate_manifest'],
            **{s: ['candidate_manifest', 'stage_evidence'] for s in STAGES[2:-1]},
            'evaluate': ['evaluation']}


def load_json(path: Path) -> Any:
    def invalid(value):
        raise ValueError(f'Non-finite JSON number: {value}')
    value = json.loads(path.read_text(), parse_constant=invalid)
    json.dumps(value, allow_nan=False)
    return value


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def object_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def artifact_path(ref: dict, base: Path) -> Path:
    if not isinstance(ref, dict):
        raise ValueError('Artifact reference must be an object')
    raw = ref.get('path_or_uri', ref.get('path'))
    if not isinstance(raw, str) or not raw or '://' in raw:
        raise ValueError('Evidence must be materialized as a local file before use')
    p = Path(raw)
    return (p if p.is_absolute() else base / p).resolve()


def verify_artifact(ref: dict, base: Path) -> Path:
    p = artifact_path(ref, base)
    if not p.is_file() or ref.get('sha256') != digest(p):
        raise ValueError(f'Missing or changed evidence: {p}')
    return p


def verify_nested(value: Any, base: Path) -> None:
    if isinstance(value, dict):
        if ('path_or_uri' in value or 'path' in value) and 'sha256' in value:
            verify_artifact(value, base)
        for item in value.values():
            verify_nested(item, base)
    elif isinstance(value, list):
        for item in value:
            verify_nested(item, base)


def schema_check(value: dict, name: str) -> None:
    Draft202012Validator(load_json(ROOT / 'config' / name)).validate(value)


def check_generation(value: dict, base: Path) -> None:
    schema_check(value, 'generation.schema.json')
    if value['status'] != 'ready':
        raise ValueError('Generation inputs are still draft')
    a = value['assembly']
    chains = a['sequence_groups'][0]['chain_ids']
    if len(set(chains)) != a['subunit_count'] or len(chains) != len(set(chains)):
        raise ValueError('Generation chain mapping is inconsistent')
    sites = a['active_sites']
    if len({s['site_id'] for s in sites}) != len(sites):
        raise ValueError('Duplicate generation site identifier')
    if any(not set(s['chain_ids']).issubset(chains) for s in sites):
        raise ValueError('Generation site references an unknown chain')
    verify_nested(value, base)


def check_request(value: dict) -> None:
    schema_check(value, 'request.schema.json')
    json.dumps(value, allow_nan=False)
    length = value['constraints']['length']
    e = value['execution']
    if length['min'] > length['max']:
        raise ValueError('Reversed sequence length range')
    if not e['final_count'] <= e['max_chemistry_candidates'] <= e['max_generated']:
        raise ValueError('Inconsistent candidate quotas')
    if e['controller_mode'] != 'fixed':
        raise ValueError('This runtime implements fixed execution; RL needs a separate integration')


def _indexed(items: list[dict], field: str) -> dict:
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError(f'{field} collection must be a list of objects')
    result = {}
    for item in items:
        identifier = item.get(field)
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', identifier):
            raise ValueError(f'Invalid {field}')
        if identifier in result:
            raise ValueError(f'Duplicate {field}: {identifier}')
        result[identifier] = item
    return result


def _numeric(value: Any) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _acceptance_valid(rule: dict) -> None:
    operator = rule['acceptance']['operator']
    target = rule['acceptance']['value']
    if operator in {'ge', 'le'} and not _numeric(target):
        raise ValueError('Ordered acceptance requires a finite numeric threshold')
    if operator == 'between':
        if not isinstance(target, list) or len(target) != 2 or not all(map(_numeric, target)):
            raise ValueError('Between acceptance requires two finite numeric bounds')
        if target[0] > target[1]:
            raise ValueError('Acceptance bounds are reversed')
    if operator == 'in' and (not isinstance(target, list) or not target):
        raise ValueError('Membership acceptance requires a nonempty list')
    if isinstance(target, bool) and rule['units'] != 'boolean':
        raise ValueError('Boolean acceptance requires boolean units')
    if rule['units'] == 'boolean':
        if operator == 'eq' and not isinstance(target, bool):
            raise ValueError('Boolean equality requires a boolean threshold')
        if operator == 'in' and not all(isinstance(item, bool) for item in target):
            raise ValueError('Boolean membership requires boolean values')
        if operator in {'ge', 'le', 'between'}:
            raise ValueError('Boolean quantities cannot use numeric ordered acceptance')
    transform = rule['reward_transform']
    if transform['kind'] == 'bounded_linear' and transform['lower'] >= transform['upper']:
        raise ValueError('Reward transform bounds must increase')


def check_protocol(value: dict, base: Path) -> None:
    """Check a full qualified profile and its materialized evidence contracts.

    These checks enforce consistency and evidence identity, not the scientific
    truth of a profile's qualification claim. Independent scientific review is
    still required. Early exploratory generation uses check_generation instead.
    """
    schema_check(value, 'protocol.schema.json')
    json.dumps(value, allow_nan=False)
    if value['status'] != 'qualified':
        raise ValueError('Full chemistry profile remains unqualified')
    for name in ['pH_range', 'temperature_C_range']:
        if value['scope'][name][0] > value['scope'][name][1]:
            raise ValueError(f'Reversed profile domain: {name}')
    assembly = value['assembly']
    chains = set(assembly['sequence_groups'][0]['chain_ids'])
    if len(chains) != assembly['subunit_count']:
        raise ValueError('Assembly chain count mismatch')
    sites = _indexed(assembly['active_sites'], 'site_id')
    states = _indexed(value['states'], 'state_id')
    steps = _indexed(value['steps'], 'step_id')
    rules = _indexed(value['rules'], 'rule_id')
    for site in sites.values():
        if not set(site['chain_ids']).issubset(chains):
            raise ValueError('Active site refers to unknown chain')
    for state in states.values():
        if not set(state['site_ids']).issubset(sites):
            raise ValueError('State refers to unknown active site')
    for step in steps.values():
        if step['from_state'] not in states or step['to_state'] not in states:
            raise ValueError('Chemical step refers to unknown state')
        covered = set(step['site_ids'])
        if not covered.issubset(sites):
            raise ValueError('Chemical step refers to unknown active site')
        if any(not covered.issubset(states[step[end]]['site_ids'])
               for end in ['from_state', 'to_state']):
            raise ValueError('Chemical-step site is absent from an endpoint state')
    if {site for step in steps.values() for site in step['site_ids']} != set(sites):
        raise ValueError('Active-site chemical-step coverage is incomplete')
    if {step[end] for step in steps.values() for end in ['from_state', 'to_state']} != set(states):
        raise ValueError('Declared chemical states lack step coverage')
    required = [rule for rule in rules.values() if rule['required']]
    if {rule['group'] for rule in required} != GROUPS:
        raise ValueError('Mandatory scientific rule-group coverage is incomplete')
    if not math.isclose(sum(rule['reward_weight'] for rule in rules.values()), 1.0,
                        rel_tol=0, abs_tol=1e-9):
        raise ValueError('Rule reward weights do not sum to one')
    for rule in rules.values():
        _acceptance_valid(rule)
        for key, known in [('chain_ids', chains), ('site_ids', sites),
                           ('state_ids', states), ('step_ids', steps)]:
            if not set(rule[key]).issubset(known):
                raise ValueError(f'Rule references unknown {key}')
    for group in ['fold_and_physical_integrity', 'assembly_and_interface']:
        if {chain for rule in required if rule['group'] == group
            for chain in rule['chain_ids']} != chains:
            raise ValueError(f'Incomplete chain coverage in {group}')
    for group in ['reactive_geometry', 'protonation_and_stabilization', 'states_and_chemical_steps']:
        if {site for rule in required if rule['group'] == group
            for site in rule['site_ids']} != set(sites):
            raise ValueError(f'Incomplete active-site coverage in {group}')
    chemistry_rules = [rule for rule in required if rule['group'] == 'states_and_chemical_steps']
    for key, items in [('state_ids', states), ('step_ids', steps)]:
        for identifier, item in items.items():
            coverage = {site for rule in chemistry_rules if identifier in rule[key]
                        for site in rule['site_ids']}
            if not set(item['site_ids']).issubset(coverage):
                raise ValueError('Missing state/step-site chemistry rule')
    verify_nested(value, base)
    for ref in value['qualification_evidence'] + value['chemistry']['controls']:
        if verify_artifact(ref, base).stat().st_size == 0:
            raise ValueError('Qualification and chemistry-control evidence cannot be empty')


def candidate_hash(candidate: dict) -> str:
    """Bind a result to a particular sequence/structure revision, not its label."""
    try:
        return object_hash({key: candidate[key] for key in
                            ['candidate_id', 'revision', 'sequence', 'structure']})
    except KeyError as exc:
        raise ValueError(f'Candidate identity is missing {exc.args[0]}') from exc


def _fasta_sequence(path: Path) -> str:
    records = []
    current = None
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if not line[1:].strip():
                raise ValueError('FASTA header is empty')
            if current is not None:
                records.append(''.join(current))
            current = []
        else:
            if current is None:
                raise ValueError('Sequence artifact must use FASTA headers')
            if not re.fullmatch('[ACDEFGHIKLMNPQRSTVWY]+', line):
                raise ValueError('Sequence must contain canonical uppercase amino acids only')
            current.append(line)
    if current is not None:
        records.append(''.join(current))
    if not records or any(not record for record in records) or len(set(records)) != 1:
        raise ValueError('Each assembly needs exactly one unique nonempty FASTA sequence')
    return records[0]


def _candidate_shape(candidate: dict, base: Path) -> str:
    _indexed([candidate], 'candidate_id')
    revision = candidate.get('revision')
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
        raise ValueError('Candidate revision must be a positive integer')
    if candidate.get('generation_kind') != 'de_novo' or candidate.get('sequence_designed') is not True:
        raise ValueError('A fixture, placeholder or reference-backbone redesign is not a de novo candidate')
    if candidate.get('status') not in {'exploratory', 'screened', 'chemistry_evaluated',
                                      'rejected', 'unresolved'}:
        raise ValueError('Candidate status cannot claim qualification before final evaluation')
    if 'sequence' not in candidate or 'structure' not in candidate:
        raise ValueError('Candidate sequence and structure artifacts are required')
    sequence = _fasta_sequence(verify_artifact(candidate['sequence'], base))
    if verify_artifact(candidate['structure'], base).stat().st_size == 0:
        raise ValueError('Candidate structure artifact is empty')
    candidate_hash(candidate)
    return sequence


def check_candidates(manifest: dict, base: Path, request: dict) -> None:
    """Validate candidate records, file identity and sequence/assembly quotas.

    Coordinate interpretation (chain mapping, physical geometry, motif retention)
    is performed by scientific adapters and reviewers, not this file validator.
    """
    check_request(request)
    if not isinstance(manifest, dict) or 'candidates' not in manifest:
        raise ValueError('Candidate manifest requires a candidates list')
    json.dumps(manifest, allow_nan=False)
    candidates = _indexed(manifest['candidates'], 'candidate_id')
    execution = request['execution']
    if len(candidates) > execution['max_generated']:
        raise ValueError('Candidate manifest exceeds the generation quota')
    chemistry_count = sum(c.get('status') == 'chemistry_evaluated' for c in candidates.values())
    if chemistry_count > execution['max_chemistry_candidates']:
        raise ValueError('Candidate manifest exceeds the chemistry quota')
    bounds = request['constraints']['length']
    for candidate in candidates.values():
        sequence = _candidate_shape(candidate, base)
        if not bounds['min'] <= len(sequence) <= bounds['max']:
            raise ValueError('Candidate sequence violates requested per-chain length')


def _equal(value: Any, target: Any) -> bool:
    # bool is a Python int subclass: True must not satisfy a numeric value of 1.
    if isinstance(target, bool) or isinstance(value, bool):
        return isinstance(value, bool) and isinstance(target, bool) and value == target
    if _numeric(value) and _numeric(target):
        return value == target
    if isinstance(value, list) and isinstance(target, list):
        return len(value) == len(target) and all(_equal(a, b) for a, b in zip(value, target))
    return type(value) is type(target) and value == target


def _matches(value: Any, acceptance: dict) -> bool:
    operator, target = acceptance['operator'], acceptance['value']
    if operator == 'eq':
        return _equal(value, target)
    if operator == 'in':
        return any(_equal(value, item) for item in target)
    if not _numeric(value):
        return False
    if operator == 'ge':
        return value >= target
    if operator == 'le':
        return value <= target
    if operator == 'between':
        return target[0] <= value <= target[1]
    raise ValueError(f'Unknown frozen acceptance operator: {operator}')


def qualified_ids(evaluation: dict, manifest: dict, protocol: dict, base: Path) -> list[str]:
    """Return only current candidates satisfying every mandatory frozen rule.

    Missing or failed scientific measurements yield no qualification. Malformed
    identities, changed evidence or altered coverage are contract errors. Evidence
    content and control validity must additionally pass independent scientific
    review; nonempty files and self-reported PASS labels are not scientific proof.
    """
    check_protocol(protocol, base)
    if not isinstance(evaluation, dict) or not isinstance(manifest, dict):
        raise ValueError('Evaluation and manifest must be objects')
    json.dumps(evaluation, allow_nan=False)
    candidates = _indexed(manifest.get('candidates'), 'candidate_id')
    for candidate in candidates.values():
        _candidate_shape(candidate, base)
    rows = _indexed(evaluation.get('candidates'), 'candidate_id')
    rules = _indexed(protocol['rules'], 'rule_id')
    required = {identifier for identifier, rule in rules.items() if rule['required']}
    accepted = []
    for candidate_id, row in rows.items():
        if candidate_id not in candidates:
            raise ValueError('Evaluation refers to a candidate outside the current manifest')
        candidate = candidates[candidate_id]
        if row.get('candidate_sha256') != candidate_hash(candidate):
            raise ValueError('Evaluation is bound to a stale or unknown candidate revision')
        measured = _indexed(row.get('rules'), 'rule_id')
        if not set(measured).issubset(rules):
            raise ValueError('Evaluation introduced a rule absent from the frozen profile')
        passes = candidate['status'] == 'chemistry_evaluated' and required.issubset(measured)
        for identifier, metric in measured.items():
            rule = rules[identifier]
            if metric.get('status') not in {'PASS', 'FAIL', 'UNRESOLVED'}:
                raise ValueError('Rule outcome must be PASS, FAIL or UNRESOLVED')
            if 'value' not in metric or 'units' not in metric or 'evidence' not in metric:
                raise ValueError('Rule measurements require value, units and evidence fields')
            if metric['units'] != rule['units']:
                raise ValueError('Measurement units differ from the frozen rule')
            evidence = metric['evidence']
            if not isinstance(evidence, list):
                raise ValueError('Rule evidence must be a list of artifact references')
            for ref in evidence:
                if verify_artifact(ref, base).stat().st_size == 0:
                    raise ValueError('Rule evidence artifact is empty')
            for key in ['chain_ids', 'site_ids', 'state_ids', 'step_ids']:
                if key in metric and (not isinstance(metric[key], list)
                                      or sorted(metric[key]) != sorted(rule[key])):
                    raise ValueError('Measurement coverage differs from the frozen rule')
            if identifier in required:
                passes = passes and metric['status'] == 'PASS' and bool(evidence)
                passes = passes and metric['value'] is not None and _matches(metric['value'], rule['acceptance'])
        if passes:
            accepted.append(candidate_id)
    return accepted
