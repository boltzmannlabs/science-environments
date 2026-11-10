#!/usr/bin/env python3
"""Parameterize CS3 with bounded AmberTools GAFF2/AM1-BCC execution."""
from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs/CS3_ideal.sdf"
OUT = ROOT / "execution"
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mol2, frcmod = OUT / "CS3_gaff2.mol2", OUT / "CS3.frcmod"
    with (OUT / "CS3_antechamber.log").open("w") as log:
        ac = subprocess.run(["antechamber", "-i", str(INPUT), "-fi", "sdf", "-o", str(mol2), "-fo", "mol2", "-c", "bcc", "-nc", "0", "-rn", "CS3", "-at", "gaff2", "-pf", "y"], stdout=log, stderr=subprocess.STDOUT, timeout=120, check=False).returncode
    pc = None
    if ac == 0:
        with (OUT / "CS3_parmchk2.log").open("w") as log:
            pc = subprocess.run(["parmchk2", "-i", str(mol2), "-f", "mol2", "-o", str(frcmod), "-s", "2"], stdout=log, stderr=subprocess.STDOUT, timeout=30, check=False).returncode
    result = {"input": str(INPUT.relative_to(ROOT)), "charge_method": "AM1-BCC", "forcefield": "GAFF2", "antechamber_exit": ac, "parmchk2_exit": pc, "outputs_present": mol2.is_file() and frcmod.is_file(), "status": "PASS" if ac == 0 and pc == 0 and mol2.is_file() and frcmod.is_file() else "REVIEW", "limitations": ["binding-pose coordinates are not included in ideal ligand SDF", "protein force-field revision and complex topology remain unresolved"]}
    (OUT / "CS3_parameterization.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
