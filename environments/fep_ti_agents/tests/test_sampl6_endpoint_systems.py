import json
from pathlib import Path


def test_sampl6_complex_and_solvent_endpoints_are_recorded():
    result = json.loads((Path(__file__).parents[1] / "results" / "sampl6_endpoint_systems_001.json").read_text())
    assert result["status"] == "PASS"
    assert result["engine"]["platform"] == "CUDA"
    assert {(r["guest"], r["leg"]) for r in result["records"]} == {
        ("OA-G3-0", "complex"), ("OA-G3-0", "solvent"),
        ("OA-G6-0", "complex"), ("OA-G6-0", "solvent"),
    }
    assert all(r["finite_energy"] for r in result["records"])
