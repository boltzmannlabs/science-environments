#!/usr/bin/env python
"""Prepare antibody/antigen input PDBs by text-filtering chains (robust)."""
import os

base = "/home/boltzmann10/shared_metric_tools/prepared"

def save_chain_subset(src, keep, dst):
    """Keep ATOM/HETATM lines whose chain id (col 22) is in keep; drop others.
    Also keep header-ish lines (HEADER, TITLE, COMPND, REMARK) once."""
    keep = set(keep)
    out = []
    seen_header = set()
    for line in open(src):
        tag = line[:6]
        if tag in ("ATOM  ", "HETATM"):
            if line[21] in keep:
                out.append(line)
        elif tag in ("HEADER","TITLE ","COMPND","REMARK"):
            # keep a few global header lines (dedup by tag)
            if tag not in seen_header:
                out.append(line)
                seen_header.add(tag)
        # skip everything else (other chains' atoms, END, etc.)
    with open(dst, "w") as f:
        f.writelines(out)
        f.write("END\n")
    return len(out)

jobs = [
    ("1N8Z.pdb", {"A","B"}, "task001_antibody_1N8Z.pdb"),
    ("1N8Z.pdb", {"C"},     "task001_antigen_1N8Z.pdb"),
    ("35TL.pdb", {"A","B","C"}, "task002_full_35TL.pdb"),
    ("5BV7.pdb", {"B","C"}, "task004_antibody_5BV7.pdb"),
    ("5BV7.pdb", {"A"},     "task004_antigen_5BV7.pdb"),
    ("5BV7.pdb", {"A","B","C"}, "task004_full_5BV7.pdb"),
]
for src, keep, dst in jobs:
    n = save_chain_subset(f"{base}/{src}", keep, f"{base}/{dst}")
    print(f"{dst}: {n} atom lines")
print("done")
