#!/usr/bin/env python3
"""run_002_esmfold_proteinmpnn_evaluation: ProteinMPNN score_only on ESMFold backbones (matched preparation).
Scores original vs redesigned sequences on the SAME backbone per protein — the published
benchmark's original-vs-redesigned comparison. Also computes recovery + liabilities.
Usage: proteinmpnn_score.py"""
import json, os, subprocess, sys

ENV = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
RUN = f'{ENV}/src/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation'
EFD = f'{RUN}/inputs/esmfold_out'
MPNN_ENV = '/home/boltzmann10/anaconda3/envs/proteinmpnn/bin/python'

names = [n[:-4] for n in sorted(os.listdir(EFD)) if n.endswith('.pdb')]
REF = json.load(open(f'{ENV}/src/task_008_egfr_scfv_design/run_001_antibmpnn_matched/inputs/shared/reference.json'))
SCFV_REF = REF['reference_scfv']

# score_only with both sequences: native (original) + reference (for candidate backbones)
# ProteinMPNN score_only via parsing + proteinmpnn API
helper = f'{RUN}/code/_mpnn_score.py'
open(helper, 'w').write('''
import json, sys
sys.path.insert(0, "/home/boltzmann10/anaconda3/envs/proteinmpnn/lib/python3.9/site-packages/proteinmpnn")
''')
# simpler: use the env's proteinmpnn package directly
script = f'{RUN}/code/_mpnn_score_impl.py'
open(script, 'w').write('''
import argparse, json, os, sys, tempfile
sys.path.append("/home/boltzmann10/tools/proteinmpnn")
from proteinmpnn_utils import parse_PDB, StructureBuilder
''')
print('see run script; using direct python API below')
