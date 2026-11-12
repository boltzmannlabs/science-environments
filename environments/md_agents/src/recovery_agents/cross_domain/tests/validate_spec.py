import json
from pathlib import Path

ROOT = Path(__file__).parents[4]
folders = [ROOT/'md_agents/recovery_agents/cross_domain/contracts.json', ROOT/'spe_agents/problem_solving/contracts.json', ROOT/'geo_opt_agents/problem_solving/contracts.json', ROOT/'homo_lumo_agents/problem_solving/contracts.json', ROOT/'qmmm_agents/problem_solving/contracts.json', ROOT/'fep_ti_agents/problem_solving/contracts.json']
contracts = [item for path in folders for item in json.loads(path.read_text())]
assert len(contracts) == 41
assert len({x['id'] for x in contracts}) == 41
assert len(list((ROOT/'md_agents/recovery_agents/cross_domain').glob('task.md'))) == 1
print('PASS: 41 distributed problem-solving contracts and shared task family')
