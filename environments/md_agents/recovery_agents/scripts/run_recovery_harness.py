#!/usr/bin/env python3
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from runtime import AGENTS, run_agent

ROOT = Path(__file__).parents[1]
cases = json.loads((ROOT / 'cases/fixtures.json').read_text())
results = [run_agent(case) for case in cases]
out = ROOT / 'results'
out.mkdir(exist_ok=True)
payload = {
    'benchmark': 'md-recovery-fixtures-v1',
    'agents': len(AGENTS),
    'results': results,
    'scope': 'deterministic recovery-fixture qualification; not production engine qualification',
}
(out / 'results.json').write_text(json.dumps(payload, indent=2) + '\n')
print(json.dumps(payload, indent=2))
