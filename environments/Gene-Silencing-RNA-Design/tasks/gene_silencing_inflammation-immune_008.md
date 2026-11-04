# Task: gene_silencing_inflammation-immune

**Task family:** application-aware siRNA design — **Inflammation / immune-modulation siRNA design**. **Status:** In Progress; protocol v1.2, frozen gates, computational scope only. Shares the environment battery, ranking contract and gates with all application tasks; only the application-specific requirements differ. Start from the [general task](gene_silencing_rna_001.md) for mode routing.

## Description

intended pathway modulation kept distinct from siRNA-induced innate response and general cell injury, for a resolved human transcript under the user's confirmed requirement brief. Generate paired 19-nt core candidates, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked, per-dimension-evidenced shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: exact family-member resolution before design ('NFKB target' is ambiguous: RELA? NFKB1? IKBKB? — ask); family-member near-match screen; immune flags are HARD filters here and double as confound controls.

## Target

Resolved per request — never defaulted. Example gene (TNF) and any example values are illustrative, not defaults.

- **Reference:** exact versioned transcript (RNA alphabet), hashed into provenance.
- **Brief:** [inflammation-immune.request.example.json](inflammation-immune.request.example.json) illustrates syntax only.
- **Default vetoes:** immune_ugugu AND gu_top_decile (confound control).
- **Default weight emphasis:** efficacy .30 / specificity .25 / immune .30 / seed_tox .10 / stability .05.

## Design Constraints

- Representation: paired 19-nt RNA cores; clinical-format overhang duplexes currently reject at intake (backlog #1).
- Two efficacy endpoints, never blended; both strands screened; heuristic caps disclosed.
- Frozen gates tightened-only by the brief; constraint adaptations PROPOSED with diagnosis.
- Innate stimulation can masquerade as efficacy (cytokine readouts confounded); lower cytokine output is not specific pathway inhibition.

## Required Execution Steps

| Step                       | What must happen                                                                                                                                                                                           | Required result                              |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| 1. Route + brief           | Confirm mode=inflammation_immune_modulation brief; resolve priorities (defaults above where user silent).                                                                                                  | Confirmed hashed brief.                      |
| 2. Verify reference        | Exact transcript (+ variant only where this application requires it).                                                                                                                                      | Verified `transcript.fa` or stage blocker. |
| 3. Application preparation | exact family-member resolution before design ('NFKB target' is ambiguous: RELA? NFKB1? IKBKB? — ask); family-member near-match screen; immune flags are HARD filters here and double as confound controls | Application readiness record.                |
| 4. Generate                | Local generator; all windows retained; fresh run directory.                                                                                                                                                | `candidate_pool.csv`.                      |
| 5–8. Battery E1–E4       | Validation; both efficacy endpoints; structure; both-strand specificity (E4e NOT_RUN(broken-binary)).                                                                                                      | Per-dimension values + flags.                |
| 9. Application layers (E5) | Immune scan mandatory; chemistry/expression context per application; allele assay only where required.                                                                                                     | Typed flags/context.                         |
| 10. Gates (R1)             | Frozen gates ∪ brief vetoes ∪ application defaults.                                                                                                                                                      | Survivor set + decision log.                 |
| 11. Rank (R2/R3)           | Cohort-percentile weighting under confirmed weights; ±25% stability; seed-distinct panel.                                                                                                                 | Ranked table + stability report.             |
| 12. Deliver                | panel + immune-flag report per strand + confound framing; per-dimension values; provenance; honest tier.                                                                                                   | Complete typed bundle.                       |

## Expected Output

Fresh run directory: ranked candidates with per-dimension evidence, gate log, stability report, provenance block, evidence tier, and the application-specific next-evidence recommendation.

## Constraints

Antiviral/pathogen/pest work is review-only; plant/pest inactive; human models never transfer; license tiers bind redistribution.

## Important Instructions

A UGUGU-containing candidate is unusable in this application regardless of efficacy score. Application benchmark status: Immune-filter behavior characterized on the labeled cohort (UGUGU incidence orthogonal to efficacy label; 97.8% pass) — ../../benchmark/README.md; no application-specific measured cohort.
