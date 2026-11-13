#!/usr/bin/env python
"""Task 005: BDBV-43 reference-derived CDR-H3 design.

Design backbone: BDBV-43 Fab (PDB 7KEW chains G=VH, J=VL).
Fix: all positions except CDR-H3 (VH, ARDEIIGAD, after YYC before WGQG).
Design: CDR-H3 sequence (20 samples, ProteinMPNN).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import metrics as m
import run_proteinmpnn as rpm

PDB = "/home/boltzmann10/shared_metric_tools/prepared/task005_bdbv43_fab.pdb"
OUT = "/home/boltzmann10/shared_metric_tools/results/task005_proteinmpnn"
FJ = "/home/boltzmann10/shared_metric_tools/prepared/task005_fixed_positions.jsonl"

atoms = m.parse_pdb(PDB)
pdb_name = "task005_bdbv43_fab"

one = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
def chain_res(atoms, ch):
    seen={}; s=[]
    for a in atoms:
        if a[0]==ch and not a[7] and a[1] not in seen: seen[a[1]]=a[2]; s.append((a[1],a[2]))
    return s

# CDR-H3 = after last YYC, before WGQG (IGHV1-69 FR3 ends TAIYYC, not TAVYYC)
g = chain_res(atoms, "G")
gs = "".join(one.get(r,"X") for _,r in g)
i = gs.rfind("YYC"); j = gs.find("WGQG")
cdr_resi = [r for r,_ in g][i+3:j]
print(f"CDR-H3 (chain G): {gs[i+3:j]}, residues {cdr_resi[0]}-{cdr_resi[-1]} ({len(cdr_resi)})")

fixed = {pdb_name: {}}
for ch in "GJ":
    resi = [r for r,_ in chain_res(atoms, ch)]
    if ch == "G": resi = [r for r in resi if r not in set(cdr_resi)]
    fixed[pdb_name][ch] = resi
with open(FJ, "w") as f:
    f.write(json.dumps(fixed) + "\n")
print("G fixed:", len(fixed[pdb_name]["G"]), "J fixed:", len(fixed[pdb_name]["J"]))
rpm.main(PDB, FJ, OUT, 20)
