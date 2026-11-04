# FM04 — Formulation Variables Affecting ASD Tablet Disintegration

**Environment:** `FM04_asd_tablet_disintegration` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Formulation variables affecting ASD tablet disintegration (2025) |
| Original paper objective | Investigate how formulation variables affect disintegration of spray-dried amorphous solid-dispersion (ASD) tablets. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "amorphous solid dispersion tablet disintegration formulation variables 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **ASD tablet disintegration improvement** — the agent scientist must:

1. Model the factor space: **polymer loading in the ASD, filler type, disintegrant level, and compression force** against responses: **disintegration time, wetting time, tensile strength, dissolution**.
2. Predict responses over the blinded matrix; identify which variables dominate disintegration for spray-dried ASD systems (slow disintegration is the known failure mode of high-polymer ASDs).
3. Propose the optimized set achieving **faster disintegration without compromising tablet integrity** — the explicit trade-off of this task.
4. Explain the mechanism: disintegrant performance vs. polymer viscosity/swellability conflict.

## 3. Expected Outputs

- **Faster disintegration** vs. paper baseline (Δ ≤ −30% DT, or match optimum).
- **Tablet integrity maintained** (tensile strength/friability in spec).
- Ranked variable-importance analysis matching the paper's findings.
- A mechanism-based explanation of the dominant interaction.

## 4. Ground Truth to Capture

- DoE tables: variables × responses (DT, wetting, strength, dissolution).
- Spray-dried intermediate properties (particle size, density) if reported.
- Paper's conclusions on dominant variables.

## 5. Environment Setup

```
sci_paper/env/FM04/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Variable importance | top-2 paper variables identified |
| 2 | Response prediction MAE (blind) | DT ≤ 30 s; tensile strength ≤ 0.3 MPa |
| 3 | Trade-off optimum | DT target met with strength in spec |
| 4 | Mechanism | interaction explanation consistent with paper |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- Shared scoring core with FM02 (different failure mode: ASD slow-disintegration vs. immediate-release optimization).
