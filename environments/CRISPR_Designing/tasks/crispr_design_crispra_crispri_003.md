# Task: crispr_design_crispra_crispri_003

**Task family:** application-aware CRISPR guide design — **CRISPR activation / interference guide design**.
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Design and rank guides for transcriptional modulation of a resolved gene using CRISPRa or CRISPRi. The deliverable is a promoter/TSS-aware candidate panel with positional evidence, specificity assessment, and separate interpretation for activation versus repression.

Application-specific requirements: mode-specific effector confirmation; transcript/TSS selection; promoter-relative guide placement; isoform coverage; regulatory-region context; expression evidence when available.

## Target and Reference (Fixed)

This task uses a fixed human **CDKN1A (p21)** promoter target. The primary benchmark mode is CRISPRi; CRISPRa may be reported as a separate mode only if the configured effector profile supports it. Do not ask the user to provide a target gene.

- **Organism:** Homo sapiens
- **Gene:** `CDKN1A`
- **Reference assembly:** GRCh38
- **Transcript:** `NM_000389.5` (RefSeq; verify accession and sequence)
- **Target region:** promoter/TSS-relative region for the selected transcript; derive TSS coordinates from the pinned annotation release and record the exact coordinate and convention in `reference_validation.json`
- **Reference source:** NCBI RefSeq plus a pinned GRCh38 annotation release
- **Fixed-input behavior:** use the gene and transcript above; annotation-derived TSS resolution is a required validation step, not a user prompt. Stop with `REFERENCE_VALIDATION_FAILED` if transcript/TSS mapping cannot be verified.
- **Default vetoes:** unresolved TSS; incompatible PAM; guide outside allowed design region; unacceptable off-target risk.
- **Default weight emphasis:** promoter/TSS compatibility .35 / specificity .30 / guide quality .20 / transcript coverage .15.

## Design Constraints

- CRISPRa and CRISPRi are distinct tasks; do not reuse their ranking assumptions without review.
- Position candidates relative to the selected TSS and report the coordinate convention.
- Where multiple TSSs exist, disclose which transcript start sites are covered.
- Expression or chromatin context may inform interpretation but cannot be fabricated when unavailable.
- Predicted modulation is not experimentally established expression change.

## Required Execution Steps

| Step                       | What must happen                                                                    | Required result                         |
| -------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------- |
| 1. Route + brief           | Confirm CRISPRa or CRISPRi mode, effector, target, and TSS preference.              | Confirmed, hashed brief.                |
| 2. Verify reference        | Verify assembly, annotation, transcript, and TSS.                                   | Verified reference or blocker.          |
| 3. Application preparation | Define promoter-relative region and relevant isoforms; record context availability. | Application readiness record.           |
| 4. Generate                | Generate compatible guides in a fresh run directory.                                | `candidate_pool.csv`.                 |
| 5–8. Battery E1–E4       | Validate guide, assess activity/quality, and evaluate specificity.                  | Per-dimension evidence and flags.       |
| 9. Application layer (E5)  | Annotate distance/orientation to TSS, transcript coverage, and regulatory context.  | TSS-context report.                     |
| 10. Gates (R1)             | Apply frozen gates and application-specific region/TSS constraints.                 | Survivor set and decision log.          |
| 11. Rank (R2/R3)           | Rank under confirmed weights; assess sensitivity to TSS and weight choices.         | Ranked candidates and stability report. |
| 12. Deliver                | Provide panel, positional evidence, limitations, and validation recommendations.    | Complete typed bundle.                  |

## Expected Output

Fresh run directory containing `candidate_pool.csv`, `ranked_candidates.csv`, `tss_position_report.csv`, `off_target_summary.csv`, `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`.

## Constraints

Computational design only. CRISPRa/i effector systems, promoter definitions, and coordinate conventions must be recorded. Do not claim measured activation or repression without experimental evidence.

## Important Instructions

Report the selected TSS and distance/orientation for every candidate. Explain transcript ambiguity and context-data gaps. Benchmark separately for CRISPRa and CRISPRi using suitable reference data.

---
