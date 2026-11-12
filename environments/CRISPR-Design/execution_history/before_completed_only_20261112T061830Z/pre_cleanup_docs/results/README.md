# Results — task-specific artifacts and evaluation records

Structure: results/00N_application/Run-ID/, parallel to tasks/ and benchmark/. Matching Run-2_2026-11-12 IDs connect result artifacts, confirmed example inputs, benchmark status and provenance for all 13 tasks, following the sibling Gene-Silencing-RNA-Design layout.

Historical example outputs are copied, not rerun during integration. Fresh scientific model evaluations were executed in the source workspace and are separately labeled. No full application or experimental validation; best_design=null. Draft gates remain draft.

Start with the [campaign report](../benchmark/000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md) and [coverage matrix](../benchmark/000_Protocol-reproduction/Run-2_2026-11-12/modality_performance_coverage_matrix.csv).

| Task | Evidence status | Result | Benchmark |
| --- | --- | --- | --- |
| 001 general | SHARED_COMPONENT_BENCHMARKS | [Report](../results/001_general/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/001_general-routing/Run-2_2026-11-12/README.md) |
| 002 knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION | [Report](../results/002_knockout_gene_disruption/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/002_knockout/Run-2_2026-11-12/README.md) |
| 003 therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY | [Report](../results/003_therapeutic_in_vivo_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/003_therapeutic-in-vivo/Run-2_2026-11-12/README.md) |
| 004 variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS | [Report](../results/004_variant_correction_precision_repair/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/004_variant-correction/Run-2_2026-11-12/README.md) |
| 005 base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST | [Report](../results/005_base_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/005_base-editing/Run-2_2026-11-12/README.md) |
| 006 prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS | [Report](../results/006_prime_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/006_prime-editing/Run-2_2026-11-12/README.md) |
| 007 crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY | [Report](../results/007_crispr_regulation/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/007_regulation/Run-2_2026-11-12/README.md) |
| 008 epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT | [Report](../results/008_epigenome_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/008_epigenome-editing/Run-2_2026-11-12/README.md) |
| 009 rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION | [Report](../results/009_rna_targeting_cas13/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/009_rna-targeting-cas13/Run-2_2026-11-12/README.md) |
| 010 diagnostics_pathogen | REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY | [Report](../results/010_diagnostics_pathogen/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/010_diagnostics/Run-2_2026-11-12/README.md) |
| 011 library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION | [Report](../results/011_library_screen_design/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/011_library-screen-design/Run-2_2026-11-12/README.md) |
| 012 plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY | [Report](../results/012_plant_genome_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/012_plant-editing/Run-2_2026-11-12/README.md) |
| 013 microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY | [Report](../results/013_microbial_crispr_design/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/013_microbial/Run-2_2026-11-12/README.md) |

All copied scientific files have source and destination hashes in [PROVENANCE.json](../benchmark/000_Protocol-reproduction/Run-2_2026-11-12/PROVENANCE.json). Large data, checkpoints and environments remain external, indexed by absolute source handles; this is not a self-contained portable distribution. Prior runs remain unchanged.
