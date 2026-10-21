from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spe_agents.specialist_value import load_dataset
from spe_agents.specialist_value_batch2_v1_1 import evaluate


MANIFEST = ROOT / "benchmark/specialist_qualification_v1/batch2_v1_1/dataset_manifest.json"


def response_for(reference: dict[str, object]) -> dict[str, object]:
    return {
        "disposition": reference["disposition"],
        "selected_records": deepcopy(reference["selected_records"]),
        "excluded_records": deepcopy(reference["excluded_records"]),
        "warning_codes": deepcopy(reference["warning_codes"]),
        "quantity_scope": reference["quantity_scope"],
        "values": deepcopy(reference["values"]),
        "explanation": "Evidence-bounded decision.",
    }


def test_batch2_v1_1_dataset_is_separate_hash_verified_and_balanced() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    assert dataset.manifest["schema_version"] == "1.1"
    assert dataset.manifest["supersedes"] == "boltzmann-spe-specialist-qualification-batch2-v1"
    assert len(dataset.cases) == len(dataset.references) == 15
    assert all("batch2_v1_1/cases/" in item["case_file"] for item in dataset.manifest["cases"])


def test_batch2_v1_1_accepts_only_predeclared_optional_warnings() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    reference = dataset.references["SQ17-H2"]
    response = response_for(reference)
    response["warning_codes"] = ["fragment_geometry_mismatch", "missing_required_reference"]
    assert evaluate({"response": response}, reference, 1e-8)["passed"]
    response["warning_codes"] = ["fragment_geometry_mismatch", "counterpoise_evidence_missing"]
    result = evaluate({"response": response}, reference, 1e-8)
    assert not result["passed"]
    assert result["findings"] == ["unexpected warning codes: ['counterpoise_evidence_missing']"]


def test_batch2_v1_1_accepts_predeclared_value_withholding() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    reference = dataset.references["SQ17-H3"]
    response = response_for(reference)
    response["values"] = {}
    assert evaluate({"response": response}, reference, 1e-8)["passed"]


def test_batch2_v1_1_accepts_predeclared_conservative_review() -> None:
    dataset = load_dataset(ROOT, MANIFEST)
    reference = dataset.references["SQ11-H1"]
    response = response_for(reference)
    response["disposition"] = "review"
    response["values"] = {}
    assert evaluate({"response": response}, reference, 1e-8)["passed"]


def test_batch2_v1_1_protocol_freeze_is_intact() -> None:
    freeze_path = ROOT / "benchmark/specialist_qualification_v1/batch2_v1_1/PROTOCOL_FREEZE.json"
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    assert all(
        hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
        for path, expected in freeze["sha256"].items()
    )
