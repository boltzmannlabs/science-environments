"""Check review provenance, numerical invariants and original-file preservation."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = 'task_001_d2r_peripheral_candidate_prioritisation'
RESULT = ROOT / 'results' / TASK
BENCH = RESULT / 'benchmark_results'

def validate(root=ROOT):
    errors = []
    result = root / 'results' / TASK
    bench = result / 'benchmark_results'
    metric = json.loads((bench / 'metrics.json').read_text())
    manifest = json.loads((result / 'submission_manifest.json').read_text())
    for record in manifest['files']:
        path = result / ('task_as_executed.md' if record['path']=='task.md' else 'submitted/' + record['path'].removeprefix('deliverables/'))
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
            errors.append('Supplied artifact changed: ' + record['path'])
    if (result/'task_as_executed.md').read_bytes() != (root/'tasks'/(TASK+'.md')).read_bytes():
        errors.append('Canonical task differs from executed task')
    if not metric['library']['all_input_identity_checks_pass']:
        errors.append('Source input identities not verified')
    agent = metric['agent']
    if not agent['NESSO_rows_match_input_and_DRD2_sequence'] or not agent['NESSO_values_match_integrated_table']:
        errors.append('Affinity source mappings differ')
    if agent['vina_pose_rows'] != agent['vina_SDF_pose_count'] or not agent['vina_ranking_matches_raw_pose_minima']:
        errors.append('Vina CSV/SDF/minimum-score reconciliation differs')
    if agent['diffdock_numeric_pose_rows'] + agent['diffdock_rows_without_confidence'] != agent['diffdock_raw_table_rows']:
        errors.append('DiffDock accounting incomplete')
    if agent['diffdock_compounds_with_returned_poses'] != 20 or agent['final_shortlist_with_diffdock_count'] != 5:
        errors.append('Frozen DiffDock count changed; review the source snapshot')
    defs = json.loads((result/'audit/endpoint_definitions_as_returned.json').read_text())
    if defs['BCRP']['display'] != 'BCRP inhibitor':
        errors.append('BCRP source definition changed')
    if metric['new_scientific_jobs_run_by_this_review'] != 0:
        errors.append('Unexpected claim of a new scientific job')
    if len(list(csv.DictReader((bench/'compound_comparison.csv').open()))) != 400:
        errors.append('Comparison must account for 400 library IDs')
    return errors

if __name__ == '__main__':
    problems = validate()
    print('\n'.join(problems) if problems else 'PASS: original artifacts, task identity, numerical mappings, endpoint definitions and coverage reconciliation')
    raise SystemExit(bool(problems))
