#!/usr/bin/env python3
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))
from orchestrator import route

ROOT = Path(__file__).parents[1]
cases = json.loads((ROOT/'cases/fixtures.json').read_text())
records = [route(c) for c in cases]
out = ROOT/'results'; out.mkdir(exist_ok=True)
payload = {'benchmark':'problem-solving-orchestrator-v1','cases':records,'scope':'routed fixture workflow; not production engine qualification'}
(out/'orchestrator_results.json').write_text(json.dumps(payload, indent=2)+'\n')
print(json.dumps(payload, indent=2))
