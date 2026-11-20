#!/usr/bin/env python3
"""task009 corrected-epitope AntiBMPNN adapter (v3 contract) for one backbone sample."""
import json, sys
from pathlib import Path
TOOL = Path("/home/boltzmann10/agent_sci_boltpro_errors_tools/antibmpnn")
sys.path.insert(0, str(TOOL))
import antibmpnn_service as svc
from anarcii import Anarcii

INPUT = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_009_trem2_scfv_design/run_004_epitope_abgen_local/inputs/correction_v2/repaired_for_antibmpnn/trem2_ref_scFv_T009_v2_all_CDR_platform_sample001_seed2027_repaired.pdb"
OUT = Path("/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_004_epitope_abgen_local/raw/antibmpnn_corr_sample001")
assert not OUT.exists(), f"refusing to overwrite /home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/results/task_009_trem2_scfv_design/run_004_epitope_abgen_local/raw/antibmpnn_corr_sample001"

DESIGNED = ("H", "L")
ANTIGEN = "A"
numberer = Anarcii(seq_type="antibody", mode="accuracy", batch_size=8, cpu=True, ncpu=4)
def key_chain(key): return chr(int(key.split("::")[1]))

three2one = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}
seqs = {}
seen = set()
for ln in open(INPUT):
    if ln.startswith("ATOM") and ln[12:16].strip() == "CA":
        k = (ln[21], int(ln[22:26]))
        if k in seen: continue
        seen.add(k)
        aa = three2one.get(ln[17:20].strip(), None)
        if aa is None or aa == "X":
            continue  # UNK design residues carry no sequence; chain lengths from real AAs only
        seqs.setdefault(ln[21], []).append(aa)
seqs = {c: "".join(v) for c, v in seqs.items()}
pdb_name = Path(INPUT).stem
hl_map = {f"{pdb_name}::{ord(c):03d}": s for c, s in seqs.items() if c in DESIGNED}
other = [c for c in seqs if c not in DESIGNED and c != ANTIGEN]
assert not other, f"unexpected chains: {other}"
print("pre-check chains (real-AA lengths):", {c: len(s) for c, s in seqs.items()})

raw_hl = numberer.number(hl_map, scfv=True)
if not isinstance(raw_hl, dict):
    raise RuntimeError(f"unexpected ANARCII bulk return {type(raw_hl)}")
for k, r in raw_hl.items():
    print(f"  {k}: chain_type={r.get('chain_type')} score={r.get('score')} numbering_len={len(r.get('numbering') or [])}")
n_h = sum(1 for r in raw_hl.values() if isinstance(r, dict) and str(r.get("chain_type")) == "H")
n_l = sum(1 for r in raw_hl.values() if isinstance(r, dict) and str(r.get("chain_type")) in ("K", "L"))
assert n_h == 1 and n_l <= 1, f"domain assignment failed: {n_h}H/{n_l}L"

def backend(sequence_map):
    out = {}
    for key in sequence_map:
        ch = key_chain(key)
        if ch in DESIGNED:
            r = raw_hl.get(key)
            if r is None:
                raise RuntimeError(f"no ANARCII record for designed chain key {key}")
            out[key] = r
        elif ch == ANTIGEN:
            out[key] = {"chain_type": "F", "numbering": None, "score": 0.0,
                        "note": "TREM2 antigen context chain; fixed (all positions); Ig-like V-set ectodomain is not an antibody domain"}
        else:
            raise RuntimeError(f"unhandled chain {ch} in {key}")
    return out

req = svc.JobRequest(
    job_name="task009_corr_epitope_antibmpnn_sample1_seed2027",
    experiment_id="task009_corrected_epitope_local",
    user_id="local_adapter",
    input_path=INPUT,
    chains_to_design=DESIGNED,
    residue_positions_to_design={"H": tuple(range(28,36)) + tuple(range(53,61)) + tuple(range(99,113)),
                                  "L": tuple(range(27,33)) + (50,51,52) + tuple(range(89,98))},
    generation_count=40,
)
result = svc.run_antibmpnn_job(req, TOOL, OUT, domain_backend=backend)
print("JOB RESULT:", result)
