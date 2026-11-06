# Task: gene_silencing_functional-genomics_009

**Task family:** application-aware siRNA design — **Functional-genomics siRNA panel design**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](001_gene_silencing_rna.md) for mode routing.

## Description

gene-function hypothesis with off-target/seed confound control as a first-class objective; the deliverable is a PANEL, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: seed-distinctness maximization across the panel with seed-overlap reporting; paralog coverage report; orthogonal-evidence lookup (OpenTargets); pooled-screen reagent-uniqueness considerations.

## Target

Resolved per request — never defaulted. Example gene (KIF11) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [009_009_functional-genomics.request.example.json](009_009_functional-genomics.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu; seed collision within the panel.
- **Default weight emphasis:** specificity .40 / efficacy .30 / seed_tox .15 / immune .10 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- One reagent phenotype is not gene function; pooled and individual-reagent evidence are distinct.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm mode=functional_genomics brief; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Exact transcript (+ variant only where this application requires it). | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | seed-distinctness maximization across the panel with seed-overlap reporting; paralog coverage report; orthogonal-evidence lookup (OpenTargets); pooled-screen reagent-uniqueness considerations | Application readiness record. |
| 4. Generate | Local generator; all windows retained; fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)). | Per-dimension values + flags. |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required. | Typed flags/context. |
| 10. Gates (R1) | Frozen gates ∪ brief vetoes ∪ application defaults. | Survivor set + decision log. |
| 11. Rank (R2/R3) | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel. | Ranked table + stability report. |
| 12. Deliver | seed-distinct panel (>=3 recommended) + per-member per-dimension values + rescue/orthogonal plan; per-dimension values; provenance; honest tier. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

Maximize seed diversity; report overlaps explicitly; never deliver a single 'best' siRNA as a gene-function answer. Application benchmark status: Panel-construction logic exercised in the TTR and HIF1A runs — ../../benchmark/README.md; no screen-outcome cohort.
