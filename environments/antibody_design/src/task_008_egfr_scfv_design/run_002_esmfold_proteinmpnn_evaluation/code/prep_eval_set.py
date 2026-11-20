#!/usr/bin/env python3
"""run_002_esmfold_proteinmpnn_evaluation: benchmark-matched open-source evaluation lane.
Reproduces the published benchmark protocol: ESMFold scFv structure prediction (pLDDT) +
ProteinMPNN score_only (original vs redesigned, matched backbone) + sequence recovery + pI/MW.
Reference: task_008 benchmark doc (EGFR scFv design benchmark, ESMFold/ProteinMPNN endpoints).
"""
import csv, json, os, subprocess, sys

ENV = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{ENV}/src/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation'
RES = f'{ENV}/results/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation'
os.makedirs(f'{RUN}/code', exist_ok=True)
os.makedirs(f'{RUN}/inputs', exist_ok=True)
os.makedirs(f'{RUN}/logs', exist_ok=True)
os.makedirs(RES, exist_ok=True)

REF = json.load(open(f'{ENV}/src/task_008_egfr_scfv_design/run_001_antibmpnn_matched/inputs/shared/reference.json'))
SCFV_REF = REF['reference_scfv']

# lane inputs: reference + run_001_antibmpnn_matched shortlist (already CDR-redesigned, screened)
short = list(csv.DictReader(open(f'{ENV}/results/task_008_egfr_scfv_design/run_001_antibmpnn_matched/shortlist.csv')))
with open(f'{RUN}/inputs/eval_set.fasta', 'w') as f:
    f.write('>reference_cetuximab_scFv\n' + SCFV_REF + '\n')
    for r in short:
        f.write(f">{r['candidate_id']}\n{r['scfv']}\n")
print(f'eval set: 1 reference + {len(short)} candidates')
