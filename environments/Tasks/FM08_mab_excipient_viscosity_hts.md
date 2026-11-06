# FM08 — High-Throughput Excipient Compatibility & Viscosity Screening for High-Concentration mAbs

**Environment:** `FM08_mab_viscosity_hts` · **Series:** Pharmaceutical formulation B — excipient compatibility, stability & viscosity
**Tools:** formulation environment (agent scientist) · excipient-knowledge screening

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | High-throughput excipient compatibility and viscosity screening for high-concentration mAb formulations (2024) |
| Original paper objective | Rapidly screen excipient compatibility and viscosity in high-concentration monoclonal antibody formulations. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "high-throughput excipient viscosity screening high concentration monoclonal antibody 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **excipient compatibility and viscosity reduction** — the agent scientist must:

1. Given the mAb (or mAb class) and concentration context, **prioritize an excipient screen**: buffer species/pH, amino acids (arginine, proline, histidine classes), sugars (sucrose/trehalose), surfactants (polysorbate class) — rank by expected viscosity effect **and** compatibility risk.
2. Predict viscosity response across the blinded excipient matrix (relative viscosity vs. baseline).
3. Predict **compatibility flags**: excipients risking aggregation, deamidation/oxidation pathways, polysorbate degradation/peroxide risk.
4. Propose a **shortlist formulation set** (top-3) expected to reduce viscosity while maintaining stability indicators (DLS/SEC-monitored), with a suggested confirmation assay cascade.

## 3. Expected Outputs

- Identified excipients that **reduce viscosity** (≥ 20% relative reduction at paper's screening concentration) **while remaining compatible**.
- Blind viscosity-prediction accuracy across the matrix.
- A risk map: excipient × degradation pathway.
- Shortlist + confirmatory assay plan.

## 4. Ground Truth to Capture

- Screening matrix: excipient × concentration × pH → viscosity.
- Compatibility/stability readouts (aggregation %, turbidity, etc.).
- Paper's selected excipient(s)/formulation(s).

## 5. Environment Setup

```
sci_paper/env/FM08/
├── input/mab_context.yaml + blinded_matrix.csv
├── ground_truth/full_screen.csv + selections.md   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Best viscosity reducer in top-3 predicted | yes/no |
| 2 | Viscosity prediction MAE (blind) | ≤ 15% relative |
| 3 | Incompatible excipients | ≥ 70% of paper's failures flagged |
| 4 | Shortlist quality | all shortlisted excipients compatible per paper data |
| 5 | Assay plan | confirmation cascade covers viscosity + aggregation + chemical stability |

## 7. Notes

- Biologic-formulation task — no small-molecule chemistry tool applies; this scores the agent-scientist's formulation knowledge directly (protein-specific failure modes like polysorbate oxidation are the discriminators).
- Pairs with FM09 (the phase-separation extension).
