#!/usr/bin/env python3
"""Prepare masked antibody and antigen PDB files from 5BV7 for target-aware workflows."""
from collections import OrderedDict
import re

def parse_pdb(pdb_path):
    """Parse PDB file into ATOM lines grouped by chain."""
    chains = OrderedDict()
    other_lines = []
    with open(pdb_path) as f:
        for line in f:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                resn = line[17:20].strip()
                if resn in ('HOH', 'WAT', 'EDO', 'GLC', 'NAG', 'BME', 'CLR', 'SUL', 'PO4', 'NA', 'CL', 'UNL', 'PEG', 'GOL', 'DOD'):
                    continue
                chain_id = line[21]
                if chain_id not in chains:
                    chains[chain_id] = []
                chains[chain_id].append(line)
            elif line.startswith(('END', 'MASTER', 'REMARK')):
                continue
    return chains

def write_pdb(chain_ids, chains, output_path):
    """Write selected chains to a PDB file."""
    with open(output_path, 'w') as f:
        for cid in chain_ids:
            if cid in chains:
                f.writelines(chains[cid])
        f.write("END\n")
    # Count atoms
    n_atoms = sum(len(chains[cid]) for cid in chain_ids if cid in chains)
    print(f"Written {output_path}: chains {chain_ids}, {n_atoms} atoms")

chains = parse_pdb('5BV7.pdb')
print("Available chains:", list(chains.keys()))
for cid in chains:
    print(f"  Chain {cid}: {len(chains[cid])} atoms")

# Create antibody PDB (heavy C + light B)
write_pdb(['C', 'B'], chains, 'antibody_5bv7.pdb')

# Create antigen PDB (chain A)
write_pdb(['A'], chains, 'antigen_5bv7.pdb')

# Also create a combined complex PDB (for reference)
write_pdb(['C', 'B', 'A'], chains, 'complex_5bv7.pdb')

print("\n=== Done ===")
print("antibody_5bv7.pdb: Heavy C + Light B (with CDR-H3 present for AgCDR-Diff)")
print("antigen_5bv7.pdb: Antigen A (LCAT L4F/N5D)")
print("complex_5bv7.pdb: Full complex (for reference)")
