#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path
from collections import Counter
from rdkit import Chem
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation/input_validation.json"
def main():
    manifest = json.loads((ROOT / "inputs/input_manifest.json").read_text()); pdb = ROOT / "inputs" / manifest["structure"]
    lines = pdb.read_text().splitlines(); atoms = [x for x in lines if x.startswith(("ATOM", "HETATM"))]; lig = [x for x in atoms if x[17:20].strip() == manifest["ligand_resname"]]
    ligand = ROOT / "inputs" / manifest["ligand_structure"]
    molecule = Chem.MolFromMolFile(str(ligand), removeHs=False) if ligand.is_file() else None
    ligand_hash_ok = ligand.is_file() and hashlib.sha256(ligand.read_bytes()).hexdigest() == manifest["ligand_sha256"]
    result = {"structure_present": pdb.is_file(), "sha256": hashlib.sha256(pdb.read_bytes()).hexdigest(), "sha_matches": hashlib.sha256(pdb.read_bytes()).hexdigest() == manifest["sha256"], "atom_records": len(atoms), "ligand_atom_records_in_pdb": len(lig), "ligand_sdf_present": ligand.is_file(), "ligand_sdf_hash_matches": ligand_hash_ok, "ligand_sdf_atoms": molecule.GetNumAtoms() if molecule else 0, "ligand_resname": manifest["ligand_resname"], "status": "PASS" if ligand_hash_ok and molecule is not None and hashlib.sha256(pdb.read_bytes()).hexdigest() == manifest["sha256"] else "REVIEW", "missing": [] if ligand_hash_ok and molecule is not None else ["CS3 ligand structure/topology"], "scope": "input identity and ligand structure validation; topology and dynamics qualification remain separate"}
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(json.dumps(result, indent=2) + "\n"); print(json.dumps(result, indent=2))
if __name__ == "__main__": main()
