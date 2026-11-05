# Task: crispr_design_gene_knockout_001

**Task family:** application-aware CRISPR guide design — **Gene knockout guide design**.
**Status:** In Progress; protocol v1.0, computational scope only. Shares the environment battery, ranking contract, and gates with all application tasks; only application-specific requirements differ. Start from the [general task](../gene_editing_rna_001.md) for mode routing.

## Description

Design a ranked set of CRISPR-Cas guides for disrupting a resolved human gene through coding-region editing. The deliverable is a guide shortlist with activity, specificity, transcript coverage, and predicted-disruption evidence. Return alternatives and clearly label all candidates `NEEDS_EXPERIMENTAL_VALIDATION`; computational predictions do not establish a knockout phenotype.

Application-specific requirements: coding-exon and transcript coverage reporting; predicted coding consequence; paralog review; off-target burden; guide diversity across target regions.

## Target and Reference (Fixed)

This task uses a fixed human **HPRT1 knockout** benchmark target. Do not ask the user to supply a gene or target.

- **Organism:** Homo sapiens
- **Gene:** `HPRT1`
- **Reference assembly:** GRCh38
- **Transcript:** `NM_000194.3` (RefSeq; verify accession and sequence against the selected reference source)
- **Target region:** protein-coding exons of the fixed transcript; report transcript/exon coverage
- **Reference source:** NCBI RefSeq and GRCh38
- **Benchmark purpose:** reference-validation and coding-region guide-evaluation workflow; use any separately provided benchmark guide set as the comparison set, and do not invent published guide outcomes
- **Fixed-input behavior:** use these values as the task inputs. Resolve the transcript sequence and annotation automatically; if accession/version or assembly validation fails, stop with `REFERENCE_VALIDATION_FAILED` rather than asking for a replacement target.
- **Default vetoes:** unresolved reference; incompatible PAM; invalid spacer; unacceptable predicted off-target risk under the shared frozen gates.
- **Default weight emphasis:** specificity .40 / efficacy .30 / coding coverage .20 / sequence quality .10.

## Design Constraints

- Target coding sequence and report which transcript(s) are covered.
- Evaluate efficacy and specificity separately; do not merge into a single untraceable score.
- Consider alternative transcripts and paralogs where relevant.
- Predicted frameshift or coding disruption is not equivalent to experimentally demonstrated gene knockout.
- Gates may be tightened by the brief; changes to shared gates require a diagnosed proposal and approval.

## Required Execution Steps

| Step                       | What must happen                                                                                                    | Required result                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1. Route + brief           | Confirm `mode=gene_knockout`; resolve target, nuclease, assembly, transcript priorities, and ranking preferences. | Confirmed, hashed brief.             |
| 2. Verify reference        | Validate exact genome/transcript reference and version.                                                             | Verified reference or stage blocker. |
| 3. Application preparation | Extract coding exons; map transcript context; assess paralogs and coverage needs.                                   | Application readiness record.        |
| 4. Generate                | Run the configured local generator; retain eligible windows and use a fresh run directory.                          | `candidate_pool.csv`.              |
| 5–8. Battery E1–E4       | Run validation, efficacy, sequence-quality, and specificity checks.                                                 | Per-dimension values and flags.      |
| 9. Application layer (E5)  | Annotate exon, coding position, transcript coverage, and predicted consequence.                                     | Typed application annotations.       |
| 10. Gates (R1)             | Apply frozen gates plus user-confirmed vetoes.                                                                      | Survivor set and decision log.       |
| 11. Rank (R2/R3)           | Apply confirmed weights; assess ±25% weight stability and guide diversity.                                         | Ranked table and stability report.   |
| 12. Deliver                | Provide ranked candidates, alternatives, evidence, provenance, limitations, and validation plan.                    | Complete typed bundle.               |

## Expected Output

Fresh run directory containing `candidate_pool.csv`, `ranked_candidates.csv`, `off_target_summary.csv`, `coding_region_coverage.csv`, `gate_log.json`, `ranking_stability.json`, `provenance.json`, and `report.md`. Include spacer/PAM, coordinates, scores by dimension, gate decisions, evidence tier, and next-evidence recommendation.

## Constraints

Human gene knockout only unless separately reviewed. Genome assembly and transcript versions cannot transfer silently. Pathogen, pest, and plant applications require separate review. Computational scope only; licensing restrictions apply to redistribution.

## Important Instructions

Report multiple candidates and transcript coverage. Do not call one guide “the best” without showing alternatives and dimension-level evidence. Distinguish guide activity, predicted disruption, and experimentally demonstrated knockout. Benchmark results must be explicitly sourced; do not infer experimental outcomes.

---
