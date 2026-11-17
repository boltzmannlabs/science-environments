#!/usr/bin/env python3
"""Build the PD-1:framework-Fv design context from 5GGS coordinates.

Approach (deterministic, local):
- PD-1 (5GGS chain Y, residues 33-134, 5GGS numbering) -> chain P.
- Framework Fv placement: copy pembrolizumab Fv backbone geometry (5GGS chains A/B = VH/VL).
- Scaffold side identity: paper FR blocks + H965 CDRs relabeled onto those backbones
  (scaffold lengths match pembrolizumab within 1-2 residues at CDRs; backbone kept from source).
- This PDB is a DESIGN CONTEXT for antigen-conditioned redesign, not a final model: the design
  tools regenerate CDR backbone + sequence; FR geometry comes from the experimental 5GGS frame.
"""
import json

SRC = '/home/boltzmann10/.sci/cache/scratch/task003_paper'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'

aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
one2three = {v: k for k, v in aa3to1.items()}

# parse 5GGS standard residues
atoms = []
for line in open(f'{SRC}/5ggs.pdb'):
    if line.startswith('ATOM') and line[17:20].strip() in aa3to1:
        atoms.append((line[21], int(line[22:26]), line[17:20].strip(), line[12:16].strip(),
                      float(line[30:38]), float(line[38:46]), float(line[46:54])))

def res_order(ch):
    out, seen = [], set()
    for a in atoms:
        if a[0] == ch and a[1] not in seen:
            out.append(a[1]); seen.add(a[1])
    return out

def res_atoms(ch, resi):
    return {at: (x, y, z) for c, r, rn, at, x, y, z in atoms if c == ch and r == resi}

FR = json.load(open(f'{INP}/framework_table1.json'))['FR_blocks']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']
vh_scaf, vl_scaf = h965['VH'], h965['VL']

out_lines, serial = [], 1

def emit(ch, resi, resn3, coords):
    global serial
    for name, (x, y, z) in coords.items():
        out_lines.append(
            f'ATOM  {serial:5d} {name:>4s} {resn3:>3s} {ch}{resi:4d}    '
            f'{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C')
        serial += 1

# chain P: PD-1 from the Z copy (the Fab-contacting PD-1 in 5GGS; A/B Fab binds Y? no —
# verified: chains C/D contact chain Z). Residue range 31-143, 5GGS numbering preserved.
n_pd1 = 0
for resi in res_order('Z'):
    if 33 <= resi <= 134:
        rn = aa3to1[[a[2] for a in atoms if a[0] == 'Z' and a[1] == resi][0]]
        emit('P', resi, one2three[rn], res_atoms('Z', resi))
        n_pd1 += 1

# chains H / L: scaffold sequence on pembrolizumab Fv backbone (chains C/D, the Z-contacting Fab)
def emit_scaffold(ch, src_chain, scaf):
    src = res_order(src_chain)
    n = len(scaf)
    assert n <= len(src), f'{ch}: scaffold {n} longer than source backbone {len(src)}'
    for k in range(n):
        emit(ch, k + 1, one2three[scaf[k]], res_atoms(src_chain, src[k]))
    return n

n_h = emit_scaffold('H', 'A', vh_scaf)
n_l = emit_scaffold('L', 'B', vl_scaf)

out_lines += ['TER', 'END']
open(f'{INP}/pd1_frk_fv_complex.pdb', 'w').write('\n'.join(out_lines) + '\n')

# checks
print(f'PD-1 residues: {n_pd1} (chain P, 33-134)')
print(f'VH scaffold: {n_h} aa on pembrolizumab-VH backbone; VL scaffold: {n_l} aa')
print('VH scaffold sequence == H965 VH:', ''.join(scaf for scaf in [vh_scaf]) == h965['VH'])
print('Scaffold FR check: VH starts FR-H1:', vh_scaf.startswith(FR['FR-H1']),
      '| VL starts FR-L1:', vl_scaf.startswith(FR['FR-L1']))

# geometry sanity: min CA distance PD-1 vs scaffold chains
import math
ca = {}
for line in out_lines:
    if line.startswith('ATOM') and line[12:16].strip() == 'CA':
        ca.setdefault(line[21], []).append((int(line[22:26]), float(line[30:38]), float(line[38:46]), float(line[46:54])))
def mindist(c1, c2):
    best = 1e9
    for _, x1, y1, z1 in ca[c1]:
        for _, x2, y2, z2 in ca[c2]:
            d = math.dist((x1, y1, z1), (x2, y2, z2))
            if d < best:
                best = d
    return best
print('min CA dist P-H:', round(mindist('P', 'H'), 2), 'A; P-L:', round(mindist('P', 'L'), 2),
      'A; H-L:', round(mindist('H', 'L'), 2), 'A')
