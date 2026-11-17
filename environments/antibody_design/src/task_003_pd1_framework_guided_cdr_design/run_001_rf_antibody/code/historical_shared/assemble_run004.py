#!/usr/bin/env python3
"""Assemble run_004 (Prodigy + ipSAE) results; update run_002 metrics.csv and benchmark_comparison.csv."""
import csv, json, os, shutil

OUTW = '/home/boltzmann10/.sci/workspace/outputs'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
R4 = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation'
R2 = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn'
SRC = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design'
os.makedirs(f'{R4}/raw', exist_ok=True)

# Prodigy per-model results (doc -> tag)
prodigy = {
    ('H965_control', 'VH'): -13.1, ('H965_control', 'VL'): -9.7,
    ('cand_rank1', 'VH'): -7.9, ('cand_rank1', 'VL'): -10.9,
    ('cand_rank2', 'VH'): -10.9, ('cand_rank2', 'VL'): -10.1,
    ('cand_rank3', 'VH'): -12.4, ('cand_rank3', 'VL'): -8.9,
    ('cand_rank4', 'VH'): -12.6, ('cand_rank4', 'VL'): -13.7,
    ('cand_rank5', 'VH'): -10.9, ('cand_rank5', 'VL'): -11.8,
}
docs = {
    ('H965_control','VH'): '6af886c89850a93adf67d73b', ('H965_control','VL'): '6af886d2239a6b9f38bec324',
    ('cand_rank1','VH'): '6af886df9850a93adf67d773', ('cand_rank1','VL'): '6af886ea9de6b44b075d86f1',
    ('cand_rank2','VH'): '6af886a89de6b44b075d8685', ('cand_rank2','VL'): '6af886f4239a6b9f38bec38d',
    ('cand_rank3','VH'): '6af886ff9de6b44b075d872a', ('cand_rank3','VL'): '6af887099de6b44b075d8750',
    ('cand_rank4','VH'): '6af88713239a6b9f38bec3dd', ('cand_rank4','VL'): '6af8871d239a6b9f38bec3fb',
    ('cand_rank5','VH'): '6af887289de6b44b075d8791', ('cand_rank5','VL'): '6af887329850a93adf67d827',
}
files = {
    ('H965_control','VH'): 'prodigy_h965_VH.csv', ('H965_control','VL'): 'prodigy_h965_VL.csv',
    ('cand_rank1','VH'): 'prodigy_cand1_VH.csv', ('cand_rank1','VL'): 'prodigy_cand1_VL.csv',
    ('cand_rank2','VH'): 'prodigy_cand2_VH.csv', ('cand_rank2','VL'): 'prodigy_cand2_VL.csv',
    ('cand_rank3','VH'): 'prodigy_cand3_VH.csv', ('cand_rank3','VL'): 'prodigy_cand3_VL.csv',
    ('cand_rank4','VH'): 'prodigy_cand4_VH.csv', ('cand_rank4','VL'): 'prodigy_cand4_VL.csv',
    ('cand_rank5','VH'): 'prodigy_cand5_VH.csv', ('cand_rank5','VL'): 'prodigy_cand5_VL.csv',
}
# verify values from downloaded CSVs (never trust transcription)
for key, fn in files.items():
    r = list(csv.DictReader(open(f'{OUTW}/{fn}')))
    v = float(r[0]['binding_affinity for AB'])
    assert v == prodigy[key], f'{key}: file {v} != recorded {prodigy[key]}'
    shutil.copy(f'{OUTW}/{fn}', f'{R4}/raw/{fn}')

# ipSAE
ipsae = {}
for r in csv.DictReader(open(f'{OUTW}/ipsae_results.csv')):
    entry = r['npz_file_path'].split('::')[1].split('/')[0]
    ipsae[entry] = r
shutil.copy(f'{OUTW}/ipsae_results.csv', f'{R4}/raw/ipsae_results.csv')

rank_cid = {1: 'PD1T3-069', 2: 'PD1T3-019', 3: 'PD1T3-011', 4: 'PD1T3-038', 5: 'PD1T3-054'}
tag_of = {v: k for k, v in rank_cid.items()}
tag_of['H965_control'] = 'H965_control'

def kd_nm(dg):
    import math
    return round(math.exp(dg / (0.0019872041 * 298.15)) * 1e9, 1)  # kcal/mol -> nM (assumes Prodigy outputs dG; flag as interpretation)

# run_004 metrics.csv
with open(f'{R4}/metrics.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['record_id', 'record_type', 'pair', 'metric', 'value', 'unit', 'tool', 'doc_id', 'scope'])
    for (tag, pair), dg in sorted(prodigy.items()):
        rid = 'H965_control' if tag == 'H965_control' else rank_cid[int(tag.split('rank')[1])]
        w.writerow([rid, 'control' if tag == 'H965_control' else 'candidate', f'PD1:{pair}',
                    'prodigy_binding_affinity', dg, 'predicted units (raw)', 'Prodigy', docs[(tag, pair)], 'structure-based prediction'])
    for entry, r in sorted(ipsae.items()):
        if entry.startswith('H965_control_PD1_VH'):
            rid, pair = 'H965_control', 'VH'
        elif entry.startswith('H965_control'):  # 108_113 entry = PD1:VL
            rid, pair = 'H965_control', 'VL'
        else:
            parts = entry.split('_')  # cand_rankN_PD1_VX
            rid, pair = rank_cid[int(parts[1].replace('rank', ''))], parts[-1]
        w.writerow([rid, 'control' if rid == 'H965_control' else 'candidate', f'PD1:{pair}',
                    'ipSAE_A_B_asym', r.get('A_B_asym_ipSAE'), '', 'ipsae-protein', '6af88746d29658acc304eb69', 'PAE-weighted interface score'])

# append Prodigy/ipSAE to run_002 metrics.csv
with open(f'{R2}/metrics.csv', 'a', newline='') as f:
    w = csv.writer(f)
    for (tag, pair), dg in sorted(prodigy.items()):
        rid = 'H965_control' if tag == 'H965_control' else rank_cid[int(tag.split('rank')[1])]
        w.writerow([rid, 'control' if tag == 'H965_control' else 'candidate', f'prodigy_PD1_{pair}', dg, 'predicted units (raw)', 'Prodigy', 'run_004 prediction'])
    for entry, r in sorted(ipsae.items()):
        if entry.startswith('H965_control_PD1_VH'):
            rid, pair = 'H965_control', 'VH'
        elif entry.startswith('H965_control'):
            rid, pair = 'H965_control', 'VL'
        else:
            parts = entry.split('_')
            rid, pair = rank_cid[int(parts[1].replace('rank', ''))], parts[-1]
        w.writerow([rid, 'control' if rid == 'H965_control' else 'candidate', f'ipSAE_PD1_{pair}', r.get('A_B_asym_ipSAE'), '', 'ipsae-protein', 'run_004 prediction'])

print('run_004 metrics.csv written; run_002 metrics.csv extended')
print('Prodigy summary:')
for (t, p), v in sorted(prodigy.items()):
    print(f'  {t:14s} {p}: {v}')
print('ipSAE entries:', len(ipsae))
