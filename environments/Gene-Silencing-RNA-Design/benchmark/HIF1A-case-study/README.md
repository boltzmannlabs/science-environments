# HIF1AN — end-to-end DESIGN case study vs public measured data

Target: HIF1AN NM_001530.4 (public RefSeq, 3,946 nt; envelope extension disclosed). Generator:
3,928 windows. Benchmark: 100 measured siRNAs (Sciabola/Simone; clean). Frozen engine, no tuning.

| Model | AUC | Pearson | Spearman |
|---|---|---|---|
| OligoFormer (generator, native) | **0.7600** | 0.6350 | 0.3629 |
| RN.Ai-Predict | 0.7803 | 0.6729 | 0.4903 |

Rank recovery: measured-top-10 at **median 97.5th percentile** of our ranking (min 68.8 /
max 99.9); all 100 measured average the 82nd percentile (random 50th). Full join in
`benchmark_join.json`.

Key finding: the frozen absolute off-target cap (<=10 hits) **saturates for this target** —
every window and every measured-top-10 siRNA carries 18–37 hits; honest DESIGN outcome under
v1.0 gates is "no deliverable panel" (backlog #3: per-target calibration). Explorer-mode
post-hoc (`posthoc_benchmark.json`): constraint re-anchored cohort-relatively (q25=28);
3/18 clean candidates intersect the measured tiling at **0.92/0.92/0.87** (blind selection).

**Correction (2026-11-05):** the gate-saturation finding below is reframed — all counted hits were same-gene isoform matches (cross-gene = 0); a mislabeled input gene symbol silently disengaged locus-scoping. Under the adapter's semantics the gate was not saturated and the protocol would have delivered panels. See the source workspace `12_head_to_head/TOOL_EXECUTION_VERIFICATION.md`.

## Benchmark metrics

| Model | AUC | 95% CI | Pearson | Spearman |
|---|---|---|---|---|
| OligoFormer (generator) | **0.76** | None | 0.635 | 0.3629 |
| RN.Ai-Predict | **0.7803** | None | 0.6729 | 0.4903 |

Rank recovery (n=100 joined): measured-top-10 at median **97.53054989816701th** pct (min 68.78818737270875, max 99.949083503055); all-100 mean percentile 82.0 (random 50.0); label+ mean 87.5 vs label− 59.9.

Corrected-battery outcome (v1.2.1 semantics, `13_liveness/runs_rescoped/`): locus-scoped off-target hits 0–1; gate-clean 40/60 — the v1.0 protocol delivers panels (supersedes the archived scoping-artifact runs).
