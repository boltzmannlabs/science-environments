#!/usr/bin/env python3
"""Task 003 stage-0 input preparation (reproducible).

Builds, from the tFold reference pose (predicted H965(VH)+H965(VL)+PD-1 complex):
  1. framework.pdb      - VH (chain A) + VL (chain B) framework atoms only (CDR removed)
  2. pd1_target.pdb     - PD-1 chain, resSeq renumbered to native 4ZQK numbering (33-146)
  3. epitope.json       - PD-1 ligand-binding surface residues from native 4ZQK
                          (chain-B residues within 6.0 A of any PD-L1 heavy atom)

H965 sequences are comparison controls only; no H965 CDR sequence is carried into
candidates (all CDR geometry is removed from the design input).
"""
import json, os, math

REF = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/evidence/reference/task003_h965_pd1.pdb"
NATIVE = "/home/boltzmann10/.sci/cache/scratch/4ZQK.pdb"
OUT = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/evidence/inputs"
os.makedirs(OUT, exist_ok=True)

three2one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

def chain_seqs(path):
    res = {}
    with open(path) as f:
        for line in f:
            if line.startswith('ATOM'):
                ch = line[21]; ss = int(line[22:26].strip())
                res.setdefault(ch, {})[ss] = three2one[line[17:20].strip()]
    return {c: ''.join(r[k] for k in sorted(r)) for c, r in res.items()}

# Table 1 FR templates (Chothia), from PMC12815924
FR = {
    'H1':'EVQLLESGGGLVQPGGSLRLSCAAS','H2':'AMSWVRQAPGKGLEWVSAI',
    'H3':'TYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK','H4':'WGQGTLVTVSS',
    'L1':'DIQMTQSPSTLSASVGDRVTITC','L2':'WYQQKPGKAPKLLIY',
    'L3':'GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC','L4':'FGQGTKVEIK'}

seqs = chain_seqs(REF)
vh, vl, pd1 = seqs['A'], seqs['B'], seqs['C']
assert pd1 == "NPPTFSPALLVVTEGDNATFTCSFSNTSESFVLNWYRMSPSNQTDKLAAFPESRFRVTQLPNGRDFHMSVVRARRNDSGTYLCGAISLAPKAQIKESLRAELRVTE", "PD-1 mismatch"

# Exact CDR boundaries by substring location of FR templates
def boundaries(chain_seq, fr1, fr2, fr3, fr4):
    b = {}
    for name, fr in (('FR1',fr1),('FR2',fr2),('FR3',fr3),('FR4',fr4)):
        i = chain_seq.find(fr)
        assert i >= 0, f"{name} not found"
        b[name] = (i, i+len(fr))  # 0-based half-open
    # CDRs are the gaps
    cds = {}
    for k, (s,e) in enumerate([b['FR1'],b['FR2'],b['FR3'],b['FR4']]):
        if k == 0: continue
        prev_e = list(b.values())[k-1][1]
        cds[f'CDR{k}'] = (prev_e, s)
    return b, cds

vb, vcd = boundaries(vh, FR['H1'],FR['H2'],FR['H3'],FR['H4'])
lb, lcd = boundaries(vl, FR['L1'],FR['L2'],FR['L3'],FR['L4'])
print("VH boundaries:", vb, "VH CDRs:", {k:(vcd[k][0]+1,vcd[k][1]) for k in vcd}, "lengths:", {k:vcd[k][1]-vcd[k][0] for k in vcd})
print("VL boundaries:", lb, "VL CDRs:", {k:(lcd[k][0]+1,lcd[k][1]) for k in lcd}, "lengths:", {k:lcd[k][1]-lcd[k][0] for k in lcd})

def in_cdr(pos1, cds):
    return any(s < pos1 <= e for s,e in cds.values())

# Build framework.pdb (remove CDR atoms, keep FR atoms; chains A/B)
# Build pd1_target.pdb (chain C -> chain B, resSeq +32 to native 4ZQK numbering)
fw_lines, tg_lines = [], []
with open(REF) as f:
    for line in f:
        if not line.startswith(('ATOM','TER','END')):
            fw_lines.append(line) if line.startswith('HEADER') else None
            continue
        if line.startswith('ATOM'):
            ch = line[21]; ss = int(line[22:26].strip())
            if ch in ('A','B'):
                if not in_cdr(ss, vcd if ch=='A' else lcd):
                    fw_lines.append(line)
            elif ch == 'C':
                newseq = ss + 32
                tg_lines = tg_lines  # no-op
                nl = line[:22] + str(newseq).rjust(4) + line[26:]
                tg_lines.append(nl.replace(line[21], 'B', 1) if False else nl)
        elif line.startswith('TER'):
            pass
        elif line.startswith('END'):
            pass
# fix chain ID on target lines (replace column 22 char only in ATOM records)
tg_lines = []
with open(REF) as f:
    for line in f:
        if line.startswith('ATOM') and line[21]=='C':
            ss = int(line[22:26].strip()); nl = line[:21]+'B'+str(ss+32).rjust(4)+line[26:]
            tg_lines.append(nl)
with open(OUT+'/framework.pdb','w') as f:
    f.write(''.join(fw_lines)); f.write('END\n')
with open(OUT+'/pd1_target.pdb','w') as f:
    f.write('HEADER    PD-1 EC domain (construct seq of PDB 4ZQK chain B; coords from tFold reference pose)\n')
    f.write(''.join(tg_lines)); f.write('END\n')

# Epitope: native 4ZQK chain B residues within 6.0 A of chain A heavy atoms
def heavy_atoms(path, chain):
    atoms = []
    with open(path) as f:
        for line in f:
            if line.startswith('ATOM') and line[21]==chain:
                try:
                    xyz = tuple(map(float, line[30:54].split()))
                    if any(map(math.isnan, xyz)): raise ValueError
                except ValueError:
                    continue
                atoms.append((int(line[22:26].strip()), xyz))
    return atoms
aA, aB = heavy_atoms(NATIVE,'A'), heavy_atoms(NATIVE,'B')
epi = set()
for ss, p in aB:
    for _, q in aA:
        if math.dist(p,q) <= 6.0:
            epi.add(ss); break
epi_sorted = sorted(epi)
with open(OUT+'/epitope.json','w') as f:
    json.dump({'cutoff_A':6.0,'source':'PDB 4ZQK chain B (PD-1) heavy atoms within 6.0 A of any chain A (PD-L1) heavy atom','residues':[str(x) for x in epi_sorted],'chain_qualified':[f'B:{x}' for x in epi_sorted]}, f, indent=2)
print(f"epitope: {len(epi_sorted)} residues: {epi_sorted}")
print("wrote", OUT)
