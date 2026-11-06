# Benchmark: PD-1: Framework-Guided CDR Design

**Task ID:** `task_003_pd1_framework_guided_cdr_design`

**Task:** [PD-1: Framework-Guided CDR Design](../../tasks/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md)

**Reviewed:** 2026-11-05

## Benchmark Scope

Framework-conditioned PD-1 antibody design with H965 as the published comparator. Screening-panel classification and sequence reconstruction are supplementary benchmark contexts, not individual candidate scores.

## Published Results

**Source:** [De novo design of epitope-specific antibodies via a structure-driven computational workflow](https://doi.org/10.1038/s41467-025-67361-9), Nature Communications, online December 2025, volume 17 (2026); [accessible text, Figures 5–6 and Supplementary Table 4](https://pmc.ncbi.nlm.nih.gov/articles/PMC12815924/).

| Published metric | Reported value | Scope and interpretation |
| --- | ---: | --- |
| PD-1 virtual-screening AUROC | **0.76** | Separate panel of 745 antibodies containing 27 positives. Higher is better. |
| PD-1 top-1% enrichment factor | **7.41** | Same screening panel; two positives among seven selected antibodies. |
| PD-1 designed-antibody discrimination AUROC | **0.95** | Design-campaign analysis; distinct from the 745-antibody screening benchmark. |
| Epitope-informed CDR-H3 amino-acid recovery | **0.317** | SAbDab-22-DesignAb aggregate, not H965-specific or PD-1-only. |
| Final H965 ipTM, designed-region confidence, PAE and DockQ | **Not verified** | No exact individual values established by the inspected evidence. |

The strongest reported AUROC above concerns the design campaign; it must not replace the separate virtual-screening AUROC. Use panel benchmarks only when reproducing their panel and evaluation definitions. Report individual new-candidate scores separately, and do not interpret recovery or classification performance as a binding-energy result.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| New design evidence | Verify framework input, permitted edits, epitope contacts and complex plausibility for each paired candidate. | Candidate-level numerical cutoffs require the supplied evaluation protocol. |
| AUROC and enrichment | Use the original labelled panel, score orientation and top-percentile rule. | A single candidate cannot reproduce the reported classification benchmark. |
| CDR recovery | Evaluate held-out native residues with the same mask and dataset definition. | The aggregate AAR is not an H965-specific binding metric. |
