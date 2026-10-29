import json
from pathlib import Path

def test_harness_covers_all_62_packets():
    root = Path(__file__).parents[1]
    packets = list((root / "inputs").glob("MD-??/task.json"))
    assert len(packets) == 62
    for path in packets:
        data = json.loads(path.read_text())
        assert data["agent_id"].startswith("MD-")
        assert data["input"]["fixture"]
        assert data["acceptance"]
