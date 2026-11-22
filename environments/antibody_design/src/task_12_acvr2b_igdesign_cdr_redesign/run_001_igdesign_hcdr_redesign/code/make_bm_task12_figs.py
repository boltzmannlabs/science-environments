import csv, os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BM = "/home/boltzmann4/srivani/Agent_Sci_Ab/8,9,10_Ab/BM/task_12_acvr2b_igdesign_cdr_redesign"
BK = "/home/boltzmann4/.sci/profiles/ab_task_10/workspace/results/task_12_acvr2b_igdesign_cdr_redesign/run_001_igdesign_hcdr_redesign_full_backup"

rows = [r for r in csv.reader(open(BK + "/metrics.csv")) if r]
val = {}
for r in rows[1:]:
    if r[1].startswith("scRMSD_"):
        val.setdefault(r[0], {})[r[1].replace("scRMSD_", "")] = float(r[2])
KEEP = ["T12-C008","T12-C007","T12-C001","T12-C011","T12-C017"]
nat = val["REFERENCE"]
pub = {"ABB2":[0.3593,0.3204,0.2988,0.3271,0.4350],
       "ABB3":[0.3690,0.6996,0.8772,0.6819,0.7242],
       "ABB3-LM":[0.4611,0.6991,0.6228,0.6026,0.9211],
       "ESMFold":[0.4362,0.7643,0.5768,0.6075,1.1243]}
REG = ["HCDR1","HCDR2","HCDR3","HCDR123","Fv_whole"]

# ---------- results_comparison.png with explicit legend ----------
fig, axes = plt.subplots(1, 3, figsize=(20, 8))
labels = ["Native\n(ours)"] + KEEP
data = [nat] + [val[k] for k in KEEP]

for ax, region, title in [(axes[0], "HCDR123", "HCDR123 C-alpha scRMSD (A)"),
                          (axes[1], "Fv_whole", "Fv (VH+VL) C-alpha scRMSD (A)")]:
    x = np.arange(len(labels) + len(pub))
    vals = [d[region] for d in data] + [p[REG.index(region)] for p in pub.values()]
    cols = ["#666666"] + ["#2171b5"]*5 + ["#fdae6b"]*len(pub)
    bars = ax.bar(x, vals, color=cols, edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, v, f"{v:.3f}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(labels + list(pub.keys()), rotation=40, ha="right", fontsize=7)
    ax.set_title(title, fontsize=11)
    ax.set_ylabel("C-alpha scRMSD (A)")
    ax.axhline(nat[region], color="red", ls="--", lw=1, alpha=0.7)
    best = min(vals)
    ax.text(0.02, 0.97, f"best: {best:.3f} A", transform=ax.transAxes, va="top", fontsize=8,
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9))

ax = axes[2]
aar_x = ["HCDR3-only\nHCDR3", "HCDR123\nHCDR1", "HCDR123\nHCDR2", "HCDR123\nHCDR3"]
one = [0.875, 0.750, 0.750, 0.750]
best = [0.875, 1.000, 0.875, 1.000]
mean = [0.750, 0.897, 0.703, 0.757]
x = np.arange(4); w = 0.26
ax.bar(x-w, one, w, label="1-shot", color="#9ecae1")
ax.bar(x,   best, w, label="best-of-100", color="#2171b5")
ax.bar(x+w, mean, w, label="mean (100)", color="#6baed6")
for xi, a in zip(x, one): ax.text(xi-w, a+0.01, f"{a:.2f}", ha="center", fontsize=7)
for xi, a in zip(x, best): ax.text(xi, a+0.01, f"{a:.2f}", ha="center", fontsize=7)
for xi, a in zip(x, mean): ax.text(xi+w, a+0.01, f"{a:.2f}", ha="center", fontsize=7)
ax.set_xticks(x); ax.set_xticklabels(aar_x, fontsize=8)
ax.set_ylim(0, 1.15); ax.set_ylabel("AAR (per-position identity vs native)")
ax.set_title("Native-recovery AAR (executed)", fontsize=11)
ax.legend(fontsize=8)

# explicit shared legend
handles = [mpatches.Patch(color="#666666", label="Native reference (executed AF2-Multimer v3)"),
           mpatches.Patch(color="#2171b5", label="Designed candidates (T12-C0xx)"),
           mpatches.Patch(color="#fdae6b", label="Published paper rows (other predictors)")]
fig.legend(handles=handles, loc="upper center", ncol=3, fontsize=10, frameon=True,
           bbox_to_anchor=(0.5, 0.985))
fig.suptitle("Task 12 - ACVR2B / Bimagrumab IgDesign CDR redesign: executed scRMSD and AAR", fontsize=13, y=0.93)
fig.tight_layout(rect=[0,0,1,0.90])
fig.savefig(BM + "/figures/results_comparison.png", dpi=150)
plt.close(fig)

# ---------- workflow_results.png, no text overflow ----------
fig, ax = plt.subplots(figsize=(26, 5.6))
ax.axis("off")
steps = [
    ("Input preparation",
     ["5NGV Fv: VH 113 aa, VL 111 aa",
      "ACVR2B fragment 93 aa",
      "(Q13705 mature 25-117)",
      "CDR windows H1 24:32",
      "H2 49:57, H3 95:103"]),
    ("IgDesign generation",
     ["ACVR2B-holdout checkpoint",
      "+ ProteinMPNN holdout",
      "reference-backbone",
      "conditioning",
      "200 samples (100/scope), T=0.5"]),
    ("Deduplicate + select",
     ["133 unique (44 HCDR3-only,",
      "89 HCDR123)",
      "top 10 per scope by summed",
      "cross-entropy loss",
      "= 20 candidates"]),
    ("AF2-Multimer v3",
     ["Boltzmann Multimer_Structure",
      "_Prediction, rank-1 model",
      "native + 20 candidates",
      "identical protocol",
      ""]),
    ("scRMSD + AAR",
     ["whole-Fv Kabsch onto 5NGV",
      "HCDR1/2/3/123 + Fv C-alpha",
      "RMSD",
      "AAR per CDR position",
      ""]),
    ("task_12 shortlist",
     ["17/20 beat native HCDR123",
      "(0.4434 A)",
      "best C008: 0.3803 A",
      "(HCDR3-only)",
      "best C011: 0.3879 A (HCDR123)"]),
]
n = len(steps); bw = 3.9; bh = 3.4; gap = 0.55
for i, (title, body) in enumerate(steps):
    x0 = i*(bw+gap)
    ax.add_patch(plt.Rectangle((x0, 0.6), bw, bh,
                 facecolor="#e8f0f8" if i%2==0 else "#fdf0e0",
                 edgecolor="#333333", lw=1.5))
    ax.text(x0+bw/2, 0.6+bh-0.28, title, ha="center", va="top", fontsize=11.5, fontweight="bold")
    lines = [b for b in body if b]
    ax.text(x0+bw/2, 0.6+bh/2-0.15, "\n".join(lines), ha="center", va="center", fontsize=9)
    if i < n-1:
        ax.annotate("", xy=(x0+bw+gap-0.04, 0.6+bh/2), xytext=(x0+bw+0.04, 0.6+bh/2),
                    arrowprops=dict(arrowstyle="-|>", lw=2, color="#333333"))
ax.set_xlim(-0.3, n*(bw+gap)); ax.set_ylim(0.2, 5.0)
ax.set_title("Executed workflow: task_12_acvr2b_igdesign_cdr_redesign", fontsize=13, pad=10)
fig.savefig(BM + "/figures/workflow_results.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print("both figures regenerated")
