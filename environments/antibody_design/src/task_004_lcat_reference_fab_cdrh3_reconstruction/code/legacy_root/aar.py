#!/usr/bin/env python
"""Task 004: CDR-H3 reconstruction sequence metrics (AAR, CAAR)."""
import sys, json, re
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import numpy as np
import metrics as m

# native CDR-H3
native = "AREGAAVRSFYYSYYGMDV"
native_residues = list(range(97, 116))  # PDB residue numbers

# designed sequences
fa = "/home/boltzmann10/shared_metric_tools/results/task004_proteinmpnn/seqs/task004_full_5BV7.fa"
designed = []
lines = open(fa).read().splitlines()
for i, line in enumerate(lines):
    if line.startswith(">") and "sample=" in line:
        sid = re.search(r"sample=(\d+)", line).group(1)
        score = re.search(r"score=([0-9.]+)", line).group(1)
        seq = lines[i+1].strip()
        designed.append((int(sid), float(score), seq))

def extract_cdrh3(seq):
    """Extract CDR-H3 from full VH sequence (between TAVYYC and WGQG)."""
    i = seq.find("TAVYYC")
    j = seq.find("WGQG")
    if i < 0 or j < 0: return None
    return seq[i+6:j]

# AAR for each
results = []
for sid, score, seq in designed:
    cdr = extract_cdrh3(seq)
    if cdr is None or len(cdr) != len(native):
        results.append({"sample": sid, "pmnn_score": score, "cdr_len": len(cdr) if cdr else 0, "aar": None, "cdr": cdr})
        continue
    matches = sum(1 for a, b in zip(cdr, native) if a == b)
    aar = matches / len(native)
    results.append({"sample": sid, "pmnn_score": score, "cdr": cdr, "aar": round(aar,4), "matches": matches, "cdr_len": len(cdr)})

# sort by AAR
results.sort(key=lambda x: -(x["aar"] or 0))
print(f"{'sample':>6} {'pmnn':>7} {'AAR':>7} {'matches':>7}  CDR-H3")
for r in results:
    print(f"{r['sample']:>6} {r['pmnn_score']:>7} {str(r['aar']):>7} {str(r.get('matches','')):>7}  {r['cdr']}")

# Identify CDR-H3 contact positions (which native CDR-H3 residues contact LCAT)
atoms = m.parse_pdb("/home/boltzmann10/shared_metric_tools/prepared/5BV7.pdb")
# CDR-H3 CA coords (chain C, res 97-115)
cdr_ca = m.ca_coords(atoms, chains={"C"}, resi_range=(97,115))
# LCAT atoms
lcat = np.array([[a[4],a[5],a[6]] for a in atoms if a[0]=="A" and not a[7]])
# for each CDR-H3 residue, check if any atom within 5A of LCAT
cdr_atoms = [a for a in atoms if a[0]=="C" and not a[7] and 97<=a[1]<=115]
contact_res = set()
for a in cdr_atoms:
    ac = np.array([a[4],a[5],a[6]])
    if np.min(np.linalg.norm(lcat-ac, axis=1)) < 5.0:
        contact_res.add(a[1])
contact_positions = sorted(contact_res)
print(f"\nCDR-H3 contact residues (PDB): {contact_positions} ({len(contact_positions)} of {len(native_residues)})")

# CAAR: AAR restricted to contact positions
# map PDB residue -> 1-based position in CDR-H3
res_to_pos = {r:i+1 for i,r in enumerate(native_residues)}
caar_results = []
for r in results:
    if r["aar"] is None: continue
    cdr = r["cdr"]; 
    # count matches at contact positions
    cm = 0; ct = 0
    for res in contact_positions:
        pos = res_to_pos[res]-1
        ct += 1
        if cdr[pos] == native[pos]: cm += 1
    r["caar"] = round(cm/ct,4) if ct else None
    r["caar_matches"] = cm
    r["caar_total"] = ct

out = {"native_cdrh3": native, "native_residues": native_residues, "contact_residues": contact_positions,
       "candidates": results}
open("/home/boltzmann10/shared_metric_tools/results/task004_aar.json","w").write(json.dumps(out,indent=2))
print("\nSaved task004_aar.json")
# best AAR
best = max([r for r in results if r["aar"]], key=lambda x:x["aar"])
print(f"Best AAR: {best['aar']} (sample {best['sample']})")
