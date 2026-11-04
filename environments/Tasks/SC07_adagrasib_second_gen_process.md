# SC07 — Adagrasib Second-Generation Synthesis: Cost-Effective API Process Development

**Environment:** `SC07_adagrasib_process` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** retrosynthesis (route redesign) · condition recommendation · impurity prediction

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Adagrasib second-generation synthesis (2024) |
| Original paper objective | Improve the original API manufacturing route through process redesign and impurity control. |
| Full citation | **To fill:** authors, journal (likely *OPRD*), volume/pages, DOI (retrieve via "adagrasib second-generation synthesis process 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **cost-effective API process development** — the agent scientist, given only the target structure (adagrasib) and the first-generation route's problem list (high cost reagents, low-yield step, impurity carryover — from `input/gen1_summary.yaml`), must:

1. **Route redesign (retrosynthesis):** propose ≥ 3 alternative disconnections/reagent sets for the expensive or low-yielding transformation(s); rank by predicted step economy and cost.
2. **Reagent/solvent substitution:** for each retained step, swap high-cost/hazardous reagents and Class-2 solvents with cheaper/greener equivalents (condition tool, cost-constrained mode).
3. **Impurity control:** predict the process impurity profile of the redesigned route — flag genotoxic/mutagenic-alert impurities (e.g., alkyl sulfonate risk from sulfonate chemistry if present), late-stage impurity carryover, and crystallization purge capability.
4. **Purification/crystallization:** propose isolation strategy per intermediate (crystallization vs. chromatography-free telescoping).

## 3. Expected Outputs

- A redesigned process with **reduced cost of goods** (estimate cost per kg vs. gen-1 baseline; target ≥ 30% reduction potential).
- **Improved yield** (predicted route overall yield ≥ gen-2 paper's route, or within 10% with fewer steps).
- **Reduced impurities**: predicted impurity register with purge rationale; critical impurities flagged with control strategy.
- **Simplified process**: fewer isolations/telescoped steps count vs. gen-1.

## 4. Ground Truth to Capture

- Gen-1 → gen-2 changes: which reagents/solvents/steps were replaced and why.
- Per-step yields and overall yield of the gen-2 route.
- Impurity structures the paper controlled (esp. late-stage, genotoxic).

## 5. Environment Setup

```
sci_paper/env/SC07/
├── input/target.smi + gen1_summary.yaml   # gen-1 route + pain points
├── ground_truth/gen2_route.yaml           # paper's redesigned route, yields, impurity controls (fill)
├── runs/                                  # redesigned routes + conditions + impurity registers
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Route overlap | redesigned route shares ≥ 1 key improvement with paper's gen-2 (same reagent-class swap or same new disconnection) |
| 2 | Step count/economy | ≤ gen-2 paper's longest linear sequence |
| 3 | Yield realism | predicted overall yield within 3× of paper's gen-2 yield |
| 4 | Impurity anticipation | ≥ 1 of the paper's controlled critical impurities predicted by tool |
| 5 | Cost direction | predicted cost-reduction levers include the paper's main cost driver |

## 7. Notes

- This is the flagship **SC-P03 (cost-effective API synthesis)** instance — see `SC-P_FM-P_research_problem_statements.md`.
- Mask the paper and any post-cutoff adagrasib process literature from tool corpora.
