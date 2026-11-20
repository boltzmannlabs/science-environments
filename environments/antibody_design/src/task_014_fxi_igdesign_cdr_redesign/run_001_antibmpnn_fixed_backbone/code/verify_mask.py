#!/usr/bin/env python3
"""S3 mask-verification gate for run_001 AntiBMPNN results.

Hard gate per workflow.md: for every returned sequence assert
- light_chain byte-identical to reference VL,
- heavy_chain length == 120,
- every difference vs reference VH inside the declared mask
  (1-based 26-33, 51-58, 97-109 -> 0-based 25-32, 50-57, 96-108).
Also records CDR sequences, substitution counts and AAR for each row.
"""
import csv
import json
import os

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
RES = os.path.join(A, "results/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone")

REF_VH = ("EVQLLESGGGLVQPGGSLRLSCAASGFTFSQYGMDWVRQAPGKGLEWVSGIGPSGGSTVYADSVK"
          "GRFTISRDNSKNTLYLQMNSLRAEDTAVYYCTRGGPYYYYGMDVWGQGTTVTVSS")
REF_VL = ("DIQMTQSPSSLSASVGDRVTITCQASQDISNYLNWYQQKPGKAPKLLIYDASNLETGVPSRFSG"
          "SGSGTDFTFTISSLQPEDIATYYCQQANSFPVTFGGGTKVEIK")
MASK = set(range(25, 33)) | set(range(50, 58)) | set(range(96, 109))
POS = {"hcdr1": list(range(25, 33)), "hcdr2": list(range(50, 58)),
       "hcdr3": list(range(96, 109))}
NATIVE = {"hcdr1": REF_VH[25:33], "hcdr2": REF_VH[50:58], "hcdr3": REF_VH[96:109]}


def verify(scope):
    rows = list(csv.DictReader(open(os.path.join(RES, "raw", scope, "antibmpnn_results.csv"))))
    metrics = {int(r["sample"]): r for r in csv.DictReader(
        open(os.path.join(RES, "raw", scope, "antibmpnn_generation_metrics.csv")))}
    out = []
    n_pass = 0
    for i, r in enumerate(rows):
        vh, vl = r["heavy_chain"], r["light_chain"]
        diffs = [j for j, (a, b) in enumerate(zip(vh, REF_VH)) if a != b] if len(vh) == 120 else list(range(120))
        in_mask = len(vh) == 120 and all(j in MASK for j in diffs)
        vl_ok = vl == REF_VL
        cdrs = {"hcdr1": vh[25:33], "hcdr2": vh[50:58], "hcdr3": vh[96:109]}
        is_native = vh == REF_VH
        design_scope = set(range(96, 109)) if scope == "hcdr3_scope" else MASK
        scope_diffs = [j for j in diffs]
        aar = 1 - (len(diffs) / len(design_scope)) if design_scope else None
        m = metrics.get(i + 1, {})
        rec = {"sample": i + 1, "candidate_id": f"t014r001_{scope}_s{i+1:02d}",
               "vl_identical": vl_ok, "vh_len_120": len(vh) == 120,
               "edits_outside_mask": len(diffs) - sum(1 for j in diffs if j in MASK) if len(vh) == 120 else 120,
               "gate_pass": in_mask and vl_ok,
               "is_exact_native": is_native, "vh": vh,
               "cdrs": cdrs,
               "n_substitutions": len(diffs),
               "designed_scope_aar": round(aar, 4) if aar is not None else None,
               "scrmpnn_score": float(m.get("score", "nan")),
               "global_score": float(m.get("global_score", "nan")),
               "seq_recovery": float(m.get("seq_recovery", "nan"))}
        out.append(rec)
        n_pass += rec["gate_pass"]
    return out, n_pass, len(rows)


def main():
    report = {"gate_definition": "VL byte-identical; VH len 120; all edits inside 0-based mask 25-32,50-57,96-108 (1-based 26-33,51-58,97-109)",
              "reference_vh_sha_like": None, "scopes": {}}
    all_rows = {}
    for scope in ("hcdr3_scope", "hcdr123_scope"):
        rows, npass, ntot = verify(scope)
        report["scopes"][scope] = {"n_samples": ntot, "gate_pass": npass,
                                   "gate_failed": ntot - npass,
                                   "n_exact_native": sum(r["is_exact_native"] for r in rows),
                                   "unique_vh": len({r["vh"] for r in rows})}
        all_rows[scope] = rows
    report["gate_all_pass"] = all(s["gate_failed"] == 0 for s in report["scopes"].values())
    json.dump({"report": report, "rows": all_rows},
              open(os.path.join(RES, "mask_gate_results.json"), "w"), indent=1)
    for scope, s in report["scopes"].items():
        print(scope, s)
    print("ALL PASS:", report["gate_all_pass"])


if __name__ == "__main__":
    main()
