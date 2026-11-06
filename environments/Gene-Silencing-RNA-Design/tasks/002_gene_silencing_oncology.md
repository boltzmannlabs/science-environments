# Task: gene_silencing_oncology_002

**Task family:** application-aware siRNA design — **Oncology siRNA design**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](001_gene_silencing_rna.md) for mode routing.

## Description

tumor-associated knockdown study without assuming tumor-selective delivery or dependence, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: isoform decision (all expressed vs specific) BEFORE generation; paralog/pseudogene full-transcriptome screen; 6merDB seed-toxicity deconvolution (seed-driven viability changes are not efficacy); GTEx normal-tissue expression margin for the target.

## Target

Resolved per request — never defaulted. Example gene (KRAS) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [002_oncology.request.example.json](../config/002_oncology.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu + paralog_full_length_hits.
- **Default weight emphasis:** efficacy .35 / specificity .35 / seed_tox .15 / immune .10 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- Target mRNA reduction is not tumor regression and not selective toxicity.

## Required Execution Steps

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Route + brief | Confirm mode=oncology brief; resolve priorities (defaults above where user silent). | Confirmed hashed brief. |
| 2. Verify reference | Exact transcript (+ variant only where this application requires it). | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | isoform decision (all expressed vs specific) BEFORE generation; paralog/pseudogene full-transcriptome screen; 6merDB seed-toxicity deconvolution (seed-driven viability changes are not efficacy); GTEx normal-tissue expression margin for the target | Application readiness record. |
| 4. Generate | Local generator; all windows retained; fresh run directory. | `candidate_pool.csv`. |
| 5–8. Battery E1–E4 | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)). | Per-dimension values + flags. |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required. | Typed flags/context. |
| 10. Gates (R1) | Frozen gates ∪ brief vetoes ∪ application defaults. | Survivor set + decision log. |
| 11. Rank (R2/R3) | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel. | Ranked table + stability report. |
| 12. Deliver | >=2 seed-distinct candidates + non-targeting control note + orthogonal-confirmation recommendation; per-dimension values; provenance; honest tier. | Complete typed bundle. |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

A candidate whose seed hits a viability-depleting 6mer may look effective for the wrong reason — flag and deconvolute; never report seed-toxicity as efficacy. Application benchmark status: BENCHMARKED end-to-end on two clean public cohorts — HPSE (n=106) and HK2 (n=95) measured siRNAs: rank-recovery median 94.5th/95.1st pct; per-sequence AUC 0.58-0.72 (target-dependent; deep review windows advised). See ../../benchmark/002_Oncology-HPSE-HK2-cohorts/README.md.
