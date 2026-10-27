from pathlib import Path
import json

ROOT = Path(__file__).parents[1]

def test_registry_and_tasks():
    contracts = json.loads((ROOT / 'agents/contracts.json').read_text())
    assert len(contracts) == 20
    assert len(list((ROOT / 'tasks').glob('cg_*.md'))) == 10
