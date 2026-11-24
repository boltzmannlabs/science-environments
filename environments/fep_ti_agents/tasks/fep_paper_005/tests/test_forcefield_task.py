import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_inputs_and_paper_fields_are_frozen():
    data = json.loads((ROOT / "evaluation" / "input_validation.json").read_text())
    assert data["status"] == "PASS"
    assert data["system"] == "CDK2"
    assert data["edge"] == "17->1h1q"
    assert all(item["matches_reference"] for item in data["inputs"].values())
    assert data["reported_fields"]["water_model"] == "TIP3P"


def test_sensitivity_and_fault_configurations_are_explicit():
    alternative = json.loads((ROOT / "configs" / "config_C_alternative.json").read_text())
    fault = json.loads((ROOT / "configs" / "config_D_perturbed.json").read_text())
    assert alternative["changed_factor"] == "charge_method"
    assert alternative["all_other_parameters"] == "same_as_config_A"
    assert fault["status"] == "FAIL"
    assert fault["execution"] == "STOPPED"
