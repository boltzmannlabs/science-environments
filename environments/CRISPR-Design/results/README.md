# Results — task records and benchmark executions

Task records use `results/00N_<application>/Run-<number>_<YYYY-MM-DD>/`.
All 13 task records retain `Run-2_2026-11-12`; the first knockout execution is
normalized to `Run-1_2026-11-10`. Campaign numbers are preserved, not reassigned
per task. See [history and evidence availability](HISTORY.md) for the full mapping.

Each Run-2 record includes `REPORT.md`, `provenance.json`, the actual
`00_inputs/requirement_brief.json`, and `large_artifact_index.json`. These lightweight
records are eligible for Git tracking. Raw `artifacts/` and reference data remain
local and ignored; the source handles in provenance identify their origin.
Historical examples were copied, not rerun during this reorganization.

| Task | Evidence status | Result |
| --- | --- | --- |
| 001 general | SHARED_COMPONENT_BENCHMARKS | [Report](001_general/Run-2_2026-11-12/REPORT.md) |
| 002 knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION | [Report](002_knockout_gene_disruption/Run-2_2026-11-12/REPORT.md) |
| 003 therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY | [Report](003_therapeutic_in_vivo_editing/Run-2_2026-11-12/REPORT.md) |
| 004 variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS | [Report](004_variant_correction_precision_repair/Run-2_2026-11-12/REPORT.md) |
| 005 base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST | [Report](005_base_editing/Run-2_2026-11-12/REPORT.md) |
| 006 prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS | [Report](006_prime_editing/Run-2_2026-11-12/REPORT.md) |
| 007 crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY | [Report](007_crispr_regulation/Run-2_2026-11-12/REPORT.md) |
| 008 epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT | [Report](008_epigenome_editing/Run-2_2026-11-12/REPORT.md) |
| 009 rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION | [Report](009_rna_targeting_cas13/Run-2_2026-11-12/REPORT.md) |
| 010 diagnostics_pathogen | REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY | [Report](010_diagnostics_pathogen/Run-2_2026-11-12/REPORT.md) |
| 011 library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION | [Report](011_library_screen_design/Run-2_2026-11-12/REPORT.md) |
| 012 plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY | [Report](012_plant_genome_editing/Run-2_2026-11-12/REPORT.md) |
| 013 microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY | [Report](013_microbial_crispr_design/Run-2_2026-11-12/REPORT.md) |

The first knockout run has a retained [stage-1 record](002_knockout_gene_disruption/Run-1_2026-11-10/run_record_stage1.json)
and input snapshots. Its large stage-1 artifacts are local; stage-2 outputs are
absent. See [runtime contracts](../src/CONTRACTS.md) for validation limitations.

Seven completed benchmark execution packages live under
[benchmarks/](benchmarks/README.md), with definitions and evaluation criteria in
[benchmark/](../benchmark/README.md). The earlier Run-2/Run-3 comparison archive is
[unavailable in this checkout](HISTORY.md).

No full application or experimental validation is established; `best_design=null`
and draft gates remain draft. [Task evidence](../tasks/README.md) distinguishes
shared benchmarks, component tests, replays and blocked endpoints.
