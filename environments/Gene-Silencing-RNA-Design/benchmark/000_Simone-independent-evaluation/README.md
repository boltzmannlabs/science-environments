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

## Published reference

| Metric | Published value | Source |
|---|---|---|
| AUC (Mixset, N-padded) | 0.808 | RN.Ai repo/registry, DOI 10.1101/2025.08.12.669916 |
| Spearman (Mixset) | 0.596 | same |
| AUC (RNAiSpline, same cohort) | 0.818 | RNAiSpline registry validation |
| AUC (OligoFormer paper protocol) | 0.8163 | PMID 39321261 |
| Simone/Sciabola cohort | **no published RN.Ai number** — Run-1b is the reference-setter | — |

## Run configuration

| Run | Config | Date |
|---|---|---|
| Run-1a | Mix-469 replay: frozen v1.0 gates, no refit, fixed seeds | 2026-11-03 |
| Run-1b | Simone-322: real 57-nt context from dataset transcripts; cutoff 0.7; labels post-hoc | 2026-11-03 |

## Benchmark metrics

| Metric | Value |
|---|---|
| n scored / pos / neg | 322 / 241 / 81 |
| **AUC** (cutoff label >= 0.7) | **0.7021** |
| Pearson | 0.5074 |
| Spearman | 0.393 |
| Context quality | 321 in-domain / 2 N-padded |

Reference context: exposed Mix-469 replay — RN.Ai AUC 0.8195 (descriptive, not like-for-like); generalization gap ≈ 0.12 AUC.
