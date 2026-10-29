from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from cg_agents.runtime import run_all_agents

def test_all_agent_runtime_records():
    records = run_all_agents({'finite_energy': True, 'finite_coordinates': True, 'mapping_valid': True, 'model': 'toy', 'parameters_complete': True, 'box_valid': True, 'minimized': True, 'steps': 100, 'bonds': 2, 'replicas': 2, 'repeat_energy_delta': 0.1, 'family': 'protein'})
    assert len(records) == 20
    assert {x['agent_id'] for x in records} == {f'CG-{i:02d}' for i in range(1, 21)}
