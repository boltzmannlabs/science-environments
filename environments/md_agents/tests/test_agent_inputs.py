import json
from pathlib import Path

def test_every_md_agent_has_a_distinct_explicit_input_packet():
    root = Path(__file__).parents[1]
    data = json.loads((root / "cases/agent_inputs.json").read_text())
    contracts = json.loads((root / "agents/contracts.json").read_text())
    assert data["count"] == 62
    assert len(data["cases"]) == len(contracts) == 62
    assert {x["agent_id"] for x in data["cases"]} == {x["id"] for x in contracts}
    fingerprints = {json.dumps(x["input"], sort_keys=True) for x in data["cases"]}
    assert len(fingerprints) == 62
    assert all(x["expected_output"] and x["acceptance"] for x in data["cases"])
    for case in data["cases"]:
        packet = json.loads((root / "inputs" / case["agent_id"] / "task.json").read_text())
        assert packet["agent_id"] == case["agent_id"]
        assert packet["input"] == case["input"]
