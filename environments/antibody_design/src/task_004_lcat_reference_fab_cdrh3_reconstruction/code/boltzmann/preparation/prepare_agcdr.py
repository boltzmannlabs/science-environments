#!/usr/bin/env python3
"""Prepare antibody and antigen PDBs with SEQRES matching modeled atoms (native format)."""
from collections import OrderedDict

AA1to3 = {'A':'ALA','R':'ARG','N':'ASN','D':'ASP','C':'CYS','Q':'GLN','E':'GLU',
          'G':'GLY','H':'HIS','I':'ILE','L':'LEU','K':'LYS','M':'MET','F':'PHE',
          'P':'PRO','S':'SER','T':'THR','W':'TRP','Y':'TYR','V':'VAL'}
AA3to1 = {v:k for k,v in AA1to3.items()}

def collect(pdb_path, target_chains):
    chains = OrderedDict()
    chains_atoms = OrderedDict()
    seen = set()
    header = []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM'):
                resn = line[17:20].strip()
                if resn in ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL','UNL','PEG','GOL','DOD'):
                    continue
                if resn not in AA3to1:
                    continue
                cid = line[21]
                if cid not in target_chains:
                    continue
                resseq = int(line[22:26].strip()); icode = line[26]
                key = (cid, resseq, icode)
                if key not in seen:
                    seen.add(key)
                    chains.setdefault(cid, []).append(AA3to1[resn])
                chains_atoms.setdefault(cid, []).append(line)
            elif line.startswith(('HEADER','TITLE','COMPND','SOURCE','EXPDTA')):
                header.append(line)
    return chains, chains_atoms, header

def write_seqres(f, cid, aas):
    n = len(aas); per = 13
    for i in range(0, n, per):
        serial = i//per + 1
        chunk = aas[i:i+per]
        res_str = ''.join(AA1to3[a]+' ' for a in chunk)
        line = "SEQRES" + f"{serial:>4d}" + " " + cid + " " + f"{n:>4d}" + "  " + res_str
        f.write(line.ljust(80) + '\n')

# Antibody: chains C, B
chains, atoms, header = collect('5BV7.pdb', ('C','B'))
with open('antibody_v3.pdb','w') as f:
    f.writelines(header)
    for cid in ('C','B'):
        write_seqres(f, cid, chains[cid])
    for cid in ('C','B'):
        f.writelines(atoms[cid])
    f.write("END\n")
print(f"antibody_v3.pdb: C={len(chains['C'])}, B={len(chains['B'])}")

# Antigen: chain A
chains, atoms, header = collect('5BV7.pdb', ('A',))
with open('antigen_v3.pdb','w') as f:
    f.writelines(header)
    write_seqres(f, 'A', chains['A'])
    f.writelines(atoms['A'])
    f.write("END\n")
print(f"antigen_v3.pdb: A={len(chains['A'])}")
