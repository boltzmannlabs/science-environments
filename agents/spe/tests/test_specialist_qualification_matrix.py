from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_IDS = [f"{number:02d}" for number in range(1, 21) if number not in {13, 16}]


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_matrix_covers_active_roster_with_three_unique_heldout_cases_each() -> None:
    matrix = load("reports/specialist_qualification_v1/qualification_matrix.json")
    assert [agent["environment_id"] for agent in matrix["agents"]] == ACTIVE_IDS
    assert matrix["summary"]["active_agents"] == 18

    test_ids = [
        case["test_id"]
        for agent in matrix["agents"]
        for case in agent["held_out_cases"]
    ]
    assert len(test_ids) == 54
    assert len(set(test_ids)) == 54
    assert all(len(agent["held_out_cases"]) >= 3 for agent in matrix["agents"])
    assert all(
        case["scenario"] and case["expected_outcome"]
        for agent in matrix["agents"]
        for case in agent["held_out_cases"]
    )


def test_execution_evidence_is_not_mislabeled_as_incremental_value() -> None:
    matrix = load("reports/specialist_qualification_v1/qualification_matrix.json")
    assert matrix["summary"]["execution_pass"] == 18
    assert matrix["summary"]["specialist_value_status_counts"] == {
        "measured-no-incremental-benefit": 1,
        "not-measured": 17,
    }
    assert not any(
        agent["specialist_value_qualification"]["status"] == "value-demonstrated"
        for agent in matrix["agents"]
    )
    assert all(
        agent["held_out_dataset_status"] == "specified-not-executed"
        for agent in matrix["agents"]
        if agent["environment_id"] != "20"
    )
    assert next(
        agent for agent in matrix["agents"] if agent["environment_id"] == "20"
    )["held_out_dataset_status"] == "executed-3-repeats"


def test_agent20_measurement_matches_frozen_v21_aggregate() -> None:
    matrix = load("reports/specialist_qualification_v1/qualification_matrix.json")
    agent20 = next(agent for agent in matrix["agents"] if agent["environment_id"] == "20")
    value = agent20["specialist_value_qualification"]
    aggregate = load(value["evidence"])["metrics"]

    assert value["status"] == "measured-no-incremental-benefit"
    assert value["comparison"]["general_agent"] == {
        key: aggregate["agent-scientist"][key]
        for key in value["comparison"]["general_agent"]
    }
    assert value["comparison"]["general_agent_plus_specialist"] == {
        key: aggregate["agent-scientist-plus-specialist"][key]
        for key in value["comparison"]["general_agent_plus_specialist"]
    }
    assert aggregate["agent-scientist"]["cases_passed"] == 27
    assert aggregate["agent-scientist-plus-specialist"]["cases_passed"] == 27
    assert (
        aggregate["agent-scientist-plus-specialist"]["total_runtime_seconds"]
        > aggregate["agent-scientist"]["total_runtime_seconds"]
    )


def test_matrix_contract_and_report_hashes_are_current() -> None:
    matrix = load("reports/specialist_qualification_v1/qualification_matrix.json")
    sources = matrix["source_integrity"]
    assert sources["qualification_plan_sha256"] == sha256(
        ROOT / "benchmark/specialist_qualification_v1/qualification_plan.json"
    )
    assert sources["qualification_protocol_sha256"] == sha256(
        ROOT / "benchmark/specialist_qualification_v1/PROTOCOL.md"
    )
    assert sources["qualification_v2_campaign_sha256"] == sha256(
        ROOT / "reports/qualification_v2/campaign_report.json"
    )
    assert sources["specialist_value_evidence_sha256"] == {
        "reports/spe_benchmark_v2/heldout_aggregate/aggregate_results.json": sha256(
            ROOT / "reports/spe_benchmark_v2/heldout_aggregate/aggregate_results.json"
        )
    }
    assert all(
        sha256(ROOT / agent["contract"]["path"]) == agent["contract"]["sha256"]
        for agent in matrix["agents"]
    )


def test_published_matrix_artifacts_match_integrity_manifest() -> None:
    report_dir = ROOT / "reports/specialist_qualification_v1"
    integrity = load("reports/specialist_qualification_v1/integrity.json")
    assert integrity == {
        "qualification_matrix.json": sha256(report_dir / "qualification_matrix.json"),
        "qualification_matrix.md": sha256(report_dir / "qualification_matrix.md"),
        "summary.md": sha256(report_dir / "summary.md"),
    }


def test_specialist_qualification_protocol_freeze_is_intact() -> None:
    freeze = load("benchmark/specialist_qualification_v1/PROTOCOL_FREEZE.json")
    assert freeze["benchmark_id"] == "boltzmann-spe-18-specialist-qualification-v1"
    assert all(sha256(ROOT / path) == digest for path, digest in freeze["files"].items())


def test_v2_matrix_merges_batch1_without_rewriting_v1() -> None:
    matrix = load("reports/specialist_qualification_v2/qualification_matrix.json")
    assert matrix["matrix_id"] == "boltzmann-spe-18-specialist-qualification-v2"
    assert matrix["supersedes"] == "boltzmann-spe-18-specialist-qualification-v1"
    assert matrix["summary"] == {
        "active_agents": 18,
        "execution_pass": 18,
        "specialist_value_status_counts": {
            "measured-no-incremental-benefit": 6,
            "not-measured": 9,
            "review-inconclusive": 2,
            "value-demonstrated": 1,
        },
    }
    statuses = {
        agent["environment_id"]: agent["specialist_value_qualification"]["status"]
        for agent in matrix["agents"]
    }
    assert statuses["07"] == "value-demonstrated"
    assert statuses["08"] == statuses["14"] == "review-inconclusive"
    assert statuses["20"] == "measured-no-incremental-benefit"


def test_v2_matrix_integrity_manifest_is_current() -> None:
    report_dir = ROOT / "reports/specialist_qualification_v2"
    integrity = load("reports/specialist_qualification_v2/integrity.json")
    assert integrity == {
        "qualification_matrix.json": sha256(report_dir / "qualification_matrix.json"),
        "qualification_matrix.md": sha256(report_dir / "qualification_matrix.md"),
    }
