#!/usr/bin/env python3
"""Build BioDesignBench-style task/result cards for the 18 Geo-Opt agents."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT_TASK=ROOT/'examples/geo_opt_tasks'; OUT_RESULT=ROOT/'examples/geo_opt_results'
def bullets(values): return '\n'.join(f'- {v}' for v in values) or '- None declared'
def main():
    contracts={json.loads(p.read_text())['id']:json.loads(p.read_text()) for p in (ROOT/'contracts').glob('agent_*.json')}
    qual=json.loads((ROOT/'reports/agent_qualification/summary.json').read_text()); results={r['agent_id']:r for r in qual['results']}
    OUT_TASK.mkdir(parents=True,exist_ok=True); OUT_RESULT.mkdir(parents=True,exist_ok=True); rows=[]
    for aid in sorted(contracts):
        c=contracts[aid]; r=results[aid]; slug=c['slug']; task_path=ROOT/'agents'/f'agent_{aid}'/'task.json'; task=json.loads(task_path.read_text())
        observed=[]; ev=r.get('evidence',{})
        if ev.get('energy_hartree') is not None: observed.append(f"Energy: `{ev['energy_hartree']:.12f} Hartree`; max gradient: `{ev.get('max_gradient_hartree_per_bohr',0):.3e} Hartree/Bohr`; backend: `{ev.get('backend','GPU4PySCF')}`.")
        if ev.get('reason'): observed.append(ev['reason'])
        if not observed: observed.append(f"Fixture decision target: `{r['expected_decision']}`; deterministic checks recorded.")
        status=r['status']; execution=r['execution']; note='Live engine evidence is available for this case.' if execution=='live_gpu_engine' else 'This is a deterministic contract/fixture evaluation, not a completed production optimization.'
        result=f"""# Result: geo_opt_{aid}_{slug}

## Description

{c['role']}

## System input

- Task ID: `{r['agent_id']}` / `{r['case']}`
- Input fixture: `{r['input']}`
- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution was used
- Acceptance criteria: finite coordinates, finite energy, verified convergence where applicable

## Expected output

{bullets(c['required_outputs'])}

## Observed result

- Status: **{status}**
- Execution: `{execution}`
- {' '.join(observed)}

## Limitations and review notes

{note}
The result is scoped to this frozen input packet and does not claim capabilities outside the agent contract.
"""
        result_name=f'geo_opt_{aid}_{slug}.md'; (OUT_RESULT/result_name).write_text(result)
        task=f"""# Task: geo_opt_{aid}_{slug}

## Description

{c['role']}

## Target

- Agent ID: `{r['agent_id']}`
- Task ID: `{r['case']}`
- Input: `{r['input']}`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `{r['input']}`

## Required inputs

{bullets(task.get('acceptance_criteria',{}).keys())}

## Expected output

{bullets(c['required_outputs'])}

## Acceptance criteria

{bullets(c['acceptance_criteria'])}

## Observed benchmark result

- Status: **{status}**
- Execution: `{execution}`
- {' '.join(observed)}

Detailed evidence: [`{result_name}`](../geo_opt_results/{result_name})
"""
        (OUT_TASK/f'geo_opt_{aid}_{slug}.md').write_text(task)
        rows.append({'id':aid,'slug':slug,'status':status,'task':f'geo_opt_{aid}_{slug}.md','result':result_name})
    (OUT_TASK/'manifest.json').write_text(json.dumps({'task_count':18,'tasks':rows},indent=2)+'\n'); (OUT_RESULT/'manifest.json').write_text(json.dumps({'result_count':18,'results':rows},indent=2)+'\n'); print(json.dumps({'tasks':18,'results':18}))
if __name__=='__main__': main()
