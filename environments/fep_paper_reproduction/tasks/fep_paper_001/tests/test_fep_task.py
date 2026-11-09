import json
from pathlib import Path
ROOT = Path(__file__).parents[1]
def test_reference_protocol():
    ref = json.loads((ROOT / "reference/extracted_parameters.json").read_text())
    assert ref["engine"] == "OpenMM 7.2"
    assert set(ref["legs"]) == {"complex", "solvent"}
def test_matrix():
    assert len(list((ROOT / "configs").glob("config_*.json"))) == 4

def test_independent_config_b_reconstruction():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import reconstruct_config_b
    result = reconstruct_config_b.reconstruct()
    cfg = result["configuration"]
    assert result["provenance"]["read_config_A"] is False
    assert cfg["engine"] == "OpenMM 7.2"
    assert cfg["ligand_forcefield"] == "GAFF 2.11"
    assert set(cfg["legs"]) == {"complex", "solvent"}
    assert result["status"] == "REVIEW"

def test_config_b_comparison_is_complete():
    comparison = json.loads((ROOT / "evaluation/config_B_comparison.json").read_text())
    assert comparison["matched"] == comparison["total"]
    assert comparison["parameter_accuracy"] == 1.0
    assert comparison["status"] == "REVIEW"

def test_selected_edge_is_pinned():
    manifest = json.loads((ROOT / "inputs/input_manifest.json").read_text())
    edge = manifest["selected_edge"]
    assert (edge["ligand_a"], edge["ligand_b"], edge["direction"]) == ("17", "1h1q", "17->1h1q")
    assert edge["source_line"] == 2

def test_endpoint_readiness_does_not_claim_production():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    import check_endpoint_readiness
    result = check_endpoint_readiness.main()
    assert result["status"] == "REVIEW"
    assert "complex_endpoint_topology_present" in result["missing"]
    assert "lambda_trajectories_present" in result["missing"]

def test_pinned_source_artifacts_exist():
    source = ROOT / "inputs/source_cdk2"
    for name in ("cdk2_pairs.txt", "Alchaware.cfg", "ligands.mol2", "protein.pdb"):
        assert (source / name).is_file()
    pairs = (source / "cdk2_pairs.txt").read_text().splitlines()
    assert pairs[1].split() == ["17", "1h1q"]

def test_mapping_is_generated_but_reviewed():
    mapping = json.loads((ROOT / "inputs/atom_map.json").read_text())
    assert mapping["ligand_a"] == "17"
    assert mapping["ligand_b"] == "1h1q"
    assert mapping["mapped_atom_count"] > 0
    assert mapping["status"] in {"PASS", "REVIEW"}
