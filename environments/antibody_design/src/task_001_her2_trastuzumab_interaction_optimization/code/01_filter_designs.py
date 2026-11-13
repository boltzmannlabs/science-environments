#!/usr/bin/env python
"""Task 001: sequence-level filtering of AntiBMPNN designs.
- Dedupe paired H/L
- Verify framework integrity (non-CDR positions unchanged from reference)
- Verify disulfide cysteines preserved
- Count CDR edits per candidate
- Rank by AntiBMPNN score (lower=better) with diversity tiebreak
"""
import csv, json
from collections import Counter

RES = "/home/boltzmann10/.sci/workspace/outputs/antibmpnn_results"
SEQS = "/home/boltzmann10/.sci/cache/scratch/task001_seqs.json"

# Reference variable-domain sequences (from 1N8Z clean chains)
# Designed VH is 120 (ends VTVSS), VL is 107 (ends VEIK); align reference to same length
ref = json.load(open(SEQS))
REF_VH = ref["VH_full"][:120]
REF_VL = ref["VL_full"][:107]
print(f"REF_VH len={len(REF_VH)}: {REF_VH}")
print(f"REF_VL len={len(REF_VL)}: {REF_VL}")

# CDR design ranges (0-based) matching the AntiBMPNN mask
# Chain B (VH): H1 26-32, H2 50-65, H3 97-109  (1-based) -> 0-based
VH_CDR = set(range(25,32)) | set(range(49,65)) | set(range(96,109))
# Chain A (VL): L1 24-34, L2 50-56, L3 89-97 (1-based) -> 0-based
VL_CDR = set(range(23,34)) | set(range(49,56)) | set(range(88,97))

# Disulfide Cys positions (0-based): VH C22(21), C96(95); VL C23(22), C88(87)
VH_CYS = {21, 95}
VL_CYS = {22, 87}

# Load designs
rows = list(csv.DictReader(open(f"{RES}/antibmpnn_results.csv")))
metrics = {int(r["sample"]): r for r in csv.DictReader(open(f"{RES}/antibmpnn_generation_metrics.csv"))}

seen = set()
candidates = []
for i, r in enumerate(rows):
    h, l = r["heavy_chain"], r["light_chain"]
    key = (h, l)
    if key in seen:
        continue
    seen.add(key)
    # Framework integrity: non-CDR positions must match reference
    fh = [j for j in range(len(h)) if j not in VH_CDR and h[j] != REF_VH[j]]
    fl = [j for j in range(len(l)) if j not in VL_CDR and l[j] != REF_VL[j]]
    # Disulfide check
    cys_h = [j for j in VH_CYS if h[j] != 'C']
    cys_l = [j for j in VL_CYS if l[j] != 'C']
    # CDR edit count
    eh = sum(1 for j in VH_CDR if h[j] != REF_VH[j])
    el = sum(1 for j in VL_CDR if l[j] != REF_VL[j])
    candidates.append({
        "id": f"AB_{i+1:02d}",
        "heavy": h, "light": l,
        "framework_violations_H": fh, "framework_violations_L": fl,
        "cys_violations_H": cys_h, "cys_violations_L": cys_l,
        "cdr_edits_H": eh, "cdr_edits_L": el,
        "total_cdr_edits": eh+el,
    })

# Filter: no framework violations, no disulfide violations
eligible = [c for c in candidates if not c["framework_violations_H"] and not c["framework_violations_L"]
            and not c["cys_violations_H"] and not c["cys_violations_L"]]
print(f"\nTotal unique: {len(candidates)}, Eligible (framework+disulfide OK): {len(eligible)}")

# Rank: eligible by total CDR edits (diversity) — keep a spread
# Also report AntiBMPNN scores
eligible_sorted = sorted(eligible, key=lambda c: c["total_cdr_edits"], reverse=True)
for c in eligible_sorted:
    print(f"{c['id']}: H_edits={c['cdr_edits_H']} L_edits={c['cdr_edits_L']} total={c['total_cdr_edits']}")

# Save all candidates + eligible
with open("/home/boltzmann10/.sci/cache/scratch/task001_candidates.json","w") as f:
    json.dump({"all": candidates, "eligible": eligible, "ref_vh": REF_VH, "ref_vl": REF_VL}, f, indent=1)
print("\nSaved to task001_candidates.json")
