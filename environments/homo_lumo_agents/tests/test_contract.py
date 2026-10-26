import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def test_tasks_have_required_fields():
    for path in (ROOT / "tasks").glob("*.json"):
        task = json.loads(path.read_text())
        assert {"task_id", "geometry", "charge", "multiplicity", "method", "basis_set"} <= task.keys()
        assert len(task["geometry"]) > 0

def test_eighteen_contracts():
    contracts = json.loads((ROOT / "agents/contracts.json").read_text())
    assert len(contracts) == 18
    assert [x["id"] for x in contracts] == [f"HL-{i:02d}" for i in range(1, 19)]
