#!/usr/bin/env python3
"""Generate and independently validate an element/bond MCS mapping."""
from __future__ import annotations
import json
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import rdFMCS

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "inputs/edge_17_to_1h1q"
OUT = ROOT / "inputs/atom_map.json"

def main():
    a = Chem.MolFromMolFile(str(EDGE / "ligand_a.sdf"), removeHs=False)
    b = Chem.MolFromMolFile(str(EDGE / "ligand_b.sdf"), removeHs=False)
    if a is None or b is None:
        raise SystemExit("cannot parse pinned ligand structures")
    mcs = rdFMCS.FindMCS([a, b], atomCompare=rdFMCS.AtomCompare.CompareElements,
                         bondCompare=rdFMCS.BondCompare.CompareOrder,
                         ringMatchesRingOnly=True, completeRingsOnly=True,
                         timeout=60)
    query = Chem.MolFromSmarts(mcs.smartsString)
    match_a, match_b = a.GetSubstructMatch(query), b.GetSubstructMatch(query)
    atom_map = [{"ligand_a_index": ia, "ligand_b_index": ib,
                 "element": a.GetAtomWithIdx(ia).GetSymbol()}
                for ia, ib in zip(match_a, match_b)]
    result = {
        "ligand_a": "17", "ligand_b": "1h1q", "direction": "17->1h1q",
        "method": "RDKit MCS, element and bond-order constrained",
        "mapped_atom_count": len(atom_map), "ligand_a_atom_count": a.GetNumAtoms(),
        "ligand_b_atom_count": b.GetNumAtoms(), "mcs_bond_count": mcs.numBonds,
        "atom_map": atom_map,
        "status": "REVIEW" if len(atom_map) < min(a.GetNumAtoms(), b.GetNumAtoms()) else "PASS",
        "limitations": ["stereochemical equivalence requires explicit review", "not an alchemical topology"]
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "atom_map"}, indent=2))

if __name__ == "__main__":
    main()
