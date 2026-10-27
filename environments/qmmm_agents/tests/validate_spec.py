import json
from pathlib import Path
ROOT = Path(__file__).parents[1]
contracts = json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts) == 7
assert [x['id'] for x in contracts] == [f'QMMM-PS0{i}' for i in range(1, 8)]
assert len(list((ROOT/'tasks').glob('qmmm_*.md'))) == 7
json.loads((ROOT/'config/request.schema.json').read_text())
json.loads((ROOT/'config/protocol.schema.json').read_text())
print('PASS: QM/MM package and 7-agent registry')
