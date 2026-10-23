from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_eighteen_specialist_contracts_are_frozen_in_manifest() -> None:
    manifest = json.loads((ROOT / "tasks/manifest.json").read_text())
    assert manifest["task_count"] == 18
    assert len(list((ROOT / "contracts").glob("agent_*.json"))) == 18
    assert len(manifest["tasks"]) == 18


def test_five_workflows_have_explicit_steps() -> None:
    data = json.loads((ROOT / "workflows/manifest.json").read_text())
    assert data["workflow_count"] == 5
    assert all(item["steps"] for item in data["workflows"])


def test_pilot_fixture_is_explicit_and_not_claimed_as_reference() -> None:
    fixture = ROOT / "references/pilot_initial_geometry.xyz"
    assert fixture.read_text().splitlines()[0] == "3"
    assert "placeholder" in (ROOT / "references/README.md").read_text()


def test_all_eighteen_contracts_are_covered_by_tasks_and_prompts() -> None:
    manifest = json.loads((ROOT / "tasks/manifest.json").read_text())
    ids = {task["agent_id"] for task in manifest["tasks"]}
    assert ids == {f"{i:02d}" for i in range(1, 19)}
    assert len(list((ROOT / "tasks/prompts").glob("task_*.md"))) == 18


def test_agent_qualification_matrix_has_one_result_per_agent() -> None:
    data = json.loads((ROOT / "reports/agent_qualification/summary.json").read_text())
    assert data["agent_count"] == 18
    assert len(data["results"]) == 18
    assert {row["agent_id"] for row in data["results"]} == {f"{i:02d}" for i in range(1, 19)}


def test_common_input_pack_has_eighteen_packets_and_expected_adversarial_case() -> None:
    data = json.loads((ROOT / "reports/suite/summary.json").read_text())
    assert data["agent_packets"] == 18
    assert data["valid_packets"] == 18
    malformed = next(x for x in data["structures"] if x["case"] == "GEO-004-malformed-input")
    assert malformed["valid"] is False


def test_expanded_case_set_and_production_qmmm_evidence_exist() -> None:
    expanded = json.loads((ROOT / "cases/expanded_v1/manifest.json").read_text())
    assert expanded["case_count"] == 36
    qmmm = json.loads((ROOT / "reports/production_qmmm/qualification.json").read_text())
    assert qmmm["status"] == "pass"
    assert qmmm["checks"]["electronic_embedding_active"] is True
    assert qmmm["checks"]["scf_converged"] is True
