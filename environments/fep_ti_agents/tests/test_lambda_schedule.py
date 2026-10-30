import json, sys
from pathlib import Path
ROOT = Path(__file__).parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
from validate_lambda_schedule import validate

CONFIG = ROOT / "tasks/inputs/fep_lambda_schedule_001/transformation.json"

def test_valid_schedule_passes(tmp_path):
    assert validate(CONFIG, tmp_path)["status"] == "PASS"

def test_duplicate_schedule_fails_when_shape_is_invalid(tmp_path):
    data = json.loads(CONFIG.read_text()); data["lambda_electrostatics"] = [1.0, .5, .5, 0.0]
    p = tmp_path / "bad.json"; p.write_text(json.dumps(data))
    assert validate(p, tmp_path / "out")["status"] == "FAIL"

def test_missing_softcore_fails(tmp_path):
    data = json.loads(CONFIG.read_text()); data["softcore"]["enabled"] = False
    p = tmp_path / "bad.json"; p.write_text(json.dumps(data))
    assert validate(p, tmp_path / "out")["status"] == "FAIL"

def test_charge_change_without_staging_requires_review(tmp_path):
    data = json.loads(CONFIG.read_text()); data["charge_change"] = True
    data["lambda_electrostatics"] = [1.0, .8, .6, .4, .2, 0.0]
    p = tmp_path / "charge.json"; p.write_text(json.dumps(data))
    result = validate(p, tmp_path / "out")
    assert result["status"] == "REVIEW"
    assert any("electrostatics-off" in item for item in result["warnings"])

def test_window_configuration_is_materialized(tmp_path):
    out = tmp_path / "out"; validate(CONFIG, out)
    assert len(list((out / "window_configuration").glob("window_*.json"))) == 6
