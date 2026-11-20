#!/usr/bin/env python
"""Bounded local AntiBMPNN adapter v3 for task_009 run_003 (authorized fallback).

Differences from failed v2 (kept as evidence in scratch):
  - Uses the SAME keyed bulk ANARCII protocol as the unmodified service:
    numberer.number(<keyed sequence_map>, scfv=True) for the declared H/L
    chains only; result records keep the service's expected shape
    (chain_type/numbering/score) and pass through the service's own
    confidence + boundary gates untouched.
  - ONLY the explicitly known antigen chain A is given the F (fixed-context)
    role. Any other unexpected chain raises instead of being silently marked F.
  - Pre-inference verification step prints and asserts the H/L domain
    assignments before any model call.
  - Unique output dir (antibmpnn_local_run5); service itself enforces
    empty-dir; no rmtree anywhere.
"""
import json, sys
from pathlib import Path

TOOL = Path("/home/boltzmann10/agent_sci_boltpro_errors_tools/antibmpnn")
sys.path.insert(0, str(TOOL))
import antibmpnn_service as svc
from anarcii import Anarcii

INPUT = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_009_trem2_scfv_design/run_003_agcdr_backbone/inputs/agcdr_sample7_design_input.pdb"
OUT = Path("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_003_agcdr_backbone/raw/antibmpnn_local_run5")
assert not OUT.exists(), f"refusing to overwrite {OUT}"

DESIGNED = ("H", "L")
ANTIGEN = "A"  # TREM2 ectodomain context chain, explicitly known

numberer = Anarcii(seq_type="antibody", mode="accuracy", batch_size=8, cpu=True, ncpu=4)

def key_chain(key: str) -> str:
    return chr(int(key.split("::")[1]))

def classify_hl(hl_map):
    """Bulk keyed ANARCII for H/L only — same call shape as the service."""
    raw = numberer.number(hl_map, scfv=True)
    # normalize to dict (service iterates .items())
    if not isinstance(raw, dict):
        raise RuntimeError(f"unexpected ANARCII bulk return type {type(raw)}")
    return raw

# ---- pre-inference verification (no model call yet) ----
three2one = {'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
seqs = {}
for ln in open(INPUT):
    if ln.startswith("ATOM") and ln[12:16].strip() == "CA":
        seqs.setdefault(ln[21], "")
        seqs[ln[21]] += three2one.get(ln[17:20].strip(), "X")
pdb_name = Path(INPUT).stem
hl_map = {f"{pdb_name}::{ord(c):03d}": s for c, s in seqs.items() if c in DESIGNED}
ag_keys = [f"{pdb_name}::{ord(c):03d}" for c in seqs if c == ANTIGEN]
other = [c for c in seqs if c not in DESIGNED and c != ANTIGEN]
assert not other, f"unexpected chains present: {other}"
print("pre-check chains:", {c: len(s) for c, s in seqs.items()})

raw_hl = classify_hl(hl_map)
print("pre-check ANARCII raw result for H/L:")
for k, r in raw_hl.items():
    if isinstance(r, dict):
        print(f"  {k}: chain_type={r.get('chain_type')} score={r.get('score')} numbering_len={len(r.get('numbering') or [])}")
    else:
        print(f"  {k}: NON-DICT {type(r)} {str(r)[:100]}")

n_h = sum(1 for r in raw_hl.values() if isinstance(r, dict) and str(r.get("chain_type")) == "H")
n_l = sum(1 for r in raw_hl.values() if isinstance(r, dict) and str(r.get("chain_type")) in ("K", "L"))
assert n_h == 1, f"expected exactly 1 heavy domain, got {n_h}"
assert n_l <= 1, f"expected at most 1 light domain, got {n_l}"
print(f"pre-check PASS: {n_h} heavy + {n_l} light; antigen chain(s) {ag_keys} -> fixed context F")

def backend(sequence_map):
    # real classification for H/L keys; F ONLY for the explicit antigen chain
    out = {}
    for key in sequence_map:
        ch = key_chain(key)
        if ch in DESIGNED:
            r = raw_hl.get(key)
            if r is None:
                raise RuntimeError(f"no ANARCII record for designed chain key {key}")
            # service gates apply verbatim inside classify_antibody_domains
            out[key] = r
        elif ch == ANTIGEN:
            out[key] = {"chain_type": "F", "numbering": None, "score": 0.0,
                        "note": "TREM2 antigen context chain; fixed (all positions); Ig-like V-set ectodomain is not an antibody domain"}
        else:
            raise RuntimeError(f"unhandled chain {ch} in {key}; refusing to mark unknown chains as F")
    return out

req = svc.JobRequest(
    job_name="task009_trem2_antibmpnn_agcdr_sample7_run5_local",
    experiment_id="6afb4568c3dde753301b1bda_LOCAL_FALLBACK",
    user_id="local_adapter",
    input_path=INPUT,
    chains_to_design=DESIGNED,
    residue_positions_to_design={"H": tuple(range(28,36)) + tuple(range(53,61)) + tuple(range(99,113)),
                                  "L": tuple(range(27,33)) + (50,51,52) + tuple(range(89,98))},
    generation_count=40,
)
result = svc.run_antibmpnn_job(req, TOOL, OUT, domain_backend=backend)
print("JOB RESULT:", result)
