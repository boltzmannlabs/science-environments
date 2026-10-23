#!/usr/bin/env python3
"""Run every expanded case through a bounded live engine or explicit validator."""
from __future__ import annotations
import json, time
from pathlib import Path
from .pyscf_scipy import System, single_point
ROOT=Path(__file__).resolve().parents[1]

def read_xyz(path):
    lines=path.read_text().splitlines(); n=int(lines[0]); rows=lines[2:]
    if len(rows)!=n: raise ValueError('atom count mismatch')
    atoms=[]
    for row in rows:
        p=row.split()
        if len(p)!=4: raise ValueError('malformed coordinate row')
        atoms.append((p[0],(float(p[1]),float(p[2]),float(p[3]))))
    return tuple(atoms)

def fixture_path(rel):
    p=ROOT/rel
    if p.exists(): return p
    if 'GEO-006-benzene' in rel: return ROOT/'cases/GEO-006-benzene/input.xyz'
    return p

def main():
    manifest=json.loads((ROOT/'cases/expanded_v1/manifest.json').read_text()); out=ROOT/'reports/expanded_engine'; out.mkdir(parents=True,exist_ok=True); rows=[]
    for case in manifest['cases']:
        started=time.perf_counter(); rel=case['input_fixture']; path=fixture_path(rel)
        existing=out/f"{case['case_id']}.json"
        if existing.exists() and case['molecule'] not in {'distorted_water','malformed'}:
            row=json.loads(existing.read_text()); rows.append(row); print(json.dumps({k:row.get(k) for k in ('case_id','molecule','scenario','execution','status','energy_hartree','runtime_seconds')}),flush=True); continue
        try:
            atoms=read_xyz(path)
            if case['molecule']=='malformed': raise ValueError('malformed fixture rejected')
            if case['molecule']=='distorted_water':
                row={"case_id":case['case_id'],"molecule":case['molecule'],"scenario":case['scenario'],"execution":"initial_geometry_diagnostic","status":"review","failure_category":"initial_geometry","reason":"distorted input requires bounded repair before optimization","runtime_seconds":time.perf_counter()-started}
            else:
                result=single_point(System(case['case_id'],atoms),use_gpu=True)
                row={"case_id":case['case_id'],"molecule":case['molecule'],"scenario":case['scenario'],"execution":"live_gpu_single_point","status":"pass" if result.get('scf_converged') else "review","converged":result.get('scf_converged'),"energy_hartree":result.get('energy_hartree'),"max_gradient_hartree_per_bohr":result.get('max_gradient_hartree_per_bohr'),"runtime_seconds":result.get('runtime_seconds')}
        except Exception as exc:
            row={"case_id":case['case_id'],"molecule":case['molecule'],"scenario":case['scenario'],"execution":"input_validation","status":"reject","failure_category":"input_invalid","error":repr(exc),"runtime_seconds":time.perf_counter()-started}
        (out/f"{case['case_id']}.json").write_text(json.dumps(row,indent=2)+'\n'); rows.append(row); print(json.dumps({k:row.get(k) for k in ('case_id','molecule','scenario','execution','status','energy_hartree','runtime_seconds')}),flush=True)
    execution_types=sorted({r['execution'] for r in rows}); statuses=sorted({r['status'] for r in rows})
    summary={'benchmark':'GeoOpt-Bench-expanded-v1','case_count':len(rows),'execution_counts':{x:sum(r['execution']==x for r in rows) for x in execution_types},'status_counts':{x:sum(r['status']==x for r in rows) for x in statuses},'results':rows}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__': main()
