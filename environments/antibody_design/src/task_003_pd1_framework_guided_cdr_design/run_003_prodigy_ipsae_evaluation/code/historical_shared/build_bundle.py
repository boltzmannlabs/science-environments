#!/usr/bin/env python3
"""Build the final task_003 deliverable bundle under results/.../pd1_results/."""
import csv, json, os, shutil

OUTW = '/home/boltzmann10/.sci/workspace/outputs'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'
RUN = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/runs/run_001'
RES = f'{BASE}/results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/pd1_results'
os.makedirs(f'{RES}/structures', exist_ok=True)
os.makedirs(f'{RES}/raw_outputs', exist_ok=True)

pool = json.load(open(f'{RUN}/candidates/agcdr_pool.json'))['pool']
sel = json.load(open(f'{RUN}/candidates/screening_selection.json'))['selected']
panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']
raw = json.load(open(f'{RUN}/metrics_raw.json'))
b2, props = raw['boltz2'], raw['properties']

# ---- 1. designed_sequences.fasta: all 115 eligible paired candidates ----
with open(f'{RES}/designed_sequences.fasta', 'w') as f:
    for k, c in enumerate(pool, start=1):
        cid = f'PD1T3-{k:03d}'
        c['candidate_id'] = cid
        f.write(f'>{cid}_VH|task_003|run_001|track=agcdr_diff+AntiBMPNN|framework=IGHV3-23/IGKV1-5\n{c["VH"]}\n')
        f.write(f'>{cid}_VL|task_003|run_001|track=agcdr_diff+AntiBMPNN|framework=IGHV3-23/IGKV1-5\n{c["VL"]}\n')
sel_ids = {}
for s in sel:
    m = [c for c in pool if c['VH'] == s['VH'] and c['VL'] == s['VL']]
    sel_ids[f"cand_rank{s['selection_rank']}"] = m[0]['candidate_id'] if m else 'UNMAPPED'
with open(f'{RES}/published_controls.fasta', 'w') as f:
    for name, d in panel.items():
        tag = name.replace('Anti-PD1-', '')
        f.write(f'>{tag}_VH|{name}|KD={d["KD_nM"]}nM|published_control\n{d["VH"]}\n')
        f.write(f'>{tag}_VL|{name}|KD={d["KD_nM"]}nM|published_control\n{d["VL"]}\n')

# ---- 2. shortlist.csv ----
# Model chain-A residue i (1-based) = UniProt 32+i for BOTH constructs
# (control 33-145 -> 113 res; candidates 33-134 -> 102 res).
PDL1_SURFACE = set(list(range(63, 85)) + list(range(124, 135)))
rows = []
for k in range(1, 6):
    tag = f'cand_rank{k}'
    cid = sel_ids[tag]
    m = b2[tag]
    pd1_vh = m.get('PD1:VH', {})
    pd1_vl = m.get('PD1:VL', {})
    iface = {32 + r for r in pd1_vh.get('interface_residues_pd1', [])} | \
            {32 + r for r in pd1_vl.get('interface_residues_pd1', [])}
    overlap = sorted(iface & PDL1_SURFACE)
    s = [x for x in sel if x['selection_rank'] == k][0]
    p = props.get(tag, {})
    rows.append({
        'rank': k, 'candidate_id': cid, 'pool_tag': s['tag'],
        'H3': s['CDRs']['H3'], 'L3': s['CDRs']['L3'],
        'gates': 'PASS',
        'iptm_PD1_VH': pd1_vh.get('iptm'), 'iplddt_PD1_VH': pd1_vh.get('complex_iplddt'),
        'iptm_PD1_VL': pd1_vl.get('iptm'), 'iplddt_PD1_VL': pd1_vl.get('complex_iplddt'),
        'contacts_lt5A_VH': pd1_vh.get('n_atom_contacts_lt5A'),
        'contacts_lt5A_VL': pd1_vl.get('n_atom_contacts_lt5A'),
        'PD1_iface_residues_uniprot_union_VH_VL': ';'.join(map(str, sorted(iface))) or 'none',
        'n_PD1_iface_residues_union': len(iface),
        'overlap_with_PDL1_surface_63_84_124_134': ';'.join(map(str, overlap)),
        'n_overlap_PDL1_surface': len(overlap),
        'thermal_stability_esm_C': p.get('Thermal_Stability_ESM', {}).get('Thermal_stab_esm'),
        'solubility_esm': p.get('Solubility_ESM', {}).get('solubility'),
        'min_cdr_hamming_to_other_selected': s.get('min_cdr_hamming_to_other_selected'),
    })
rows.sort(key=lambda r: (-(r['iptm_PD1_VH'] or 0), -(r['contacts_lt5A_VH'] or 0)))
with open(f'{RES}/shortlist.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

# ---- 3. metrics.json ----
h965_vh = b2['H965_control'].get('PD1:VH', {})
h965_vl = b2['H965_control'].get('[108, 113]', {})
metrics = {
  'run': 'run_001', 'date': '2026-11-14',
  'framework': {
     'template': 'Paper Table 1 (PMC12815924), Chothia layout',
     'heavy_germline': 'IGHV3-23*01 + IGHJ4', 'light_germline': 'IGKV1-5*01 + IGKJ1',
     'fr_blocks_byte_identical': True,
     'permitted_changes': 'six CDRs only; lengths H1=7 H2=6 H3 7-18 L1=11 L2=7 L3 9-11',
     'enforcement': 'AntiBMPNN residue mask verified position-by-position (100/100 scaffold track, 160/160 agcdr track) + FR byte-identity assert on every candidate',
  },
  'design_tracks': {
     'rfdiffusion_proteinmpnn': {'doc_id': '6af8769f239a6b9f38beba18', 'requested': 20, 'returned_pairs': 40,
        'passed_gates': 0,
        'reason': '39/40 carry a 7-residue H2 window and framework/junction edits vs the locked template; 1 failed length extraction. Zero promoted; raw kept.'},
     'AntiBMPNN_on_5GGS_fv_scaffold': {'doc_ids': ['6af87806d29658acc304df8c', '6af8799d445ae94313c3b012'],
        'samples': 100, 'passed_gates': 0,
        'reason': '100/100 place a novel Cys at CDR-L3 position 92 (deterministic); violates no-Cys gate.'},
     'agcdr_diff+AntiBMPNN': {'agcdr_doc_id': '6af879a3d29658acc304e059', 'antibmpnn_doc_id': '6af87c36445ae94313c3b280',
        'backbones': 20, 'sequences': 160, 'passed_gates': 115,
        'edit_mask_verified': '160/160', 'cdr_rmsd_vs_scaffold_A': 10.9},
  },
  'screening': {
     'policy': 'frozen before scoring: 5 CDR-diverse candidates (greedy max-min Hamming, min pairwise 32/60 CDR positions) + H965 control',
     'predictor': 'Boltz2 (boltz_structure_prediction); platform emits pairwise predictions PD1:VH and PD1:VL per submission',
     'h965_control': {'iptm_PD1_VH': h965_vh.get('iptm'), 'iplddt_PD1_VH': h965_vh.get('complex_iplddt'),
                      'iptm_PD1_VL': h965_vl.get('iptm')},
     'candidates': {r['candidate_id']: {k: r[k] for k in
        ('iptm_PD1_VH', 'iptm_PD1_VL', 'contacts_lt5A_VH', 'contacts_lt5A_VL',
         'n_PD1_iface_residues_union', 'n_overlap_PDL1_surface', 'thermal_stability_esm_C', 'solubility_esm')} for r in rows},
     'ranking_rule': 'ipTM(PD1:VH) desc, then contacts<5A(PD1:VH) desc — frozen in configs/workflow.md',
  },
  'provenance': {
     'paper': 'Nat Commun, DOI 10.1038/s41467-025-67361-9; PMC12815924; Suppl. Table 7 = published PD-1 panel',
     'target': 'UniProt Q15116 ECD; design construct 33-134 (candidates); control construct 33-145 (S93 form, from paper H965 VH/VL submission)',
     'structural_frame': 'PDB 5GGS (PD-1:pembrolizumab Fab; chains Z+A/B); epitope definition PDB 4ZQK (PD-1:PD-L1; residues 63-84, 124-134)',
     'construct_notes': '4ZQK/5GGS use S93 (UniProt C93) construct substitution; 4ZQK 85-92 disordered',
     'controls': 'H965 + 9 published PD-1 designs (comparison only; never design inputs)',
     'boltz2_doc_ids': {'H965_control': '6af87d71445ae94313c3b729', 'cand_rank1': '6af87d939030bff416447c9a',
        'cand_rank2': '6af87d99239a6b9f38bebe2d', 'cand_rank3': '6af87da39030bff416447cb6',
        'cand_rank4': '6af87da99de6b44b075d81f2', 'cand_rank5': '6af87db19850a93adf67d249'},
     'antibody_prediction_doc_ids': {'Thermal_Stability_ESM': '6af87dd4d29658acc304e596',
        'Solubility_ESM': '6af87dda445ae94313c3b7bb', 'CDR_Prediction': '6af87ded445ae94313c3b850'},
  },
  'missing_evidence': [
     'NEEDS_INPUT: paper individual H965 ipTM/PAE/DockQ never published; H965 Boltz2 row is our own prediction, not the paper value',
     'NEEDS_INPUT: 745-antibody labelled screening panel not released -> AUROC 0.76 / EF 7.41 not reproducible',
     'NEEDS_INPUT: SAbDab-22-DesignAb reconstruction dataset -> CDRH3 AAR 0.317 is aggregate, not candidate-level',
     'Antigen_Antibody_binding property absent from active connector contract (enum drift) — not run',
     'Antibody_Numbering platform job deadlocked (scheme enum drift); CDR boundaries frozen from paper Table-1 layout validated on all 10 published sequences',
     'No wet-lab measurements: nothing here demonstrates binding, affinity, or PD-1 blockade',
  ],
  'published_benchmarks_unreproduced': {
     'screening_AUROC': 0.76, 'top1pct_enrichment': 7.41,
     'design_discrimination_AUROC': 0.95, 'epitope_informed_CDRH3_AAR': 0.317,
     'note': 'Paper aggregate values; not assigned to any candidate or to H965 individually.'},
}
json.dump(metrics, open(f'{RES}/metrics.json', 'w'), indent=1)

# ---- 4. benchmark_comparison.csv: separately labelled record classes ----
with open(f'{RES}/benchmark_comparison.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['record_type', 'record_id', 'metric', 'value', 'scope', 'source'])
    for r in rows:
        w.writerow(['individual_new_candidate', r['candidate_id'], 'iptm_PD1_VH', r['iptm_PD1_VH'], 'our Boltz2 prediction, single candidate', 'run_001'])
        w.writerow(['individual_new_candidate', r['candidate_id'], 'iptm_PD1_VL', r['iptm_PD1_VL'], 'our Boltz2 prediction, single candidate', 'run_001'])
        w.writerow(['individual_new_candidate', r['candidate_id'], 'n_overlap_PDL1_surface', r['n_overlap_PDL1_surface'], 'model-derived contacts', 'run_001'])
        w.writerow(['individual_new_candidate', r['candidate_id'], 'H3_identity_to_H965', f"{sum(a == b for a, b in zip(r['H3'], h965['CDRs']['H3']))}/8", 'novelty distance', 'run_001'])
        w.writerow(['individual_new_candidate', r['candidate_id'], 'thermal_stability_esm_C', r['thermal_stability_esm_C'], 'ESM prediction', 'run_001'])
        w.writerow(['individual_new_candidate', r['candidate_id'], 'solubility_esm', r['solubility_esm'], 'ESM prediction', 'run_001'])
    w.writerow(['individual_control', 'H965', 'iptm_PD1_VH_our_prediction', h965_vh.get('iptm'), 'our Boltz2 prediction of published H965 (paper never published individual values)', 'run_001'])
    w.writerow(['individual_control', 'H965', 'iptm_PD1_VL_our_prediction', h965_vl.get('iptm'), 'our Boltz2 prediction of published H965', 'run_001'])
    w.writerow(['individual_control', 'H965', 'KD_nM_measured', 81.6, 'published SPR measurement (Suppl. Table 7)', 'PMC12815924'])
    w.writerow(['screening_panel', 'PD-1_745_panel', 'AUROC', 0.76, 'published aggregate; NOT reproduced (panel unavailable)', 'paper'])
    w.writerow(['screening_panel', 'PD-1_745_panel', 'top1pct_enrichment', 7.41, 'published aggregate; NOT reproduced', 'paper'])
    w.writerow(['screening_panel', 'design_campaign', 'discrimination_AUROC', 0.95, 'published aggregate; distinct from 745-panel AUROC; NOT reproduced', 'paper'])
    w.writerow(['reconstruction', 'SAbDab-22-DesignAb', 'CDRH3_AAR_epitope_informed', 0.317, 'published aggregate recovery; NOT a binding metric; NOT H965-specific', 'paper'])

# ---- 5. report.md ----
def fmt(x, nd=3):
    return '-' if x in (None, '') else (f'{x:.{nd}f}' if isinstance(x, float) else x)
top = rows[0]
lines = []
lines.append('# task_003 PD-1 Framework-Guided CDR Design — run_001 report')
lines.append('')
lines.append('## What was executed')
lines.append('- Framework: paper Table-1 template (humanized IGHV3-23*01/IGKV1-5*01 + IGHJ4/IGKJ1), verified byte-exact')
lines.append('  by decomposition of all 10 published PD-1 panel sequences (Suppl. Table 7, parsed programmatically).')
lines.append('- Target: PD-1 (UniProt Q15116) ECD; design construct 33-134; structural context from 5GGS')
lines.append('  (PD-1:pembrolizumab Fab, chains Z+A/B); ligand-binding epitope from 4ZQK (PD-1:PD-L1; 63-84, 124-134).')
lines.append('  Construct note: S93 substitution in both structures vs UniProt C93; 4ZQK 85-92 disordered.')
lines.append('- Design tracks (platform jobs, all completed):')
lines.append('  1. RF-Antibody (rfdiffusion_proteinmpnn), 40 pairs -> 0 eligible: 39/40 use a 7-residue H2 window')
lines.append('     and edit the locked framework at FR/CDR junctions; gates enforced, zero promoted, raw kept.')
lines.append('  2. AntiBMPNN on the Fv scaffold (2 rounds, 100 sequences; mask verified 100/100) -> 0 eligible:')
lines.append('     100/100 place a novel Cys at CDR-L3 position 92 (gate G3, deterministic artifact at T=0.1).')
lines.append('  3. agcdr_diff backbone sampling (20 backbones; CDR RMSD ~10.9 A) + AntiBMPNN (160 sequences;')
lines.append('     mask verified 160/160) -> 115 unique gate-passing candidates -> designed_sequences.fasta.')
lines.append('- Screening (selection frozen before any score existed): 5 CDR-diverse candidates (min pairwise')
lines.append('  Hamming 32/60 CDR positions) + H965 control; Boltz2 pairwise predictions (PD1:VH, PD1:VL);')
lines.append('  Antibody_Prediction properties (Thermal_Stability_ESM, Solubility_ESM, CDR_Prediction).')
lines.append('')
lines.append('## Headline results (computational predictions — NOT measurements)')
lines.append('| rank after scoring | candidate | ipTM PD1:VH | ipTM PD1:VL | contacts<5A VH/VL | PD-L1-surface overlap | Tm_pred (C) | sol |')
lines.append('| --- | --- | --- | --- | --- | --- | --- | --- |')
lines.append(f"| control | H965 (published; our Boltz2) | {fmt(h965_vh.get('iptm'))} | {fmt(h965_vl.get('iptm'))} | 65/62 | - | - | - |")
for r in rows:
    lines.append(f"| {r['rank']} | {r['candidate_id']} | {fmt(r['iptm_PD1_VH'])} | {fmt(r['iptm_PD1_VL'])} | "
                 f"{r['contacts_lt5A_VH']}/{r['contacts_lt5A_VL']} | {r['n_overlap_PDL1_surface']} res | "
                 f"{fmt(float(r['thermal_stability_esm_C']), 1) if r['thermal_stability_esm_C'] else '-'} | {r['solubility_esm']} |")
best = rows[0]
lines.append('')
lines.append(f"Top candidate {best['candidate_id']} (selection rank {best['rank']}): ipTM PD1:VH {fmt(best['iptm_PD1_VH'])} "
             f"vs H965 control {fmt(h965_vh.get('iptm'))} under identical predictor and preparation; "
             f"{best['n_overlap_PDL1_surface']} contacted PD-1 residues lie on the PD-L1-binding surface "
             '(competition-consistent epitope). This is a screening-confidence comparison only — it is NOT '
             'evidence of affinity and no functional blockade is demonstrated.')
lines.append('')
lines.append('## H965 / published-panel comparison')
lines.append('- H965 and the 9 other published PD-1 designs were comparison controls only; none entered design.')
lines.append('- Measured: H965 KD = 81.6 nM (SPR, paper Suppl. Table 7). Everything we produced is computational.')
lines.append('- The paper never published individual H965 ipTM/PAE/DockQ; our H965 row is OUR Boltz2 prediction')
lines.append('  under identical preparation (NEEDS_INPUT for the paper value, if it exists).')
lines.append('- Aggregate paper metrics (screening AUROC 0.76; top-1% enrichment 7.41; design discrimination AUROC 0.95;')
lines.append('  epitope-informed CDRH3 AAR 0.317) are reported as published values only — they concern a 745-antibody')
lines.append('  screening panel, a campaign-level analysis, and a reconstruction benchmark. None are reproducible from')
lines.append('  this task\'s inputs, and none are assigned to H965 or to any new candidate (see benchmark_comparison.csv).')
lines.append('')
lines.append('## Tooling deviations (recorded, not silently absorbed)')
lines.append('- Antibody_Numbering deadlocked (connector enum capitalized vs backend lowercase); CDR boundaries')
lines.append('  frozen from paper Table-1 layout, validated on all 10 published sequences.')
lines.append('- Antigen_Antibody_binding property rejected by active connector enum (contract drift) — not run.')
lines.append('- Boltz2 artifact downloads: connector 400 on outputs.zip; retrieved via status re-poll + direct')
lines.append('  signed-URL fetch inside the 300 s window (all 6 jobs + 3 property CSVs retrieved).')
lines.append('- Boltz2 emits pairwise (PD1:VH / PD1:VL) predictions per 3-chain submission, not a ternary complex;')
lines.append('  metrics reported per pair, never summed into a single "complex score".')
lines.append('')
lines.append('## Deliverables')
lines.append('- designed_sequences.fasta — 115 unique paired candidates (FR byte-identical, all gates passed)')
lines.append('- published_controls.fasta — 10 published panel sequences (controls only)')
lines.append('- shortlist.csv — ranked screening results with all criteria')
lines.append('- metrics.json — framework identity, permitted changes, all scores, provenance, missing evidence')
lines.append('- benchmark_comparison.csv — individual / screening-panel / reconstruction records, separately labelled')
lines.append('- structures/ — Boltz2 models (PD1:VH, PD1:VL per candidate + H965 control)')
lines.append('- raw_outputs/ — platform result tables, property CSVs, Boltz2 archives')
open(f'{RES}/report.md', 'w').write('\n'.join(lines) + '\n')

# ---- 6. structures + raw outputs ----
for tag in ['H965_control', 'cand_rank1', 'cand_rank2', 'cand_rank3', 'cand_rank4', 'cand_rank5']:
    for pair, m in b2[tag].items():
        if 'pdb' not in m:
            continue
        shutil.copy(m['pdb'], f"{RES}/structures/{tag}_{pair.replace(':', '_').replace('[','').replace(']','').replace(', ','_').replace(' ','')}.pdb")
for src, dst in [
    (f'{OUTW}/rf_antibody/ab_des_output_0_mpnn.csv', 'rf_antibody_mpnn_set0.csv'),
    (f'{OUTW}/rf_antibody/ab_des_output_1_mpnn.csv', 'rf_antibody_mpnn_set1.csv'),
    (f'{OUTW}/antibmpnn/antibmpnn_results.csv', 'antibmpnn_fv_round1.csv'),
    (f'{OUTW}/antibmpnn2/antibmpnn_results.csv', 'antibmpnn_fv_round2.csv'),
    (f'{OUTW}/antibmpnn_agcdr/antibmpnn_results.csv', 'antibmpnn_agcdr.csv'),
    (f'{OUTW}/agcdr/reports/metrics.json', 'agcdr_metrics.json'),
    (f'{OUTW}/output-1.csv', 'properties_thermal_stability.csv'),
    (f'{OUTW}/output-2.csv', 'properties_solubility.csv'),
    (f'{OUTW}/output-3.csv', 'properties_cdr_prediction.csv'),
    (f'{OUTW}/boltz2_h965/outputs.zip', 'boltz2_H965_control.zip'),
    (f'{OUTW}/boltz2_cand1/outputs.zip', 'boltz2_cand_rank1.zip'),
    (f'{OUTW}/boltz2_cand2/outputs.zip', 'boltz2_cand_rank2.zip'),
    (f'{OUTW}/boltz2_cand3/outputs.zip', 'boltz2_cand_rank3.zip'),
    (f'{OUTW}/boltz2_cand4/outputs.zip', 'boltz2_cand_rank4.zip'),
    (f'{OUTW}/boltz2_cand5/outputs.zip', 'boltz2_cand_rank5.zip'),
]:
    shutil.copy(src, f'{RES}/raw_outputs/{dst}')

print('Bundle written to', RES)
print('top-level:', sorted(os.listdir(RES)))
print('structures:', len(os.listdir(f'{RES}/structures')), 'raw_outputs:', len(os.listdir(f'{RES}/raw_outputs')))
print('selected ids:', sel_ids)
print('top:', rows[0]['candidate_id'], rows[0]['iptm_PD1_VH'])
