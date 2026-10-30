import json
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_transformation import validate

CONFIG = ROOT / "tasks" / "inputs" / "fep_transformation_001" / "transformation.json"


def test_valid_transformation_is_pass_with_diagnostics(tmp_path):
    result = validate(CONFIG, tmp_path)
    assert result["status"] == "PASS"
    assert result["charge_change"] == 0
    assert any(x["kind"] == "bond_order_change" for x in result["chemical_changes"])
    assert json.loads((tmp_path / "qualification.json").read_text())["qualification"] == "PASS"


def test_charge_change_requires_review(tmp_path):
    config = json.loads(CONFIG.read_text())
    config["charge_b"] = 0
    config["ligand_a"] = str((CONFIG.parent / config["ligand_a"]).resolve())
    config["ligand_b"] = str((CONFIG.parent / config["ligand_b"]).resolve())
    config["atom_map"] = str((CONFIG.parent / config["atom_map"]).resolve())
    changed = tmp_path / "charge_change.json"
    changed.write_text(json.dumps(config))
    result = validate(changed, tmp_path / "out")
    assert result["status"] == "REVIEW"
    assert result["charge_change"] == 1


def test_missing_metadata_fails(tmp_path):
    changed = tmp_path / "bad.json"
    changed.write_text(json.dumps({"task_id": "bad"}))
    result = validate(changed, tmp_path / "out")
    assert result["status"] == "FAIL"
    assert result["errors"]
