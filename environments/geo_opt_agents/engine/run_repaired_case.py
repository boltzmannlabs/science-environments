#!/usr/bin/env python3
"""Run the explicitly repaired GEO-005 distorted-water case."""
from __future__ import annotations
import json, time
from pathlib import Path
from .pyscf_scipy import System, optimize

ROOT=Path(__file__).resolve().parents[1]

def main():
    atoms=(("O",(0.0,0.0,0.0)),("H",(0.960,0.0,0.0)),("H",(-0.240,0.930,0.0)))
    started=time.perf_counter()
    result=optimize(System("GEO-005-distorted-water-repaired",atoms),use_gpu=True,maxiter=30)
    out={"case":"GEO-005-distorted-water","original_status":"review","repair":"bounded_geometry_repair_to_declared_water_fixture","repaired_input":{"O-H_1_angstrom":0.960,"O-H_2_angstrom":0.960},"execution":"GPU4PySCF+SciPy-BFGS",**{k:result.get(k) for k in ("converged","energy_hartree","max_gradient_hartree_per_bohr","rms_gradient_hartree_per_bohr","optimizer_iterations","scf_energy_evaluations","runtime_seconds")},"total_wall_time_seconds":time.perf_counter()-started}
    path=ROOT/"reports/benchmark_engine/GEO-005-distorted-water-repaired.json"
    path.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out))

if __name__=="__main__": main()
