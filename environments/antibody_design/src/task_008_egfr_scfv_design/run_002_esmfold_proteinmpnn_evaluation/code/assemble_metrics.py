#!/usr/bin/env python3
"""run_002_esmfold_proteinmpnn_evaluation: assemble benchmark-matched metrics — ESMFold mean pLDDT (from PDB B-factors),
ProteinMPNN score_only (original sequence on own ESMFold backbone), recovery, pI/MW."""
import csv, json, os

ENV = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{ENV}/src/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation'
RES = f'{ENV}/results/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation'
EFD = f'{RUN}/inputs/esmfold_out'
REF = json.load(open(f'{ENV}/src/task_008_egfr_scfv_design/run_001_antibmpnn_matched/inputs/shared/reference.json'))
SCFV_REF = REF['reference_scfv']

def mean_bfactor(pdb):
    vals = [float(l[60:66]) for l in open(pdb) if l.startswith('ATOM') and l[12:16].strip() == 'CA']
    return sum(vals) / len(vals), len(vals)

short = {r['candidate_id']: r for r in csv.DictReader(open(f'{ENV}/results/task_008_egfr_scfv_design/run_001_antibmpnn_matched/shortlist.csv'))}
seqs = {}
name = None
for l in open(f'{RUN}/inputs/eval_set.fasta'):
    if l.startswith('>'):
        name = l[1:].strip()
    else:
        seqs[name] = seqs.get(name, '') + l.strip()

rows = []
for name in sorted(seqs):
    plddt, nres = mean_bfactor(f'{EFD}/{name}.pdb')
    npz = f'{RUN}/inputs/mpnn_score/{name}/score_only/{name}_pdb.npz'
    import numpy as np
    z = np.load(npz, allow_pickle=True)
    mpnn = float(z['score'][0])
    seq = seqs[name]
    lab = 'reference' if name.startswith('reference') else name
    row = {'entity': lab, 'esmfold_mean_plddt': round(plddt, 2), 'n_res': nres,
           'mpnn_score_own_backbone': round(mpnn, 4),
           'full_recovery_vs_reference': round(sum(a == b for a, b in zip(seq, SCFV_REF)) / len(SCFV_REF), 4)}
    if lab in short:
        row['cdr_recovery'] = short[lab]['cdr_recovery']
        row['n_mutations'] = short[lab]['n_mutations']
        row['pI'] = short[lab]['pI']
        row['MW_da'] = short[lab]['MW_da']
        row['antibmpnn_score'] = short[lab]['antibmpnn_score']
    rows.append(row)

os.makedirs(RES, exist_ok=True)
cols = ['entity', 'esmfold_mean_plddt', 'mpnn_score_own_backbone', 'full_recovery_vs_reference',
        'cdr_recovery', 'n_mutations', 'pI', 'MW_da', 'antibmpnn_score', 'n_res']
with open(f'{RES}/metrics.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

# sequences + structures + raw
with open(f'{RES}/sequences.fasta', 'w') as f:
    for n, s in sorted(seqs.items()):
        f.write(f'>{n}\n{s}\n')
import shutil
os.makedirs(f'{RES}/structures', exist_ok=True)
for name in sorted(seqs):
    shutil.copy(f'{EFD}/{name}.pdb', f'{RES}/structures/{name}__esmfold.pdb')
os.makedirs(f'{RES}/raw', exist_ok=True)
for name in sorted(seqs):
    src = f'{RUN}/inputs/mpnn_score/{name}/score_only/{name}_pdb.npz'
    if os.path.exists(src):
        shutil.copy(src, f'{RES}/raw/{name}_mpnn_score.npz')

ref_row = [r for r in rows if r['entity'] == 'reference'][0]
with open(f'{RES}/benchmark_comparison.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['metric', 'reference', 'best_candidate'])
    best = max((r for r in rows if r['entity'] != 'reference'), key=lambda r: r['esmfold_mean_plddt'])
    w.writerow(['esmfold_mean_plddt', ref_row['esmfold_mean_plddt'], f"{best['esmfold_mean_plddt']} ({best['entity']})"])
    bestm = min((r for r in rows if r['entity'] != 'reference'), key=lambda r: r['mpnn_score_own_backbone'])
    w.writerow(['mpnn_score_own_backbone(lower_better)', ref_row['mpnn_score_own_backbone'],
                f"{bestm['mpnn_score_own_backbone']} ({bestm['entity']})"])
    w.writerow(['experimental_KD_reference', '6.6e-9 M (ProteinBase vast-bear-marble, Strong)', 'not measured'])

print('run_002_esmfold_proteinmpnn_evaluation metrics written')
for r in rows:
    print(f"  {r['entity']:26s} plddt {r['esmfold_mean_plddt']:7.2f} mpnn {r['mpnn_score_own_backbone']:.4f} "
          f"rec {r['full_recovery_vs_reference']:.3f}")
