#!/usr/bin/env python
"""Task 003: framework-guided CDR-H3 design.

Design backbone: Boltz2-predicted H965(VH)+H965(VL)+PD-1 complex.
Fix: all positions except CDR-H3 (heavy chain, between TAVYYC and WGQG).
Design: CDR-H3 sequence (20 samples, ProteinMPNN).
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import metrics as m
import run_proteinmpnn as rpm

PDB = "/home/boltzmann10/shared_metric_tools/results/task003_boltz2/boltz_results_task003_h965_pd1/predictions/task003_h965_pd1/task003_h965_pd1_model_0.pdb"
OUT = "/home/boltzmann10/shared_metric_tools/results/task003_proteinmpnn"
FJ = "/home/boltzmann10/shared_metric_tools/prepared/task003_fixed_positions.jsonl"

atoms = m.parse_pdb(PDB)
pdb_name = "task003_h965_pd1_model_0"  # must match the copied PDB basename

def chain_seq(atoms, chain):
    seen = {}; s = []
    for a in atoms:
        if a[0] == chain and not a[7] and a[1] not in seen:
            seen[a[1]] = a[2]; s.append((a[1], a[2]))
    return s

# CDR-H3 = between TAVYYC and WGQG in the heavy chain (chain A)
one = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
hres = chain_seq(atoms, "A")
hs = "".join(one.get(r, "X") for _, r in hres)
i = hs.find("TAVYYC"); j = hs.find("WGQG")
cdr_resi = [r for r, _ in hres][i+6:j]
print(f"CDR-H3 residues (chain A): {cdr_resi[0]}-{cdr_resi[-1]} ({len(cdr_resi)} res), seq {hs[i+6:j]}")

# fixed: all residues of A except CDR-H3, plus all of B and C
fixed = {pdb_name: {}}
for ch in "ABC":
    resi = [r for r, _ in chain_seq(atoms, ch)]
    if ch == "A":
        resi = [r for r in resi if r not in set(cdr_resi)]
    fixed[pdb_name][ch] = resi

with open(FJ, "w") as f:
    f.write(json.dumps(fixed) + "\n")  # {pdb_name: {chain: [resi]}}
print("Fixed positions written to", FJ)
print("A fixed:", len(fixed[pdb_name]["A"]), "B fixed:", len(fixed[pdb_name]["B"]), "C fixed:", len(fixed[pdb_name]["C"]))

# Run ProteinMPNN (20 designs)
rpm.main(PDB, FJ, OUT, 20)
