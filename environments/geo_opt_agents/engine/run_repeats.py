#!/usr/bin/env python3
"""Run independent GPU repeats for representative frozen inputs."""
from __future__ import annotations
import json
from pathlib import Path
from .pyscf_scipy import SYSTEMS, optimize

ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/"reports/repeats"; out.mkdir(parents=True,exist_ok=True)
    selected=[s for s in SYSTEMS if s.name in {"water","methane"}]
    rows=[]
    for rep in (1,2):
        for system in selected:
            result=optimize(system,use_gpu=True,maxiter=10)
            row={"repeat":rep,"system":system.name,"backend":"GPU4PySCF+SciPy-BFGS",**{k:result.get(k) for k in ("converged","energy_hartree","max_gradient_hartree_per_bohr","runtime_seconds","scf_energy_evaluations")}}
            (out/f"{system.name}_repeat{rep}.json").write_text(json.dumps(row,indent=2)+"\n"); rows.append(row); print(json.dumps(row))
    (out/"summary.json").write_text(json.dumps({"repeat_count":2,"systems":["water","methane"],"results":rows},indent=2)+"\n")

if __name__=="__main__": main()
