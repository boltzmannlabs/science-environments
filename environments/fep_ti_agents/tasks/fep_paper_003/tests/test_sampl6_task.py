import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_frozen_sampl6_inputs_match_reference():
    data = json.loads((ROOT / "evaluation" / "input_validation.json").read_text())
    assert data["status"] == "PASS"
    assert data["edge"]["direction"] == "OA-G3->OA-G6"
    assert data["edge"]["experimental_ddg_kcal_mol"] == 0.21
    assert len(data["inputs"]) == 4
    assert all(item["matches_reference"] for item in data["inputs"].values())


def test_fault_configuration_is_stopped_and_qualification_is_conservative():
    fault = json.loads((ROOT / "configs" / "config_D_perturbed.json").read_text())
    qualification = json.loads((ROOT / "expected_outputs" / "qualification.json").read_text())
    assert fault["status"] == "FAIL"
    assert fault["execution"] == "STOPPED"
    assert qualification["required_status"] == "REVIEW"
