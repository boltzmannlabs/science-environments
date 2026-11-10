#!/usr/bin/env python3
"""Build Amber endpoint topologies for the pinned ligands and CDK2 complex."""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARAM = ROOT / "execution/ligand_parameterization"
PROTEIN = ROOT / "inputs/source_cdk2/protein.pdb"
OUT = ROOT / "execution/endpoints"

def build(label: str):
    work = OUT / label
    work.mkdir(parents=True, exist_ok=True)
    script = work / "tleap.in"
    mol2 = PARAM / f"ligand_{label}_gaff2.mol2"
    frcmod = PARAM / f"ligand_{label}.frcmod"
    script.write_text(f"""source leaprc.protein.ff14SB
source leaprc.phosaa10
source leaprc.gaff2
loadAmberParams {frcmod}
lig = loadMol2 {mol2}
prot = loadPdb {PROTEIN}
complex = combine {{prot lig}}
saveAmberParm complex {work}/complex.prmtop {work}/complex.inpcrd
saveAmberParm lig {work}/solvent.prmtop {work}/solvent.inpcrd
quit
""")
    log = work / "tleap.log"
    with log.open("w") as fh:
        code = subprocess.run(["tleap", "-f", str(script)], stdout=fh, stderr=subprocess.STDOUT, timeout=60, check=False).returncode
    files = {name: (work / name).is_file() and (work / name).stat().st_size > 0 for name in ("complex.prmtop", "complex.inpcrd", "solvent.prmtop", "solvent.inpcrd")}
    return {"ligand": label, "tleap_exit": code, "files": files, "status": "PASS" if code == 0 and all(files.values()) else "REVIEW"}

def main():
    records = {label: build(label) for label in ("a", "b")}
    result = {"edge": "17->1h1q", "records": records, "status": "PASS" if all(x["status"] == "PASS" for x in records.values()) else "REVIEW", "scope": "unsolvated Amber endpoint topologies; no water box or lambda simulation", "limitations": ["source-compatible Jaguar charges retained", "solvation, ion composition and alchemical hybrid topology remain separate gates"]}
    (OUT / "endpoint_build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
