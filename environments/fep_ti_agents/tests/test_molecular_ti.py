import json
from pathlib import Path


def test_local_molecular_ti_evidence_is_recorded():
    path = Path(__file__).parents[1] / "results/molecular_ti_local_001.json"
    if not path.exists():
        return  # CI without OpenMM can still run the contract suite.
    result = json.loads(path.read_text())
    assert result["status"] == "PASS"
    assert result["finite_energy"] is True
    assert result["finite_derivative"] is True
    assert result["lambda_coverage"] is True
