#!/usr/bin/env python3
"""Analyze the two parallel design lanes (AntiBMPNN CDR-only; RF-Antibody).
Verifies framework preservation, extracts CDRs at declared boundaries,
computes diversity, and emits a candidate table."""
import csv
import glob
import json
import os
import sys

sys.path.insert(0, '/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/code')
from prep_design_inputs import parse_protein, THREE2ONE  # noqa: E402

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
CDRS = {'H1': (26, 33), 'H2': (51, 58), 'H3': (97, 109),
        'L1': (24, 29), 'L2': (50, 55), 'L3': (89, 97)}
# parent framework sequences (trastuzumab scFv from study pdbs/scfv.pdb)
PARENT_H = ('EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIH_WVRQAPGKGLEWVARIYPTNGYTRYAD'
            'SVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYC_--------WGQGTLVTVSS')
# derive parent from study framework file instead:
st = parse_protein('/home/boltzmann10/new_agent_scienece_env/science-environments/'
                   'environments/antibody_design/src/task_002_pdl1_epitope_targeted_scfv_design/'
                   'run1_epitope_abgen/inputs/study_framework_scfv.pdb')
res = list(st.values())
PARENT_VH = ''.join(THREE2ONE[r['resn']] for r in res[:120])
PARENT_VL = ''.join(THREE2ONE[r['resn']] for r in res[135:])  # 136-242 -> 107 aa
assert len(PARENT_VH) == 120 and len(PARENT_VL) == 107, (len(PARENT_VH), len(PARENT_VL))


def framework_ok(seq, parent):
    """All non-CDR positions match parent."""
    bad = []
    for i, (a, b) in enumerate(zip(seq, parent)):
        cdr = any(lo <= i + 1 <= hi for lo, hi in CDRS.values()
                  if (lo, hi) in [CDRS['H1'], CDRS['H2'], CDRS['H3']])
        if a != b and not cdr:
            bad.append(i + 1)
    return bad


def framework_ok_h(seq):
    bad = []
    for i, (a, b) in enumerate(zip(seq, PARENT_VH)):
        in_cdr = any(lo <= i + 1 <= hi for lo, hi in (CDRS['H1'], CDRS['H2'], CDRS['H3']))
        if a != b and not in_cdr:
            bad.append(i + 1)
    return bad


def framework_ok_l(seq):
    bad = []
    for i, (a, b) in enumerate(zip(seq, PARENT_VL)):
        in_cdr = any(lo <= i + 1 <= hi for lo, hi in (CDRS['L1'], CDRS['L2'], CDRS['L3']))
        if a != b and not in_cdr:
            bad.append(i + 1)
    return bad


def get_cdrs(seq, chain):
    return {n: seq[lo - 1:hi] for n, (lo, hi) in CDRS.items() if n[0] == chain}


report = {'antibmpnn': [], 'rfab': []}

# ---- AntiBMPNN lane ----
rows = list(csv.DictReader(open(f'{SCRATCH}/antibmpnn_raw/extracted/antibmpnn_results.csv')))
print(f'AntiBMPNN: {len(rows)} rows')
for i, r in enumerate(rows):
    h, l = r['heavy_chain'], r['light_chain']
    assert len(h) == 120 and len(l) == 107, (len(h), len(l))
    fh, fl = framework_ok_h(h), framework_ok_l(l)
    mut_h = sum(a != b for a, b in zip(h, PARENT_VH))
    mut_l = sum(a != b for a, b in zip(l, PARENT_VL))
    report['antibmpnn'].append(dict(
        idx=i, mut_H=mut_h, mut_L=mut_l,
        framework_violations_H=fh, framework_violations_L=fl,
        CDRs={**get_cdrs(h, 'H'), **get_cdrs(l, 'L')},
        VH=h, VL=l))
    print(f'  #{i}: mut H {mut_h} L {mut_l}; framework violations H={fh} L={fl}')

# ---- RF-Antibody lane ----
rf_rows = []
for csvf in sorted(glob.glob(f'{SCRATCH}/rfab_raw/extracted/ab_des_output_*_mpnn.csv')):
    base = os.path.basename(csvf).replace('_mpnn.csv', '')
    entries = {}
    for r in csv.DictReader(open(csvf)):
        tag = r['tag']
        design = tag.rsplit('_', 1)[0]
        entries.setdefault(design, {})[r['chain']] = (r['sequence'], float(r['score']))
    for design, chains in entries.items():
        hs = chains.get('Heavy_chain', ('', None))[0]
        ls = chains.get('Light_chain', ('', None))[0]
        rf_rows.append(dict(backbone=base, design=design, VH=hs, VL=ls,
                            score=chains.get('Heavy_chain', ('', None))[1]))
print(f'RF-Antibody: {len(rf_rows)} designs')
for i, r in enumerate(rf_rows):
    h, l = r['VH'], r['VL']
    fh = framework_ok_h(h) if len(h) == 120 else [f'len={len(h)}']
    fl = framework_ok_l(l) if len(l) == 107 else [f'len={len(l)}']
    r.update(framework_violations_H=fh, framework_violations_L=fl,
             CDRs={**get_cdrs(h, 'H'), **get_cdrs(l, 'L')} if len(h) == 120 and len(l) == 107 else {})
    r['mut_H'] = sum(a != b for a, b in zip(h, PARENT_VH)) if len(h) == 120 else None
    r['mut_L'] = sum(a != b for a, b in zip(l, PARENT_VL)) if len(l) == 107 else None
    print(f"  {r['backbone']}/{r['design']}: VH {len(h)}aa VL {len(l)}aa score {r['score']} "
          f"violations H={len(fh)} L={len(fl)}")
report['rfab'] = rf_rows

out = f'{SCRATCH}/parallel_lanes_analysis.json'
json.dump(report, open(out, 'w'), indent=1)
print('wrote', out)
