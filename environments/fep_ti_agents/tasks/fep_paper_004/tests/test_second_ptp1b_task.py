import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_second_edge_identity_and_hashes():
    data = json.loads((ROOT / "evaluation" / "input_validation.json").read_text())
    assert data["status"] == "PASS"
    assert data["edge"] == {"direction": "23477->23479", "ddg_kcal_mol": -0.29}
    assert all(value["matches_reference"] for value in data["inputs"].values())


def test_invalid_reversed_edge_stops():
    config = json.loads((ROOT / "configs" / "config_D_perturbed.json").read_text())
    assert config["status"] == "FAIL"
    assert config["execution"] == "STOPPED"
