import json, sys
from pathlib import Path
ROOT = Path(__file__).parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
from validate_parameters import validate

SYSTEM = ROOT / "tasks/inputs/fep_parameter_validation_001/system.json"
FF = ROOT / "tasks/inputs/fep_parameter_validation_001/forcefield.json"

def test_valid_parameters_pass(tmp_path):
    assert validate(SYSTEM, FF, tmp_path)["status"] == "PASS"

def test_missing_atom_type_fails(tmp_path):
    data = json.loads(SYSTEM.read_text()); data["atoms"][0]["type"] = "unknown"
    s = tmp_path / "system.json"; s.write_text(json.dumps(data))
    result = validate(s, FF, tmp_path / "out")
    assert result["status"] == "FAIL"

def test_incompatible_water_model_fails(tmp_path):
    data = json.loads(SYSTEM.read_text()); data["water_model"] = "SPC"
    s = tmp_path / "system.json"; s.write_text(json.dumps(data))
    assert validate(s, FF, tmp_path / "out")["status"] == "FAIL"
