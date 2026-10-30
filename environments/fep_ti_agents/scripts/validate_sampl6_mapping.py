"""Validate the GST guest mapping in downloaded SAMPL6 OA-G3/OA-G6 PDBs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def guest_atoms(path: Path):
    atoms = {}
    for line in path.read_text().splitlines():
        if line.startswith(("ATOM", "HETATM")) and line[17:20].strip() == "GST":
            name = line[12:16].strip()
            element = (line[76:78].strip() or name[0]).upper()
            atoms[name] = element
    if not atoms:
        raise ValueError(f"GST guest not found in {path}")
    return atoms


def validate(root: Path) -> dict:
    a = guest_atoms(root / "upstream/OA-G3_complex.pdb")
    b = guest_atoms(root / "upstream/OA-G6_complex.pdb")
    common = sorted(set(a) & set(b))
    unmapped = {"a": sorted(set(a) - set(common)), "b": sorted(set(b) - set(common))}
    mismatches = [{"atom": name, "a": a[name], "b": b[name]} for name in common if a[name] != b[name]]
    warnings = []
    if unmapped["a"] or unmapped["b"]:
        warnings.append({"type": "unmapped_guest_atoms", **unmapped})
    status = "FAIL" if mismatches else ("REVIEW" if warnings else "PASS")
    files = [root / "upstream/OA-G3_complex.pdb", root / "upstream/OA-G6_complex.pdb"]
    return {
        "task_id": "fep_atom_mapping_001",
        "qualification": status,
        "guest_residue": "GST",
        "mapped_atom_names": common,
        "element_mismatches": mismatches,
        "warnings": warnings,
        "provenance": {"source": "SAMPL6 manifest URLs", "input_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}, "silent_repair": False},
        "limitation": "PDB guest coordinates provide no complete bond-order/stereochemistry metadata; topology validation remains required.",
    }


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
