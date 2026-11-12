#!/bin/bash
# Batch Boltz-2 prediction for task002 RF-Antibody candidates
cd /home/boltzmann10/.sci/cache/scratch/boltz2_task002
BOLTZ=/home/boltzmann10/anaconda3/bin/boltz
for id in rf0_d0 rf0_d2 rf0_d5 rf0_d8 rf1_d2 rf1_d3 rf1_d5 rf1_d6 rf1_d9; do
  if [ -d "pred_${id}/boltz_results_${id}/predictions" ]; then
    echo "SKIP ${id} (already done)"; continue
  fi
  echo "=== ${id} ==="
  timeout 900 $BOLTZ predict inputs/${id}.yaml --out_dir pred_${id} --recycling_steps 3 --use_msa_server > boltz_${id}.log 2>&1
  echo "exit=$?"
done
echo "ALL DONE"
