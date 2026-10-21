from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents.specialist_value import (
    analysis_payload,
    combined_usage,
    evaluate,
    load_dataset,
)


MANIFEST = ROOT / "benchmark/specialist_qualification_v1/batch1/dataset_manifest.json"


def test_batch1_dataset_is_hash_verified_and_balanced() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    assert len(dataset.cases) == 24
    assert len(dataset.references) == 24
    counts = {
        environment_id: sum(
            case["environment_id"] == environment_id for case in dataset.cases.values()
        )
        for environment_id in dataset.manifest["agents"]
    }
    assert counts == {agent: 3 for agent in ("01", "03", "04", "05", "06", "07", "08", "14")}


def test_hidden_references_are_not_in_public_case_files() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    encoded = json.dumps(dataset.cases, sort_keys=True)
    assert "expected" not in encoded
    assert "forbidden_terms" not in encoded
    assert "numeric_tolerance" not in encoded


def test_only_specialist_payload_receives_contract() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    case = dataset.cases["SQ08-H2"]
    general = analysis_payload(case, role="general-controller")
    specialist = analysis_payload(
        case, role="spe-specialist", specialist_contract={"id": "08"}
    )
    assert "specialist_contract" not in general
    assert specialist["specialist_contract"] == {"id": "08"}
    assert "references" not in json.dumps(general)
    assert "references" not in json.dumps(specialist)


def test_independent_evaluator_accepts_exact_response_and_rejects_wrong_value() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    reference = dataset.references["SQ14-H1"]
    run = {
        "response": {
            "disposition": reference["disposition"],
            "selected_records": reference["selected_records"],
            "excluded_records": reference["excluded_records"],
            "warning_codes": reference["warning_codes"],
            "quantity_scope": reference["quantity_scope"],
            "values": dict(reference["values"]),
            "explanation": "A fixed-geometry electronic reaction energy.",
        }
    }
    assert evaluate(run, reference, 1e-8)["passed"] is True
    run["response"]["values"]["reaction_energy_hartree"] += 1.0
    checked = evaluate(run, reference, 1e-8)
    assert checked["passed"] is False
    assert any("reaction_energy_hartree" in item for item in checked["findings"])


def test_usage_combines_specialist_and_controller_calls() -> None:
    calls = [
        {
            "response": {
                "agent_scientist_usage": {
                    "total_including_auxiliary": {
                        "api_calls": 2,
                        "total_tokens": 100,
                        "estimated_cost_usd": 0.1,
                    }
                }
            }
        },
        {
            "response": {
                "agent_scientist_usage": {
                    "total_including_auxiliary": {
                        "api_calls": 1,
                        "total_tokens": 50,
                        "estimated_cost_usd": 0.05,
                    }
                }
            }
        },
    ]
    assert combined_usage(calls) == {
        "api_calls": 3.0,
        "total_tokens": 150.0,
        "estimated_cost_usd": 0.15000000000000002,
    }


def test_batch1_protocol_freeze_is_intact() -> None:
    freeze = json.loads(
        (
            ROOT
            / "benchmark/specialist_qualification_v1/batch1/PROTOCOL_FREEZE.json"
        ).read_text(encoding="utf-8")
    )
    import hashlib

    assert all(
        hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        for path, expected in freeze["sha256"].items()
    )


def test_batch1_v11_preserves_responses_and_has_expected_scoring() -> None:
    old = json.loads(
        (
            ROOT / "reports/specialist_qualification_batch1/main/batch1_results.json"
        ).read_text(encoding="utf-8")
    )
    corrected = json.loads(
        (
            ROOT / "reports/specialist_qualification_batch1/v1_1/batch1_results.json"
        ).read_text(encoding="utf-8")
    )
    assert corrected["model_responses_regenerated"] is False
    assert len(old["runs"]) == len(corrected["runs"]) == 144
    assert [item["response"] for item in old["runs"]] == [
        item["response"] for item in corrected["runs"]
    ]
    assert [item["usage"] for item in old["runs"]] == [
        item["usage"] for item in corrected["runs"]
    ]
    general = sum(
        item["agent-scientist"]["passed"]
        for item in corrected["aggregate"].values()
    )
    specialist = sum(
        item["agent-scientist-plus-specialist"]["passed"]
        for item in corrected["aggregate"].values()
    )
    assert (general, specialist) == (64, 72)
    assert corrected["aggregate"]["07"]["agent-scientist"]["passed"] == 3
    assert (
        corrected["aggregate"]["07"]["agent-scientist-plus-specialist"]["passed"]
        == 9
    )


def test_batch1_v11_freeze_and_qualification_updates_are_intact() -> None:
    freeze = json.loads(
        (
            ROOT
            / "benchmark/specialist_qualification_v1/batch1_v1_1/PROTOCOL_FREEZE.json"
        ).read_text(encoding="utf-8")
    )
    import hashlib

    assert all(
        hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        for path, expected in freeze["sha256"].items()
    )
    updates = json.loads(
        (
            ROOT
            / "reports/specialist_qualification_batch1/v1_1/qualification_updates.json"
        ).read_text(encoding="utf-8")
    )["updates"]
    statuses = {item["environment_id"]: item["status"] for item in updates}
    assert statuses == {
        "01": "measured-no-incremental-benefit",
        "03": "measured-no-incremental-benefit",
        "04": "measured-no-incremental-benefit",
        "05": "measured-no-incremental-benefit",
        "06": "measured-no-incremental-benefit",
        "07": "value-demonstrated",
        "08": "review-inconclusive",
        "14": "review-inconclusive",
    }
