"""Resolve historical report inputs through explicit native run identities."""
import json

def historical_result(env, task_id, approach="agent-alone"):
    registry = json.loads((env / "runs/registry.json").read_text())
    matches = [r for r in registry["runs"] if r["task_id"] == task_id
               and r["approach"] == approach and r["source_kind"] == "historical_publication"]
    if len(matches) != 1:
        raise ValueError("Expected one explicitly identified historical execution")
    return env / "results" / task_id / matches[0]["run_id"]
