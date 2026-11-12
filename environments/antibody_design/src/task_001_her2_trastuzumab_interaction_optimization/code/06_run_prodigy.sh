#!/usr/bin/env bash
# Task 001 — ProDIGy binding metric (open-source, contact-based).
# Fixed-pose evaluation: Fab (chains A=VL, B=VH) vs HER2 (chain C) on the
# 1N8Z backbone with designed CDR side chains (see 04_reconstruct_fixed_pose.py).
#
# Usage:
#   ./06_run_prodigy.sh <structure.pdb>
#
# Outputs: intermolecular contact count, binding affinity (kcal/mol),
# dissociation constant (M) at 25 C.
set -euo pipefail
PRODIGY=/home/boltzmann10/anaconda3/bin/prodigy
STRUCT="$1"
"$PRODIGY" "$STRUCT" --selection "A,B" C
#
# Commands actually run for this task (reference + 5 candidates):
#   prodigy 1N8Z_deposited_complex.pdb --selection "A,B" C            # REF_1N8Z
#   prodigy reconstructed/AB_08_reconstructed.pdb --selection "A,B" C
#   prodigy reconstructed/AB_20_reconstructed.pdb --selection "A,B" C
#   prodigy reconstructed/AB_04_reconstructed.pdb --selection "A,B" C
#   prodigy reconstructed/AB_05_reconstructed.pdb --selection "A,B" C
#   prodigy reconstructed/AB_13_reconstructed.pdb --selection "A,B" C
