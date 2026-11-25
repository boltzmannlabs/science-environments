#!/usr/bin/env python3
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from runtime import run_case, CONTRACTS

ROOT = Path(__file__).parents[1]
cases = json.loads((ROOT/'cases/fixtures.json').read_text())
records = [{'case_id': c['case_id'], 'domain': c['domain'], 'results': run_case(c)} for c in cases]
out = ROOT/'results'
out.mkdir(exist_ok=True)
payload = {'benchmark':'problem-solving-fixtures-v1','agents':len(CONTRACTS),'cases':records,'scope':'fixture qualification; not production engine qualification'}
(out/'results.json').write_text(json.dumps(payload, indent=2)+'\n')
print(json.dumps(payload, indent=2))
