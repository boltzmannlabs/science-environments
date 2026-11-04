# FM14 — Orodispersible Herbal Tablet Optimization Using DoE

**Environment:** `FM14_herbal_odt` · **Series:** Pharmaceutical formulation C — manufacturing & process optimization
**Tools:** formulation environment (agent scientist + DoE)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Orodispersible herbal tablet optimization using DoE (2025) |
| Original paper objective | Optimize an orodispersible herbal tablet formulation. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "orodispersible herbal tablet design of experiments 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **multicomponent tablet formulation optimization** — the agent scientist must:

1. Optimize the excipient set around a **multicomponent herbal extract load** (hygroscopic, poor-flowing, sticky active): disintegrant, filler/diluent ratio, binder, and compression force against responses: **disintegration time, hardness/friability, dissolution of marker actives, flow of the blend**.
2. Predict blinded-matrix responses; identify which **excipient-compatibility constraints** dominate with herbal extracts (moisture-driven stickiness, incompatibility of superdisintegrants at high humidity).
3. Propose the optimized formulation meeting all CQAs with a **moisture-management rationale** (extract hygroscopicity control).
4. Produce a quality-attribute summary with predicted consistency.

## 3. Expected Outputs

- Optimized formulation with **consistent quality attributes** (DT, hardness, friability, marker dissolution all in spec).
- Compatibility-driven excipient-selection rationale (which excipients were excluded and why).
- Blind-prediction table for the formulation matrix.
- Moisture-control strategy for the extract.

## 4. Ground Truth to Capture

- DoE tables: excipient/process factors × responses.
- Herbal extract characteristics (hygroscopicity, dose/load).
- Optimized formulation + validation.

## 5. Environment Setup

```
sci_paper/env/FM14/
├── input/factor_space.yaml + blinded_matrix.csv + extract_context.yaml
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | DT ≤ 15 s; hardness ≤ 2 kp |
| 2 | Compatibility exclusions | ≥ 1 paper-incompatible excipient avoided with stated reason |
| 3 | Multi-CQA optimum | all quality attributes in spec simultaneously |
| 4 | Moisture rationale | hygroscopicity strategy present and consistent |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- Instantiates **FM-P02** at maximum composition complexity (multicomponent actives) — a robustness stress test compared with single-API tasks FM02/FM05.
