#!/usr/bin/env python3
"""task_008 run preparation: extract cetuximab Fv + EGFR from 1YY9 into Boltzmann-ready PDBs.

Outputs (written next to this script's run inputs/):
  shared/complex_hla.pdb    chains H (VH 1-119), L (VL 1-107), A (EGFR ECD 1-613), same frame
  shared/antibody_hl.pdb    chains H, L only (agcdr_diff antibody input)
  shared/antigen_egfr.pdb   chain A only (agcdr_diff antigen input)
  shared/reference.json     VH/VL/linker/scFv, Chothia CDR map (ANARCI), EGFR construct, hashes
Validation: extracted VH/VL must equal the ProteinBase vast-bear-marble reference sequence.
"""
import json, hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
TASK = os.path.dirname(RUN)
SHARED = os.path.join(RUN, 'inputs', 'shared')
os.makedirs(SHARED, exist_ok=True)
SRC_PDB = os.path.join(RUN, 'inputs', '1yy9.pdb')

# ProteinBase vast-bear-marble reference (fetched 2026-11-14, verified vs record page)
REF_SCFV = ('QVQLKQSGPGLVQPSQSLSITCTVSGFSLTNYGVHWVRQSPGKGLEWLGVIWSGGNTDYNTPFTSRLSINKDNSKSQVFFK'
            'MNSLQSNDTAIYYCARALTYYDYEFAYWGQGTLVTVSA'
            'GGGGSGGGGSGGGGS'
            'DILLTQSPVILSVSPGERVSFSCRASQSIGTNIHWYQQRTNGSPRLLIKYASESISGIPSRFSGSGSGTDFTLSINSVE'
            'SEDIADYYCQQNNNWPTTFGAGTKLELK')
LINKER = 'GGGGSGGGGSGGGGS'
VH_REF = REF_SCFV.split(LINKER)[0]
VL_REF = REF_SCFV.split(LINKER)[1]

three2one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G',
             'HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S',
             'THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

# ---- parse 1YY9 (first altloc only) ----
residues = {}   # (ch, resseq, icode) -> [lines]
order = {}      # ch -> [(resseq, icode)] in file order
for l in open(SRC_PDB):
    if not l.startswith('ATOM'):
        continue
    alt = l[16]
    if alt not in (' ', 'A'):
        continue
    key = (l[21], int(l[22:26]), l[26])
    if key not in residues:
        residues[key] = []
        order.setdefault(key[0], []).append((key[1], key[2]))
    residues[key].append(l)

def chain_seq(ch):
    out = []
    for (rs, ic) in order[ch]:
        aa = residues[(ch, rs, ic)][0][17:20].strip()
        out.append((rs, ic, three2one.get(aa, 'X')))
    return out

# insertion codes present?
icodes = {ch: [k for k in order[ch] if k[1] not in (' ', '')] for ch in order}
print('insertion-code residues per chain:', {c: len(v) for c, v in icodes.items()})

# ---- Fv extraction: observed-order first 119 (heavy D) / 107 (light C) residues ----
heavy = chain_seq('D')[:119]
light = chain_seq('C')[:107]
vh = ''.join(x[2] for x in heavy)
vl = ''.join(x[2] for x in light)
assert vh == VH_REF, f'VH mismatch vs ProteinBase reference:\n{vh}'
assert vl == VL_REF, f'VL mismatch vs ProteinBase reference:\n{vl}'
print(f'VH {len(vh)} aa and VL {len(vl)} aa match vast-bear-marble reference exactly')

egfr = chain_seq('A')
egfr_seq = ''.join(x[2] for x in egfr)
assert len(egfr) == 613 and 'X' not in egfr_seq
print(f'EGFR ECD chain A: {len(egfr)} residues (1YY9 construct, UNP 25-642)')

def write_pdb(path, chain_map):
    """chain_map: {src_chain: (new_chain, keep_keys)} renumbered sequentially."""
    with open(path, 'w') as f:
        for src, (new, keys) in chain_map.items():
            n = 0
            for key in keys:
                n += 1
                for l in residues[(src, key[0], key[1])]:
                    f.write(l[:21] + new + f'{n:4d}' + l[26:].rstrip('\n') + '\n')
        f.write('TER\nEND\n')

h_keys = [(rs, ic) for rs, ic, _ in heavy]
l_keys = [(rs, ic) for rs, ic, _ in light]
a_keys = [(rs, ic) for rs, ic, _ in egfr]
write_pdb(os.path.join(SHARED, 'complex_hla.pdb'), {'D': ('H', h_keys), 'C': ('L', l_keys), 'A': ('A', a_keys)})
write_pdb(os.path.join(SHARED, 'antibody_hl.pdb'), {'D': ('H', h_keys), 'C': ('L', l_keys)})
write_pdb(os.path.join(SHARED, 'antigen_egfr.pdb'), {'A': ('A', a_keys)})

# ---- Chothia CDR map via ANARCI (igdesign env) ----
ANARCI_PY = '/home/boltzmann10/anaconda3/envs/igdesign/bin/python'
script = os.path.join(HERE, 'anarci_cdr.py')
r = subprocess.run([ANARCI_PY, script, VH_REF, VL_REF, os.path.join(SHARED, '_anarci_cdr.json')],
                   capture_output=True, text=True, timeout=600)
if r.returncode != 0:
    print('ANARCI FAILED:', r.stderr[-500:]); sys.exit(1)
cdrmap = json.load(open(os.path.join(SHARED, '_anarci_cdr.json')))
for dom in ('VH', 'VL'):
    for cdr in (k for k in cdrmap[dom] if k != 'positions'):
        d = cdrmap[dom][cdr]
        print(f"{cdr}: {dom} {d['start']}-{d['end']} ({d['length']}) {d['segment']}")

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

files = {os.path.basename(p): sha(os.path.join(SHARED, p))
         for p in os.listdir(SHARED) if os.path.isfile(os.path.join(SHARED, p))}
json.dump({
    'reference_record': 'ProteinBase vast-bear-marble (Cetuximab scFv parent; binding EGFR Strong, KD 6.6e-9 M)',
    'reference_scfv': REF_SCFV, 'vh': VH_REF, 'vl': VL_REF, 'linker': LINKER,
    'source_structure': 'PDB 1YY9 (EGFR ECD + cetuximab Fab, experimental)',
    'egfr_construct': {'chain': 'A', 'length': len(egfr_seq), 'unp': 'P00533 residues 25-642',
                       'sequence': egfr_seq},
    'cdr_chothia': {d: {c: cdrmap[d][c] for c in cdrmap[d] if c != 'positions'} for d in ('VH', 'VL')},
    'scfv_cdr_positions': {
        'H1': [cdrmap['VH']['H1']['start'], cdrmap['VH']['H1']['end']],
        'H2': [cdrmap['VH']['H2']['start'], cdrmap['VH']['H2']['end']],
        'H3': [cdrmap['VH']['H3']['start'], cdrmap['VH']['H3']['end']],
        'L1': [cdrmap['VL']['L1']['start'] + 134, cdrmap['VL']['L1']['end'] + 134],
        'L2': [cdrmap['VL']['L2']['start'] + 134, cdrmap['VL']['L2']['end'] + 134],
        'L3': [cdrmap['VL']['L3']['start'] + 134, cdrmap['VL']['L3']['end'] + 134]},
    'canonical_cys_scfv': [22, 95, 157, 222],
    'file_sha256': files,
}, open(os.path.join(SHARED, 'reference.json'), 'w'), indent=1)
open(os.path.join(SHARED, 'reference_scfv.fasta'), 'w').write(
    '>vast-bear-marble_cetuximab_scFv_reference\n' + REF_SCFV + '\n')
open(os.path.join(SHARED, 'egfr_construct.fasta'), 'w').write(
    '>EGFR_ECD_1yy9_UNP25_642\n' + egfr_seq + '\n')
print('shared preparation complete ->', SHARED)
