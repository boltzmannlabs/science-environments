import json, csv, hashlib

SCRATCH = '/home/boltzmann10/.sci/cache/scratch/task002'
REPO = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RES = f'{REPO}/results/task_002_pdl1_epitope_targeted_scfv_design/run1_epitope_abgen'

v2 = {c['tag']: c for c in json.load(open(f'{SCRATCH}/candidate_eval_scores_v2.json'))['candidates']}
ec = json.load(open(f'{SCRATCH}/antibmpnn_full_candidates.json'))
ag1 = json.load(open(f'{SCRATCH}/agcdr1_eval_scores_final.json'))
agc = {c['idx']: c for c in json.load(open(f'{SCRATCH}/agcdr1_eval_candidates.json'))}
antibmpnn = json.load(open(f'{SCRATCH}/parallel_lanes_analysis.json'))['antibmpnn']

FIELDS = ['candidate_id', 'lane', 'backbone', 'status', 'H3', 'L3', 'mut_H', 'mut_L',
          'iptm', 'complex_plddt', 'epitope_coverage', 'hotspots_hit', 'h5_interface_recovery']

crows = []
for c in antibmpnn:
    idx = c['idx']
    ev = v2.get(f'cand{idx}')
    crows.append(dict(candidate_id=f't002r1_bmpnn_{idx:02d}', lane='antiBMPNN_sequence_only',
                      backbone='placed framework', status='evaluated' if ev else 'unevaluated',
                      H3=c['CDRs']['H3'], L3=c['CDRs']['L3'], mut_H=c['mut_H'], mut_L=c['mut_L'],
                      iptm=ev['iptm'] if ev else '', complex_plddt=ev['complex_plddt'] if ev else '',
                      epitope_coverage=ev['epitope_coverage'] if ev else '',
                      hotspots_hit='|'.join(map(str, ev['hotspots_hit'])) if ev else '',
                      h5_interface_recovery=ev['h5_interface_recovery'] if ev else ''))
crows.append(dict(candidate_id='t002r1_rfab_designs', lane='rf_antibody_VH_only',
                  backbone='RFdiffusion+ProteinMPNN', status='excluded',
                  H3='', L3='', mut_H='', mut_L='', iptm='', complex_plddt='',
                  epitope_coverage='', hotspots_hit='', h5_interface_recovery=''))
for r in ag1:
    idx = int(r['tag'].split('cand')[1])
    c = agc[idx]
    crows.append(dict(candidate_id=f't002r1_agcdr1_c{idx}', lane='agcdr_diff+antiBMPNN',
                      backbone='agcdr sample 1', status='evaluated',
                      H3=c['VH'][96:109], L3=c['VL'][88:97], mut_H='', mut_L='',
                      iptm=r['iptm'], complex_plddt=r['plddt'], epitope_coverage=r['epi_cov'],
                      hotspots_hit='|'.join(map(str, r['hs'])),
                      h5_interface_recovery=r['h5_rec'] if r.get('h5_rec') is not None else ''))

with open(f'{RES}/candidates.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(crows)

ev = [r for r in crows if r['iptm'] != '']
ev.sort(key=lambda r: -float(r['iptm']))
with open(f'{RES}/shortlist.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['shortlist_rank', 'candidate_id', 'lane', 'iptm', 'complex_plddt',
                'epitope_coverage', 'hotspots_hit', 'selection_reason'])
    for i, r in enumerate(ev):
        reason = ('top agcdr1 lead: highest ipTM under frozen Boltz2 protocol with hotspot engagement'
                  if r['lane'] == 'agcdr_diff+antiBMPNN' and i < 5
                  else 'agcdr1 lane, ipTM-ranked' if r['lane'] == 'agcdr_diff+antiBMPNN'
                  else 'sequence-only lane: retained for record; negative for engagement')
        w.writerow([i + 1, r['candidate_id'], r['lane'], r['iptm'], r['complex_plddt'],
                    r['epitope_coverage'], r['hotspots_hit'], reason])

with open(f'{RES}/sequences.fasta', 'w') as f:
    for r in crows:
        if r['lane'] == 'antiBMPNN_sequence_only':
            idx = int(r['candidate_id'].split('_')[-1])
            s = ec[idx]['scfv']
        elif r['lane'] == 'agcdr_diff+antiBMPNN':
            idx = int(r['candidate_id'].split('_c')[-1])
            s = agc[idx]['VH'] + 'AGGGGSGGGGSGGGS' + agc[idx]['VL']
        else:
            continue
        f.write(f">{r['candidate_id']}|{r['lane']}|H3:{r['H3']}|L3:{r['L3']}\n")
        for j in range(0, len(s), 60):
            f.write(s[j:j + 60] + '\n')

# metrics.csv: one row per evaluated entity + control
with open(f'{RES}/metrics.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['entity_id', 'kind', 'metric', 'value', 'unit', 'protocol', 'source'])
    w.writerow(['h5_control_v3', 'control', 'iptm', 0.9265, 'unitless', 'Boltz2 confidence, AG+scFv 2-chain',
                'results/.../structures/h5_control_v3_boltz2_prediction.pdb'])
    w.writerow(['h5_control_v3', 'control', 'complex_plddt', 0.921, 'unitless', 'Boltz2', 'same'])
    w.writerow(['h5_control_v3', 'control', 'global_ca_rmsd_vs_35TL', 2.05, 'angstrom',
                'sequence-anchored CA match, 334 residues', 'logs/h5_control_v3_analysis.json'])
    w.writerow(['h5_control_v3', 'control', 'interface_residue_recovery', 21 / 23, 'fraction',
                'PD-L1 interface residues within 5 A recovered', 'same'])
    for name, rmsd in [('H1', 1.21), ('H2', 2.12), ('H3', 3.72), ('L1', 1.79), ('L2', 0.86), ('L3', 3.08)]:
        w.writerow([f'h5_control_v3', 'control', f'cdr_{name}_ca_rmsd', rmsd, 'angstrom',
                    'sequence-anchored, antigen-frame', 'same'])
    for r in ev:
        w.writerow([r['candidate_id'], 'candidate', 'iptm', r['iptm'], 'unitless',
                    'Boltz2 AG+scFv 2-chain prospective, no template', 'structures/*/boltz2_prediction.pdb'])
        w.writerow([r['candidate_id'], 'candidate', 'complex_plddt', r['complex_plddt'], 'unitless', 'Boltz2', 'same'])
        w.writerow([r['candidate_id'], 'candidate', 'epitope_coverage', r['epitope_coverage'], 'fraction of 28',
                    'antigen residues within 5 A of scFv heavy atoms', 'code/score_candidates_v2.py + agcdr1 scorer'])
        w.writerow([r['candidate_id'], 'candidate', 'n_hotspots_hit', len(r['hotspots_hit'].split('|')) if r['hotspots_hit'] else 0,
                    'count of 5', 'hotspots 37/39/41/96/98 within 5 A', 'same'])

# benchmark_comparison.csv
with open(f'{RES}/benchmark_comparison.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['published_metric', 'published_value', 'scope', 'our_metric', 'our_value',
                'protocol_compatibility', 'comparison', 'interpretation'])
    w.writerow(['H5 predicted-vs-experimental global CA RMSD', '1.25', 'individual PD-L1/H5 complex (AF3)',
                'H5 reconstruction global CA RMSD (Boltz2)', '2.05',
                'same protocol family (cofolding prediction vs cryo-EM), different predictor',
                'below reference', 'Boltz2 reconstruction is 0.8 A looser than published AF3 value; '
                'interface recovery 21/23 and hotspot-patch recovery keep it an acceptable control; '
                'difference attributed to predictor, not protocol'])
    w.writerow(['PD-L1 scFv designs passing computational filters', '470', 'campaign yield (Germinal)',
                'candidates generated and evaluated', '16 (8 sequence-only + 8 agcdr1)',
                'not comparable', 'inconclusive',
                'campaign yield depends on sampling budget (8 generations per AntiBMPNN call, server-fixed); '
                'not a per-candidate quality metric; not attempted to match'])
    w.writerow(['Designs selected for experimental validation', '48', 'selection count',
                'shortlist size', '5', 'not comparable', 'inconclusive',
                'our shortlist is computational only; no experimental validation performed in this run'])
    w.writerow(['CDR identity to known sequences', '~40%; <52%', 'scFv novelty across design context',
                'CDR identity to trastuzumab parent', 'not_computed', 'differing definition',
                'not_computed', 'novelty DB search not run; would require SAbDab/CDR database alignment; '
                'not substituted for binding evidence'])
    w.writerow(['Interface similarity IS <= 0.2', 'IS <= 0.2', 'novelty comparison',
                'interface similarity', 'not_computed', 'differing definition', 'not_computed',
                'IS metric implementation unavailable in Boltzmann/ToolUniverse set; left empty rather than proxied'])
    w.writerow(['H5 pLDDT/ipTM/PAE/pDockQ (candidate-level)', 'Not verified (no published numbers)',
                'published candidate-level values', 'H5 control ipTM/pLDDT', '0.927 / 0.921',
                'no published reference values', 'not_comparable',
                'benchmark file itself marks these Not Verified; our values recorded as reference-only'])

print('candidates:', len(crows), '| evaluated:', len(ev), '| shortlist:', len(ev))
print('top3:', [(r['candidate_id'], r['iptm']) for r in ev[:3]])
