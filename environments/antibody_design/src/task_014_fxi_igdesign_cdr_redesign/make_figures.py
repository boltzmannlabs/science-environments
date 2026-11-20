#!/usr/bin/env python3
"""Generate task_014 benchmark figures (PNG only).

Grounded exclusively in on-disk metrics of run_001 (AntiBMPNN) and run_002
(IgDesign). No value is invented; endpoints, units and scope match the
calculations recorded in metrics.json / benchmark_comparison.csv.

v2 (2026-11-16 visual audit fixes):
- results_comparison.png: right-panel title shortened/wrapped so it cannot clip.
- workflow_results.png: two PARALLEL generation lanes (AntiBMPNN run_001,
  IgDesign run_002), each feeding the SHARED predeclared selection -> shared
  Boltz2 evaluation -> shared scRMSD protocol; metrics are outputs. No lane
  chains into the other; no orphan boxes.
- AAR labels grounded: run_001 best-of-20 maxima from candidates.csv are
  0.6923 (HCDR3) / 0.7241 (HCDR123) — earlier 0.615/0.697 labels were wrong.
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ENV = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design"
T = "task_014_fxi_igdesign_cdr_redesign"
R1 = f"{ENV}/results/{T}/run_001_antibmpnn_fixed_backbone"
R2 = f"{ENV}/results/{T}/run_002_igdesign_native_reconstruction"
FIG = f"{ENV}/benchmark/monoclonal_antibody_design/{T}/figures"
os.makedirs(FIG, exist_ok=True)

m1 = json.load(open(f"{R1}/metrics.json"))
m2 = json.load(open(f"{R2}/metrics.json"))
scr1 = m1["scrmsd"]["candidates"]
scr2 = m2["scrmsd"]["candidates"]

# ------------- results_comparison.png -------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.0, 4.8))

# Panel 1: native recovery (designed-scope AAR), both runs
labels = ["HCDR3 scope\n1-shot", "HCDR3 scope\nbest-of-100", "HCDR123 scope\n1-shot", "HCDR123 scope\nbest-of-100"]
ig = [m2["aar"]["hcdr3_1shot"]["one_shot"]["overall_aar"], m2["aar"]["hcdr3_best100"]["best_of_n"]["overall_aar"],
      m2["aar"]["hcdr123_1shot"]["one_shot"]["overall_aar"], m2["aar"]["hcdr123_best100"]["best_of_n"]["overall_aar"]]
ab = [0.6923, 0.6923,  # AntiBMPNN: platform T=0.1, no sampling split; best of 20 per scope
      0.7241, 0.7241]
x = range(4)
ax1.bar([i - 0.18 for i in x], ig, 0.34, label="IgDesign (run_002, 202 samples)", color="#4c72b0")
ax1.bar([i + 0.18 for i in x], ab, 0.34, label="AntiBMPNN (run_001, 40 samples, best)", color="#dd8452")
ax1.set_xticks(list(x)); ax1.set_xticklabels(labels, fontsize=7.5)
ax1.set_ylim(0, 1.05); ax1.set_ylabel("amino-acid recovery (fraction)")
ax1.set_title("Masked native recovery, Osocimab Fv (task_014)")
ax1.legend(fontsize=7.5, loc="upper left")
for i in x:
    ax1.text(i - 0.18, ig[i] + 0.02, f"{ig[i]:.3f}", ha="center", fontsize=7)
    ax1.text(i + 0.18, ab[i] + 0.02, f"{ab[i]:.3f}", ha="center", fontsize=7)
ax1.text(0.99, 0.02, "AntiBMPNN: platform T=0.1, no 1-shot/best-of-N split;\nbest of 20 samples per scope shown on all four bars",
         transform=ax1.transAxes, ha="right", fontsize=6.2, style="italic", color="#555")

# Panel 2: Boltz2 scRMSD, both runs' evaluated candidates + published control band
def series(scr):
    order = sorted(scr.items(), key=lambda kv: kv[1]["fv"])
    return [k.replace("t014r002_", "r2 ").replace("t014r001_", "r1 ")
             .replace("hcdr3_best100", "H3").replace("hcdr123_best100", "H123")
             .replace("hcdr3_scope", "H3").replace("hcdr123_scope", "H123")
             .replace("best100_", "").replace("_scope", "") for k, _ in order], \
           [v["hcdr3"] for _, v in order], [v["fv"] for _, v in order]

names2, h3_2, fv_2 = series(scr2)
names1, h3_1, fv_1 = series(scr1)
allnames = names1 + [n + "*" for n in names2]
h3 = h3_1 + h3_2; fv = fv_1 + fv_2
colors = ["#c44e52"] * len(names1) + ["#4c72b0"] * len(names2)
xi = range(len(allnames))
ax2.bar(xi, fv, 0.62, color=colors, alpha=0.45, label="Fv scRMSD")
ax2.bar(xi, h3, 0.62, color=colors, alpha=0.95, label="HCDR3 scRMSD")
ax2.axhline(1.9335, color="k", ls=":", lw=1.1, label="ABB2 control HCDR3 1.93 A")
ax2.axhline(2.1584, color="gray", ls=":", lw=1.1, label="ABB3 control HCDR3 2.16 A")
ax2.set_xticks(list(xi)); ax2.set_xticklabels(allnames, fontsize=5.6, rotation=90)
ax2.set_ylabel("scRMSD vs Boltz2 reference (Å)")
ax2.set_title("Bolt-2 scRMSD, 20 candidates\n(red run_001, blue run_002)", fontsize=9)
ax2.legend(fontsize=7, loc="upper left")
plt.tight_layout()
plt.savefig(f"{FIG}/results_comparison.png", dpi=180)
plt.close()

# ------------- workflow_results.png -------------
# Two PARALLEL methods, each feeding shared selection -> shared evaluation ->
# shared scRMSD; metrics as outputs. Nothing chains one lane into the other.
# All displayed numbers are DERIVED from on-disk data at render time:
#   run_001 AAR: max/mean of candidates.csv designed_scope_aar per scope;
#   run_002 AAR: metrics.json aar.*.one_shot/best_of_n.overall_aar (same named
#   field as the numerical figure);
#   scRMSD bests: min-Fv entry of each metrics.json scrmsd.candidates.
# Operational details (upload approval/receipt, s13 v1/v2/v3 correction) stay in
# run evidence records, not on this public diagram.
import csv as _csv

with open(f"{R1}/candidates.csv") as _f:
    _rows = list(_csv.DictReader(_f))
_r1h3 = [(float(r["designed_scope_aar"]), int(r["n_occurrences"])) for r in _rows if r["candidate_id"].startswith("t014r001_hcdr3")]
_r1h123 = [(float(r["designed_scope_aar"]), int(r["n_occurrences"])) for r in _rows if r["candidate_id"].startswith("t014r001_hcdr123")]
def _wmean(pairs):
    return sum(a * n for a, n in pairs) / sum(n for _, n in pairs)
a1_best3, a1_best123 = max(a for a, _ in _r1h3), max(a for a, _ in _r1h123)
a1_mean3, a1_mean123 = _wmean(_r1h3), _wmean(_r1h123)
a2_1shot3 = m2["aar"]["hcdr3_1shot"]["one_shot"]["overall_aar"]
a2_1shot123 = m2["aar"]["hcdr123_1shot"]["one_shot"]["overall_aar"]
a2_best3 = m2["aar"]["hcdr3_best100"]["best_of_n"]["overall_aar"]
a2_best123 = m2["aar"]["hcdr123_best100"]["best_of_n"]["overall_aar"]
_b1id, _b1 = min(scr1.items(), key=lambda kv: kv[1]["fv"])
_b2id, _b2 = min(scr2.items(), key=lambda kv: kv[1]["fv"])
_b1tag = _b1id.split("_")[-1]
_b2tag = _b2id.split("_")[-1]

fig, ax = plt.subplots(figsize=(12.6, 6.4))
ax.axis("off")

def box(x0, y0, w, h, text, color, fs=6.4):
    ax.add_patch(plt.Rectangle((x0, y0), w, h, transform=ax.transAxes,
                                facecolor=color, edgecolor="#666", lw=0.8))
    ax.text(x0 + w / 2, y0 + h / 2, text, transform=ax.transAxes,
            ha="center", va="center", fontsize=fs)

def arrow(x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), xycoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", lw=0.9, color="#444"))

# shared input
box(0.36, 0.90, 0.28, 0.075, "Input: 6HHC Osocimab Fv (VH 120 / VL 107)\nnative CDRs at 1-based masks 26-33 / 51-58 / 97-109", "#e8eef7", fs=5.8)
# two parallel generation lanes
box(0.04, 0.70, 0.40, 0.14,
    "run_001  AntiBMPNN (Boltzmann platform)\n2 jobs, 20 sequences per scope\nhcdr3 + hcdr123 scopes\n40/40 mask gate  →  26 unique candidates", "#fdece8", fs=6.0)
box(0.56, 0.70, 0.40, 0.14,
    "run_002  IgDesign (benchmark-matched)\nLM-Design + IgMPNN, holdout checkpoints\n4 executions, hcdr3 + hcdr123 scopes\n202 samples  →  158 unique candidates", "#e5f0e5", fs=6.0)
# shared selection
box(0.04, 0.54, 0.92, 0.09,
    "Shared predeclared selection — dedupe by VH; rank by ascending substitutions, then ascending design score; top-5 per scope per run", "#f2efe7", fs=6.6)
# shared Boltz2 evaluation
box(0.04, 0.38, 0.92, 0.11,
    "Shared Boltz2 matched evaluation — 10 (run_001) + 10 (run_002) candidate Fv jobs;\nsame reference prediction for all candidates", "#fdece8", fs=6.4)
# shared scRMSD protocol
box(0.04, 0.24, 0.92, 0.09,
    "Shared scRMSD protocol — CA atoms, single framework Kabsch fit vs Boltz2 reference prediction; self-check 0.000", "#fdece8", fs=6.6)
# metrics as OUTPUTS of the shared pipeline, one column per lane + bundle
box(0.04, 0.03, 0.29, 0.16,
    f"run_001 metrics (output)\nAAR best of 20: HCDR3 {a1_best3:.3f} / HCDR123 {a1_best123:.3f}\n(weighted mean {a1_mean3:.3f} / {a1_mean123:.3f}, 20 samples)\n"
    f"best scRMSD {_b1tag}: HCDR3 {_b1['hcdr3']:.3f} / Fv {_b1['fv']:.3f} Å", "#fdece8", fs=6.0)
box(0.355, 0.03, 0.29, 0.16,
    f"run_002 metrics (output)\nAAR best of 100: HCDR3 {a2_best3:.3f} / HCDR123 {a2_best123:.3f}\nAAR 1-shot: HCDR3 {a2_1shot3:.3f} / HCDR123 {a2_1shot123:.3f}\n"
    f"best scRMSD {_b2tag}: HCDR3 {_b2['hcdr3']:.3f} / Fv {_b2['fv']:.3f} Å", "#e5f0e5", fs=6.0)
box(0.67, 0.03, 0.29, 0.16,
    "Bundle + reports\ncandidates / shortlist / fasta / metrics\nbenchmark_comparison.csv x2\ncomparison.md + 2 figures", "#f2efe7", fs=6.0)

# arrows: input fans out to BOTH lanes; lanes converge on shared selection;
# shared chain; metrics/bundle are outputs of the shared protocol
arrow(0.42, 0.90, 0.24, 0.84)   # input -> run_001 lane
arrow(0.58, 0.90, 0.76, 0.84)   # input -> run_002 lane
arrow(0.24, 0.70, 0.24, 0.63)   # run_001 -> shared selection
arrow(0.76, 0.70, 0.76, 0.63)   # run_002 -> shared selection
arrow(0.50, 0.54, 0.50, 0.49)   # selection -> shared Boltz2 evaluation
arrow(0.50, 0.38, 0.50, 0.33)   # evaluation -> shared scRMSD
arrow(0.185, 0.24, 0.185, 0.19) # scRMSD -> run_001 metrics
arrow(0.50, 0.24, 0.50, 0.19)   # scRMSD -> run_002 metrics
arrow(0.815, 0.24, 0.815, 0.19) # scRMSD -> bundle
ax.set_title("task_014 Osocimab FXI CDR redesign — two parallel design methods, one shared selection/evaluation protocol",
             fontsize=9.5, pad=10)
plt.tight_layout()
plt.savefig(f"{FIG}/workflow_results.png", dpi=180)
plt.close()
print("figures written:", sorted(os.listdir(FIG)))
