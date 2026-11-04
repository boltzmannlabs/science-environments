# FM12 — Fluid-Bed Granulation & Drying Process Development Using DoE

**Environment:** `FM12_fluid_bed_doe` · **Series:** Pharmaceutical formulation C — manufacturing & process optimization
**Tools:** DoE environment (agent scientist)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Fluid-bed granulation and drying process development using DoE (2024) |
| Original paper objective | Establish a robust pharmaceutical granulation and drying process. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "fluid bed granulation drying design of experiments 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **granulation and drying parameter optimization** — the agent scientist must:

1. Optimize **inlet temperature, airflow, spray rate, and binder concentration** (granulation phase) plus drying end-point parameters against responses: **granule size/moisture content, flow, yield (fines/oversize), and process consistency across batches**.
2. Predict responses over the blinded matrix; identify the **spray-rate × inlet-temperature coupling** (over-wetting vs. excessive fines) — the classic fluid-bed failure axis.
3. Define the **drying end-point control** strategy (moisture target with time/temperature trade-off).
4. Propose a robust operating space with predicted batch-to-batch consistency.

## 3. Expected Outputs

- Improved **granule properties** (D50/span within target) and **moisture control** (end-point moisture within spec, e.g., LOD target ± band).
- **Process consistency**: predicted response variation across the design space below paper's observed variation.
- Operating space + end-point strategy definition.

## 4. Ground Truth to Capture

- DoE tables: parameters × responses (granule PSD, LOD, flow, yield).
- Batch consistency data.
- Paper's final robust process definition.

## 5. Environment Setup

```
sci_paper/env/FM12/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + process_definition.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | LOD ≤ 0.5% abs; D50 ≤ 15% rel |
| 2 | Coupling axis | spray-rate × inlet-T interaction found if present |
| 3 | Operating space | proposed space within paper's robust region |
| 4 | End-point strategy | moisture target achievable with stated margin |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- **FM-P05** instance focused on unit-operation depth (one process, four coupled parameters) — complements FM10's breadth (formulation+process joint).
