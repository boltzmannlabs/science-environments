# Task: crispr_design_base_editing_002

**Task family:** application-aware CRISPR guide design — **Base-editing guide and editor-window design**.
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Identify guide candidates that place the requested nucleotide change within a compatible base editor's editing window while minimizing bystander edits and predicted off-target effects. The deliverable is a ranked, evidence-backed candidate set—not a claim that the desired edit will occur experimentally.

Application-specific requirements: exact variant normalization; reference/alternate allele confirmation; editor and strand compatibility; editing-window occupancy; bystander-edit inventory; consequence annotation.

## Target and Reference (Fixed)

This task uses the PKD1 variant from the supplied case study. Do not ask the user to provide a target or variant.

<<<<<<< HEAD
Resolved per request — never defaulted.Example gene (KIF11), variant, editor, and nucleotide conversion are illustrative, not defaults.

- **Reference:** exact versioned transcript and genome assembly; target sequence hashed into provenance.
- **Variant:** user-confirmed reference and alternate alleles with genomic coordinates.
- **Editor:** specified base editor and compatible PAM requirements.
- **Brief:** desired nucleotide conversion, editing scope, bystander tolerance, and prioritization requirements.
- **Default vetoes:** incorrect reference allele; incompatible editor chemistry; incompatible PAM; target outside supported editing window; failed sequence validation.
- **Default weight emphasis:** intended-edit compatibility and specificity; weights resolved through the common ranking contract.
  =======
- **Organism:** Homo sapiens
- **Gene:** `PKD1`
- **Variant:** `NM_001009944.3:c.6658C>T` (`p.Arg2220Trp`)
- **Reference assembly:** GRCh38
- **Transcript:** `NM_001009944.3` / `ENST00000262304.9`
- **Genomic locus:** `chr16:2,108,509` (GRCh38, minus strand; validate normalized coordinate and REF allele against the assembly)
- **Editing mode:** adenine base editing, correcting the pathogenic variant on the appropriate strand
- **Benchmark reference:** Ibel et al. (2025), *In vivo base editing reduces liver cysts in autosomal dominant polycystic kidney disease*, Molecular Therapy 33(11):5373–5382
- **Fixed-input behavior:** use the variant, transcript, and assembly above. Validate them programmatically; on any mismatch, stop with `REFERENCE_VALIDATION_FAILED` and report the discrepancy. Do not prompt for a target.
- **Default vetoes:** REF mismatch; unsupported substitution/editor chemistry; target outside the configured editing window; unresolved strand or coordinate convention.
- **Default weight emphasis:** desired-edit compatibility .35 / specificity .30 / bystander risk .20 / guide quality .15.

>>>>>>> bd1dd1b (Added new CRISPR designing tasks)
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

## Design Constraints

- Confirm the reference allele against the selected assembly before design.
- Model the editor's documented window and compatible substitutions; do not assume all editors share a window.
- Enumerate potential bystander edits in the window and annotate their consequences.
- Keep desired-edit feasibility separate from general guide activity and specificity.
- No claim of measured editing efficiency without experimental data.

## Required Execution Steps

| Step                       | What must happen                                                                                       | Required result                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------- |
| 1. Route + brief           | Confirm `mode=base_editing`; resolve variant, editor, assembly, transcript, and bystander tolerance. | Confirmed, hashed brief.                 |
| 2. Verify reference        | Normalize variant and confirm REF allele and coordinate system.                                        | Verified variant record or blocker.      |
| 3. Application preparation | Enumerate compatible guide orientations and editor windows around the locus.                           | Application readiness record.            |
| 4. Generate                | Generate candidates using configured editor/PAM rules in a fresh run directory.                        | `candidate_pool.csv`.                  |
| 5–8. Battery E1–E4       | Validate guide, score activity/quality, and assess specificity.                                        | Per-dimension evidence and flags.        |
| 9. Application layer (E5)  | Report desired-base window position, bystanders, strand, and predicted consequences.                   | Bystander and edit-compatibility report. |
| 10. Gates (R1)             | Apply frozen gates, REF-match gate, editor compatibility, and user bystander vetoes.                   | Survivor set and decision log.           |
| 11. Rank (R2/R3)           | Rank using confirmed weights; test weight stability and bystander sensitivity.                         | Ranked candidates and stability report.  |
| 12. Deliver                | Provide guide alternatives, desired-edit evidence, bystander profile, provenance, and limitations.     | Complete typed bundle.                   |

## Expected Output

Fresh run directory containing `candidate_pool.csv`, `ranked_candidates.csv`, `variant_validation.json`, `bystander_edits.csv`, `off_target_summary.csv`, `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`.

## Constraints

Base-editing design only; editor assumptions must be versioned. Do not treat predicted bystander edits as confirmed outcomes. Organism-specific work requires reference validation and application review.

## Important Instructions

A candidate must be compatible with the desired substitution, not merely score well as a guide. Explicitly list bystanders and distinguish predicted edits from observed editing. Benchmark against a named reference dataset or paper and disclose differences in editor, cell context, and assay.

---
