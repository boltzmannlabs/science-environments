#!/usr/bin/env python3
"""Generate the frozen benzene GPU reference artifact."""
from __future__ import annotations
import json, time
from pathlib import Path
from .pyscf_scipy import System, optimize
ROOT=Path(__file__).resolve().parents[1]
def main():
    xyz=(ROOT/"cases/GEO-006-benzene/input.xyz").read_text().splitlines()
    atoms=tuple((p[0],(float(p[1]),float(p[2]),float(p[3]))) for p in (row.split() for row in xyz[2:]))
    started=time.perf_counter(); r=optimize(System("GEO-006-benzene",atoms),use_gpu=True,maxiter=20)
    out={"case":"GEO-006-benzene","input":"cases/GEO-006-benzene/input.xyz","backend":"GPU4PySCF+SciPy-BFGS","method":"B3LYP","basis":"6-31G*",**{k:r.get(k) for k in ("converged","energy_hartree","max_gradient_hartree_per_bohr","rms_gradient_hartree_per_bohr","optimizer_iterations","scf_energy_evaluations","runtime_seconds")},"artifact_generated_seconds":time.time()}
    p=ROOT/"reports/references"; p.mkdir(parents=True,exist_ok=True); (p/"benzene_gpu.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out))
if __name__=="__main__": main()
