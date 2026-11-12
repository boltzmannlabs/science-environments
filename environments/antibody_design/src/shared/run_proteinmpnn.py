#!/usr/bin/env python
"""Shared ProteinMPNN design wrapper.

Designs a masked region of a structure, fixing every other position.
Shared by Tasks 001, 003 and 004 (single model installation, not copied
per task, per user instruction).

Usage:
    python run_proteinmpnn.py <input_pdb> <fixed_positions_jsonl> <out_dir> <n_samples>

The fixed_positions_jsonl maps {pdb_basename: {chain: [fixed residue numbers]}}.
pdb_basename = input PDB filename without .pdb. Positions NOT listed are masked.
"""
import os, shutil, subprocess, sys

# ProteinMPNN: single shared installation (the her2_design build handles
# --pdb_path + --fixed_positions_jsonl cleanly). Not copied per task.
PMNN = "/home/boltzmann10/her2_design/ProteinMPNN"

def main(input_pdb, fixed_jsonl, out_dir, n_samples):
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, os.path.join(PMNN, "protein_mpnn_run.py"),
           "--pdb_path", input_pdb,
           "--fixed_positions_jsonl", fixed_jsonl,
           "--out_folder", out_dir, "--num_seq_per_target", str(n_samples)]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=False)
    print("Done. Outputs in", out_dir)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
