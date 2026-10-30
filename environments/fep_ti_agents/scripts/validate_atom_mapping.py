"""Dependency-free validator for the FEP-AG01 benchmark fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def mol2(path: Path):
    text = path.read_text().splitlines()
    atoms, bonds = {}, []
    section = None
    for line in text:
        if line.startswith("@<TRIPOS>ATOM"):
            section = "atom"; continue
        if line.startswith("@<TRIPOS>BOND"):
            section = "bond"; continue
        if line.startswith("@<TRIPOS>"):
            section = None; continue
        fields = line.split()
        if section == "atom" and len(fields) >= 6:
            atoms[int(fields[0])] = {"element": fields[5].split(".")[0].upper()}
        elif section == "bond" and len(fields) >= 4:
            bonds.append((int(fields[1]), int(fields[2]), fields[3]))
    if not atoms:
        raise ValueError(f"no MOL2 atoms found in {path}")
    return atoms, bonds


def validate(root: Path) -> dict:
    a, bonds_a = mol2(root / "ligand_a.mol2")
    b, bonds_b = mol2(root / "ligand_b.mol2")
    mapping = json.loads((root / "atom_map.json").read_text())["mapping"]
    errors, warnings = [], []
    seen_a, seen_b = set(), set()
    for item in mapping:
        ia, ib = item.get("a"), item.get("b")
        if ia not in a or ib not in b:
            errors.append({"type": "unknown_atom", "mapping": item}); continue
        if ia in seen_a or ib in seen_b:
            errors.append({"type": "duplicate_mapping", "mapping": item}); continue
        seen_a.add(ia); seen_b.add(ib)
        if a[ia]["element"] != b[ib]["element"]:
            errors.append({"type": "element_mismatch", "mapping": item})
    if len(seen_a) != len(a) or len(seen_b) != len(b):
        warnings.append({"type": "unmapped_atoms", "a": sorted(set(a) - seen_a), "b": sorted(set(b) - seen_b)})
    bond_a = {(min(x, y), max(x, y)): order for x, y, order in bonds_a if x in seen_a and y in seen_a}
    bond_b = {(min(x, y), max(x, y)): order for x, y, order in bonds_b if x in seen_b and y in seen_b}
    changes = []
    for pair in sorted(set(bond_a) | set(bond_b)):
        if bond_a.get(pair) != bond_b.get(pair):
            changes.append({"atoms": pair, "a": bond_a.get(pair), "b": bond_b.get(pair)})
    if changes:
        warnings.append({"type": "bond_changes", "changes": changes})
    # Bond-order changes are expected transformation diagnostics, not an
    # automatic failure. Missing/ambiguous mappings remain REVIEW.
    non_bond_warnings = [w for w in warnings if w["type"] != "bond_changes"]
    status = "FAIL" if errors else ("REVIEW" if non_bond_warnings else "PASS")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in ("ligand_a.mol2", "ligand_b.mol2", "atom_map.json", "transformation.json")}
    return {"task_id": "fep_atom_mapping_001", "qualification": status, "errors": errors, "warnings": warnings, "mapped_atoms": len(seen_a), "provenance": {"input_sha256": hashes, "silent_repair": False}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.input)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["qualification"])
    return 0 if result["qualification"] != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
