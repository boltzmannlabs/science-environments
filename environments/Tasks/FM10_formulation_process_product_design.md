# FM10 — Formulation–Process–Product Integrated Design for Tablet Development

**Environment:** `FM10_fpp_integrated` · **Series:** Pharmaceutical formulation B — excipient compatibility, stability & viscosity
**Tools:** formulation environment (agent scientist + DoE) · process model

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Formulation–Process–Product integrated design for tablet development (2025) |
| Original paper objective | Integrate formulation and manufacturing parameters in pharmaceutical tablet development. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "formulation process product integrated design tablet development 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **integrated formulation and process optimization** — the agent scientist must:

1. Treat formulation variables (excipient ratios) and process variables (granulation parameters, compression force) as **one joint design space** — not sequential blocks — and predict responses: tablet quality (hardness, friability, disintegration, dissolution) and manufacturing robustness (weight uniformity, ejection force proxies).
2. Identify **cross-domain interactions** (e.g., binder level × impeller speed on granule properties; lubricant × compression on dissolution) — the defining challenge of integrated design.
3. Propose a **joint optimum**: formulation + process set achieving quality targets with maximal robustness margin (batch-to-batch consistency).
4. Map a **design space** (per ICH Q8): proven-acceptable region in the combined variable space.

## 3. Expected Outputs

- Joint formulation–process optimum with predicted CQAs in spec.
- Cross-domain interaction map (≥ 2 interactions identified if present in paper).
- ICH Q8-style design space with rationale.
- **Batch-to-batch consistency**: predicted response variance under realistic input variation.

## 4. Ground Truth to Capture

- Combined formulation–process DoE tables.
- Response surfaces and the paper's design space.
- Robustness/validation results.

## 5. Environment Setup

```
sci_paper/env/FM10/
├── input/factor_space.yaml + blinded_matrix.csv   # formulation + process factors together
├── ground_truth/full_doe.csv + design_space.yaml  # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Joint (not staged) optimization | agent reasons over the combined space; sequential-only designs score 0 here |
| 2 | Cross-domain interactions | ≥ 2 identified if present in paper |
| 3 | Response prediction MAE (blind) | hardness ≤ 2 kp; DT ≤ 30 s; dissolution ≤ 10 pp |
| 4 | Design space | proposed space ⊆ or equal to paper's acceptable region (no unsafe extensions) |
| 5 | Consistency | predicted variance under input noise below paper's observed batch variation |

## 7. Notes

- This is the **FM-P05 (manufacturing process optimization)** flagship; scoring metric 1 deliberately punishes the common agent shortcut of optimizing formulation first, process second.
