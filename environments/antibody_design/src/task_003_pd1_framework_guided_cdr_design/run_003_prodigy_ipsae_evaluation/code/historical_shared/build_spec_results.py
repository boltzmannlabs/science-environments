#!/usr/bin/env python3
"""Build spec-named result files (candidates.csv, metrics.csv, report.md) for run_001/run_002
from existing artifacts; convert metrics.json -> metrics.csv."""
import csv, json, os

BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
SRC = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design'
R1 = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody'
R2 = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn'
os.makedirs(R1, exist_ok=True)

pool = json.load(open(f'{SRC}/run_001/candidates/agcdr_pool.json'))['pool']
raw = json.load(open(f'{SRC}/run_001/metrics_raw.json'))
b2, props = raw['boltz2'], raw['properties']
sel = json.load(open(f'{SRC}/run_001/candidates/screening_selection.json'))['selected']

# candidates.csv (run_002): all 115 with gates + candidate IDs (stable IDs)
sel_keys = {(s['VH'], s['VL']): s for s in sel}
with open(f'{R2}/candidates.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['candidate_id', 'pool_tag', 'track', 'VH', 'VL', 'H1', 'H2', 'H3', 'L1', 'L2', 'L3',
                'gates_passed', 'selected_for_screening', 'screening_rank'])
    for i, c in enumerate(pool, start=1):
        cid = f'PD1T3-{i:03d}'
        s = sel_keys.get((c['VH'], c['VL']))
        w.writerow([cid, c.get('tag', c.get('source_tag', '')), 'agcdr_diff+AntiBMPNN',
                    c['VH'], c['VL'],
                    c['CDRs']['H1'], c['CDRs']['H2'], c['CDRs']['H3'],
                    c['CDRs']['L1'], c['CDRs']['L2'], c['CDRs']['L3'],
                    'PASS', bool(s), s['selection_rank'] if s else ''])

# metrics.csv (run_002): long-form candidate/control metrics
with open(f'{R2}/metrics.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['record_id', 'record_type', 'metric', 'value', 'unit', 'tool', 'scope'])
    hc = b2['H965_control']['PD1:VH']; hl = b2['H965_control']['[108, 113]']
    w.writerow(['H965_control', 'control', 'iptm_PD1_VH', hc['iptm'], '', 'Boltz2', 'our prediction'])
    w.writerow(['H965_control', 'control', 'iptm_PD1_VL', hl['iptm'], '', 'Boltz2', 'our prediction'])
    w.writerow(['H965_control', 'control', 'KD', 81.6, 'nM', 'SPR', 'published measurement (Suppl. Table 7)'])
    rank_cid = {1: 'PD1T3-069', 2: 'PD1T3-019', 3: 'PD1T3-011', 4: 'PD1T3-038', 5: 'PD1T3-054'}
    for k in range(1, 6):
        tag = f'cand_rank{k}'; cid = rank_cid[k]
        for pair, mname in [('PD1:VH', 'iptm_PD1_VH'), ('PD1:VL', 'iptm_PD1_VL')]:
            m = b2[tag].get(pair, {})
            w.writerow([cid, 'candidate', mname, m.get('iptm'), '', 'Boltz2', 'our prediction'])
            w.writerow([cid, 'candidate', 'iplddt_' + mname.split('_', 1)[1], m.get('complex_iplddt'), '', 'Boltz2', 'our prediction'])
            w.writerow([cid, 'candidate', 'contacts_lt5A_' + mname.split('_', 1)[1], m.get('n_atom_contacts_lt5A'), 'count', 'local analysis', 'model-derived'])
        p = props.get(tag, {})
        w.writerow([cid, 'candidate', 'thermal_stability_esm', p.get('Thermal_Stability_ESM', {}).get('Thermal_stab_esm'), 'C', 'Antibody_Prediction', 'prediction'])
        w.writerow([cid, 'candidate', 'solubility_esm', p.get('Solubility_ESM', {}).get('solubility'), '', 'Antibody_Prediction', 'prediction'])
print('run_002 candidates.csv + metrics.csv written')

# run_001: keep raw evidence + zero-candidate statement
import shutil
shutil.copy(f'{SRC}/run_001/candidates/rf_antibody_pool.json', f'{R1}/rf_antibody_pool.json')
shutil.copy(f'{SRC}/run_001/candidates/antibmpnn_pool.json', f'{R1}/antibmpnn_pool.json')
print('run_001 evidence copied')
