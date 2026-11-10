#!/usr/bin/env python3
"""Assign GAFF2 atom types to the pinned endpoints using source charges.

The public CDK2 source ships Jaguar partial charges. They are preserved as the
charge input; this script does not silently replace them with AM1-BCC/RESP.
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "inputs/source_cdk2/ligands_jaguarcharges.mol2"
OUT = ROOT / "execution/ligand_parameterization"

def extract(text: str, name: str) -> str:
    for part in text.split("@<TRIPOS>MOLECULE")[1:]:
        lines = part.splitlines()
        idx = next((i for i, line in enumerate(lines) if line.strip()), None)
        if idx is not None and lines[idx].strip() == name:
            return "@<TRIPOS>MOLECULE\n" + "\n".join(lines[idx:]) + "\n"
    raise ValueError(f"missing ligand {name}")

def run(cmd, cwd, log):
    with log.open("w") as fh:
        return subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, timeout=60, check=False).returncode

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text()
    records = {}
    for name, label in (("17", "a"), ("1h1q", "b")):
        mol2 = OUT / f"ligand_{label}_source_charged.mol2"
        mol2.write_text(extract(source, name))
        lines = mol2.read_text().splitlines()
        start = next(i for i, x in enumerate(lines) if x.startswith("@<TRIPOS>ATOM"))
        end = next(i for i, x in enumerate(lines[start + 1:], start + 1) if x.startswith("@<TRIPOS>BOND"))
        charges = OUT / f"ligand_{label}.charges"
        charges.write_text("\n".join(x.split()[-1] for x in lines[start + 1:end]) + "\n")
        gaff = OUT / f"ligand_{label}_gaff2.mol2"
        frcmod = OUT / f"ligand_{label}.frcmod"
        ac_code = run(["antechamber", "-i", str(mol2), "-fi", "mol2", "-o", str(gaff), "-fo", "mol2", "-c", "rc", "-cf", str(charges), "-nc", "0", "-rn", "LIG", "-at", "gaff2", "-pf", "y"], OUT, OUT / f"ligand_{label}_antechamber.log")
        parm_code = None
        if ac_code == 0:
            parm_code = run(["parmchk2", "-i", str(gaff), "-f", "mol2", "-o", str(frcmod), "-s", "2"], OUT, OUT / f"ligand_{label}_parmchk2.log")
        records[label] = {"source_id": name, "antechamber_exit": ac_code, "parmchk2_exit": parm_code, "gaff2_mol2": str(gaff.relative_to(ROOT)) if gaff.exists() else None, "frcmod": str(frcmod.relative_to(ROOT)) if frcmod.exists() else None}
    result = {"edge": "17->1h1q", "charge_source": "public source Jaguar partial charges", "records": records, "status": "PASS" if all(x["antechamber_exit"] == 0 and x["parmchk2_exit"] == 0 for x in records.values()) else "REVIEW", "limitations": ["complex and solvent endpoint topologies still require assembly", "source charges are not AM1-BCC/RESP"]}
    (OUT / "parameterization.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
