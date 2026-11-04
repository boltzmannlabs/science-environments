# SC03 — Microwave Suzuki–Miyaura in Betaine/Glycerol: Green Solvent Substitution

**Environment:** `SC03_green_suzuki_des` · **Series:** Synthetic chemistry A — reaction yield & condition improvement
**Tools:** condition recommendation (green-solvent-constrained) · impurity prediction · forward reaction

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Microwave-assisted Suzuki–Miyaura coupling in betaine/glycerol solvent (2025) |
| Original paper objective | Develop a rapid, sustainable coupling procedure using a natural eutectic solvent. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "microwave Suzuki betaine glycerol deep eutectic solvent 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **green solvent substitution in cross-coupling reactions** — the agent scientist must:

1. **Benchmark conventional vs. alternative solvents**: given the coupling pair and catalyst from the paper, rank a solvent set spanning (a) conventional (dioxane, DMF, MeCN), (b) greener molecular solvents (2-MeTHF, CPME, ethanol/water), and (c) the betaine/glycerol deep-eutectic system — predicting yield for each.
2. Optimize **catalyst loading and microwave parameters** (temperature, time) in the winning green medium.
3. Quantify the **sustainability/yield trade-off**: predicted yield loss vs. E-factor/solvent-hazard improvement for each option.
4. Predict **impurity profile changes** on switching medium (Pd black formation, homocoupling, protodeboronation are known to shift with solvent polarity/water content).

## 3. Expected Outputs

- A green-medium condition set that **maintains or improves yield** vs. the conventional solvent baseline (within −5 pp or better).
- **Hazardous solvent elimination**: final recommendation contains no REACH/ICH Class 1–2 solvents.
- **Reduced reaction time** vs. conventional heating (microwave axis).
- A trade-off table: predicted yield, E-factor estimate, solvent hazard class per option.

## 4. Ground Truth to Capture

- Conventional-solvent baseline yields vs. DES yields.
- Catalyst-loading and µw condition tables.
- Substrate scope in the DES medium.
- Any reported Pd-black/side-product observations.

## 5. Environment Setup

```
sci_paper/env/SC03/
├── input/reaction.smi + solvent_space.yaml
├── ground_truth/solvent_comparison.csv   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | DES/betaine-glycerol predicted among top-3 media | yes/no |
| 2 | Yield prediction MAE across media | ≤ 15 pp |
| 3 | Green recommendation excludes Class 1–2 solvents | yes/no |
| 4 | Predicted yield of green set vs. conventional | within −5 pp |
| 5 | Impurity-shift direction correct (DES vs. conventional) | ≥ 1 correct qualitative call |

## 7. Notes

- Scoring rewards tools whose priors extend beyond "standard" solvent space; a tool that can only rank dioxane/DMF fails metric 1 regardless of chemistry quality.
- Ties into the derived research topic **Solvent replacement** (see `SC-C_derived_research_topics.md`).
