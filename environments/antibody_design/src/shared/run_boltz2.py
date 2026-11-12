#!/usr/bin/env python
"""Shared Boltz2 structure-prediction wrapper.

Predicts a complex structure from a FASTA (one chain per sequence).
Shared by Task 002 and Task 004 (single local Boltz2 installation, not
copied per task, per user instruction).

Usage:
    python run_boltz2.py <fasta> <out_dir>

Uses the local Boltz2 installation. MSA is fetched via the server.
"""
import os, subprocess, sys

# Single shared Boltz2 installation.
BOLTZ = "/home/boltzmann10/boltz2"

def main(fasta, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, "-m", "boltz", "predict",
           "--fasta_path", fasta,
           "--output_dir", out_dir,
           "--model_location", BOLTZ,
           "--use_msa_server"]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=False)
    print("Done. Outputs in", out_dir)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
