#!/usr/bin/env python
"""Map AntiBMPNN scores to candidates and select a diverse shortlist."""
import csv, json

RES = "/home/boltzmann10/.sci/workspace/outputs/antibmpnn_results"
cands = json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_candidates.json"))
rows = list(csv.DictReader(open(f"{RES}/antibmpnn_results.csv")))
metrics = list(csv.DictReader(open(f"{RES}/antibmpnn_generation_metrics.csv")))

# Map by order (results.csv row i == candidate AB_{i+1}, since dedup kept order)
# Actually candidates were built in order of rows, so AB_{i+1} = row i
for i, c in enumerate(cands["all"]):
    m = metrics[i]
    c["score"] = float(m["score"])
    c["global_score"] = float(m["global_score"])
    c["seq_recovery"] = float(m["seq_recovery"])

# Rank by score (lower=better), keep diversity
ranked = sorted(cands["all"], key=lambda c: c["score"])
print("Ranked by AntiBMPNN score (lower=better):")
for c in ranked:
    print(f"{c['id']}: score={c['score']:.4f} global={c['global_score']:.4f} recov={c['seq_recovery']:.3f} edits={c['total_cdr_edits']}")

# Select shortlist: top by score, but ensure CDR-edit diversity
# Take the 5 lowest-score, then swap in a high-edit one if needed
shortlist_ids = ["AB_05","AB_13","AB_01","AB_02","AB_03"]  # will refine below
# Actually select: lowest 3 scores + 2 highest-edit (for diversity)
low3 = ranked[:3]
high_edit = sorted(cands["all"], key=lambda c: c["total_cdr_edits"], reverse=True)[:2]
shortlist = low3 + [h for h in high_edit if h not in low3]
print("\nSelected shortlist (3 lowest-score + 2 highest-edit):")
for c in shortlist:
    print(f"{c['id']}: score={c['score']:.4f} edits={c['total_cdr_edits']}")

# Save shortlist
with open("/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json","w") as f:
    json.dump({"shortlist": shortlist, "all_ranked": ranked}, f, indent=1)
print("Saved shortlist.")
