#!/usr/bin/env python3
"""Materialize one JSON input packet per registered MD agent."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
manifest = json.loads((ROOT / "cases/agent_inputs.json").read_text())
for case in manifest["cases"]:
    out_dir = ROOT / "inputs" / case["agent_id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    packet = {
        "task_id": case["agent_id"],
        "agent_id": case["agent_id"],
        "agent_name": case["agent_name"],
        "group": case["group"],
        "input": case["input"],
        "expected_output": case["expected_output"],
        "acceptance": case["acceptance"],
        "execution_status": "input_packet_materialized; engine execution is case-specific"
    }
    (out_dir / "task.json").write_text(json.dumps(packet, indent=2) + "\n")
print(f"Materialized {len(manifest['cases'])} MD input files under {ROOT / 'inputs'}")
