#!/usr/bin/env python3
"""Extend Hessian/minimum verification to methane and benzene."""
from __future__ import annotations
import json,time
from pathlib import Path
from pyscf import dft,gto
from pyscf.hessian import thermo
ROOT=Path(__file__).resolve().parents[1]
CASES={'methane':'cases/GEO-002-methane/input.xyz','benzene':'cases/GEO-006-benzene/input.xyz'}
def main():
 out=ROOT/'reports/hessian'; out.mkdir(parents=True,exist_ok=True)
 for name,rel in CASES.items():
  lines=(ROOT/rel).read_text().splitlines(); atoms=[(p[0],tuple(map(float,p[1:]))) for p in (x.split() for x in lines[2:])]
  mol=gto.M(atom=atoms,basis='6-31G*',unit='Angstrom',verbose=0); mf=dft.RKS(mol); mf.xc='B3LYP'; mf.conv_tol=1e-9; started=time.perf_counter(); energy=float(mf.kernel()); h=mf.Hessian().kernel(); freqs=[float(x) for x in thermo.harmonic_analysis(mol,h)['freq_wavenumber']]
  row={'case':f'GEO-HESSIAN-{name}','backend':'PySCF CPU Hessian','method':'B3LYP/6-31G*','energy_hartree':energy,'frequencies_cm-1':freqs,'stationary_point':'local_minimum' if min(freqs)>0 else 'saddle_or_inconclusive','scf_converged':bool(mf.converged),'runtime_seconds':time.perf_counter()-started}; (out/f'{name}_minimum.json').write_text(json.dumps(row,indent=2)+'\n'); print(json.dumps(row))
if __name__=='__main__': main()
