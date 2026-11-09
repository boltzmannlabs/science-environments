#!/usr/bin/env python3
"""Stage 1b: prepare 6CM4 receptor (chain A protein atoms, 8NU/waters removed)
from the raw PDB text, preserving original coordinates; compute native 8NU box."""
import json
import numpy as np

BASE = "environments/hit-identification"
OUT = f"{BASE}/results/run_rsi"
COMPLEX = f"{BASE}/inputs/targets/6CM4_crystal_complex.pdb"

STANDARD = {"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU",
            "LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL"}

receptor_lines = []
lig_coords = []
with open(COMPLEX) as f:
    for line in f:
        if line.startswith(("ATOM", "HETATM")):
            resname = line[17:20].strip()
            chain = line[21]
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            if chain == "A" and resname == "8NU":
                lig_coords.append((x, y, z))
            elif chain == "A" and resname in STANDARD and line.startswith("ATOM"):
                receptor_lines.append(line.rstrip("\n"))

out_path = f"{OUT}/prepared/6CM4_receptor_prep.pdb"
with open(out_path, "w") as f:
    f.write("REMARK   6CM4 receptor preparation for BoltChem Vina docking\n")
    f.write("REMARK   chain A protein atoms only; 8NU ligand and waters removed\n")
    f.write("REMARK   original crystal coordinates preserved\n")
    for l in receptor_lines:
        f.write(l + "\n")
    f.write("END\n")

lig = np.array(lig_coords)
centroid = lig.mean(axis=0)
extents = lig.max(axis=0) - lig.min(axis=0)
box = int(np.ceil(float(extents.max()) + 8))
info = {
    "source": COMPLEX,
    "ligand": "8NU (risperidone) native pose",
    "ligand_atoms": len(lig),
    "centroid_A": {"x": round(float(centroid[0]), 3), "y": round(float(centroid[1]), 3), "z": round(float(centroid[2]), 3)},
    "ligand_extent_A": {"x": round(float(extents[0]), 2), "y": round(float(extents[1]), 2), "z": round(float(extents[2]), 2)},
    "box_diameter_A": box,
    "receptor_atom_count": len(receptor_lines),
    "output_pdb": out_path,
    "note": "receptor = chain A of 6CM4 (DRD2/T4-lysozyme fusion construct), 8NU and waters removed, original coordinates",
}
with open(f"{OUT}/prepared/binding_box.json", "w") as f:
    json.dump(info, f, indent=1)
print(json.dumps(info, indent=1))
