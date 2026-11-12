#!/usr/bin/env python
"""Task 004: prepare FASTA for top designed CDR-H3 structures (Boltz2 input).
Combines LCAT (A) + light chain (B) + designed heavy chain (C)."""
import sys, json
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import metrics as m

base = "/home/boltzmann10/shared_metric_tools/prepared"
atoms = m.parse_pdb(f"{base}/5BV7.pdb")

def chain_seq(atoms, chain):
    seen = {}; seq = []
    for a in atoms:
        if a[0] == chain and not a[7] and a[1] not in seen:
            seen[a[1]] = a[2]; seq.append((a[1], a[2]))
    one = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
    return "".join(one.get(r,"X") for _, r in seq)

lcat = chain_seq(atoms, "A")
light = chain_seq(atoms, "B")

# top 3 by AAR
aar = json.load(open("/home/boltzmann10/shared_metric_tools/results/task004_aar.json"))
top3 = aar["candidates"][:3]

# designed heavy chain: take the full native heavy chain and swap in the designed CDR-H3
native_heavy = chain_seq(atoms, "C")
# CDR-H3 position in the full sequence
i = native_heavy.find("TAVYYC")
j = native_heavy.find("WGQG")
pre = native_heavy[:i+6]
post = native_heavy[j:]

outdir = "/home/boltzmann10/shared_metric_tools/prepared/task004_struct"
import os
os.makedirs(outdir, exist_ok=True)
for r in top3:
    sid = r["sample"]
    heavy = pre + r["cdr"] + post
    fasta = f">A|protein\n{lcat}\n>B|protein\n{light}\n>C|protein\n{heavy}\n"
    path = f"{outdir}/task004_sample{sid}.fasta"
    open(path, "w").write(fasta)
    print(f"sample {sid}: AAR {r['aar']} -> {path}")
    print(f"  heavy CDR-H3: {r['cdr']}")
