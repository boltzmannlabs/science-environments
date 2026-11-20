#!/usr/bin/env python3
"""run_001_antibmpnn_matched stage 3b: submit Boltz2 structure+affinity prediction for reference + shortlisted
candidates (scFv + EGFR ECD as separate entities), matched conditions."""
import csv, json, os, subprocess, sys

ENV = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{ENV}/src/task_008_egfr_scfv_design/run_001_antibmpnn_matched'
RES = f'{ENV}/results/task_008_egfr_scfv_design/run_001_antibmpnn_matched'
REF = json.load(open(f'{RUN}/inputs/shared/reference.json'))
EGFR = REF['egfr_construct']['sequence']
LINKER = REF['linker']

jobs = [{'id': 'reference', 'scfv': REF['reference_scfv']}]
for r in csv.DictReader(open(f'{RES}/shortlist.csv')):
    jobs.append({'id': r['candidate_id'], 'scfv': r['scfv']})

os.makedirs(f'{RUN}/inputs/submitted_requests', exist_ok=True)
reg = []
for j in jobs:
    payload = {'job_name': 'Boltz2',
               'experiment_name': f"task008_r1_{j['id']}",
               'experiment_data': {'Protein_Sequences': [j['scfv'], EGFR],
                                   'DNA_Sequences': [], 'RNA_Sequences': [], 'SMILES': []}}
    pf = f"{RUN}/inputs/submitted_requests/boltz2_{j['id']}.json"
    json.dump(payload, open(pf, 'w'), indent=1)
    reg.append({'id': j['id'], 'payload_file': pf})
json.dump(reg, open(f'{RUN}/inputs/submitted_requests/boltz2_registry.json', 'w'), indent=1)
print(f'{len(jobs)} Boltz2 payloads written (reference + {len(jobs)-1} candidates)')
