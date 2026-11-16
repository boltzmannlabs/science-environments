#!/usr/bin/env python3
"""Build run_004 benchmark_comparison.csv: Prodigy + ipSAE predictions vs H965 control (same-protocol pairs)."""
import csv

R4 = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation'

prodigy = {
    'H965_control': {'VH': -13.1, 'VL': -9.7},
    'PD1T3-069': {'VH': -7.9, 'VL': -10.9},
    'PD1T3-019': {'VH': -10.9, 'VL': -10.1},
    'PD1T3-011': {'VH': -12.4, 'VL': -8.9},
    'PD1T3-038': {'VH': -12.6, 'VL': -13.7},
    'PD1T3-054': {'VH': -10.9, 'VL': -11.8},
}
ipsae = {
    'H965_control': {'VH': 0.785058, 'VL': 0.269031},
    'PD1T3-069': {'VH': 0.31789, 'VL': 0.468605},
    'PD1T3-019': {'VH': 0.899311, 'VL': 0.815554},
    'PD1T3-011': {'VH': 0.891207, 'VL': 0.181306},
    'PD1T3-038': {'VH': 0.726325, 'VL': 0.641322},
    'PD1T3-054': {'VH': 0.755745, 'VL': 0.390241},
}

with open(f'{R4}/benchmark_comparison.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['candidate_id', 'record_type', 'pair', 'metric', 'candidate_value', 'h965_control_value', 'delta_vs_control', 'comparison_verdict', 'reference_value', 'reference_source', 'notes'])
    for cid in ['PD1T3-019', 'PD1T3-011', 'PD1T3-038', 'PD1T3-054', 'PD1T3-069']:
        for pair in ['VH', 'VL']:
            pv, hv = prodigy[cid][pair], prodigy['H965_control'][pair]
            verdict = 'more favorable (lower)' if pv < hv else ('equal' if pv == hv else 'less favorable (higher)')
            w.writerow([cid, 'candidate', f'PD1:{pair}', 'prodigy_binding_affinity_raw', pv, hv, round(pv - hv, 1), verdict, '', '', 'structure-based prediction on Boltz2 model; raw units uninterpreted'])
            iv, ih = ipsae[cid][pair], ipsae['H965_control'][pair]
            verdict = 'above control' if iv > ih else ('equal' if iv == ih else 'below control')
            w.writerow([cid, 'candidate', f'PD1:{pair}', 'ipSAE_A_B_asym', iv, ih, round(iv - ih, 6), verdict, '', '', 'PAE-weighted interface score, higher = more confident interface'])
    # control reference rows: measured KD from paper for context
    w.writerow(['H965_control', 'control', 'PD1:VH+VL', 'measured_KD_SPR', '', '', '', 'reference_only', 81.6, 'nM; paper Suppl. Table 7 (SPR)', 'experimental measurement; candidates have no measured values'])
    w.writerow(['PD1T3-019', 'candidate', 'PD1:VH+VL', 'measured_KD_SPR', 'not_measured', 81.6, '', 'not_comparable', 81.6, 'nM; paper Suppl. Table 7 (SPR)', 'no experimental assay run in this task'])

print(open(f'{R4}/benchmark_comparison.csv').read().count('\n') - 1, 'comparison rows written')
