import json
from pathlib import Path
ROOT = Path(__file__).parents[1]
def test_reference_protocol():
    ref = json.loads((ROOT / "reference/extracted_parameters.json").read_text())
    assert ref["engine"] == "OpenMM 7.2"
    assert set(ref["legs"]) == {"complex", "solvent"}
def test_matrix():
    assert len(list((ROOT / "configs").glob("config_*.json"))) == 4
