"""Stage 2: verify AntiBMPNN edit mask, dedupe, build candidate table.

Checks per skill pitfall list:
- VH/VL lengths unchanged (120/107)
- every mutation inside the declared CDR mask (H 31-35,50-65,95-102; L 24-34,50-56,89-97)
- framework byte-identical to reference
- no new cysteines in CDRs (liability flag)
- dedupe by (VH,VL) pair and by CDR-set
Outputs: inputs/candidates.json with unique candidates ranked by design score.
"""
import json
import zipfile
from collections import Counter

INP = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs"

VH_REF = "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSS"
VL_REF = "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIK"

MASK = {
    "H": set(list(range(31, 36)) + list(range(50, 66)) + list(range(95, 103))),
    "L": set(list(range(24, 35)) + list(range(50, 57)) + list(range(89, 98))),
}

z = zipfile.ZipFile(f"{INP}/antibmpnn_results.zip")
rows = []
hdr = None
for ln in z.read("antibmpnn_results.csv").decode().splitlines():
    parts = ln.split(",")
    if hdr is None:
        hdr = parts
        continue
    if len(parts) >= 3:
        rows.append((parts[1], parts[2]))
metrics = {}
for ln in z.read("antibmpnn_generation_metrics.csv").decode().splitlines()[1:]:
    p = ln.split(",")
    if len(p) > 3:
        metrics[int(p[1])] = {"score": float(p[2]), "global_score": float(p[3]), "seq_recovery": float(p[4])}

print("rows:", len(rows), "metrics:", len(metrics))

n_mask_ok = 0
n_fw_ok = 0
n_len_ok = 0
cands = []
for i, (vh, vl) in enumerate(rows, start=1):
    ok = True
    notes = []
    if len(vh) != len(VH_REF) or len(vl) != len(VL_REF):
        ok = False; notes.append("length change")
    else:
        n_len_ok += 1
        muts_h = [(p + 1, a, b) for p, (a, b) in enumerate(zip(VH_REF, vh)) if a != b]
        muts_l = [(p + 1, a, b) for p, (a, b) in enumerate(zip(VL_REF, vl)) if a != b]
        outside = [m for m in muts_h if m[0] not in MASK["H"]] + [m for m in muts_l if m[0] not in MASK["L"]]
        if outside:
            ok = False; notes.append("mutations outside mask: %s" % outside)
        else:
            n_mask_ok += 1
        fw_h = "".join(vh[p - 1] for p in range(1, len(vh) + 1) if p not in MASK["H"])
        fw_l = "".join(vl[p - 1] for p in range(1, len(vl) + 1) if p not in MASK["L"])
        ref_h = "".join(VH_REF[p - 1] for p in range(1, len(VH_REF) + 1) if p not in MASK["H"])
        ref_l = "".join(VL_REF[p - 1] for p in range(1, len(VL_REF) + 1) if p not in MASK["L"])
        if fw_h == ref_h and fw_l == ref_l:
            n_fw_ok += 1
        else:
            ok = False; notes.append("framework changed")
        cdr_cys = [m for m in muts_h + muts_l if m[2] == "C"]
        if cdr_cys:
            notes.append("new Cys in CDR at %s" % [(m[0], m[1] + m[2]) for m in cdr_cys])
    cands.append({
        "sample": i, "VH": vh, "VL": vl,
        "mut_H": ["H%d%s%s" % m for m in muts_h] if len(vh) == len(VH_REF) else [],
        "mut_L": ["L%d%s%s" % m for m in muts_l] if len(vl) == len(VL_REF) else [],
        "mask_ok": ok, "notes": notes,
        **metrics.get(i, {}),
    })

print("length ok: %d/40, mask ok: %d/40, framework ok: %d/40" % (n_len_ok, n_mask_ok, n_fw_ok))
assert n_len_ok == n_mask_ok == n_fw_ok == 40, "edit mask violations"

# dedupe by (VH, VL)
seen = {}
uniq = []
for c in cands:
    k = (c["VH"], c["VL"])
    if k not in seen:
        seen[k] = c
        uniq.append(c)
print("unique candidates: %d/40" % len(uniq))

# liability scan on CDRs of unique candidates (ND/NQ deamidation, DG isomerization, unpaired Cys)
def liabilities(vh, vl):
    li = []
    for tag, seq, mask in (("H", vh, MASK["H"]), ("L", vl, MASK["L"])):
        cdr = "".join(seq[p - 1] for p in sorted(mask))
        for motif, name in (("NG", "NG_deamidation"), ("NS", "NS_deamidation"), ("NT", "NT_deamidation"),
                            ("DG", "DG_isomerization"), ("DS", "DS_isomerization"), ("DT", "DT_isomerization")):
            if motif in cdr:
                li.append("%s_CDR_%s" % (tag, name))
    return li

for c in uniq:
    c["liabilities"] = liabilities(c["VH"], c["VL"])
    c["n_mutations"] = len(c["mut_H"]) + len(c["mut_L"])

# rank by design score (lower = better recovery-fit) then fewer mutations
uniq.sort(key=lambda c: (c["score"], c["n_mutations"]))
for i, c in enumerate(uniq, start=1):
    c["candidate_id"] = "T001-C%03d" % i

with open(f"{INP}/candidates.json", "w") as f:
    json.dump({"reference": {"VH": VH_REF, "VL": VL_REF, "mask": {k: sorted(v) for k, v in MASK.items()}},
               "generated": 40, "unique": len(uniq),
               "candidates": uniq}, f, indent=2)
print("candidates.json written; top 5 by score:")
for c in uniq[:5]:
    print(c["candidate_id"], "score=%.4f" % c["score"], "muts=%d" % c["n_mutations"], c["mut_H"], c["mut_L"], c["liabilities"])
