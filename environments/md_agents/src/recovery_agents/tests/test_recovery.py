import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from runtime import run_agent

def test_all_recovery_agents_have_fixtures():
    root = Path(__file__).parents[1]
    cases = json.loads((root / 'cases/fixtures.json').read_text())
    results = [run_agent(c) for c in cases]
    assert len(results) == 10
    assert {r['agent_id'] for r in results} == {f'REC-{i:02d}' for i in range(1, 11)}
    assert all(r['status'] in {'PASS', 'REVIEW', 'FAIL'} for r in results)
