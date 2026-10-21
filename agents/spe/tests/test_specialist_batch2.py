from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents.specialist_value import load_dataset
from spe_agents.specialist_value_batch2 import analysis_payload
from spe_agents.specialist_value_v1_1 import evaluate


MANIFEST = ROOT / "benchmark/specialist_qualification_v1/batch2/dataset_manifest.json"


def test_batch2_dataset_is_hash_verified_and_balanced() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    assert len(dataset.cases) == len(dataset.references) == 15
    assert {
        agent: sum(case["environment_id"] == agent for case in dataset.cases.values())
        for agent in dataset.manifest["agents"]
    } == {agent: 3 for agent in ("09", "10", "11", "17", "18")}


def test_batch2_references_are_hidden_from_public_cases() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    encoded = json.dumps(dataset.cases, sort_keys=True)
    assert "optional_warning_codes" not in encoded
    assert "numeric_tolerance" not in encoded
    assert "expected_outcome" not in encoded


def test_only_batch2_specialist_receives_contract() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    case = dataset.cases["SQ10-H3"]
    general = analysis_payload(case, role="general-controller")
    specialist = analysis_payload(case, role="spe-specialist", specialist_contract={"id": "10"})
    assert "specialist_contract" not in general
    assert specialist["specialist_contract"] == {"id": "10"}
    assert "references" not in json.dumps(general)


def test_batch2_evaluator_accepts_reference_and_rejects_bad_value() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    reference = dataset.references["SQ17-H1"]
    run = {"response": {
        "disposition": reference["disposition"],
        "selected_records": reference["selected_records"],
        "excluded_records": reference["excluded_records"],
        "warning_codes": reference["warning_codes"],
        "quantity_scope": reference["quantity_scope"],
        "values": dict(reference["values"]),
        "explanation": "fixed-geometry electronic cluster interaction",
    }}
    assert evaluate(run, reference, 1e-8)["passed"]
    run["response"]["values"]["cluster_interaction_energy_hartree"] += 1
    assert not evaluate(run, reference, 1e-8)["passed"]


def test_batch2_acetone_fragments_are_exact_cluster_subsets() -> None:
    def coordinates(path: Path) -> list[str]:
        return [" ".join(line.split()) for line in path.read_text(encoding="utf-8").splitlines()[2:] if line.strip()]
    fixture = ROOT / "benchmark/specialist_qualification_v1/fixtures"
    cluster = coordinates(fixture / "acetone_water_cluster.xyz")
    acetone = coordinates(fixture / "acetone_from_cluster.xyz")
    water = coordinates(fixture / "water_from_acetone_cluster.xyz")
    assert cluster == acetone + water


def test_batch2_protocol_freeze_is_intact() -> None:
    freeze = json.loads((ROOT / "benchmark/specialist_qualification_v1/batch2/PROTOCOL_FREEZE.json").read_text(encoding="utf-8"))
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected for path, expected in freeze["sha256"].items())
