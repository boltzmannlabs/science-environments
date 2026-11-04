# Task: gene_silencing_genetic-disease-allele-selective

**Task family:** application-aware siRNA design — **Genetic-disease siRNA design (allele-selective)**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](gene_silencing_rna_001.md) for mode routing.

## Description

mutant-selective lowering with wild-type sparing; requires a reference-verified variant before any design, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: BLOCK until variant verified (ClinVar/dbSNP + VEP consequence via ToolUniverse); E5b allele-discrimination assay: RNAduplex delta-delta-G for guide vs mutant and vs wild-type allele, both energies reported with the discrimination margin.

## Target

Resolved per request — never defaulted. Example gene (HTT) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [genetic-disease-allele-selective.request.example.json](genetic-disease-allele-selective.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu; variant_unverified = BLOCKED_PENDING_MUTATION_SPECIFICATION.
- **Default weight emphasis:** efficacy .30 / specificity .25 / immune .15 / seed_tox .10 / stability .20 incl. allele_margin .20.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- A perfect mutant match with a WT mismatch supports sequence discrimination in silico only — never a cellular selectivity claim.

## Required Execution Steps

| Step                       | What must happen                                                                                                                                                                                                                             | Required result                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 1. Route + brief           | Confirm mode=genetic_disease_allele_selective brief; resolve priorities (defaults above where user silent).                                                                                                                                  | Confirmed hashed brief.                      |
| 2. Verify reference        | Exact transcript (+ variant only where this application requires it).                                                                                                                                                                        | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | BLOCK until variant verified (ClinVar/dbSNP + VEP consequence via ToolUniverse); E5b allele-discrimination assay: RNAduplex delta-delta-G for guide vs mutant and vs wild-type allele, both energies reported with the discrimination margin | Application readiness record.                |
| 4. Generate                | Local generator; all windows retained; fresh run directory.                                                                                                                                                                                  | `candidate_pool.csv`.                      |
| 5–8. Battery E1–E4       | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)).                                                                                                                                        | Per-dimension values + flags.                |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required.                                                                                                                                       | Typed flags/context.                         |
| 10. Gates (R1)             | Frozen gates ∪ brief vetoes ∪ application defaults.                                                                                                                                                                                        | Survivor set + decision log.                 |
| 11. Rank (R2/R3)           | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel.                                                                                                                                                   | Ranked table + stability report.             |
| 12. Deliver                | variant identity + coordinates + mutant/WT energy table + total-vs-selective recommendation; per-dimension values; provenance; honest tier.                                                                                                  | Complete typed bundle.                       |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

Construct zero hypothetical mutants; shared-reference silencing is not mutant-selective and carries no wild-type-sparing guarantee. Application benchmark status: Not benchmarked end-to-end (no verified-variant cohort executed). Cross-cutting evidence: ../../benchmark/README.md.
