#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
required = [ROOT/'README.md', ROOT/'ENVIRONMENT_SPEC.md', ROOT/'config/environment.yaml',
            ROOT/'config/request.schema.json', ROOT/'config/protocol.schema.json',
            ROOT/'tasks/homo_lumo_001_frontier_orbitals.md', ROOT/'tasks/request.example.json',
            ROOT/'tests/ACCEPTANCE.md']
for path in required:
    assert path.exists(), f'missing {path}'
json.loads((ROOT/'config/request.schema.json').read_text())
json.loads((ROOT/'config/protocol.schema.json').read_text())
json.loads((ROOT/'tasks/request.example.json').read_text())
assert len(json.loads((ROOT/'agents/contracts.json').read_text())) == 18
print('PASS: HOMO-LUMO package structure and JSON artifacts')
