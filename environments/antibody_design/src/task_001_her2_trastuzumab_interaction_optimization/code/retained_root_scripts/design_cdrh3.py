#!/usr/bin/env python
"""Task 001: HER2 / trastuzumab — CDR-H3 design with ProteinMPNN.

Pipeline:
  1. prepare_inputs.py  -> split 1N8Z into antibody (A+B) and antigen (C)
  2. Define fixed positions: ALL VH (chain B) positions EXCEPT CDR-H3 (97-109)
  3. ProteinMPNN design 20 CDR-H3 candidates (shared model installation)
  4. Extract CDR-H3 from each designed full sequence

The benchmark metric (REF15, Rosetta REU) is NOT computable here (no Rosetta),
so this task stops at the design step and reports REF15 as unavailable.
"""
import json, os, sys, re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import metrics as m  # noqa (shared library, for chain/sequence helpers)

PREP = "/home/boltzmann10/shared_metric_tools/prepared"
OUT = "/home/boltzmann10/shared_metric_tools/results/task001_cdrh3_designed.json"

# Native trastuzumab VH CDR-H3 (chain B, residues 97-109)
NATIVE_CDRH3 = "SRWGGDGFYAMDY"
CDR_START, CDR_END = 97, 109  # 1-based, inclusive

def fixed_positions_jsonl(path):
    """All chain-B positions except CDR-H3 (97-109) are fixed."""
    fixed = [r for r in range(1, 221) if not (CDR_START <= r <= CDR_END)]
    data = {"1N8Z": {"B": fixed}}
    with open(path, "w") as f:
        for k, v in data.items():
            f.write(json.dumps({k: v}) + "\n")

def extract_cdrh3(full_seq, n_cdr=len(NATIVE_CDRH3)):
    """CDR-H3 sits at a fixed position in the VH; extract by position.
    The native VH has CDR-H3 at residues 97-109; in the linear sequence
    (chain B starts at residue 1) that is index 96..108 (0-based)."""
    return full_seq[96:96+n_cdr]

def main():
    # 1. fixed positions
    fj = f"{PREP}/task001_fixed_positions.jsonl"
    fixed_positions_jsonl(fj)
    # 2. ProteinMPNN (shared installation) — 20 designs
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
    import run_proteinmpnn as rpm
    outdir = "/home/boltzmann10/shared_metric_tools/results/task001_proteinmpnn"
    rpm.main(f"{PREP}/1N8Z.pdb", fj, outdir, 20)
    # 3. extract CDR-H3 from designed sequences
    fa = f"{outdir}/seqs/1N8Z.fa"
    designed = []
    lines = open(fa).read().splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith(">") and "sample=" in ln:
            sid = re.search(r"sample=(\d+)", ln).group(1)
            score = re.search(r"score=([0-9.]+)", ln).group(1)
            seq = lines[i+1].strip()
            designed.append({"sample": int(sid), "score": float(score), "cdr": extract_cdrh3(seq)})
    out = {"native": NATIVE_CDRH3, "designed": designed, "unique": len(set(d["cdr"] for d in designed))}
    open(OUT, "w").write(json.dumps(out, indent=1))
    print(f"Designed {len(designed)} CDR-H3 variants, {out['unique']} unique")

if __name__ == "__main__":
    main()
