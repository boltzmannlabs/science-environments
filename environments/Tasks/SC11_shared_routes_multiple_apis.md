# SC11 — Shared Synthetic Routes for Multiple APIs: Retrosynthesis & Flow Chemistry

**Environment:** `SC11_shared_api_routes` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** retrosynthesis (multi-target mode) · condition recommendation · forward reaction (validation)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Shared synthetic routes for multiple APIs through retrosynthesis and flow chemistry (2025) |
| Original paper objective | Identify shared synthetic routes and improve their application to multiple APIs. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "shared synthetic routes multiple APIs retrosynthesis flow chemistry 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **common-intermediate and shared-route development** — the agent scientist, given the paper's API set (structures in `input/targets.smi`), must:

1. **Multi-target retrosynthesis**: generate route trees for each API and **detect shared branch points** — intermediates serviceable by one synthesis feeding ≥ 2 APIs.
2. **Quantify sharing**: for each candidate common intermediate, compute duplicated-step savings (steps avoided across the portfolio), predicted combined yield, and material-utilization gain.
3. **Economic ranking**: rank shared-route platforms by portfolio cost (cost per API kg, weighted by the paper's assumed demands) vs. independent routes.
4. **Flow compatibility check**: flag which shared steps can telescope in flow (condition tool + literature precedent).

> Note: the original paper itself uses computer-aided retrosynthesis — **mask it (and its outputs) from tool corpora**; this benchmark tests whether *our* retro tool independently finds the same shared-platform logic.

## 3. Expected Outputs

- ≥ 1 **common intermediate** identified that supports ≥ 2 of the APIs (matching the paper's or a chemically equivalent one).
- **Reduced duplicated steps**: portfolio-level step count vs. independent routes (quantified delta).
- **Economical route selection**: ranked platform with cost/utilization rationale.
- Forward-validated route segments (`retro_check` + forward tool pass).

## 4. Ground Truth to Capture

- The paper's API set and the shared intermediate(s)/platform it identified.
- Route tables: per-API steps/yields via the shared platform vs. standalone.
- Economic analysis assumptions (demand, cost model).

## 5. Environment Setup

```
sci_paper/env/SC11/
├── input/targets.smi            # API set from paper
├── ground_truth/shared_platform.yaml  # paper's intermediates + route economics (fill)
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Shared intermediate hit | ≥ 1 proposed intermediate matches (or is 1 step from) the paper's |
| 2 | Savings realism | portfolio step-savings within 30% of paper's claim |
| 3 | Route validity | 100% of shared-platform steps pass forward/`retro_check` validation |
| 4 | Ranking sense | economic ranking of platforms has positive rank correlation with paper's |
| 5 | Flow feasibility | telescope flags justified by precedent |

## 7. Notes

- This is the most "platform-strategy" benchmark in the suite — it scores portfolio-level reasoning, a known weak spot for single-target planners. Log the gap if the tool cannot do multi-target analysis natively.
