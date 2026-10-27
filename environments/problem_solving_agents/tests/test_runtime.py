import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from runtime import CONTRACTS, run_case

def test_all_problem_solving_agents_run():
    cases = json.loads((Path(__file__).parents[1]/'cases/fixtures.json').read_text())
    assert len(CONTRACTS) == 41
    assert all(len(run_case(case)) == 41 for case in cases)
