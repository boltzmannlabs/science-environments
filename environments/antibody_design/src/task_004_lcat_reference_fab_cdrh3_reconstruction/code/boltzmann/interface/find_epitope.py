#!/usr/bin/env python3
"""Determine LCAT epitope residues from 5BV7 complex (antigen A residues within 5A of antibody B/C)."""
import math
from collections import defaultdict

# Parse CA atoms per chain
ca = defaultdict(dict)  # chain -> {(resseq,icode): (x,y,z)}
with open('5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM') and line[12:16].strip() == 'CA':
            cid = line[21]
            if cid not in ('A','B','C'):
                continue
            resseq = int(line[22:26].strip()); icode = line[26]
            x,y,z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            ca[cid][(resseq,icode)] = (x,y,z)

# Antigen A residues within 5A of any antibody CA (B or C)
ab_pos = list(ca['B'].values()) + list(ca['C'].values())
epitope = []
for key, (x,y,z) in ca['A'].items():
    for (ax,ay,az) in ab_pos:
        d = math.sqrt((x-ax)**2+(y-ay)**2+(z-az)**2)
        if d < 5.0:
            epitope.append(key)
            break

epitope.sort()
print(f"Epitope residues (chain A, within 5A of antibody): {len(epitope)}")
# Format as A:resseq
epitope_str = [f"A:{k[0]}" for k in epitope]
print("Epitope list:", epitope_str)
# Also report the range
if epitope:
    print("Range:", epitope[0][0], "-", epitope[-1][0])
