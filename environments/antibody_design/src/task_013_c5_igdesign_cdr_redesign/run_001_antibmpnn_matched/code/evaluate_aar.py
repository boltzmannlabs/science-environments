#!/usr/bin/env python3
"""Compute per-CDR AAR for task_013 candidates (both runs) vs native CDRs.

AAR convention (IgDesign benchmark): length mismatch => 0; else identical-
position fraction. 1-shot = the single sample of the 1shot budget (run_002)
or first sample (run_001 has no separate 1-shot budget; reported separately).
best-of-N = max AAR over the N=100 pool.
"""
import csv, json, sys
from pathlib import Path

NATIVE = {"HCDR1": "GYIFSNYW", "HCDR2": "ILPGSGST", "HCDR3": "ARYFFGSSPNWYFDV"}
# 1-based positions within the 122-aa VH used by AntiBMPNN (== 0-based+1)
POS = {"HCDR1": (26, 33), "HCDR2": (51, 58), "HCDR3": (97, 111)}


def aar(pred, nat):
    if not pred or len(pred) != len(nat):
        return 0.0
    return sum(a == b for a, b in zip(pred, nat)) / len(nat)


def cdrs(vh):
    return {k: vh[a - 1:b] for k, (a, b) in POS.items()}


def eval_pool(name, vh_seqs):
    per = {k: [] for k in NATIVE}
    for vh in vh_seqs:
        c = cdrs(vh)
        for k in NATIVE:
            per[k].append(aar(c[k], NATIVE[k]))
    res = {"pool": name, "n": len(vh_seqs)}
    for k in NATIVE:
        vals = per[k]
        res[k] = {
            "mean_aar": round(sum(vals) / len(vals), 4),
            "max_aar": round(max(vals), 4),
            "n_full_recovery": sum(v == 1.0 for v in vals),
        }
    return res, per


def main():
    base = Path("/home/boltzmann10/new_agent_scienece_env/science-environments/"
                "environments/antibody_design/results/task_013_c5_igdesign_cdr_redesign")
    out = {}

    # run_001 AntiBMPNN
    for scope in ["hcdr3only", "hcdr123"]:
        rows = list(csv.DictReader(open(base / "run_001_antibmpnn_matched/raw/"
                                        f"antibmpnn_{scope}_results.csv")))
        vhs = [r["heavy_chain"] for r in rows]
        res, _ = eval_pool(f"run_001_antibmpnn_{scope}", vhs)
        out[f"run_001_{scope}"] = res

    # run_002 IgDesign (native in evaluator)
    for scope in ["hcdr3", "hcdr123"]:
        for budget in ["1shot", "100"]:
            rows = list(csv.DictReader(open(base / "run_002_igdesign_reconstruction/"
                                            "raw" / f"{scope}_{budget}.csv")))
            if scope == "hcdr3":
                vhs = None  # hcdr3-only CSV carries hcdr3 seq only
                vals = [aar(r["hcdr3"], NATIVE["HCDR3"]) for r in rows]
                out[f"run_002_{scope}_{budget}"] = {
                    "pool": f"run_002_igdesign_{scope}_{budget}", "n": len(rows),
                    "HCDR3": {"mean_aar": round(sum(vals)/len(vals), 4),
                              "max_aar": round(max(vals), 4),
                              "n_full_recovery": sum(v == 1.0 for v in vals)},
                    "HCDR1": None, "HCDR2": None,
                    "note": "HCDR3-only scope; HCDR1/2 kept native (AAR 1.0 by construction)"}
            else:
                per = {k: [] for k in NATIVE}
                for r in rows:
                    per["HCDR1"].append(aar(r["hcdr1"], NATIVE["HCDR1"]))
                    per["HCDR2"].append(aar(r["hcdr2"], NATIVE["HCDR2"]))
                    per["HCDR3"].append(aar(r["hcdr3"], NATIVE["HCDR3"]))
                res = {"pool": f"run_002_igdesign_{scope}_{budget}", "n": len(rows)}
                for k in NATIVE:
                    vals = per[k]
                    res[k] = {"mean_aar": round(sum(vals)/len(vals), 4),
                              "max_aar": round(max(vals), 4),
                              "n_full_recovery": sum(v == 1.0 for v in vals)}
                out[f"run_002_{scope}_{budget}"] = res

    # Benchmark reference (released CSV) for comparison, same convention
    csvb = base.parent.parent / "src/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/inputs/Eculizumab-C5.csv"
    rows = list(csv.DictReader(open(csvb)))
    for scope_label, designed in [("hcdr3", "HCDR3"), ("hcdr123", "HCDR123")]:
        inv = [r for r in rows if r["Method"] == "Inverse Folding"
               and r["HCDRs Designed"] == designed]
        per = {k: [] for k in NATIVE}
        for r in inv:
            for k in NATIVE:
                per[k].append(aar(r[k], NATIVE[k]))
        res = {"pool": f"benchmark_inverse_folding_{designed}", "n": len(inv)}
        for k in NATIVE:
            vals = per[k]
            res[k] = {"mean_aar": round(sum(vals)/len(vals), 4),
                      "max_aar": round(max(vals), 4)}
        out[f"benchmark_{scope_label}"] = res

    dest = base / "aar_evaluation.json"
    dest.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
