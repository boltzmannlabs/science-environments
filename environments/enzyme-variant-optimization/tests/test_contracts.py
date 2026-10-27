import copy
import json
import pytest

from enzyme_research.contracts import ResearchError, task_contract, candidate_record, safe_data, strict_load


@pytest.mark.parametrize("field,value", [("objective", ""), ("evidence_track", "experimental_success"),
    ("allowed_jobs", []), ("evidence_sources", []), ("schema_version", "old")])
def test_invalid_tasks(task, field, value):
    task[field] = value
    with pytest.raises(ResearchError): task_contract(task)


@pytest.mark.parametrize("field,value", [("max_rounds", 4), ("max_unique_candidates", 61),
    ("max_outstanding_jobs", 2), ("max_scientific_submissions", 0), ("max_rounds", True)])
def test_budget_types_and_caps(task, field, value):
    task["budget"][field] = value
    with pytest.raises(ResearchError): task_contract(task)


@pytest.mark.parametrize("sequence", ["AACAAAAAAA", "AGXAAAAAAA", "AGAAAAAAA", "agcaaaaaaa"])
def test_catalytic_or_sequence_errors(task, sequence):
    with pytest.raises(ResearchError): candidate_record(task, {"candidate_id": "c1", "parent_id": "parent", "sequence": sequence})


@pytest.mark.parametrize("value", [{"tokenid": "private"}, {"nested": {"experimental_score": 2}},
    {"url": "https://example.test/a?X-Goog-Signature=private"}, {"x": float("nan")}, {"x": "Bearer secret"}])
def test_no_answers_or_credentials(value):
    with pytest.raises(ResearchError): safe_data(value)


def test_duplicate_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"x":1,"x":2}')
    with pytest.raises(ResearchError): strict_load(path)


def test_unknown_task_fields(task):
    task["max_workers"] = 8
    with pytest.raises(ResearchError): task_contract(task)


def test_valid_candidate_invalidate_structure(task):
    result = candidate_record(task, {"candidate_id": "c1", "parent_id": "parent", "sequence": "AGCAAAAAAA"})
    assert result["structure_status"] == "requires_new_structure"
    assert result["mutations_from_reference"] == ["A3C"]
