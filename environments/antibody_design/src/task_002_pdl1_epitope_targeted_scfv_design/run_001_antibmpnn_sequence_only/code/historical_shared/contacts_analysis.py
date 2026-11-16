#!/usr/bin/env python3
"""Contact + numbering analysis for 35TL (H5 complex, eval only) and 5JDS (pose seed candidate).

- Verifies paper hotspot mapping I37/Y39/E41 on both structures' actual resSeq.
- Lists interface residues (any heavy-atom distance <= 5 A) per complex.
"""
import math
from collections import OrderedDict

THREE2ONE = {
    'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
    'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
    'THR':'T','TRP':'W','TYR':'Y','VAL':'V','MSE':'M'
}

def parse_atoms(path):
    atoms = []
    with open(path) as f:
        for line in f:
            if not line.startswith(('ATOM  ', 'HETATM')):
                continue
            atom = line[12:16].strip()
            resn = line[17:20].strip()
            chain = line[21]
            try:
                resseq = int(line[22:26])
            except ValueError:
                continue
            icode = line[26].strip()
            altloc = line[16]
            if altloc not in (' ', 'A'):
                continue
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            is_std_protein = resn in THREE2ONE
            is_het = line[:6].strip() == 'HETATM'
            atoms.append(dict(atom=atom, resn=resn, chain=chain, resseq=resseq,
                              icode=icode, xyz=(x, y, z), protein=is_std_protein, het=is_het))
    return atoms

def chain_residues(atoms, chain, protein_only=True):
    res = OrderedDict()
    for a in atoms:
        if a['chain'] != chain:
            continue
        if protein_only and not a['protein']:
            continue
        res.setdefault((a['resseq'], a['icode']), a['resn'])
    return res

def contacts(atoms, chains1, chains2, cutoff=5.0):
    """Return set of (chain,resseq,icode,resn) in chains1 within cutoff of any atom in chains2."""
    A = [a for a in atoms if a['chain'] in chains1]
    B = [a for a in atoms if a['chain'] in chains2]
    out = OrderedDict()
    for a in A:
        ax, ay, az = a['xyz']
        for b in B:
            bx, by, bz = b['xyz']
            dx = ax-bx; dy = ay-by; dz = az-bz
            if dx*dx+dy*dy+dz*dz <= cutoff*cutoff:
                key = (a['chain'], a['resseq'], a['icode'], a['resn'], a['het'])
                out[key] = True
                break
    return list(out.keys())

def fmt(cs):
    return ' '.join(f"{c}:{r}{ic}{'(het)' if het else ''}" for c, r, ic, rn, het in cs)

if __name__ == '__main__':
    base = '/home/boltzmann10/.sci/cache/scratch/task002'

    print('=== 35TL (experimental H5:PD-L1 complex; EVALUATION USE ONLY) ===')
    atoms = parse_atoms(f'{base}/35TL.pdb')
    for c in ('A', 'B', 'C'):
        res = chain_residues(atoms, c)
        first, last = next(iter(res)), list(res)[-1]
        print(f'chain {c}: {len(res)} protein residues, resSeq {first[0]}{first[1]}..{last[0]}{last[1]}')
    pdl1_contacts = contacts(atoms, ['A'], ['B', 'C'])
    vh_contacts = contacts(atoms, ['B'], ['A'])
    vl_contacts = contacts(atoms, ['C'], ['A'])
    print(f'PD-L1 interface residues (<=5A of H5): {fmt(pdl1_contacts)}')
    print(f'H5 VH interface residues: {fmt(vh_contacts)}')
    print(f'H5 VL interface residues: {fmt(vl_contacts)}')

    print()
    print('=== 5JDS (PD-L1 V-domain + anti-PD-L1 nanobody; pose-seed candidate) ===')
    atoms5 = parse_atoms(f'{base}/5JDS.pdb')
    for c in ('A', 'B'):
        res = chain_residues(atoms5, c)
        first, last = next(iter(res)), list(res)[-1]
        het_res = OrderedDict()
        for a in atoms5:
            if a['chain'] == c and a['het']:
                het_res.setdefault((a['resseq'], a['resn']), 0)
                het_res[(a['resseq'], a['resn'])] += 1
        print(f'chain {c}: {len(res)} protein residues, resSeq {first[0]}..{last[0]}; HETATM residues: {len(het_res)}')
        if het_res:
            print('   first/last het:', list(het_res.items())[:3], '...', list(het_res.items())[-3:])
    nb_contacts = contacts(atoms5, ['B'], ['A'])
    print(f'5JDS nanobody interface residues on nanobody: {len(nb_contacts)}')
    pdl1_5jds = contacts(atoms5, ['A'], ['B'])
    print(f'5JDS PD-L1 residues contacted by nanobody: {fmt(pdl1_5jds)}')

    # hotspot check on both structures
    for name, atoms_x, ch in (('35TL', atoms, 'A'), ('5JDS', atoms5, 'A')):
        res = chain_residues(atoms_x, ch)
        seqpos = list(res)
        seq = ''.join(THREE2ONE.get(r, 'X') for r in res.values())
        # find the IVYWEME motif positions
        import re
        for m in re.finditer('IVYWEME', seq):
            print(f'{name} {ch}: IVYWEME at 1-based observed index {m.start()+1}, resSeq {seqpos[m.start()][0]}..{seqpos[m.start()+6][0]}')
        # what residue sits at resSeq 37, 39, 41?
        bynum = {rs[0]: rn for rs, rn in res.items()}
        print(f'{name} {ch}: resSeq 37={bynum.get(37)} 39={bynum.get(39)} 41={bynum.get(41)}')
