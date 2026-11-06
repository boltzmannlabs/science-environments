# Functional genomics — panel-construction benchmark

Protocol panels (seed-distinct top-6 from the top-150 slice, frozen rules) evaluated against
the sparse measured tilings post-hoc: HPSE 0/6 overlap, HK2 0/6, HIF1A 2/6 — and where the
panel intersects measurement, picks are **0.92 / 0.91 (both effective; cohort base 0.80)**.

Honest status: tiling sparsity (~100 sites per 3.7–5.6 kb transcript) limits panel-level
enrichment evaluation to overlap subsets; overlap-limited result retained, not extrapolated.
Suggests panel logic surfaces top-tier reagents where measurement exists.

## Published reference

| Metric | Published value | Source |
|---|---|---|
| Panel-enrichment reference | **none exists** — Run-1 is overlap-limited | — |

## Run configuration

| Run | Config | Date |
|---|---|---|
| Run-1 | seed-distinct top-6 from top-150 slice; frozen panel rules; 3 pools | 2026-11-05 |

## Benchmark metrics

| Gene Pool | Panel / Top-150 Overlap with Tiling | Measured Labels of Panel Picks | Cohort Base Positive Rate |
|:---|:---:|:---|:---:|
| HPSE | 0/6 | — (tiling sparse) | 0.72 |
| HK2 | 0/6 | — | 0.77 |
| HIF1A | 2/6 | **0.92, 0.91** (both effective) | 0.80 |
