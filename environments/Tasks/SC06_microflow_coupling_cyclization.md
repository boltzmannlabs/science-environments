# SC06 — Microflow Sequential Coupling & Cyclization: Continuous-Flow Process Improvement

**Environment:** `SC06_microflow_seq` · **Series:** Synthetic chemistry A — reaction yield & condition improvement
**Tools:** condition recommendation (process-constrained) · impurity prediction · forward reaction

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Microflow sequential coupling and cyclization (2025) |
| Original paper objective | Optimize sequential coupling and cyclization in a continuous-flow system. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "microflow sequential coupling cyclization continuous flow 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **continuous-flow reaction process improvement** — the agent scientist must:

1. Optimize the flow parameter space: **residence time, temperature, concentration, and reagent addition sequence** (segmented vs. merged streams; order of mixing for the reactive intermediate).
2. Predict **yield and impurity profile** at each corner/center point of the flow design space — especially side products from the sequentially generated intermediate (accumulation → over-reaction in the cyclization segment).
3. Recommend a **robust operating window** (not a single point) that keeps predicted yield ≥ target despite ±10% pump/temperature drift.

> ⚠️ **Scope note (from curation):** *exclude this paper if Bayesian optimization is prohibited* — the original optimization may rely on BO. In that case run this benchmark with a **DoE/grid protocol** (factorial corner points + center) and compare against the paper's final reported optimum only, or skip the task entirely.

## 3. Expected Outputs

- Improved **product yield** vs. paper baseline (Δ ≥ +10 pp) and **shorter total reaction time** (residence time sum).
- A **reproducible process**: operating window with predicted yield surface and impurity map.
- Addition-sequence recommendation with mechanistic justification.

## 4. Ground Truth to Capture

- Flow parameter tables (residence time × T × concentration → yield/impurity).
- Addition-sequence comparisons.
- Final optimized process and its yield/purity at scale.

## 5. Environment Setup

```
sci_paper/env/SC06/
├── input/reaction.smi + flow_space.yaml   # parameter ranges from paper
├── ground_truth/flow_doe.csv              # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Paper optimum inside tool's recommended operating window | yes/no |
| 2 | Yield MAE across flow design space | ≤ 15 pp |
| 3 | Impurity hot-spot prediction | highest-impurity region correctly identified |
| 4 | Robustness | window tolerates ±10% drift with predicted yield drop ≤ 5 pp |
| 5 | Total residence time | ≤ paper's optimum |

## 7. Notes

- Flow constraints are alien to most condition tools (they optimize batch axes); scoring tolerates missing flow-native intelligence but rewards tools that at least respect concentration/time/temperature axes.
