# Simone/Sciabola-322 — clean independent predictor validation

Cohort: 322 siRNAs with measured Hep3B efficacy (Sciabola et al. 2013), joined to real 57-nt
mRNA context from the dataset transcripts. **Clean**: outside the training of every local
model (RN.Ai, OligoFormer, RNAiSpline). Model: RN.Ai-Predict (Apache-2.0) via the siRNA-Bench
adapter. Binary cutoff >= 0.7.

| n | pos/neg | AUC | Pearson | Spearman |
|---|---|---|---|---|
| 322/322 | 241/81 | **0.7021** | 0.5074 | 0.3930 |

Context quality: 320 in-domain, 2 N-padded (transcript-end clamps). Full per-record
predictions in `predictions.csv`; metrics in `metrics.json`. Frozen gates, no tuning.
Reading: first auditable independent measured-performance number for this stack; ~0.12 AUC
generalization gap vs the exposed Mix-469 cohort (descriptive replay, source workspace).
