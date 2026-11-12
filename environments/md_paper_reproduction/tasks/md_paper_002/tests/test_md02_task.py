import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_frozen_input_validation():
    result = json.loads((ROOT / "evaluation/input_validation.json").read_text())
    assert result["status"] == "PASS"
    assert result["checks"]["nvt_ns_present"]
    assert result["checks"]["input_sha256_matches"]

def test_perturbed_configuration_stops():
    cfg = json.loads((ROOT / "configs/config_D_perturbed.json").read_text())
    assert cfg["status"] == "FAIL"
    assert cfg["expected_action"] == "STOP_BEFORE_EXECUTION"

def test_scientific_status_is_conservative():
    expected = json.loads((ROOT / "expected_outputs/qualification.json").read_text())
    assert expected["required_status"] == "REVIEW"
    assert expected["production_claim"] is False
