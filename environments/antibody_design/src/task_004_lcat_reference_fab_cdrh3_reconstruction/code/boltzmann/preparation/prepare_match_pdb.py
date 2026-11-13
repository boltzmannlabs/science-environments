#!/usr/bin/env python3
"""Prepare complex PDB with SEQRES generated from modeled ATOMs (exact match)."""
from collections import OrderedDict

AA1to3 = {'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','Q':'GLN','E':'GLU',
          'G':'GLY','H':'HIS','I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE',
          'P':'PRO','S':'SER','T':'THR','W':'TRP','Y':'TYR','V':'VAL'}
AA3to1 = {v:k for k,v in AA1to3.items()}

chains = OrderedDict()  # chain -> [(resseq, icode, aa1)] in order
seen = set()
header_lines = []

with open('5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM'):
            resn = line[17:20].strip()
            if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL','UNL','PEG','GOL','DOD'):
                continue
            if resn not in AA3to1:
                continue
            cid = line[21]
            if cid not in ('A','B','C'):
                continue
            resseq = int(line[22:26].strip())
            icode = line[26]
            aa1 = AA3to1[resn]
            key = (cid, resseq, icode)
            if key not in seen:
                seen.add(key)
                chains.setdefault(cid, []).append((resseq, icode, aa1))
        elif line.startswith(('HEADER','TITLE','COMPND','SOURCE','EXPDTA')):
            header_lines.append(line)

def write_seqres(f, cid, residues):
    """Write SEQRES records for a chain, 20 residues per line."""
    n = len(residues)
    for i in range(0, n, 20):
        chunk = residues[i:i+20]
        line = f"SEQRES {i//20+1:<5d} {cid} {n:<3d}"
        line += ''.join(f"  {AA1to3[aa]}" for _,_,aa in chunk)
        f.write(line.ljust(80) + '\n')

with open('complex_5bv7_match.pdb', 'w') as f:
    f.writelines(header_lines)
    for cid in ('C','B','A'):
        write_seqres(f, cid, chains[cid])
    for cid in ('C','B','A'):
        for resseq, icode, aa1 in chains[cid]:
            # Re-emit ATOM lines - need to re-read
            pass
    f.write("END\n")

# Simpler: just collect ATOM lines too
chains_atoms = OrderedDict()
with open('5BV7.pdb') as f:
    for line in f:
        if line.startswith('ATOM'):
            resn = line[17:20].strip()
            if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL','UNL','PEG','GOL','DOD'):
                continue
            if resn not in AA3to1:
                continue
            cid = line[21]
            if cid not in ('A','B','C'):
                continue
            chains_atoms.setdefault(cid, []).append(line)

with open('complex_5bv7_match.pdb', 'w') as f:
    f.writelines(header_lines)
    for cid in ('C','B','A'):
        write_seqres(f, cid, chains[cid])
    for cid in ('C','B','A'):
        f.writelines(chains_atoms[cid])
    f.write("END\n")

for cid in ('C','B','A'):
    print(f"Chain {cid}: modeled {len(chains[cid])} residues")
print("Wrote complex_5bv7_match.pdb")
