from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1]))
from scripts.validate_sampl6_mapping import validate


ROOT = Path(__file__).parents[1] / "tasks" / "inputs" / "fep_atom_mapping_001"


def test_downloaded_sampl6_guests_have_common_elements():
    result = validate(ROOT)
    assert result["qualification"] == "REVIEW"
    assert len(result["mapped_atom_names"]) == 17
    assert any(w["type"] == "unmapped_guest_atoms" for w in result["warnings"])
    assert result["provenance"]["silent_repair"] is False
