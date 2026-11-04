# Task: crispr_design_base_editing_002

**Task family:** application-aware CRISPR design — **Base-editing guide design**. **Status:** Proposed; computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only the application-specific requirements differ.

## Description

Design and prioritize gRNAs for a resolved nucleotide-editing requirement using a specified base editor. The deliverable is a candidate set that satisfies target-variant compatibility while minimizing unintended bystander edits and predicted off-target activity.

Generate candidate guides around the target variant, evaluate them through the fixed multi-dimensional battery under frozen gates, and return a requirement-ranked shortlist capped at `NEEDS_EXPERIMENTAL_VALIDATION`.

Application-specific requirements: editor compatibility; editing-window assessment; bystander-editing reporting; reference and alternate allele validation; separation of intended-edit feasibility from predicted guide activity.

## Target

Resolved per request — never defaulted.

- **Reference:** exact versioned transcript and genome assembly; target sequence hashed into provenance.
- **Variant:** user-confirmed reference and alternate alleles with genomic coordinates.
- **Editor:** specified base editor and compatible PAM requirements.
- **Brief:** desired nucleotide conversion, editing scope, bystander tolerance, and prioritization requirements.
- **Default vetoes:** incorrect reference allele; incompatible editor chemistry; incompatible PAM; target outside supported editing window; failed sequence validation.
- **Default weight emphasis:** intended-edit compatibility and specificity; weights resolved through the common ranking contract.

## Design Constraints

- Representation: guide candidates with explicit spacer, PAM, strand, target position, and variant coordinates.
- Editor identity and editing-window definition must be explicit and versioned.
- Intended nucleotide conversion and bystander-editing risk must remain separate endpoints.
- Candidate guides must be evaluated for all editable nucleotides within the defined window.
- Predicted editing efficiency must not be interpreted as measured editing frequency.
- Variant interpretation is reference-dependent; genome assembly mismatches are a hard blocker.
- Constraints may only be tightened by the confirmed brief. Proposed adaptations require diagnosis.

## Required Execution Steps

| Step                       | What must happen                                                                                 | Required result                      |
| -------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------ |
| 1. Route + brief           | Confirm mode=base_editing; resolve variant, editor, conversion, and bystander tolerance.         | Confirmed hashed brief.              |
| 2. Verify reference        | Verify reference allele, alternate allele, transcript, assembly, and target sequence.            | Verified reference or stage blocker. |
| 3. Application preparation | Define editor compatibility, PAM rules, editing window, and bystander assessment policy.         | Application readiness record.        |
| 4. Generate                | Enumerate candidate guides spanning the variant using the local generator.                       | `candidate_pool.csv`.                |
| 5–8. Battery E1–E4         | Run common validation, efficacy, structure, and specificity assessments.                         | Per-dimension values and flags.      |
| 9. Application layers (E5) | Assess intended-edit compatibility, editing window, bystander sites, and variant context.        | Typed editing and bystander flags.   |
| 10. Gates (R1)             | Apply frozen gates ∪ brief vetoes ∪ editor-specific requirements.                                | Survivor set and decision log.       |
| 11. Rank (R2/R3)            | Rank by confirmed priorities; run ranking stability analysis.                                    | Ranked table and stability report.   |
| 12. Deliver                | Report intended edit, bystander analysis, off-target evidence, and experimental validation plan. | Complete typed bundle.               |

## Expected Output

Fresh run directory: ranked base-editing guides with variant coordinates, reference/alternate alleles, editor identity, editing-window positions, bystander assessment, per-dimension evidence, gate log, stability report, provenance block, evidence tier, and next-evidence recommendation.

## Constraints

Base-editor predictions are editor- and context-dependent. A predicted nucleotide conversion does not establish measured editing efficiency or absence of bystander edits. Reference genome and editor versions must be recorded. License tiers bind redistribution.

## Important Instructions

Do not rank a guide solely by predicted activity if it does not satisfy the intended-edit requirement. Report all editable bystander positions within the specified window. Do not claim precise correction or absence of unintended edits without experimental evidence.

**Application benchmark status:** To be established against a published base-editing dataset with guide-level editing outcomes and bystander annotations.
