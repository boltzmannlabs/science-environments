#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from collections import Counter
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/input_validation.json"
def main():
    manifest = json.loads((ROOT / "inputs/input_manifest.json").read_text()); pdb = ROOT / "inputs" / manifest["structure"]
    lines = pdb.read_text().splitlines(); atoms = [x for x in lines if x.startswith(("ATOM", "HETATM"))]; lig = [x for x in atoms if x[17:20].strip() == manifest["ligand_resname"]]
    result = {"structure_present": pdb.is_file(), "sha256": hashlib.sha256(pdb.read_bytes()).hexdigest(), "sha_matches": hashlib.sha256(pdb.read_bytes()).hexdigest() == manifest["sha256"], "atom_records": len(atoms), "ligand_atom_records": len(lig), "ligand_resname": manifest["ligand_resname"], "status": "PASS" if lig and hashlib.sha256(pdb.read_bytes()).hexdigest() == manifest["sha256"] else "REVIEW", "missing": ["CS3 ligand structure/topology"] if not lig else [], "scope": "input identity and ligand presence; no topology or dynamics qualification"}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
