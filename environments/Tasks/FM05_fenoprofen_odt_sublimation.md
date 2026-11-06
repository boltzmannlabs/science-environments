# FM05 — Fenoprofen Calcium Orodispersible Tablet: Sublimation-Process Optimization

**Environment:** `FM05_fenoprofen_odt` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Fenoprofen calcium orodispersible tablet optimization (2025) |
| Original paper objective | Develop and optimize an orodispersible tablet (ODT) using a sublimation process. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "fenoprofen calcium orodispersible tablet sublimation optimization 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **orodispersible formulation optimization** — the agent scientist must:

1. Optimize the factor space: **sublimating agent type and level (e.g., camphor/menthol/urea class), disintegrant level, compression force (hardness), resulting porosity** against responses: **disintegration time, hardness/porosity, friability, drug release**.
2. Predict blinded-matrix responses; capture the porosity–hardness–DT triad trade-off (more sublimate → more porosity → faster DT but weaker tablet).
3. Propose the optimum: minimum DT meeting friability/hardness specs for handling.
4. Recommend the sublimation process window (time/temperature) implied by the agent choice.

## 3. Expected Outputs

- **Reduced disintegration time** (≤ 30 s target or paper's optimum) with acceptable mechanical strength.
- **Improved drug release** vs. conventional tablet baseline.
- Porosity–DT model consistent with the paper's data.
- Complete ODT formula + process definition.

## 4. Ground Truth to Capture

- Factor–response DoE tables (agent, disintegrant, hardness → DT, friability, release).
- Porosity measurements vs. sublimate level.
- Optimized formula and its validation.

## 5. Environment Setup

```
sci_paper/env/FM05/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Sublimating agent choice | paper's agent in top-2 recommended |
| 2 | Response prediction MAE (blind) | DT ≤ 15 s; friability ≤ 0.3% |
| 3 | Trade-off optimum | DT + friability + hardness all in spec |
| 4 | Porosity model | predicted porosity trend matches paper (sign + rough magnitude) |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- Instantiates **FM-P02**; the sublimation axis (physical structure engineering) differentiates it from disintegrant-only ODT tasks (FM14).
