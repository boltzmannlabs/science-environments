# FM02 — Loratadine Tablet: Dissolution & Robustness Optimization

**Environment:** `FM02_loratadine_tablet` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Loratadine tablet dissolution and robustness optimization (2025) |
| Original paper objective | Improve tablet dissolution and robustness using formulation DoE. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "loratadine tablet dissolution robustness design of experiments 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **disintegrant and surfactant optimization** — the agent scientist must:

1. Model the factor space: **TPGS (surfactant) level, sodium starch glycolate (disintegrant) level, and compression force/hardness** against responses: **dissolution rate (f2/Q-timepoints), disintegration time, tablet hardness/friability**.
2. Predict responses over the blinded formulation matrix; identify **significant main effects and interactions** (e.g., surfactant × compression on disintegration-dissolution coupling).
3. Propose the **optimized formulation + process set**: dissolution target met while mechanical properties (hardness/friability) stay in spec — explicitly resolving the dissolution-vs-robustness tension.
4. Define the **robustness region**: compression-force window where responses remain acceptable.

## 3. Expected Outputs

- **Improved dissolution rate** vs. baseline (Δ ≥ +10 pp at key time point or f2 > 50 vs. reference, per paper's metric).
- **Mechanical properties maintained** (hardness/friability in spec at optimum).
- Significant-factor + interaction analysis blind-matched to the paper's DoE conclusions.
- Robust operating window for compression.

## 4. Ground Truth to Capture

- DoE tables (factors × responses incl. dissolution profiles, DT, hardness, friability).
- Paper's optimized formulation + validation.

## 5. Environment Setup

```
sci_paper/env/FM02/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | dissolution ≤ 10 pp; DT ≤ 30 s; hardness ≤ 2 kp |
| 2 | Interaction detection | surfactant × disintegrant (or equivalent) interaction found if present in paper |
| 3 | Optimum | both dissolution + mechanical targets met |
| 4 | Robust window | compression window with responses in spec |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- Classic **FM-P02/FM-P05** instance with a formulation–process coupled factor set — good stress test for agents that treat process and composition variables jointly.
