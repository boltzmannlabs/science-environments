import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
contracts = json.loads((ROOT/'agents/contracts.json').read_text())
assert len(contracts) == 41
assert len({x['id'] for x in contracts}) == 41
assert len(list((ROOT/'tasks').glob('*.md'))) == 6
print('PASS: 41 problem-solving contracts and six domain task families')
