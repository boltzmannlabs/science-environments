#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
for path in [ROOT/'README.md', ROOT/'ENVIRONMENT_SPEC.md', ROOT/'config/environment.yaml', ROOT/'agents/contracts.json', ROOT/'tasks/request.example.json']:
    assert path.exists(), f'missing {path}'
contracts = json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts) == 20
assert [x['id'] for x in contracts] == [f'CG-{i:02d}' for i in range(1, 21)]
assert len(list((ROOT/'tasks').glob('cg_*.md'))) == 10
json.loads((ROOT/'tasks/request.example.json').read_text())
print('PASS: CG package and 20-agent registry')
