"""Regression checks for preserving a scientifically critical review record."""
import importlib.util
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
module_path = ROOT/'scripts/validate_d2r_review.py'
spec = importlib.util.spec_from_file_location('validate_d2r_review', module_path)
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)

def test_original_deliverables_and_coverage_are_preserved():
    assert review.validate(ROOT) == []

def test_scientific_findings_are_not_marked_as_success():
    metric = json.loads((ROOT/'results/task_001_d2r_peripheral_candidate_prioritisation/benchmark_results/metrics.json').read_text())
    assert metric['review_status'].startswith('scientific_corrections_required')
    assert metric['scope']['MD_required_by_task'] is False
    assert metric['selection_agreement_descriptive_only']['shortlist_overlap_count'] == 0
    assert metric['agent']['vina_first_pose_heavy_atom_topology_matches'] == 400
    assert metric['agent']['vina_first_pose_formula_matches'] < 400
