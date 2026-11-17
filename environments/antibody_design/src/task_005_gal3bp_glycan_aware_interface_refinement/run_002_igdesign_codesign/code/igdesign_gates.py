#!/usr/bin/env python
"""Gates for run_002 IgDesign designs: dedupe, mask containment, framework identity, liabilities."""
import csv, json

VH = "QVQLVQSGAEVKKPGSSVKVSCRASGDSFSRKYGISWVRQAPGQGFEWMGTIMPIVGLTTSAQKFQGRVTITADKSTSTAHMELNSLTSEDTAIYYCARDEIIGARPHWFDSWGQGTLVTVS"
VL = "EIVMTQSPAIMSVSPGKRATLSCRASQSVSSNLAWYQRKPGQAPRLLIYGSSTRATGIPARFSGSGSGTEFTLTISSLQSEDFAVYYCLQYYNWPRTFGQGTKVEI"
MASK = set(range(24, 34)) | set(range(50, 59)) | set(range(96, 112))  # 0-based HCDR1/2/3
LIAB = ["NG", "NS", "NT", "DG", "DS", "DT"]

rows = list(csv.DictReader(open("/home/boltzmann10/.sci/cache/scratch/gal3bp_run/igdesign_run002_results.csv")))
print("columns:", list(rows[0].keys()))
out, seen, rejected = [], set(), []
for r in rows:
    h1, h2, h3 = r["hcdr1"], r["hcdr2"], r["hcdr3"]
    # reconstruct full VH: reference with CDR windows replaced
    cand = list(VH)
    for i, p in enumerate(range(24, 24 + len(h1))):
        cand[p] = h1[i]
    for i, p in enumerate(range(50, 50 + len(h2))):
        cand[p] = h2[i]
    for i, p in enumerate(range(96, 96 + len(h3))):
        cand[p] = h3[i]
    cand = "".join(cand)
    # gate 1: length
    if len(cand) != 122:
        rejected.append((r.get("sample_id", "?"), "VH length")); continue
    # gate 2: all edits inside mask
    edits = [i for i in range(122) if cand[i] != VH[i]]
    if any(i not in MASK for i in edits):
        rejected.append((r.get("sample_id", "?"), "edit outside mask")); continue
    # gate 3: no new Cys
    n_cys_new = sum(1 for i in edits if cand[i] == "C")
    if n_cys_new:
        rejected.append((r.get("sample_id", "?"), "new Cys")); continue
    # dedupe
    if cand in seen:
        continue
    seen.add(cand)
    # liabilities in CDRs: inherited vs new
    cdr_seq = cand[24:34] + cand[50:59] + cand[96:112]
    ref_cdr = VH[24:34] + VH[50:59] + VH[96:112]
    liab_new = [m for m in LIAB if m in cdr_seq and m not in ref_cdr]
    liab_inh = [m for m in LIAB if m in cdr_seq and m in ref_cdr]
    out.append({
        "candidate": None, "vh": cand, "vl": VL,
        "h1": h1, "h2": h2, "h3": h3,
        "n_edits": len(edits),
        "edits": [{"pos1": i + 1, "from": VH[i], "to": cand[i]} for i in edits],
        "loss": float(r.get("loss", r.get("independent_loss", "nan"))),
        "liab_new": liab_new, "liab_inherited": liab_inh,
    })
# rank by loss asc, assign IDs G3I-## (Gal3bp Igdesign)
out.sort(key=lambda x: x["loss"])
for i, c in enumerate(out, 1):
    c["candidate"] = f"G3I-{i:02d}"
json.dump({"n_samples": len(rows), "n_unique_pass": len(out), "n_rejected": len(rejected),
           "rejected_reasons": rejected, "candidates": out},
          open("/home/boltzmann10/.sci/cache/scratch/gal3bp_run/igdesign_run002_candidates.json", "w"), indent=1)
print(f"samples={len(rows)} unique_pass={len(out)} rejected={len(rejected)}")
for r in rejected[:5]: print("  rejected:", r)
print("top-5 by loss:")
for c in out[:5]:
    print(f"  {c['candidate']} loss={c['loss']:.4f} edits={c['n_edits']} liab_new={c['liab_new']} h3={c['h3']}")
