#!/usr/bin/env python3
"""Compute contact-residue AAR (CAAR). Contact = CDR-H3 heavy atom within 5A of antigen (chain A)."""
import math, csv

AA3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E',
          'GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F',
          'PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
AA1to3 = {v:k for k,v in AA3to1.items()}
SKIP = ('HOH','WAT','EDO','GLC','NAG','BME','CLR','SUL','PO4','NA','CL')

# Collect heavy atoms: CDR-H3 (chain C, 97-115) and antigen (chain A)
cdrh3_atoms = []  # (resseq, x,y,z)
antigen_atoms = []
with open('5BV7.pdb') as f:
    for line in f:
        if not line.startswith('ATOM'): continue
        resn = line[17:20].strip()
        if resn in SKIP or line[12:16].strip().startswith('H'): continue
        cid = line[21]
        rs = int(line[22:26].strip())
        x,y,z = float(line[30:38]), float(line[38:46]), float(line[46:54])
        if cid=='C' and 97<=rs<=115:
            cdrh3_atoms.append((rs,x,y,z))
        elif cid=='A':
            antigen_atoms.append((x,y,z))

# Contact residues: any CDR-H3 heavy atom within 5A of any antigen atom
contact = set()
for rs,x,y,z in cdrh3_atoms:
    for ax,ay,az in antigen_atoms:
        if math.sqrt((x-ax)**2+(y-ay)**2+(z-az)**2) < 5.0:
            contact.add(rs); break

# Map to CDR-H3 local index (0-based: res 96 -> index 0)
contact_idx = sorted(r-96 for r in contact)
print(f"Contact residues (PDB): {sorted(contact)}")
print(f"Contact local indices (0-based): {contact_idx}")
print(f"Num contact: {len(contact_idx)}/19")

native_cdrh3 = "AREGAAVRSFYYSYYGMDV"

def caar_for(seq_list, label):
    # seq_list: list of CDR-H3 strings
    caar_by_idx = {i: [] for i in contact_idx}
    for cdr in seq_list:
        for i in contact_idx:
            caar_by_idx[i].append(1 if cdr[i]==native_cdrh3[i] else 0)
    mean_caar = sum(sum(v)/len(v) for v in caar_by_idx.values())/len(contact_idx)
    print(f"{label}: CAAR = {mean_caar:.3f} ({len(contact_idx)} contact positions)")
    return mean_caar

# CDR_Generator
with open('cdr_generator_output.csv') as f:
    cdrs = [r['Sequence'][95:114] for r in csv.DictReader(f)]
caar_for(cdrs, "CDR_Generator (n=%d)" % len(cdrs))

# AntiBMPNN
with open('antibmpnn_results/antibmpnn_results.csv') as f:
    cdrs = [r['heavy_chain'][95:114] for r in csv.DictReader(f)]
caar_for(cdrs, "AntiBMPNN (n=%d)" % len(cdrs))

import json
with open('contact_residues.json','w') as f:
    json.dump({'contact_pdb_residues': sorted(contact), 'contact_local_indices': contact_idx, 'native_cdrh3': native_cdrh3}, f, indent=2)
