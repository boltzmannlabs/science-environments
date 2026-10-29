#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
required = [ROOT/'README.md', ROOT/'ENVIRONMENT_SPEC.md', ROOT/'config/environment.yaml',
            ROOT/'config/request.schema.json', ROOT/'config/protocol.schema.json',
            ROOT/'agents/contracts.json', ROOT/'tests/ACCEPTANCE.md', ROOT/'tasks/request.example.json',
            ROOT/'cases/agent_inputs.json', ROOT/'inputs/MD-CORE-001-water-box/task.json']
for path in required:
    assert path.exists(), f'missing {path}'
for path in [ROOT/'config/request.schema.json', ROOT/'config/protocol.schema.json']:
    json.loads(path.read_text())
json.loads((ROOT/'tasks/request.example.json').read_text())
contracts = json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts) == 62
assert [x['id'] for x in contracts] == [f'MD-{i:02d}' for i in range(1, 63)]
assert sum(x['group'] == 'core' for x in contracts) == 20
assert sum(x['group'] == 'online' for x in contracts) == 10
assert sum(x['group'] == 'domain' for x in contracts) == 20
assert sum(x['group'] == 'scenario' for x in contracts) == 12
assert len(list((ROOT/'tasks').glob('md_*.md'))) == 62
agent_inputs = json.loads((ROOT/'cases/agent_inputs.json').read_text())
assert agent_inputs['count'] == 62 and len(agent_inputs['cases']) == 62
assert len(list((ROOT/'inputs').glob('MD-??/task.json'))) == 62
print('PASS: MD package, schemas and 62-agent registry')
