#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]
case = json.loads((ROOT/'cases/fixture.json').read_text())
checks = {
    'QMMM-PS01': ('qm_region_defined', 'QM region definition'),
    'QMMM-PS02': ('boundary_valid', 'boundary/link-atom validation'),
    'QMMM-PS03': ('charge_accounted', 'charge and embedding accounting'),
    'QMMM-PS04': ('qm_scf_converged', 'QM-region SCF convergence'),
    'QMMM-PS05': ('coupling_checked', 'coupling and force consistency'),
    'QMMM-PS06': ('expanded_regions', 'expanded-region sensitivity'),
    'QMMM-PS07': ('checkpoint_compatible', 'trajectory restart compatibility'),
}
results = []
for agent_id, (field, evidence) in checks.items():
    ok = bool(case.get(field)) and (agent_id != 'QMMM-PS06' or case.get(field, 0) >= 2)
    results.append({'agent_id': agent_id, 'status': 'PASS' if ok else 'REVIEW', 'evidence': evidence, 'case_id': case['case_id']})
payload = {'benchmark':'qmmm-fixture-v1', 'results':results, 'provenance_complete':case['provenance_complete'], 'scope':'fixture qualification; no production QM/MM engine claim'}
out = ROOT/'results'; out.mkdir(exist_ok=True)
(out/'fixture_results.json').write_text(json.dumps(payload, indent=2)+'\n')
print(json.dumps(payload, indent=2))
