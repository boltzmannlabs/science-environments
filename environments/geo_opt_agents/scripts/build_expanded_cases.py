#!/usr/bin/env python3
"""Build a frozen 36-case GeoOpt-Bench expansion from fixed pilot inputs."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=[('water','tier1_basic'),('methane','tier1_basic'),('ethanol','tier2_flexible'),('benzene','tier3_conjugated'),('distorted_water','adversarial'),('malformed','adversarial')]
SCENARIOS=[('input_validation','validate structure and atom count'),('optimization','run fixed-geometry optimization'),('convergence','classify energy/gradient stopping'),('quality','validate final coordinates and provenance'),('recovery','diagnose bounded failure/recovery'),('reproducibility','compare repeated result')]
def main():
    cases=[]
    for i,(mol,tier) in enumerate(BASE):
        for scenario,goal in SCENARIOS:
            cid=f'GEOEXP-{i*6+SCENARIOS.index((scenario,goal))+1:03d}'
            fixture_name = {'water':'GEO-001-water','methane':'GEO-002-methane','ethanol':'GEO-003-ethanol','distorted_water':'GEO-005-distorted-water','malformed':'GEO-004-malformed-input'}.get(mol)
            cases.append({'case_id':cid,'molecule':mol,'tier':tier,'scenario':scenario,'goal':goal,'input_fixture':f'cases/{fixture_name}/input.xyz' if fixture_name else 'cases/GEO-006-benzene/input.xyz','backend':'PySCF+GPU4PySCF','method':'B3LYP','basis_set':'6-31G*','charge':0,'multiplicity':1,'acceptance_criteria':{'finite_coordinates':True,'finite_energy':scenario in {'optimization','convergence','quality'},'convergence_must_be_verified':scenario in {'optimization','convergence','quality'}}})
    out=ROOT/'cases/expanded_v1'; out.mkdir(parents=True,exist_ok=True); (out/'manifest.json').write_text(json.dumps({'schema_version':'1.0','case_count':len(cases),'repeat_policy':'single frozen pass plus selected independent repeats','cases':cases},indent=2)+'\n')
    (ROOT/'reports/expanded_benchmark').mkdir(parents=True,exist_ok=True); (ROOT/'reports/expanded_benchmark/summary.json').write_text(json.dumps({'benchmark':'GeoOpt-Bench-expanded-v1','case_count':len(cases),'counts':{'frozen_cases':len(cases),'live_engine_cases':4,'fixture_cases':len(cases)-4,'independent_repeat_cases':4},'live_engine_case_ids':['GEOEXP-002','GEOEXP-008','GEOEXP-014','GEOEXP-020'],'scope':'Expanded frozen task set; only the existing four reference systems have live engine evidence.'},indent=2)+'\n'); print(json.dumps({'cases':len(cases),'live_engine_cases':4}))
if __name__=='__main__': main()
