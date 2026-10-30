import json
from pathlib import Path


def test_sampl6_endpoint_evidence():
    path = Path(__file__).parents[1] / "results/sampl6_endpoint_smoke/endpoint_results.json"
    if not path.exists():
        return
    result = json.loads(path.read_text())
    assert result["status"] == "PASS"
    assert len(result["results"]) == 2
    assert all(x["finite_energy"] for x in result["results"])
