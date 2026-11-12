#!/usr/bin/env python3
"""Prepare complex PDB with SEQRES + header records included, for IG-Design."""
from collections import OrderedDict

chains_atoms = OrderedDict()
seqres = OrderedDict()
header_lines = []

with open('5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM'):
            resn = line[17:20].strip()
            if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL','UNL','PEG','GOL','DOD'):
                continue
            cid = line[21]
            if cid not in ('A','B','C'):
                continue
            chains_atoms.setdefault(cid, []).append(line)
        elif line.startswith('SEQRES'):
            cid = line[11]
            if cid in ('A','B','C'):
                seqres.setdefault(cid, []).append(line)
        elif line.startswith(('HEADER','TITLE','COMPND','SOURCE','EXPDTA','JRNL','SPRS','REMARK   2','REMARK   3','REMARK   4','REMARK   5','REMARK   6')):
            header_lines.append(line)

with open('complex_5bv7_full.pdb', 'w') as f:
    f.writelines(header_lines)
    for cid in ('C','B','A'):
        f.writelines(seqres.get(cid, []))
    for cid in ('C','B','A'):
        f.writelines(chains_atoms.get(cid, []))
    f.write("END\n")

for cid in ('C','B','A'):
    print(f"Chain {cid}: SEQRES {len(seqres.get(cid,[]))} lines, ATOM {len(chains_atoms.get(cid,[]))} lines")
print("Wrote complex_5bv7_full.pdb")
