#!/usr/bin/env python3
"""Benchmark analysis: local endpoints vs Xiang-2021 Day10(+dox) measured editing.

Cohort: GSE173708 GSM5277230 (Day10 SpCas9 +dox), our reprocessing: rate = 1 - filt/raw,
raw>=30, NGG only, dedup by spacer (mean). Replicate ceiling measured separately:
Day8-vs-Day10 Spearman = 0.39 (label-noise envelope for THIS reprocessing).

Metrics: Spearman rho + nDCG@20 (top-20 ground-truth guides) + bootstrap 95% CI (1000x).
Endpoints: CRISPRon (exposed: trained on this library), RS1 / RS3-Hsu2013 / CRISPRater
(RS3 possibly-exposed: 2022 model, pooled public HEK293T corpora — disclosed;
RS1 2014 / CRISPRater 2016 predate all cohorts = clean).
CRISPRon enumerates every NGG window per record (IDs get _p_N suffixes) — join on the
exact intended 30-mer string.
"""
import csv
import json
import math
import random

W = "/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/02_benchmarks/runs/xiang2021_run1"
random.seed(20261110)


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    da = math.sqrt(sum((x - ma) ** 2 for x in ra))
    db = math.sqrt(sum((y - mb) ** 2 for y in rb))
    return num / (da * db) if da and db else float("nan")


def ndcg20(pred, truth):
    order_pred = sorted(range(len(pred)), key=lambda i: -pred[i])
    order_truth = sorted(range(len(truth)), key=lambda i: -truth[i])
    top_truth = set(order_truth[:20])
    dcg = sum((1.0 if order_pred[i] in top_truth else 0.0) / math.log2(i + 2) for i in range(20))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(20))
    return dcg / idcg


def boot_ci(f, a, b, n=1000):
    vals = []
    for _ in range(n):
        idx = [random.randrange(len(a)) for _ in range(len(a))]
        vals.append(f([a[i] for i in idx], [b[i] for i in idx]))
    vals.sort()
    return vals[24], vals[975]


r = {x["spacer"]: x for x in csv.DictReader(open(f"{W}/r_endpoint_scores.csv"))}
labels = {x["spacer"]: x for x in csv.DictReader(open(f"{W}/benchmark_labels.csv"))}
crispron = {}
with open(f"{W}/crispron_out/crispron.csv") as f:
    for row in csv.DictReader(f):
        crispron[row["30mer"]] = float(row["CRISPRon"])

rows, missing_cp = [], 0
for s, x in r.items():
    m30 = labels[s]["m30"]
    if m30 not in crispron:
        missing_cp += 1
        continue
    rows.append(dict(spacer=s, y=float(x["day10_rate"]),
                     rs1=float(x["rs1"]), rs3=float(x["rs3"]),
                     crisprater=float(x["crisprater"]), crispron=crispron[m30]))
print(f"joined: {len(rows)} guides (CRISPRon missing for {missing_cp})")

y = [x["y"] for x in rows]
out = {"cohort_n": len(rows), "missing_crispron": missing_cp,
       "replicate_ceiling_day8_day10": 0.39}
for ep, col in (("crispron", "crispron"), ("rs3_hsu2013", "rs3"),
                ("crisprater", "crisprater"), ("ruleset1", "rs1")):
    v = [x[col] for x in rows]
    rho = spearman(v, y)
    lo, hi = boot_ci(spearman, v, y)
    nd = ndcg20(v, y)
    out[ep] = {"spearman": round(rho, 4), "ci95": [round(lo, 4), round(hi, 4)],
               "ndcg20": round(nd, 4)}
    print(f"{ep:>14}: Spearman {rho:.4f} [{lo:.4f}-{hi:.4f}]  nDCG@20 {nd:.4f}")

with open(f"{W}/benchmark_metrics.json", "w") as f:
    json.dump(out, f, indent=2)
print("written benchmark_metrics.json")
