# SC08 — Ceritinib Scalable Process Development Using DoE: Robustness & Scale-Up

**Environment:** `SC08_ceritinib_doe` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** condition recommendation · impurity prediction · DoE environment (agent scientist)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Scalable process development of Ceritinib using DoE (2025) |
| Original paper objective | Develop and optimize a scalable manufacturing process using statistical experimental design. |
| Full citation | **To fill:** authors, journal (likely *OPRD*), volume/pages, DOI (retrieve via "ceritinib process development design of experiments 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **process robustness and scale-up optimization** — the agent scientist must:

1. **Identify critical process parameters (CPPs)** from the paper's factor list (temperature, stoichiometry, time, addition rate, solvent/water level, etc.) — blind to the paper's analysis — and rank them by expected impact on yield and impurity.
2. **Design the DoE**: propose a screening design (fractional factorial) then a response-surface design for the top factors; justify run count.
3. **Predict the responses** across the design space: yield and key impurity level at each design point (blind), then predict the **optimum and robust operating ranges**.
4. **Intermediate quality linkage**: predict how intermediate quality attributes (e.g., residual impurity level in the isolated intermediate) propagate to the final step's performance.

## 3. Expected Outputs

- Correct CPP shortlist vs. the paper's statistical analysis.
- A reproducible process definition: **operating ranges** (not point conditions) with predicted yield/purity at range edges.
- Predicted-vs-actual response table over the paper's DoE matrix.
- Scale-up risk register (parameters whose effect grows with scale).

## 4. Ground Truth to Capture

- DoE matrices: factor levels × responses (yield, impurity %, physical attributes).
- Statistical analysis outcomes: significant factors, interactions, R².
- Final proven-acceptable ranges (PAR) and validation results at scale.

## 5. Environment Setup

```
sci_paper/env/SC08/
├── input/process.yaml          # step recipe + factor ranges from paper
├── ground_truth/doe_tables.csv # factors × responses + PARs (fill from paper)
├── runs/                       # agent's DoE design + predictions
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | CPP identification | ≥ 70% overlap with paper's significant factors |
| 2 | Response prediction MAE | yield ≤ 12 pp; key impurity ≤ 0.5 pp absolute |
| 3 | Optimum location | predicted optimum inside or adjacent to paper's PAR |
| 4 | Experiment efficiency | agent's proposed total run count ≤ paper's to reach equivalent knowledge |
| 5 | Interaction discovery | ≥ 1 significant factor interaction correctly predicted |

## 7. Notes

- This task pilots the DoE-methodology benchmark also covered by SC12; if run together, share the DoE environment implementation.
- Pairs with derived topic **Reaction time optimization** and problem statement **SC-P04 (impurity reduction)**.
