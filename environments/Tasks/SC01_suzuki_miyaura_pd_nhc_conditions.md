# SC01 — Suzuki–Miyaura Coupling with Pd-NHC Precatalysts: Catalyst & Condition Optimization

**Environment:** `SC01_suzuki_pd_nhc` · **Series:** Synthetic chemistry A — reaction yield & condition improvement
**Tools:** condition recommendation (primary) · forward reaction · impurity prediction

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Suzuki–Miyaura coupling using Pd-NHC precatalysts (2026) |
| Original paper objective | Identify the optimal catalyst and reaction conditions through experimental screening. |
| Likely candidate | "Challenges in data-driven catalysis modelling: case study on palladium-NHC catalysed Suzuki–Miyaura" ([RSC record](https://pubs.rsc.org/sc/article/17/8/4235/911133)) — 21 Pd-NHC complexes benchmarked in Suzuki–Miyaura. **Confirm identity, then capture full citation before running.** |
| Full citation | **To fill:** authors, journal, volume/pages, DOI |

## 2. What We Want to Work On (Objective)

From this paper we work on **catalyst and condition optimization for difficult Suzuki couplings** — the agent scientist, with the paper masked, must:

1. For the paper's challenging aryl halide substrates (prioritize aryl chlorides / heteroaryl halides from the screening set):
   - Rank **Pd-NHC precatalyst families** (steric/electronic descriptor space, not just names) for expected yield.
   - Recommend **catalyst loading, base, solvent (incl. water content), and temperature** as a top-10 ranked condition grid.
2. Predict yield for each recommended condition and for the paper's full screening matrix (blind).
3. Identify a **single robust condition set** expected to work across multiple substrates (not per-substrate cherry-picking), with a predicted yield floor.
4. Flag likely side products per condition (homocoupling, dehalogenation, protodeboronation) via impurity prediction.

## 3. Expected Outputs

- Improved **isolated yield** vs. the paper's baseline condition (Δ ≥ +10 pp on the difficult substrates, or match the paper's best if already optimal).
- **Reduced catalyst loading**: minimum loading (mol%) retaining ≥ 90% of best-yield performance.
- A **substrate-general condition set** with predicted per-substrate yields and a pass/fail map (electron-rich / electron-poor / hindered).
- Predicted-vs-actual yield table for the paper's screening matrix.

## 4. Ground Truth to Capture (before running)

- Catalyst screening table: precatalyst × substrate → conversion/yield.
- Condition tables: base, solvent/water fraction, temperature, loading → yield.
- Failed-condition entries (these calibrate the impurity/decomposition axis).

## 5. Environment Setup

```
sci_paper/env/SC01/
├── input/substrates.smi        # aryl halides + boronic acids from paper
├── ground_truth/screening.csv  # catalyst × condition × yield (fill from paper)
├── runs/                       # condition recommendations + yield predictions
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Paper's best catalyst family in tool's top-3 | yes/no |
| 2 | Paper's optimum condition set in top-5 recommendations (same base class, ΔT ≤ 20 °C) | yes/no |
| 3 | Yield MAE across screening matrix | ≤ 15 pp |
| 4 | Loading-reduction proposal retains ≥ 90% of best yield | predicted + literature-supported |
| 5 | Cross-substrate condition set: predicted pass rate | ≥ 70% of substrate set |

## 7. Notes

- Anti-leakage: mask tool corpora at a date preceding the paper's publication.
- If the candidate paper above is confirmed to be the data-modeling case study, use its **underlying experimental benchmarking dataset** as ground truth (the modeling wrapper is irrelevant to this benchmark).
