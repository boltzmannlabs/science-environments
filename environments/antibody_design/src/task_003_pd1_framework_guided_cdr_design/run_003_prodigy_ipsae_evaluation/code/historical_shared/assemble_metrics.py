#!/usr/bin/env python3
"""Assemble task_003 final bundle: extract Boltz2 metrics, interface contacts, properties;
build designed_sequences.fasta, metrics.json, shortlist.csv, benchmark_comparison.csv, report.md.
"""
import csv, glob, json, math, os, zipfile
from collections import defaultdict

OUTW = '/home/boltzmann10/.sci/workspace/outputs'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'
RES = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/pd1_results'
os.makedirs(f'{RES}/structures', exist_ok=True)
os.makedirs(f'{RES}/raw_outputs', exist_ok=True)

aa3to1 = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}

sel = json.load(open(f'{RUN}/candidates/screening_selection.json'))['selected']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']

def extract_boltz2(zippath, tag):
    zdir = f'{OUTW}/x_{tag}'
    os.makedirs(zdir, exist_ok=True)
    with zipfile.ZipFile(zippath) as z:
        z.extractall(zdir)
    out = {}
    for conf in glob.glob(f'{zdir}/**/confidence_*_model_0.json', recursive=True):
        j = json.load(open(conf))
        num = conf.split('confidence_')[1].split('_')[0]
        # determine pair by the accompanying pdb chain lengths
        pdb = conf.replace('confidence_', '').replace('.json', '.pdb').replace(f'{num}_', f'{num}_', 1)
        pdb = conf.rsplit('confidence_', 1)[0] + f'{num}_model_0.pdb'
        chains = []
        seen = set()
        for line in open(pdb):
            if line.startswith('ATOM'):
                k = (line[21], int(line[22:26]))
                if k not in seen:
                    seen.add(k)
                    if not chains or chains[-1][0] != line[21]:
                        chains.append([line[21], 0])
                    chains[-1][1] += 1
        if len(chains) != 2:
            continue
        lens = sorted(c[1] for c in chains)
        # PD-1 is 102/113; VH 117; VL 108
        if lens == [102, 117] or lens == [113, 117]:
            pair = 'PD1:VH'
        elif lens == [102, 108] or lens == [113, 108]:
            pair = 'PD1:VL'
        elif lens == [108, 117]:
            pair = 'VH:VL'
        else:
            pair = f'{lens}'
        # interface contacts (any heavy atom < 5A) + epitope overlap
        res_at = defaultdict(dict)
        for line in open(pdb):
            if line.startswith('ATOM') and line[17:20].strip() in aa3to1:
                res_at[(line[21], int(line[22:26]))][line[12:16].strip()] = (
                    float(line[30:38]), float(line[38:46]), float(line[46:54]))
        ch_pd1, ch_ab = chains[0][0], chains[1][0]
        if sum(1 for (c, _) in res_at if c == ch_pd1) > sum(1 for (c, _) in res_at if c == ch_ab):
            pass  # keep order as-is; identify by length instead
        pd1_ch = ch_pd1 if dict((c, n) for c, n in chains)[ch_pd1] != 117 and dict((c, n) for c, n in chains)[ch_pd1] != 108 else ch_ab
        iface = set()
        n_contacts = 0
        for (c1, r1), a1 in res_at.items():
            if c1 != pd1_ch:
                continue
            for (c2, r2), a2 in res_at.items():
                if c2 == pd1_ch:
                    continue
                for p1 in a1.values():
                    hit = False
                    for p2 in a2.values():
                        if math.dist(p1, p2) < 5.0:
                            iface.add(r1); n_contacts += 1; hit = True; break
                    if hit: break
        out[pair] = {'iptm': round(j['iptm'], 4),
                     'complex_iplddt': round(j['complex_iplddt'], 4),
                     'ptm': round(j['ptm'], 4),
                     'interface_residues_pd1': sorted(iface),
                     'n_atom_contacts_lt5A': n_contacts,
                     'pdb': pdb}
    return out

jobs = {
    'H965_control': f'{OUTW}/boltz2_h965/outputs.zip',
    'cand_rank1': f'{OUTW}/boltz2_cand1/outputs.zip',
    'cand_rank2': f'{OUTW}/boltz2_cand2/outputs.zip',
    'cand_rank3': f'{OUTW}/boltz2_cand3/outputs.zip',
    'cand_rank4': f'{OUTW}/boltz2_cand4/outputs.zip',
    'cand_rank5': f'{OUTW}/boltz2_cand5/outputs.zip',
}
metrics = {}
for tag, zp in jobs.items():
    metrics[tag] = extract_boltz2(zp, tag)
    print(tag, {k: v['iptm'] for k, v in metrics[tag].items()})

# properties
props = {}
for i, name in enumerate(['Thermal_Stability_ESM', 'Solubility_ESM', 'CDR_Prediction'], start=1):
    p = f'{OUTW}/output-{i}.csv'
    rows = list(csv.DictReader(open(p)))
    print(name, 'columns:', list(rows[0].keys()))
    for r in rows:
        sid = r.get('seq_id') or r.get('Name')
        props.setdefault(sid, {})[name] = {k: v for k, v in r.items() if k not in ('seq_id', 'Name')}

json.dump({'boltz2': metrics, 'properties': props}, open(f'{RUN}/metrics_raw.json', 'w'), indent=1)
print('saved metrics_raw.json')
