import json
from pathlib import Path
ROOT=Path(__file__).parents[1]
contracts=json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts)==10 and [x['id'] for x in contracts]==[f'FEP-PS{i:02d}' for i in range(1,11)]
assert len(list((ROOT/'tasks').glob('fep_ps*.md')))==10
json.loads((ROOT/'config/request.schema.json').read_text())
json.loads((ROOT/'config/protocol.schema.json').read_text())
print('PASS: FEP/TI package and 10-agent registry')
