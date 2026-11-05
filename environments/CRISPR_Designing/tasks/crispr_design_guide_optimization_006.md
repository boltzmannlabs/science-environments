# Task: crispr_design_guide_optimization_006

**Task family:** application-aware CRISPR guide design — **Guide candidate optimization and reranking**.  
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Optimize or rerank a supplied guide candidate set for a user-defined editing objective without changing the target or silently relaxing hard constraints. Compare the baseline ranking with the optimized ranking and identify which criteria drive any changes. The deliverable is a reproducible, constraint-preserving optimization report.

Application-specific requirements: retain baseline candidates and scores; explicitly define optimization objective; identify hard versus soft constraints; evaluate diversity and Pareto tradeoffs; document any generated candidates separately from supplied candidates.

## Target and Reference (Fixed)

This task optimizes/reranks the candidate set produced by `crispr_design_base_editing_002` for the fixed PKD1 case-study variant. Do not ask the user to provide a target.

- **Organism:** Homo sapiens
- **Gene/variant:** `PKD1 NM_001009944.3:c.6658C>T (p.Arg2220Trp)`
- **Reference assembly:** GRCh38
- **Baseline candidate source:** output of the fixed base-editing task, or the candidate table bundled with the run; retain baseline identifiers and scores unchanged
- **Reference benchmark:** Ibel et al. (2025), same PKD1 case study
- **Fixed-input behavior:** if the baseline candidate set is absent, return `BASELINE_CANDIDATES_REQUIRED` and state the expected source path; do not ask for a new target or silently generate a replacement baseline.

- **Default vetoes:** altered target/reference; candidate provenance lost; hard gate relaxed without authorization.
- **Default weight emphasis:** objective fit .35 / specificity .30 / efficacy .25 / diversity .10.
## Design Constraints

- Preserve baseline candidate identities and original scores.
- Separate hard constraints from soft objectives.
- Use a declared optimization/reranking method and fixed seed where applicable.
- Report Pareto tradeoffs when objectives conflict; do not hide them in one score.
- Any newly generated candidates must be distinguishable from the original input set.

## Required Execution Steps

| Step | What must happen | Required result |
|---|---|---|
| 1. Route + brief | Confirm `mode=guide_optimization`; define objective, candidate source, and constraints. | Confirmed, hashed brief. |
| 2. Verify reference | Confirm candidate sequences and reference provenance. | Verified input set or blocker. |
| 3. Application preparation | Mark fixed parameters, tunable parameters, and objective dimensions. | Optimization readiness record. |
| 4. Baseline | Recompute or import baseline scores under the shared battery. | `baseline_candidates.csv`. |
| 5–8. Battery E1–E4 | Validate, score, and gate candidates consistently. | Per-dimension evidence and flags. |
| 9. Optimization layer (E5) | Apply declared optimization/reranking procedure and preserve candidate lineage. | `optimized_candidates.csv` and lineage. |
| 10. Gates (R1) | Enforce unchanged frozen gates and brief constraints. | Survivor set and decision log. |
| 11. Rank (R2/R3) | Compare baseline/optimized ranks; perform sensitivity and diversity checks. | Comparison and stability report. |
| 12. Deliver | Explain rank changes, tradeoffs, provenance, and limitations. | Complete typed bundle. |

## Expected Output

Fresh run directory containing `baseline_candidates.csv`, `optimized_candidates.csv`, `rank_comparison.csv`, `pareto_summary.csv` (when applicable), `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`.

## Constraints

Optimization is computational only. No silent gate relaxation, target substitution, or unsupported efficacy claims. Reproducibility requires method, version, parameters, and seed where applicable.

## Important Instructions

Show why candidates moved in rank. Report the baseline and optimized results side by side. Do not present optimization as experimental improvement unless a relevant measured benchmark supports that claim.

---
