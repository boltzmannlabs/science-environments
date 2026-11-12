#!/usr/bin/env python3
"""Epitope: antigen A heavy atoms within 5A of antibody (B/C) heavy atoms."""
import math
from collections import defaultdict

# All heavy atoms per chain
atoms = defaultdict(list)  # chain -> [(resseq,icode,x,y,z)]
with open('5BV7.pdb') as f:
    for line in f:
        if not line.startswith('ATOM'):
            continue
        resn = line[17:20].strip()
        if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL'):
            continue
        if line[12:16].strip() in ('H','H1','H2','H3','HG1','HG2'):
            continue
        cid = line[21]
        if cid not in ('A','B','C'):
            continue
        resseq = int(line[22:26].strip()); icode = line[26]
        x,y,z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        atoms[cid].append((resseq,icode,x,y,z))

ab = atoms['B'] + atoms['C']
epitope = set()
for (rs,ic,x,y,z) in atoms['A']:
    for (ax,ay,az) in [(a[2],a[3],a[4]) for a in ab]:
        d = math.sqrt((x-ax)**2+(y-ay)**2+(z-az)**2)
        if d < 5.0:
            epitope.add((rs,ic))
            break

epitope = sorted(epitope)
print(f"Epitope residues (A, any heavy atom <5A from Ab): {len(epitope)}")
print([f"A:{k[0]}" for k in epitope])
