# SC10 — Experimental Design to Improve a Very Dilute Workup Procedure

**Environment:** `SC10_dilute_workup_doe` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** DoE environment (agent scientist) · process-cost model — *no molecule-level tool required*

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Application of experimental design to improve a very dilute workup procedure (2024) |
| Original paper objective | Improve a dilute pharmaceutical workup procedure using experimental design. |
| Full citation | **To fill:** authors, journal (likely *OPRD*), volume/pages, DOI (retrieve via "experimental design dilute workup pharmaceutical 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **workup and isolation efficiency improvement** — the agent scientist must:

1. Model the extraction/recovery physics-chemistry axes: **extraction solvent identity, phase ratio (organic:aqueous), total concentration, wash count/sequence, and recovery conditions (pH/temperature)**.
2. Given a blinded slice of the paper's DoE data (subset of runs), **predict the remaining runs' recovery and purity**.
3. Propose the **optimal workup**: minimum solvent volume and phase ratio that keeps recovery ≥ target and purity ≥ spec.
4. Quantify **cost/sustainability impact**: solvent consumption (L/kg API) and processing cost vs. the dilute baseline.

## 3. Expected Outputs

- **Reduced solvent consumption** (≥ 40% vs. the dilute baseline; or match paper's achieved reduction).
- **Improved product recovery** (Δ ≥ +5 pp vs. baseline, or match paper).
- **Decreased processing cost** estimate with assumptions stated.
- A workup design-space map (recovery vs. phase ratio vs. concentration).

## 4. Ground Truth to Capture

- DoE table: factors × responses (recovery %, purity %, cycles).
- Baseline (dilute) procedure numbers: solvent volumes, recovery, cycle time.
- Final optimized workup and validation data.

## 5. Environment Setup

```
sci_paper/env/SC10/
├── input/baseline.yaml + blinded_doe_subset.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Response prediction MAE on blinded runs | recovery ≤ 5 pp |
| 2 | Optimum location | proposed optimum within paper's design space (or better, validated by interpolation of paper data) |
| 3 | Solvent reduction | ≥ 40% vs. baseline |
| 4 | Constraint satisfaction | recovery + purity targets met at proposed point |
| 5 | Cost model | directionally correct cost reduction with explicit assumptions |

## 7. Notes

- This is the purest **process-DoE** benchmark in the SC series — no reaction-chemistry tool applies; it tests the agent-scientist's experimental-design reasoning alone (shared engine with SC12, FM-series).
