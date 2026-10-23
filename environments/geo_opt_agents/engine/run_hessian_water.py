#!/usr/bin/env python3
"""Run a real B3LYP Hessian/minimum check for the frozen water reference."""
from __future__ import annotations
import json, time
from pathlib import Path
from pyscf import dft, gto
from pyscf.hessian import thermo

ROOT=Path(__file__).resolve().parents[1]
def main():
    mol=gto.M(atom='O 0 0 0; H .758602 0 .504284; H -.758602 0 .504284',basis='6-31G*',unit='Angstrom',verbose=0)
    mf=dft.RKS(mol); mf.xc='B3LYP'; mf.conv_tol=1e-9
    started=time.perf_counter(); energy=float(mf.kernel()); hess=mf.Hessian().kernel(); analysis=thermo.harmonic_analysis(mol,hess)
    freqs=[float(x) for x in analysis['freq_wavenumber']]
    out={"case":"GEO-013-water-minimum","backend":"PySCF CPU Hessian","method":"B3LYP/6-31G*","energy_hartree":energy,"frequencies_cm-1":freqs,"stationary_point":"local_minimum" if min(freqs)>0 else "saddle_or_inconclusive","scf_converged":bool(mf.converged),"runtime_seconds":time.perf_counter()-started}
    path=ROOT/"reports/hessian"; path.mkdir(parents=True,exist_ok=True); (path/"water_minimum.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out))
if __name__=="__main__": main()
