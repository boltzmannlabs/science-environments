#!/usr/bin/env python
"""Bounded local AntiBMPNN adapter for task_009 run_003 (authorized fallback).

Runs the UNMODIFIED platform service (antibmpnn_service.py) in one process.
domain_backend: real ANARCII classification for every chain; chains whose
ANARCII result is NOT a confident antibody domain are reported as chain_type
'F' (the service's own non-antibody role) INSTEAD of raising — except for the
declared designed chains H/L, where the service's confidence gate is preserved
verbatim (a low-confidence H or L still fails the run). TREM2 chain A (antigen
context, low-confidence K per ANARCII — an Ig-like V-set domain, not an
antibody) is thereby treated as fixed context, identical in effect to the
task_002 run_004 platform behavior where the service accepted antigen
contexts that classify F/no-numbering.
"""
import json, sys
from pathlib import Path

TOOL = Path("/home/boltzmann10/agent_sci_boltpro_errors_tools/antibmpnn")
sys.path.insert(0, str(TOOL))
import antibmpnn_service as svc
from anarcii import Anarcii

DESIGNED = {"H", "L"}  # antibody chains: full gate applies

numberer = Anarcii(seq_type="antibody", mode="accuracy", batch_size=8, cpu=True, ncpu=4)

def backend(sequence_map):
    out = {}
    for key, seq in sequence_map.items():
        chain = chr(int(key.split("::")[1]))
        res = numberer.number([seq], scfv=False)
        r = res[0] if isinstance(res, list) else res
        if not isinstance(r, dict):
            r = {"chain_type": str(r)}
        r = dict(r)
        ct = str(r.get("chain_type") or "F")
        if ct in ("H", "K", "L") and not svc._confident_domain(r):
            if chain in DESIGNED:
                # preserve the service's real gate for antibody chains
                raise svc.InputError(
                    f"Low-confidence antibody domain classification for {key}: "
                    f"type={ct}, score={r.get('score')}"
                )
            # non-designed context chain: treat as non-antibody context, do not raise
            r = {"chain_type": "F", "numbering": None, "score": r.get("score"),
                 "note": "low-confidence Ig-like context chain (antigen); fixed context"}
        out[key] = r
    return out

req = svc.JobRequest(
    job_name="task009_trem2_antibmpnn_agcdr_sample7_run4_local",
    experiment_id="6afb4568c3dde753301b1bda_LOCAL_FALLBACK",
    user_id="local_adapter",
    input_path="/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_009_trem2_scfv_design/run_003_agcdr_backbone/inputs/agcdr_sample7_design_input.pdb",
    chains_to_design=("H", "L"),
    residue_positions_to_design={"H": tuple(range(28,36)) + tuple(range(53,61)) + tuple(range(99,113)),
                                  "L": tuple(range(27,33)) + (50,51,52) + tuple(range(89,98))},
    generation_count=40,
)
out_dir = Path("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw/antibmpnn_local_run4")
import shutil
if out_dir.exists():
    shutil.rmtree(out_dir)
result = svc.run_antibmpnn_job(req, TOOL, out_dir, domain_backend=backend)
print("JOB RESULT:", result)
