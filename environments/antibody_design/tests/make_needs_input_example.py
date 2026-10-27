"""Generate results/needs-input.example.json from the live example-request preflight.

The example intentionally omits every biological input, so preflight fails closed with
NEEDS_INPUT. The recorded missing_requirements list and request hash must match the exact
current example request, which is what the specification check verifies.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import validation  # noqa: E402

example = validation.read_json(ROOT / "tasks/request.example.json")
result = validation.preflight(example, ROOT / "tasks")
if result["status"] != "NEEDS_INPUT":
    raise SystemExit(f"Expected NEEDS_INPUT, got {result['status']}")

request_hash = hashlib.sha256((ROOT / "tasks/request.example.json").read_bytes()).hexdigest()
record = {
    "schema_version": "1.0",
    "task_id": "denv_antibody_001",
    "variant": "general",
    "run_id": "example-preflight",
    "run_status": "NEEDS_INPUT",
    "requested_count": 10,
    "stop_reason": (
        "Example preflight stops before any candidate work: the exact DENV-2 EDIII antigen "
        "and DV87.1 reference inputs are not supplied, so biological identity is unresolved."
    ),
    "missing_requirements": result["missing_requirements"],
    "records": [],
    "shortlist": [],
    "provenance": {
        "request_sha256": request_hash,
        "protocol_sha256": None,
        "scientific_execution": False,
        "synthetic_fixture": False,
        "knowledge_cutoff": "2024-09-01",
    },
    "resources": {
        "wall_time_minutes": 0,
        "cpu_core_hours": 0,
        "gpu_hours": 0,
        "remote_cost_units": 0,
    },
}
out = ROOT / "results/needs-input.example.json"
out.write_text(json.dumps(record, indent=2) + "\n")
print("wrote", out)
print("missing_requirements:", len(record["missing_requirements"]))
print("request_sha256:", request_hash)
