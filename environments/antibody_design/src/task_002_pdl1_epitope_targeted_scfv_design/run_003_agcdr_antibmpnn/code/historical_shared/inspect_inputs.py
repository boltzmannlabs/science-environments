#!/usr/bin/env python3
"""Inspect chains/sequences of task_002 input structures and map epitope hotspots.

Writes per-chain one-letter sequences, maps 35TL PD-L1 chain residues to the
mature PD-L1 numbering (UniProt Q9NZQ7 19-238), and reports contact context.
"""
import sys
from collections import OrderedDict

THREE2ONE = {
    'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
    'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
    'THR':'T','TRP':'W','TYR':'Y','VAL':'V','MSE':'M','PCA':'E','UNK':'X'
}

def parse(path, model=1):
    """Return OrderedDict chain -> OrderedDict resseq(,icode) -> (resname, first CA coord)."""
    chains = OrderedDict()
    cur_model = 1
    with open(path) as f:
        for line in f:
            if line.startswith('MODEL'):
                try: cur_model = int(line[6:].strip().split()[0])
                except Exception: cur_model += 1
            if line.startswith('ENDMDL'):
                cur_model = None
            if not line.startswith(('ATOM  ','HETATM')):
                continue
                if False: pass
            if cur_model not in (1, None) and not line.startswith(('ATOM  ','HETATM')):
                continue
            rec = line[:6].strip()
            if rec not in ('ATOM','HETATM'):
                continue
            atom = line[12:16].strip()
            resn = line[17:20].strip()
            chain = line[21]
            try:
                resseq = int(line[22:26])
            except ValueError:
                continue
            icode = line[26]
            altloc = line[16]
            if altloc not in (' ', 'A'):
                continue
            key = (resseq, icode.strip())
            ch = chains.setdefault(chain, OrderedDict())
            if atom == 'CA' or (resseq, icode) not in ch or atom != 'CA':
                if key not in ch:
                    ch[key] = [resn, None]
                if atom == 'CA':
                    ch[key][1] = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
    return chains

def seq_of(chain):
    return ''.join(THREE2ONE.get(v[0], 'X') for v in chain.values())

def resmap(chain):
    return list(chain.keys())

if __name__ == '__main__':
    base = '/home/boltzmann10/.sci/cache/scratch/task002'
    for p in ('35TL', '5JDS', '1N8Z'):
        chains = parse(f'{base}/{p}.pdb')
        print(f'== {p}')
        for c, ch in chains.items():
            seq = seq_of(ch)
            print(f'  chain {c}: {len(seq)} residues, seq={seq}')
        print()
