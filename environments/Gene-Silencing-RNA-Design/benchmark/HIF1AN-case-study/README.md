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
