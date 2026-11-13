#!/usr/bin/env python3
"""Compute Kabsch-aligned CDR-H3 CA RMSD and TM-score for AgCDR-Diff samples vs native 5BV7."""
import numpy as np
import glob, os

def kabsch(P, Q):
    """Kabsch alignment: align P to Q. Returns aligned P and RMSD."""
    cp = P.mean(axis=0); cq = Q.mean(axis=0)
    Pc, Qc = P-cp, Q-cq
    H = Pc.T @ Qc
    U, S, Vt = np.linalg.svd(H)
    D = np.diag([1,1,np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    Pa = (Pc @ R.T) + cq
    rmsd = np.sqrt(np.mean(np.sum((Pa-Q)**2, axis=1)))
    return Pa, rmsd

def tm_score(P, Q, n):
    """TM-score (standard formula). P aligned to Q (same coordinates, n residues)."""
    d0 = 0.33 * (n - 15) ** 0.67 + 0.5
    d = np.sqrt(np.sum((P-Q)**2, axis=1))
    return float(np.mean(1.0/(1.0+(d/d0)**2)))

# Native CDR-H3 CA (5BV7 chain C, res 97-115; framework Cys at 96 excluded)
native_ca = []
with open('/home/boltzmann10/.sci/cache/scratch/lcat_task/5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM'):
            if line[12:16].strip() != 'CA': continue
            if line[21] != 'C': continue
            rs = int(line[22:26].strip())
            if 97 <= rs <= 115:
                native_ca.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
native_ca = np.array(native_ca)
n = len(native_ca)
print(f"Native CDR-H3 CA: {n} atoms")

# Generated samples
results = []
for fpath in sorted(glob.glob('/home/boltzmann10/.sci/cache/scratch/lcat_task/agcdr_results/generated_structures/generated_sample_*.pdb'),
                    key=lambda x: int(''.join(filter(str.isdigit, os.path.basename(x))))):
    gen_ca = []
    with open(fpath) as f:
        for line in f:
            if line.startswith('ATOM'):
                if line[12:16].strip() != 'CA': continue
                if line[21] != 'A': continue  # generated chain A = heavy
                rs = int(line[22:26].strip())
                if 97 <= rs <= 115:
                    gen_ca.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
    gen_ca = np.array(gen_ca)
    if len(gen_ca) != n:
        print(f"  {os.path.basename(fpath)}: {len(gen_ca)} atoms, skip")
        continue
    aligned, rmsd = kabsch(gen_ca, native_ca)
    tms = tm_score(aligned, native_ca, n)
    sid = os.path.basename(fpath)
    results.append({'sample': sid, 'rmsd': float(rmsd), 'tm_score': float(tms)})

results.sort(key=lambda x: x['rmsd'])
print(f"\n{'Sample':<25} {'RMSD(A)':>8} {'TM-score':>9}")
for r in results:
    print(f"{r['sample']:<25} {r['rmsd']:>8.3f} {r['tm_score']:>9.4f}")
rmsds = [r['rmsd'] for r in results]; tms = [r['tm_score'] for r in results]
print(f"\nMean RMSD: {np.mean(rmsds):.3f} A | Best: {np.min(rmsds):.3f} A")
print(f"Mean TM-score: {np.mean(tms):.4f} | Best: {np.max(tms):.4f}")

import json
with open('/home/boltzmann10/.sci/cache/scratch/lcat_task/agcdr_rmsd.json','w') as f:
    json.dump(results, f, indent=2)
print("Saved agcdr_rmsd.json")
