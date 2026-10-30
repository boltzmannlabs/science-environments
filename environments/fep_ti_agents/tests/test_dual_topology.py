import json
from pathlib import Path


RESULT = Path(__file__).parents[1] / "results" / "dual_topology_qualification_001.json"


def test_dual_topology_independent_qualification():
    data = json.loads(RESULT.read_text())
    assert data["qualification"] == "PASS"
    assert all(data["independent_checks"].values())
    assert data["complex_estimate_kj_mol"] != data["solvent_estimate_kj_mol"]
    assert "not a claim of converged SAMPL6" in data["interpretation"]
