
# Task: crispr_design_paired_deletion_005

**Task family:** application-aware CRISPR design — Paired gRNA design for genomic deletion. **Status:** Proposed; computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only the application-specific requirements differ.

## Description

Identify and prioritize pairs of gRNAs intended to excise a resolved genomic interval using CRISPR-Cas9. The deliverable is a ranked set of guide pairs with evidence for individual guide compatibility, pair geometry, specificity, and expected deletion boundaries.

Generate candidate guides flanking the requested interval, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: pair orientation; genomic distance; expected deletion size; individual guide activity; pair-level off-target assessment; deletion-boundary reporting.

## Target

Resolved per request — never defaulted.

- **Reference:** exact genome assembly and target interval; sequence hashed into provenance.
- **Brief:** user-confirmed deletion boundaries or desired interval, permitted deletion-size range, and guide-pair priorities.
- **Target region:** explicit genomic coordinates with reference assembly.
- **Default vetoes:** invalid coordinates; incompatible PAM; unsupported pair orientation; out-of-range deletion size; failed individual guide validation.
- **Default weight emphasis:** pair geometry, specificity, and individual guide activity; weights resolved through the common ranking contract.

## Design Constraints

- Representation: individual guides and guide pairs must be represented separately.
- Pair orientation and predicted deletion boundaries must be explicit.
- Expected deletion size is a geometric prediction, not a measured deletion outcome.
- Individual guide efficiency and pair-level deletion probability remain separate endpoints.
- Both guides must independently pass individual guide gates.
- Pair selection must not bypass individual specificity requirements.
- Pair-level off-target combinations must be reported where supported; unavailable analysis must be typed as `NOT_RUN` or `UNSUPPORTED`.

## Required Execution Steps

| Step                       | What must happen                                                                                  | Required result                         |
| -------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------- |
| 1. Route + brief           | Confirm mode=paired_deletion; resolve interval, deletion size, and pair requirements.             | Confirmed hashed brief.                 |
| 2. Verify reference        | Verify assembly, target coordinates, and sequence orientation.                                    | Verified reference or stage blocker.    |
| 3. Application preparation | Define pair orientation, allowed distance, boundary tolerance, and pair-level evaluation.         | Application readiness record.           |
| 4. Generate                | Generate eligible guides on both sides of the target interval.                                    | `candidate_pool.csv`.                 |
| 5–8. Battery E1–E4       | Run common battery for individual guides.                                                         | Per-guide values and flags.             |
| 9. Application layers (E5) | Enumerate pairs; calculate orientation, predicted deletion size, and pair geometry.               | Pair table and application flags.       |
| 10. Gates (R1)             | Apply frozen gates ∪ brief vetoes ∪ pair-specific requirements.                                 | Survivor pairs and decision log.        |
| 11. Rank (R2/R3)           | Rank guide pairs using confirmed weights and stability analysis.                                  | Ranked pair table and stability report. |
| 12. Deliver                | Report candidate pairs, individual guide evidence, expected deletion boundaries, and limitations. | Complete typed bundle.                  |

## Expected Output

Fresh run directory: ranked guide pairs with individual sequences, genomic coordinates, orientation, predicted deletion interval and size, per-guide and pair-level evidence, gate log, stability report, provenance block, evidence tier, and next-evidence recommendation.

## Constraints

Pair-level deletion outcomes depend on cleavage, repair, cell context, and experimental delivery. A predicted deletion does not establish a measured deletion frequency or exact junction. Unsupported pair-level predictors must not be substituted with unvalidated heuristics without disclosure. License tiers bind redistribution.

## Important Instructions

Do not report an individual guide as a complete paired-deletion solution. Report both guides and the expected interval. Keep pair geometry and individual guide activity distinct. Experimental validation is required to establish deletion frequency and junction sequence.

**Application benchmark status:** To be established against a reference dataset containing experimentally measured paired-guide deletion outcomes and genomic junctions.
