import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
contracts=json.loads((ROOT/'src/agents/contracts.json').read_text())
assert len(contracts)==10 and [x['id'] for x in contracts]==[f'FEP-PS{i:02d}' for i in range(1,11)]
assert len(list((ROOT/'tasks').glob('fep_ps*.md')))==10
agent_contracts=json.loads((ROOT/'src/agents/fep_agent_contracts.json').read_text())
environment_contracts=json.loads((ROOT/'src/agents/fep_environment_contracts.json').read_text())
assert len(agent_contracts)==15 and [x['id'] for x in agent_contracts]==[f'FEP-AG{i:02d}' for i in range(1,16)]
assert len(environment_contracts)==15 and [x['id'] for x in environment_contracts]==[f'FEP-ENV-{i:02d}' for i in range(1,16)]
assert len(list((ROOT/'tasks').glob('fep_env_*.md')))==15
assert len(list((ROOT/'tasks').glob('fep_ag*.md')))==15
json.loads((ROOT/'config/request.schema.json').read_text())
json.loads((ROOT/'config/protocol.schema.json').read_text())
manifest=json.loads((ROOT/'benchmark/sampl6/manifest.json').read_text())
assert len(manifest['systems'])==2 and len(manifest['fault_injection_cases'])==12
print('PASS: FEP/TI package, 15 environment families, 15 specialist agents, and 10 problem-solving agents')
