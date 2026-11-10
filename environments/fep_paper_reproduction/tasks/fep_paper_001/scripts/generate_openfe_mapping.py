#!/usr/bin/env python3
"""Generate an OpenFE/Lomap mapping for the pinned ligand edge."""
from __future__ import annotations
import json
from pathlib import Path
from openfe import LomapAtomMapper, SmallMoleculeComponent

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "inputs/edge_17_to_1h1q"
OUT = ROOT / "inputs/openfe_atom_map.json"

def main():
    a = SmallMoleculeComponent.from_sdf_file(str(EDGE / "ligand_a.sdf"))
    b = SmallMoleculeComponent.from_sdf_file(str(EDGE / "ligand_b.sdf"))
    mappings = list(LomapAtomMapper().suggest_mappings(a, b))
    if not mappings:
        raise SystemExit("OpenFE did not produce a ligand mapping")
    mapping = mappings[0]
    pairs = [{"ligand_a_index": int(i), "ligand_b_index": int(j)}
             for i, j in sorted(mapping.componentA_to_componentB.items())]
    result = {
        "ligand_a": "17", "ligand_b": "1h1q", "direction": "17->1h1q",
        "mapper": "OpenFE LomapAtomMapper", "candidate_count": len(mappings),
        "mapped_atom_count": len(pairs), "atom_map": pairs,
        "status": "REVIEW",
        "limitations": ["mapping requires topology-level validation", "does not create endpoint topologies"]
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "atom_map"}, indent=2))

if __name__ == "__main__":
    main()
