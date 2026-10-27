#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
required = [ROOT/'README.md', ROOT/'ENVIRONMENT_SPEC.md', ROOT/'config/environment.yaml',
            ROOT/'config/request.schema.json', ROOT/'config/protocol.schema.json',
            ROOT/'agents/contracts.json', ROOT/'tests/ACCEPTANCE.md', ROOT/'tasks/request.example.json']
for path in required:
    assert path.exists(), f'missing {path}'
for path in [ROOT/'config/request.schema.json', ROOT/'config/protocol.schema.json']:
    json.loads(path.read_text())
json.loads((ROOT/'tasks/request.example.json').read_text())
contracts = json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts) == 30
assert [x['id'] for x in contracts] == [f'MD-{i:02d}' for i in range(1, 31)]
assert sum(x['group'] == 'core' for x in contracts) == 20
assert sum(x['group'] == 'online' for x in contracts) == 10
assert len(list((ROOT/'tasks').glob('*.md'))) == 30
print('PASS: MD package, schemas and 30-agent registry')
