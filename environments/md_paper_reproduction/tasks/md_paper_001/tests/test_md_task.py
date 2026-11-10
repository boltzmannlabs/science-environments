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

def test_input_validation_passes_structure_inputs():
    result = json.loads((ROOT / "evaluation/input_validation.json").read_text())
    assert result["status"] == "PASS"
    assert result["sha_matches"] is True
    assert result["ligand_sdf_hash_matches"] is True
    assert result["ligand_sdf_atoms"] == 29

def test_agent_reconstruction_is_independent():
    result = json.loads((ROOT / "execution/generated_inputs/config_B_agent_generated.json").read_text())
    assert result["provenance"]["read_config_A"] is False
    assert result["configuration"]["pdb_id"] == "4EK5"
    assert result["status"] == "REVIEW"

def test_configuration_matrix_statuses():
    result = json.loads((ROOT / "evaluation/config_matrix.json").read_text())
    assert result["configs"]["config_A_reference"]["status"] == "REVIEW"
    assert result["configs"]["config_B_agent"]["status"] == "REVIEW"
    assert result["configs"]["config_C_alternative"]["status"] == "REVIEW"
    assert result["configs"]["config_D_perturbed"]["status"] == "FAIL"

def test_cs3_parameterization_passes():
    result = json.loads((ROOT / "execution/CS3_parameterization.json").read_text())
    assert result["status"] == "PASS"
    assert result["charge_method"] == "AM1-BCC"
    assert result["outputs_present"] is True
