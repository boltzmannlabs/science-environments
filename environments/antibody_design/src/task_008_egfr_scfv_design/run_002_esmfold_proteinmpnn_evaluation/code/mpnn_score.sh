#!/usr/bin/env bash
# run_002_esmfold_proteinmpnn_evaluation: ProteinMPNN score_only (folder-mode fork) on ESMFold backbones
set -e
RUN=/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation
PY=/home/boltzmann10/anaconda3/envs/proteinmpnn/bin/python
cd /home/boltzmann10/her2_design/ProteinMPNN
for pdb in "$RUN"/inputs/esmfold_out/*.pdb; do
  name=$(basename "$pdb" .pdb)
  $PY protein_mpnn_run.py \
    --pdb_path "$pdb" \
    --out_folder "$RUN/inputs/mpnn_score/$name" \
    --score_only 1 \
    
    > "$RUN/logs/mpnn_$name.log" 2>&1
  echo "scored $name"
done
