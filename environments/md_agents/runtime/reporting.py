"""Reporting facade for versioned MD evidence."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def latest() -> dict:
    return json.loads((ROOT / "results/agent_harness.json").read_text())
