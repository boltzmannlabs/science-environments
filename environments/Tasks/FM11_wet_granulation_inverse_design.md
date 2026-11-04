# FM11 — Inverse Design of Wet Granulation: Process Optimization Benchmark (Non-AI Protocol)

**Environment:** `FM11_wet_granulation` · **Series:** Pharmaceutical formulation B — excipient compatibility, stability & viscosity
**Tools:** DoE environment (agent scientist) — **original paper uses ML: reference only, benchmark runs a non-AI protocol**

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Inverse design and optimization of wet granulation (2024) |
| Original paper objective | Optimize wet-granulation manufacturing using computational inverse design (ML). |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "inverse design wet granulation optimization 2024") |

## 2. Scope Rule (from curation)

> The original paper uses machine learning and **should only be used as a process reference, not as a non-AI benchmark target**. We use its *dataset and process knowledge* as ground truth; we do not benchmark our tools against its ML predictions. If an AI-assisted arm is ever added, revisit.

## 3. What We Want to Work On (Objective)

From this paper we work on **wet-granulation process optimization through conventional DoE** — the agent scientist must:

1. Optimize **binder concentration, liquid addition rate, and impeller speed** (plus wet-massing time if available) against: **granule size distribution (D50/span), flow properties, and downstream tablet quality**.
2. Predict responses over the blinded process matrix (interpolation within the paper's data only).
3. Propose the process set targeting a specified granule D50/span window with maximum robustness to pump/impeller variation.
4. Compare the **experiment count** the agent's DoE protocol needs vs. the dataset size the paper's ML consumed — an efficiency statement, not a modeling-parity claim.

## 4. Expected Outputs

- Granule-size-targeted process set with predicted D50/span.
- Blind-interpolation accuracy over the process matrix.
- Robustness margins to equipment variation.
- Experiment-efficiency comparison (documented, non-parity).

## 5. Ground Truth to Capture

- Process parameter × granule/tablet response dataset from the paper.
- Target granule properties the inverse design aimed at.
- Equipment/scale context.

## 6. Environment Setup

```
sci_paper/env/FM11/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_dataset.csv + targets.yaml   # fill from paper
├── runs/
└── scores/
```

## 7. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE (blind, in-range) | D50 ≤ 15% relative; span ≤ 20% |
| 2 | Target hit | proposed process reaches D50/span window per paper data |
| 3 | Robustness | ±10% parameter drift keeps responses in window |
| 4 | Efficiency statement | DoE run count vs. ML dataset size documented |
| 5 | Scope compliance | no attempt to reproduce/compare against the ML model outputs |

## 8. Notes

- Explicit non-AI-benchmark guardrail per the curation table; do not convert this task into an ML-parity benchmark without a scope decision.
