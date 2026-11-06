# Task: gene_silencing_genetic-disease-total-lowering_003

**Task family:** application-aware siRNA design — **Genetic-disease siRNA design (total lowering)**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](001_gene_silencing_rna.md) for mode routing.

## Description

total-transcript lowering for a loss-tolerable target; explicitly distinct from allele-selective design, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: wild-type-function review question raised at intake; family-member near-match screen; isoform coverage decision.

## Target

Resolved per request — never defaulted. Example gene (TTR) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [003_genetic-disease-total-lowering.request.example.json](../config/003_genetic-disease-total-lowering.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu.
- **Default weight emphasis:** efficacy .40 / specificity .30 / immune .15 / seed_tox .10 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- Total lowering and mutant-only lowering are different objectives; computational pass is not disease qualification.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm mode=genetic_disease_total_lowering brief; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Exact transcript (+ variant only where this application requires it). | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | wild-type-function review question raised at intake; family-member near-match screen; isoform coverage decision | Application readiness record. |
| 4. Generate | Local generator; all windows retained; fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)). | Per-dimension values + flags. |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required. | Typed flags/context. |
| 10. Gates (R1) | Frozen gates ∪ brief vetoes ∪ application defaults. | Survivor set + decision log. |
| 11. Rank (R2/R3) | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel. | Ranked table + stability report. |
| 12. Deliver | panel + WT-sparing statement + next-evidence recommendation; per-dimension values; provenance; honest tier. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

If wild-type function is essential (e.g., cardiac TTR), the wild-type-sparing question must be surfaced even in a total-lowering request. Application benchmark status: BENCHMARKED end-to-end: approved-drug site-rank audit (vutrisiran #62/598, patisiran #107/598), same-side battery vs all 7 approved drugs, TTR top-20 gate audit — ../../benchmark/003_TTR-approved-drugs-cohort/README.md.
