# Results — task-specific artifacts and evaluation records

Structure: `results/00N_application/Run-ID/`, parallel to `tasks/` and `benchmark/`.
Matching Run-2_2026-11-12 IDs connect result artifacts, confirmed example inputs,
benchmark status and provenance for all 13 tasks, following the sibling
Gene-Silencing-RNA-Design layout. Each run record carries `00_inputs/requirement_brief.json`
(hashed brief), `provenance.json`, `artifacts/` and a `REPORT.md`.

Historical example outputs are copied, not rerun during integration. Fresh scientific
model evaluations were executed in the source workspace and are published in the
[completed-only benchmark registry](../benchmark/BENCHMARK_RUNS.md). No full application
or experimental validation; best_design=null. Draft gates remain draft. The
pre-reorganization campaign report and coverage matrix are preserved in
[execution_history](../execution_history/before_completed_only_20261112T061830Z/benchmark/000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md).

| Task | Evidence status | Result | Historical benchmark (archived) |
| --- | --- | --- | --- |
| 001 general | SHARED_COMPONENT_BENCHMARKS | [Report](001_general/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/001_general-routing/Run-3_2026-11-12/README.md) |
| 002 knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION | [Report](002_knockout_gene_disruption/Run-2_2026-11-12/REPORT.md) + [executed Run1](002_knockout_gene_disruption/Run1_20261110/run_record_stage1.json) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/002_knockout/Run-3_2026-11-12/README.md) |
| 003 therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY | [Report](003_therapeutic_in_vivo_editing/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/003_therapeutic-in-vivo/Run-3_2026-11-12/README.md) |
| 004 variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS | [Report](004_variant_correction_precision_repair/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/004_variant-correction/Run-3_2026-11-12/README.md) |
| 005 base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST | [Report](005_base_editing/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/005_base-editing/Run-3_2026-11-12/README.md) |
| 006 prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS | [Report](006_prime_editing/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/006_prime-editing/Run-3_2026-11-12/README.md) |
| 007 crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY | [Report](007_crispr_regulation/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/007_regulation/Run-3_2026-11-12/README.md) |
| 008 epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT | [Report](008_epigenome_editing/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/008_epigenome-editing/Run-3_2026-11-12/README.md) |
| 009 rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION | [Report](009_rna_targeting_cas13/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/009_rna-targeting-cas13/Run-3_2026-11-12/README.md) |
| 010 diagnostics_pathogen | REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY | [Report](010_diagnostics_pathogen/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/010_diagnostics/Run-3_2026-11-12/README.md) |
| 011 library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION | [Report](011_library_screen_design/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/011_library-screen-design/Run-3_2026-11-12/README.md) |
| 012 plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY (task inactive) | [Report](012_plant_genome_editing/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/012_plant-editing/Run-3_2026-11-12/README.md) |
| 013 microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY | [Report](013_microbial_crispr_design/Run-2_2026-11-12/REPORT.md) | [Run-3](../execution_history/before_completed_only_20261112T061830Z/benchmark/013_microbial/Run-3_2026-11-12/README.md) |

Evidence-status labels are the same ones carried in each task's Status line; see
[tasks/README.md](../tasks/README.md) for the mapping to active completed benchmarks.
All copied scientific files have source and destination hashes in the run-level
provenance records and the campaign-level [PROVENANCE.json](../execution_history/before_completed_only_20261112T061830Z/benchmark/000_Protocol-reproduction/Run-2_2026-11-12/PROVENANCE.json).
Large data, checkpoints and environments remain external, indexed by absolute source
handles; this is not a self-contained portable distribution. Prior runs remain
unchanged.
