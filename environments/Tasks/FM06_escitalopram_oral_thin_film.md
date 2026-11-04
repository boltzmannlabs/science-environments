# FM06 — Escitalopram Oxalate Oral Thin Film: Composition & Release Optimization

**Environment:** `FM06_escitalopram_otf` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Escitalopram oxalate oral thin-film optimization (2025) |
| Original paper objective | Develop an oral thin-film formulation using DoE. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "escitalopram oral thin film design of experiments 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **oral thin-film composition and release optimization** — the agent scientist must:

1. Optimize the factor space: **film-forming polymer ratio, plasticizer level, film thickness, drying conditions (T/time)** against responses: **film flexibility/folding endurance, tensile strength, thickness uniformity, content uniformity, disintegration/dissolution time**.
2. Predict blinded-matrix responses; resolve the flexibility–brittleness trade-off (plasticizer up → flexibility up but strength/drying complications).
3. Propose the optimum formulation + process meeting all CQAs simultaneously.
4. Check **content uniformity risk**: drying conditions vs. drug migration in the film.

## 3. Expected Outputs

- Improved **mechanical performance** (folding endurance, tensile strength within target band) and **uniformity** (content/thickness RSD ≤ 5%).
- **Drug release/disintegration** target met (fast-dissolving film spec).
- A complete film formula + drying process definition with predicted CQAs.
- Trade-off analysis: plasticizer–polymer–thickness response surface summary.

## 4. Ground Truth to Capture

- DoE tables: factors × responses (mechanical, uniformity, release).
- Film-forming polymer and plasticizer identities.
- Optimized formula + validation data.

## 5. Environment Setup

```
sci_paper/env/FM06/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind) | tensile ≤ 2 MPa; DT ≤ 10 s; RSD ≤ 2 pp |
| 2 | Multi-CQA optimum | all CQA targets met at proposed point |
| 3 | Trade-off surface | plasticizer–polymer interaction correctly signed |
| 4 | Process window | drying conditions with predicted uniformity in spec |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- Instantiates **FM-P02** in a non-tablet dosage form — tests generality of the agent's formulation reasoning beyond tableting.
