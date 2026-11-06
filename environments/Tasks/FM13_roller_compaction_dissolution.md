# FM13 — Roller Compaction Effects on Dissolution of Granules and Tablets

**Environment:** `FM13_roller_compaction` · **Series:** Pharmaceutical formulation C — manufacturing & process optimization
**Tools:** DoE environment (agent scientist) · dissolution environment

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Effects of roller compaction on dissolution of granules and tablets (2025) |
| Original paper objective | Study the influence of roller compaction on dissolution of two pharmaceutical formulations. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "roller compaction dissolution granules tablets 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **roller-compaction and dissolution optimization** — the agent scientist must:

1. Optimize **roll pressure, roll speed, ribbon density, and milling conditions** against responses: **granule properties (PSD, flow), tablet hardness/disintegration, and dissolution** — for **both formulations** in the paper (a two-formulation transfer test).
2. Predict the **compaction–dissolution relationship**: how ribbon density propagates through milling to granule compactability and final dissolution; identify the loss-of-compensability risk (over-compacted ribbon → poor dissolution even after tableting).
3. Propose per-formulation operating windows that **maintain or improve dissolution** while achieving suitable granule properties.
4. State which formulation is more compaction-sensitive and why (deformability/binder system reasoning).

## 3. Expected Outputs

- Per-formilation operating windows (roll pressure/speed/ribbon density/milling) with predicted granule + dissolution outcomes.
- **Dissolution maintained or improved** vs. baseline at proposed windows.
- Compactability/dissolution transfer analysis across the two formulations.
- Compaction-sensitivity ranking with mechanistic rationale.

## 4. Ground Truth to Capture

- Per-formulation DoE: compaction parameters × responses (ribbon density, granule PSD, tablet properties, dissolution).
- The paper's conclusions on formulation-dependent sensitivity.

## 5. Environment Setup

```
sci_paper/env/FM13/
├── input/factor_space.yaml + blinded_matrix.csv (×2 formulations)
├── ground_truth/full_doe.csv + conclusions.md   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | dissolution ≤ 10 pp; hardness ≤ 2 kp |
| 2 | Density–dissolution chain | direction of ribbon-density effect on dissolution correct per formulation |
| 3 | Windows | both formulations' windows meet dissolution + granule targets |
| 4 | Sensitivity ranking | more sensitive formulation correctly identified |
| 5 | Experiment efficiency | shared learning across the 2 formulations (run count below 2× single-formulation budget) |

## 7. Notes

- The two-formulation design tests **transfer learning** in the agent's process reasoning — the only multi-product formulation task in the FM series.
