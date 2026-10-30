import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.validate_atom_mapping import validate


ROOT = Path(__file__).parents[1] / "tasks" / "inputs" / "fep_atom_mapping_001"


def test_reference_mapping_passes_with_bond_diagnostic():
    result = validate(ROOT)
    assert result["qualification"] == "PASS"  # bond-order change is reported, not hidden
    assert any(w["type"] == "bond_changes" for w in result["warnings"])
    assert result["provenance"]["silent_repair"] is False


def test_wrong_element_mapping_fails(tmp_path):
    for name in ("ligand_a.mol2", "ligand_b.mol2", "transformation.json"):
        (tmp_path / name).write_bytes((ROOT / name).read_bytes())
    mapping = json.loads((ROOT / "atom_map.json").read_text())
    mapping["mapping"][0] = {"a": 1, "b": 7}
    (tmp_path / "atom_map.json").write_text(json.dumps(mapping))
    assert validate(tmp_path)["qualification"] == "FAIL"
