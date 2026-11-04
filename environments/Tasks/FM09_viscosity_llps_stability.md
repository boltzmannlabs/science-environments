# FM09 — Viscosity-Lowering Excipients vs. Liquid–Liquid Phase Separation in Concentrated Antibodies

**Environment:** `FM09_mab_llps` · **Series:** Pharmaceutical formulation B — excipient compatibility, stability & viscosity
**Tools:** formulation environment (agent scientist)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Impact of viscosity-lowering excipients on liquid–liquid phase separation (2025) |
| Original paper objective | Investigate the relationship between viscosity-lowering excipients and phase separation in concentrated antibody formulations. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "viscosity excipients liquid-liquid phase separation concentrated antibody 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **viscosity vs. physical stability optimization** — the agent scientist must:

1. For each viscosity-lowering excipient class (argCl-class, proline-class, surfactant-class, pH shift), predict **both** responses: viscosity reduction **and** LLPS propensity shift at given concentration/pH.
2. Identify the **trade-off frontier**: excipients that lower viscosity but push the formulation into the two-phase region vs. those that are benign — this dual-response tension is the core scientific content.
3. Optimize **excipient concentration and pH**: propose conditions minimizing viscosity subject to a no-phase-separation constraint (clear solution across the paper's temperature range).
4. Predict aggregation risk coupling (LLPS → concentration-driven aggregation).

## 3. Expected Outputs

- A **dual-response map**: excipient × (viscosity, LLPS) covering the paper's matrix.
- Recommended formulation(s) that **reduce viscosity without inducing phase separation or aggregation**.
- Blind prediction accuracy on both axes.
- Mechanistic rationale (charge-charge vs. attractive-interaction modulation) consistent with the paper's discussion.

## 4. Ground Truth to Capture

- Excipient × concentration × pH → viscosity and cloud-point/LLPS observations.
- Temperature-dependent phase behavior.
- Paper's conclusions on which excipients are safe vs. risky.

## 5. Environment Setup

```
sci_paper/env/FM09/
├── input/mab_context.yaml + blinded_matrix.csv
├── ground_truth/full_matrix.csv + conclusions.md   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Dual-response direction | correct viscosity AND LLPS sign for ≥ 60% of excipients |
| 2 | Risky-excipient identification | ≥ 70% of paper's LLPS-inducers flagged |
| 3 | Constrained optimum | viscosity reduced with no predicted LLPS (validated vs paper data) |
| 4 | Mechanism rationale | consistent with paper's explanation |
| 5 | Aggregation coupling | risk linkage stated and directionally correct |

## 7. Notes

- Safety-gated like FM07: recommending a viscosity win that the paper shows phase-separates is a hard fail.
- Direct extension of FM08 — run after it to test whether the agent carries forward compatibility knowledge.
