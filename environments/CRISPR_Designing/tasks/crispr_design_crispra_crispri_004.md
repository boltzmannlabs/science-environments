# Task: crispr_design_crispra_crispri_004

**Task family:** application-aware CRISPR design — **Transcriptional activation and repression guide design**. **Status:** Proposed; computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only the application-specific requirements differ.

## Description

Design and prioritize gRNAs for transcriptional activation or repression of a resolved human gene using a specified CRISPRa or CRISPRi system. The deliverable is a ranked guide set supported by promoter-positioning, target-region, and specificity evidence.

Generate candidates within the defined transcriptional regulatory region, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: activation/repression mode routing; transcription start site (TSS) resolution; guide-to-TSS distance reporting; promoter or regulatory-region context; separate activation and repression scoring or evidence.

## Target

Resolved per request — never defaulted.

- **Reference:** exact versioned transcript and genome assembly; TSS source and version recorded.
- **Brief:** target gene, intended mode=CRISPRa or CRISPRi, selected effector system, target transcript, and desired regulatory scope.
- **Regulatory region:** user-confirmed or protocol-defined interval relative to the TSS.
- **Default vetoes:** unresolved TSS; incompatible effector; guide outside the permitted region; invalid sequence; unacceptable off-target burden.
- **Default weight emphasis:** regulatory positioning, predicted activity, and specificity; weights resolved through the common ranking contract.

## Design Constraints

- Representation: guide candidates with explicit spacer, PAM, strand, genomic coordinates, and TSS distance.
- CRISPRa and CRISPRi are distinct modes; their results must not be blended.
- Effector identity must be recorded because activity depends on the activation or repression system.
- TSS and transcript selection must be explicit; alternative TSSs may change guide interpretation.
- Position-based heuristics must be disclosed and cannot substitute for experimental expression measurements.
- Ranking must respect mode-specific gates.

## Required Execution Steps

| Step                       | What must happen                                                                            | Required result                      |
| -------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1. Route + brief           | Confirm mode=CRISPRa or CRISPRi; resolve gene, effector, transcript, and regulatory scope.  | Confirmed hashed brief.              |
| 2. Verify reference        | Verify transcript, TSS, assembly, and promoter/regulatory interval.                         | Verified reference or stage blocker. |
| 3. Application preparation | Define TSS window, effector-specific constraints, and activation/repression interpretation. | Application readiness record.        |
| 4. Generate                | Generate candidate guides within the specified regulatory interval.                         | `candidate_pool.csv`.              |
| 5–8. Battery E1–E4       | Run common validation, efficacy, structure, and specificity assessments.                    | Per-dimension values and flags.      |
| 9. Application layers (E5) | Evaluate TSS distance, regulatory-region position, and mode-specific evidence.              | Typed application flags.             |
| 10. Gates (R1)             | Apply frozen gates ∪ brief vetoes ∪ CRISPRa/i-specific requirements.                      | Survivor set and decision log.       |
| 11. Rank (R2/R3)           | Rank within the selected mode and run stability analysis.                                   | Ranked table and stability report.   |
| 12. Deliver                | Report guide ranking, TSS positions, evidence, and validation requirements.                 | Complete typed bundle.               |

## Expected Output

Fresh run directory: ranked CRISPRa or CRISPRi guides with genomic coordinates, transcript/TSS information, effector identity, regulatory-position evidence, per-dimension values, gate log, stability report, provenance block, evidence tier, and next-evidence recommendation.

## Constraints

CRISPRa/i activity depends on effector, cell type, chromatin context, and TSS selection. Computational position scores do not establish measured gene expression changes. Activation and repression evidence must remain separate. License tiers bind redistribution.

## Important Instructions

Do not treat CRISPRa and CRISPRi as interchangeable. Do not interpret a guide's predicted activity as proof of gene activation or repression. Report the selected TSS and the assumptions used to define the regulatory interval.

**Application benchmark status:** To be established against mode-specific experimental activation or repression datasets. Benchmark CRISPRa and CRISPRi independently.
