import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_input_and_reference_are_pinned():
    manifest = json.loads((ROOT / "inputs/input_manifest.json").read_text())
    assert manifest["pdb_id"] == "4EK5"
    assert len(manifest["sha256"]) == 64
    ref = json.loads((ROOT / "reference/extracted_parameters.json").read_text())
    assert ref["timestep_fs"] == 2
    assert ref["production"]["temperature_K"] == 298

def test_four_configuration_matrix_exists():
    names = {p.name for p in (ROOT / "configs").glob("config_*.json")}
    assert names == {"config_A_reference.json", "config_B_agent.json", "config_C_alternative.json", "config_D_perturbed.json"}
