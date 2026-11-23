#!/usr/bin/env python3
"""ProteinMPNN fixed-backbone CDR3 design for task_007.

Frozen canonical backbone: Boltz-2 predicted parent VHH (chain A, 1..121).
Design mask (1-based): 97, 101, 103, 104, 105, 106. All other positions fixed.
200 samples. Output: FASTA of full-length sequences.
"""
import json
import sys
from pathlib import Path

import torch
from proteinmpnn import ProteinMPNN
from Bio.PDB import PDBParser, PDBIO, Select


class ChainASelect(Select):
    def accept_chain(self, chain):
        return chain.id == 'A'


def main(pdb_in, out_fasta, out_log, samples=200, seed=2026):
    log = open(out_log, 'a')
    def p(*a):
        print(*a, file=log, flush=True)
        print(*a, flush=True)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = ProteinMPNN(device=device, seed=seed, temperature=1.0, noise=0.01)
    p('device:', device, 'samples:', samples, 'seed:', seed)

    # strip to chain A (already chain A only) and parse
    parser = PDBParser(QUIET=True)
    struct = parser.get_structure('parent', pdb_in)
    io = PDBIO()
    io.set_structure(struct)
    clean_pdb = pdb_in + '.chainA.pdb'
    io.save(clean_pdb, ChainASelect())
    p('saved clean pdb:', clean_pdb)

    # fixed positions: everything except the mask
    mask = {97, 101, 103, 104, 105, 106}
    fixed = [str(i) for i in range(1, 122) if i not in mask]
    seqs = model.fixed_from_pdb(clean_pdb, fixed_residues=fixed, sample_seq=samples)
    p('raw sequences:', len(seqs))

    with open(out_fasta, 'w') as f:
        for i, s in enumerate(seqs):
            f.write(f'>cdr3_pmnn_s{i+1:03d}\n{s}\n')
    p('wrote', out_fasta)
    log.close()


if __name__ == '__main__':
    main(*sys.argv[1:4], samples=int(sys.argv[4]) if len(sys.argv) > 4 else 200)
