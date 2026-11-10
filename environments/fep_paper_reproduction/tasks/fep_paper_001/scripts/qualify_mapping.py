#!/usr/bin/env python3
"""Independently qualify the OpenFE candidate atom mapping."""
from __future__ import annotations
import json
from pathlib import Path
from rdkit import Chem
from openfe import LomapAtomMapper, SmallMoleculeComponent

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "inputs/edge_17_to_1h1q"
MAP = ROOT / "inputs/openfe_atom_map.json"
OUT = ROOT / "evaluation/mapping_qualification.json"

def main():
    a = Chem.MolFromMolFile(str(EDGE / "ligand_a.sdf"), removeHs=False)
    b = Chem.MolFromMolFile(str(EDGE / "ligand_b.sdf"), removeHs=False)
    data = json.loads(MAP.read_text())
    pairs = data["atom_map"]
    element_ok = all(a.GetAtomWithIdx(p["ligand_a_index"]).GetAtomicNum() ==
                     b.GetAtomWithIdx(p["ligand_b_index"]).GetAtomicNum() for p in pairs)
    mapped_a = {p["ligand_a_index"] for p in pairs}
    mapped_b = {p["ligand_b_index"] for p in pairs}
    degree_ok = all(a.GetAtomWithIdx(p["ligand_a_index"]).GetDegree() ==
                    b.GetAtomWithIdx(p["ligand_b_index"]).GetDegree() for p in pairs)
    stereo_a = Chem.FindMolChiralCenters(a, includeUnassigned=True)
    stereo_b = Chem.FindMolChiralCenters(b, includeUnassigned=True)
    alternatives = list(LomapAtomMapper().suggest_mappings(
        SmallMoleculeComponent.from_sdf_file(str(EDGE / "ligand_a.sdf")),
        SmallMoleculeComponent.from_sdf_file(str(EDGE / "ligand_b.sdf"))))
    checks = {
        "all_elements_match": element_ok,
        "all_atoms_accounted_for": len(mapped_a) == a.GetNumAtoms() and len(mapped_b) == b.GetNumAtoms(),
        "mapped_atom_count_equal": len(mapped_a) == len(mapped_b),
        "local_degree_consistency": degree_ok,
        "stereochemistry_explicitly_reviewed": False,
        "alternative_mapping_candidates_checked": len(alternatives) > 0,
    }
    element_mismatches = [
        {"ligand_a_index": p["ligand_a_index"], "ligand_b_index": p["ligand_b_index"],
         "ligand_a_element": a.GetAtomWithIdx(p["ligand_a_index"]).GetSymbol(),
         "ligand_b_element": b.GetAtomWithIdx(p["ligand_b_index"]).GetSymbol()}
        for p in pairs
        if a.GetAtomWithIdx(p["ligand_a_index"]).GetAtomicNum() != b.GetAtomWithIdx(p["ligand_b_index"]).GetAtomicNum()
    ]
    result = {
        "edge": "17->1h1q",
        "mapper": data["mapper"],
        "candidate_count": len(alternatives),
        "mapped_atom_count": len(pairs),
        "ligand_a_chiral_centers": stereo_a,
        "ligand_b_chiral_centers": stereo_b,
        "checks": checks,
        "element_mismatches": element_mismatches,
        "status": "PASS" if all(checks.values()) else "REVIEW",
        "limitations": ["Br-to-H endpoint change requires explicit dummy-atom/topology validation", "bond-order correspondence requires hybrid-topology validation", "stereochemistry is intentionally not auto-approved"],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
