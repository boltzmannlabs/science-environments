#!/usr/bin/env python3
"""Materialize the two immutable ligand files for the pinned 17 -> 1h1q edge."""
from pathlib import Path
from rdkit import Chem

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "inputs/source_cdk2/ligands.mol2"
OUT = ROOT / "inputs/edge_17_to_1h1q"

def blocks(text: str):
    parts = text.split("@<TRIPOS>MOLECULE")
    for part in parts[1:]:
        lines = part.splitlines()
        nonempty = next((i for i, line in enumerate(lines) if line.strip()), None)
        if nonempty is not None and lines[nonempty].strip() in {"17", "1h1q"}:
            yield lines[nonempty].strip(), "@<TRIPOS>MOLECULE" + part

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    found = dict(blocks(SOURCE.read_text()))
    for name in ("17", "1h1q"):
        if name not in found:
            raise SystemExit(f"missing ligand {name} in {SOURCE}")
        mol2 = OUT / f"ligand_{'a' if name == '17' else 'b'}.mol2"
        mol2.write_text(found[name].rstrip() + "\n")
        mol = Chem.MolFromMol2File(str(mol2), removeHs=False, sanitize=False)
        if mol is None or mol.GetNumAtoms() == 0:
            raise SystemExit(f"RDKit could not read {mol2}")
        sdf = OUT / f"ligand_{'a' if name == '17' else 'b'}.sdf"
        writer = Chem.SDWriter(str(sdf))
        writer.write(mol)
        writer.close()
        print(name, mol.GetNumAtoms(), mol.GetNumBonds(), mol2, sdf)

if __name__ == "__main__":
    main()
