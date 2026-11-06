"""Task-profile routing and declared-identifier checks; no inference or scientific grading."""
import argparse
import json
import sys
from pathlib import Path

import yaml

from contract_io import require, read_json, sha256, _finite, _artifact_entries, artifact_path
from schema_registry import environment_config, config_path, validator_for_path


def task_profile(task):
    profiles = environment_config()['task_profiles']
    require(task in profiles, f'Unknown task: {task}')
    profile = yaml.safe_load(config_path(profiles[task]).read_text())
    require(profile['task_id'] == task, 'Profile task ID mismatch')
    return profile


def unique_ids(records, field, label):
    values = [item[field] for item in records]
    require(len(values) == len(set(values)), f'Duplicate {label}')
    return set(values)


def request_semantics(value, family):
    if family == 'monoclonal_target_only':
        require(value['evaluation']['requested_count'] <= value['constraints']['max_candidates'],
                'Requested count exceeds candidate budget')
        require({'identity', 'structure', 'interface', 'binding', 'specificity', 'developability'} <=
                set(value['evaluation']['required_evidence_domains']),
                'Target-only request omits mandatory evidence domains')
        if value['discovery']['candidate_origin'] != 'generated':
            require(value['discovery']['source_artifacts'], 'Retrieved/library candidates require source artifacts')
    if family == 'bispecific_design':
        targets = unique_ids(value['targets'], 'target_id', 'target IDs')
        architecture = value['architecture']
        chains = unique_ids(architecture['chains'], 'chain_id', 'chain IDs')
        unique_ids(architecture['arms'], 'arm_id', 'arm IDs')
        specificity = {(arm['target_id'], arm['epitope_id']) for arm in architecture['arms']}
        require(len(specificity) == 2, 'Bispecific request must declare two distinct specificities')
        for arm in architecture['arms']:
            require(arm['target_id'] in targets, 'Arm references an undeclared target')
            require(set(arm['chain_ids']) <= chains, 'Arm references an undeclared chain')
        require(value['constraints']['requested_count'] <= value['constraints']['candidate_budget'],
                'Requested count exceeds candidate budget')
        domains = set(value['evaluation']['required_evidence_domains'])
        require({'identity', 'arm_binding', 'assembly', 'function', 'developability', 'specificity'} <= domains,
                'Bispecific request omits mandatory evidence domains')
        if value['mechanism']['simultaneous_engagement'] == 'required':
            require('joint_engagement' in domains, 'Simultaneous engagement requires joint evidence')


def result_semantics(value, request, family):
    if family in {'monoclonal_target_only', 'bispecific_design'}:
        ids = unique_ids(value['records'], 'candidate_id', 'candidate IDs')
        require(set(value['shortlist']) <= ids, 'Shortlist references an undeclared candidate')
        if value['run_status'] in {'NEEDS_INPUT', 'PROTOCOL_REQUIRED', 'BLOCKED'}:
            require(not value['records'] and not value['shortlist'],
                    'Preflight failure cannot claim candidate records')
        count_key = request['evaluation'] if family == 'monoclonal_target_only' else request['constraints']
        require(value['requested_count'] == count_key['requested_count'], 'Requested count changed')
        count = len(value['shortlist'])
        require(count <= value['requested_count'], 'Shortlist exceeds requested count')
        if value['run_status'] == 'QUALIFIED':
            require(count == value['requested_count'], 'QUALIFIED requires the requested shortlist count')
        if value['run_status'] == 'PARTIAL':
            require(0 < count < value['requested_count'], 'PARTIAL requires a shorter nonempty shortlist')
        if value['run_status'] == 'NO_QUALIFYING_DESIGNS':
            require(not count, 'No-qualifying status cannot include a shortlist')
        require(value['provenance']['knowledge_cutoff'] == request['knowledge_cutoff'], 'Cutoff changed')
        protocol = request['evaluation']['protocol']
        require(value['provenance']['protocol_sha256'] == (protocol['sha256'] if protocol else None),
                'Protocol hash differs from request')
    if family == 'monoclonal_target_only':
        origins = unique_ids(value['candidate_origins'], 'candidate_id', 'origin IDs')
        require(origins == ids, 'Every target-only candidate needs exactly one origin record')
        require(value['sequence_scope'] == request['antibody']['sequence_scope'], 'Sequence scope changed')
        require(all(origin['origin'] == request['discovery']['candidate_origin']
                    for origin in value['candidate_origins']), 'Candidate origin differs from discovery policy')
        require(all(record['candidate_id'] in ids for record in value['assay_records']),
                'Assay record references an undeclared candidate')
    if family == 'bispecific_design':
        expected_arms = {arm['arm_id']: arm for arm in request['architecture']['arms']}
        expected_chains = {c['chain_id'] for c in request['architecture']['chains']}
        for record in value['records']:
            require(unique_ids(record['chains'], 'chain_id', 'result chain IDs') == expected_chains,
                    'Result chains differ from the declared architecture')
            require(unique_ids(record['arm_assignments'], 'arm_id', 'result arm IDs') == set(expected_arms),
                    'Result arms differ from the declared architecture')
            require(unique_ids(record['arm_evidence'], 'arm_id', 'arm evidence IDs') == set(expected_arms),
                    'Missing or extra arm evidence')
            for arm in record['arm_assignments']:
                declared = expected_arms[arm['arm_id']]
                require(arm['target_id'] == declared['target_id'] and
                        set(arm['chain_ids']) == set(declared['chain_ids']), 'Arm assignment changed')
            if record['candidate_id'] in value['shortlist']:
                require(record['eligibility'] == 'PASS' and record['whole_molecule_evidence'] and
                        all(a['status'] == 'PASS' and a['evidence'] for a in record['arm_evidence']),
                        'Shortlisted bispecific needs both arms and whole-molecule evidence')
    if family == 'bispecific_assessment' and value['answer'] is not None:
        answer = value['answer']
        selected = answer.get('candidate_decision', answer.get('construct',
                          answer.get('recommendation', {}).get('recommended_shuttle')))
        if selected and selected != 'INDETERMINATE':
            require(selected in request['candidate_ids'], 'Answer selects an undeclared candidate')
        ratio = answer.get('fold_change')
        if ratio is not None:
            require({ratio['numerator_candidate'], ratio['denominator_candidate']} <= set(request['candidate_ids']),
                    'Fold change references an undeclared candidate')
            require(ratio['numerator_candidate'] != ratio['denominator_candidate'],
                    'Fold change must compare different candidates')
        for observation in answer.get('observations', []):
            require(observation['candidate_id'] in request['candidate_ids'],
                    'Observation references an undeclared candidate')


def validate_task_contract(value, task, kind='request', input_root=None, request_path=None):
    require(kind in {'request', 'result'}, 'Unknown contract kind')
    _finite(value)
    profile = task_profile(task)
    validator_for_path(config_path(profile[f'{kind}_schema'])).validate(value)
    if 'variant' in profile:
        require(value.get('variant') == profile['variant'], 'DENV prompt variant does not match profile')
    family = profile['family']
    if kind == 'request':
        if family == 'monoclonal_reference':
            # Import lazily to reuse the existing semantic owner without a module cycle.
            from monoclonal_antibody_with_reference.validation import validate_request
            validate_request(value)
        else:
            request_semantics(value, family)
    else:
        require(request_path is not None, 'Result contract checking requires --request')
        request = read_json(request_path)
        validate_task_contract(request, task)
        request_digest = value.get('request_sha256', value.get('provenance', {}).get('request_sha256'))
        require(request_digest == sha256(request_path), 'Result request hash mismatch')
        require(value['task_id'] == request['task_id'], 'Result task ID mismatch')
        result_semantics(value, request, family)
    if input_root is not None:
        for artifact in _artifact_entries(value):
            artifact_path(artifact, Path(input_root))
    return {'status': 'CONTRACT_VALID', 'task': task, 'kind': kind,
            'artifacts_checked': input_root is not None,
            'scope': 'Schema and declared-identifier checks only; no scientific grading or execution. '
                     'An incomplete request can satisfy a schema. This is not a readiness result.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('document', type=Path)
    parser.add_argument('--task', required=True)
    parser.add_argument('--kind', choices=['request', 'result'], default='request')
    parser.add_argument('--input-root', type=Path, help='Check referenced files and SHA-256')
    parser.add_argument('--request', type=Path, help='Frozen request file, required for results')
    args = parser.parse_args()
    try:
        result = validate_task_contract(read_json(args.document), args.task, args.kind,
                                        args.input_root, args.request)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as exc:
        print(f'INVALID: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
