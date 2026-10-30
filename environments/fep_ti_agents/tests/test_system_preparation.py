import json, sys
from pathlib import Path
ROOT = Path(__file__).parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
from validate_system_preparation import validate

CONFIG = ROOT / "tasks/inputs/fep_system_preparation_001/sampl6_oa_systems.json"

def test_valid_complex_and_solvent_are_ready(tmp_path):
    result = validate(CONFIG, tmp_path)
    assert result["status"] == "PASS"
    assert {x["leg"] for x in result["legs"]} == {"complex", "solvent"}

def test_count_mismatch_fails(tmp_path):
    data = json.loads(CONFIG.read_text()); data["legs"][0]["coordinate_atoms"] += 1
    p = tmp_path / "bad.json"; p.write_text(json.dumps(data))
    assert validate(p, tmp_path / "out")["status"] == "FAIL"

def test_unstable_equilibration_fails(tmp_path):
    data = json.loads(CONFIG.read_text()); data["legs"][1]["equilibration"]["temperature_std_K"] = 20
    p = tmp_path / "bad.json"; p.write_text(json.dumps(data))
    assert validate(p, tmp_path / "out")["status"] == "FAIL"
