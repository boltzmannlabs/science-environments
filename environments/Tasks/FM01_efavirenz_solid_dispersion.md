# FM01 — Efavirenz Solid Dispersion: API–Polymer–Adsorbent Composition Optimization

**Environment:** `FM01_efavirenz_sd` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE) — pairs with `environments/formulation_dissolution`

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Efavirenz solid dispersion optimization (2025) |
| Original paper objective | Improve dissolution and flow properties through solid-dispersion formulation optimization. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "efavirenz solid dispersion optimization dissolution flow 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **API–polymer–adsorbent composition optimization** — the agent scientist, with the paper's DoE data blinded, must:

1. Optimize the composition space: **polymer type, polymer:drug ratio, adsorbent loading** (and carrier level if in the paper's factors) against responses: **dissolution (e.g., % dissolved at t), flow properties (angle of repose/Carr index), and assay/recovery**.
2. Predict responses across the paper's formulation matrix (blind), then propose the **optimized formulation** with predicted responses and constraint checks (dose uniformity, acceptable flow).
3. Analyze **trade-offs**: adsorbent improves flow but can retard dissolution — locate the composition where both targets are met.
4. Produce a **reproducibility argument**: proposed CQAs tolerance window vs. composition variation (robustness of the optimum).

## 3. Expected Outputs

- Improved **dissolution** vs. paper baseline (Δ ≥ +10 pp at the paper's comparison time point, or match paper optimum).
- **Flowability** maintained/improved (Carr index / angle-of-repose within acceptable limits).
- A **reproducible formulation**: optimum with a composition window keeping all responses within spec.
- Predicted-vs-actual response table for the blinded formulation matrix.

## 4. Ground Truth to Capture

- DoE matrix: factor levels × responses (dissolution, flow, recovery).
- Optimized formulation and its validation results.
- Polymer/adsorbent identities and any incompatibility observations.

## 5. Environment Setup

```
sci_paper/env/FM01/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | dissolution ≤ 10 pp; flow index ≤ 5° |
| 2 | Optimum location | proposed formulation within paper's design space (or better via paper-data interpolation) |
| 3 | Trade-off resolution | both dissolution + flow targets met simultaneously |
| 4 | Experiment efficiency | reaches optimum in ≤ paper's run count (oracle-query protocol) |
| 5 | Robustness window | composition tolerance stated with predicted response drift ≤ spec |

## 7. Notes

- Instantiates problem statements **FM-P02 (composition optimization)** and **FM-P03 (dissolution improvement)**.
- Shares the SC12 oracle/DoE engine; reuse it.
