#!/usr/bin/env python3
"""S3: Per-CDR AAR evaluation for task_014 run_002 IgDesign native reconstruction.

AAR per CDR = fraction of designed positions matching the native Osocimab CDR
(position-aligned; native reconstruction preserves loop lengths). Native editable
sequences are retained here as the evaluation reference (declared masked
reconstruction). Reports 1-shot (first sample) and best-of-100 (max overall
recovery) rules separately, per scope (HCDR3-only and HCDR123).

Writes results/<run>/aar_metrics.json and prints a summary.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.abspath(os.path.join(
    HERE, "..", "..", "..", "..", "results",
    "task_014_fxi_igdesign_cdr_redesign",
    "run_002_igdesign_native_reconstruction"))

NATIVE = {"hcdr1": "GFTFSQYG", "hcdr2": "IGPSGGST", "hcdr3": "TRGGPYYYYGMDV"}
POSITIONS = {  # 0-based within the 120-aa VH variable domain
    "hcdr1": list(range(25, 33)),
    "hcdr2": list(range(50, 58)),
    "hcdr3": list(range(96, 109)),
}
EXECUTIONS = {
    "hcdr3_1shot": ["hcdr3"],
    "hcdr3_best100": ["hcdr3"],
    "hcdr123_1shot": ["hcdr1", "hcdr2", "hcdr3"],
    "hcdr123_best100": ["hcdr1", "hcdr2", "hcdr3"],
}


def per_cdr_aar(row, regions):
    out = {}
    for r in regions:
        gen, nat = row[r], NATIVE[r]
        assert len(gen) == len(nat), (
            f"{r}: length changed {len(gen)} vs native {len(nat)} — loop-length "
            "constraint violated; sample rejected")
        out[r] = sum(a == b for a, b in zip(gen, nat)) / len(nat)
    return out


def overall(per_cdr):
    tot = sum(len(NATIVE[r]) for r in per_cdr)
    return sum(per_cdr[r] * len(NATIVE[r]) for r in per_cdr) / tot


def main():
    results = {"native_sequences": NATIVE,
               "evaluated_positions_zero_based": POSITIONS,
               "aar_definition": ("fraction of designed CDR positions matching the "
                                  "native Osocimab CDR (position-aligned masked "
                                  "native reconstruction)"),
               "runs": {}}
    for exec_id, regions in EXECUTIONS.items():
        path = os.path.join(RES, "raw", f"{exec_id}_samples.csv")
        with open(path) as f:
            rows = list(csv.DictReader(f))
        assert rows, f"empty samples file {path}"
        per_sample = [per_cdr_aar(row, regions) for row in rows]
        overalls = [overall(p) for p in per_sample]
        # sequence-length verification passed for every sample (asserted above)
        one_shot = per_sample[0]
        best_idx = max(range(len(overalls)), key=lambda i: overalls[i])
        best = per_sample[best_idx]
        n = len(rows)
        mean = {r: sum(p[r] for p in per_sample) / n for r in regions}
        results["runs"][exec_id] = {
            "scope": regions,
            "n_samples": n,
            "one_shot": {"per_cdr_aar": one_shot, "overall_aar": overall(one_shot),
                         "sample_index": 0,
                         "sequences": {r: rows[0][r] for r in regions}},
            "best_of_n": {"per_cdr_aar": best, "overall_aar": overalls[best_idx],
                          "sample_index": best_idx,
                          "sequences": {r: rows[best_idx][r] for r in regions}},
            "mean_aar": mean,
            "best_rule": f"max overall recovery over {n} samples",
        }
        print(f"=== {exec_id} (n={n}) ===")
        print(f"  1-shot  per-CDR AAR: { {k: round(v,3) for k,v in one_shot.items()} } overall={overall(one_shot):.3f}")
        print(f"  best-of-{n} per-CDR AAR: { {k: round(v,3) for k,v in best.items()} } overall={overalls[best_idx]:.3f} (sample #{best_idx})")
        print(f"  mean    per-CDR AAR: { {k: round(v,3) for k,v in mean.items()} }")
    out = os.path.join(RES, "aar_metrics.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"WROTE {out}")


if __name__ == "__main__":
    main()
