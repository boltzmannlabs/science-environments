# Gene regulation — MYC end-to-end case study (public measured data)

MYC NM_002467.6 (bHLH transcription factor — this application's exemplar class): DESIGN run
on the 3,703-window pool; 7/7 measured siRNAs (Sciabola/Simone, clean) joined post-hoc.

- OligoFormer: AUC degenerate (only 1 measured negative of 7) — **percentile-only reporting**:
  measured-top siRNAs at median **92.6th pct** (min 56.5 / max 99.5) of our ranking.
- RN.Ai: Pearson 0.5322 on the 7 rows; Spearman negative (n too small to interpret).
- Honest status: rank-recovery consistent with other targets; **cohort too small for
  discrimination metrics** — reported as such, not padded.

## Published reference

| Metric | Published value | Source |
|---|---|---|
| Per-gene (MYC) reference | **none exists** — Run-1 sets reference (percentile-only at n=7) | — |

## Run configuration

| Run | Config | Date |
|---|---|---|
| Run-1 | same engine; 3,703 windows; gene-regulation weights .35/.35/.10/.10/.10 | 2026-11-05 |

## Benchmark metrics

| Metric | Value |
|---|---|
| n joined / measured positives | 7 / 1 |
| AUC | degenerate at n=7 (1 negative) — not reported |
| Rank recovery (top-10) | median **92.6th** pct (min 56.5, max 99.5) |
| RN.Ai Pearson / Spearman | 0.5322 / -0.1071 (n too small to interpret) |
