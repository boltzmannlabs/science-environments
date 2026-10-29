"""Agent registry facade for the MD packet harness."""
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]

def contracts() -> list[dict]:
    return json.loads((ROOT / "agents/contracts.json").read_text())
