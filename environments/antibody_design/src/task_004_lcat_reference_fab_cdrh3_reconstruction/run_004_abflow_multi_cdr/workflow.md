# Workflow — run_004_abflow_multi_cdr

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`.

## Objective and inputs

All-CDR sequence/structure co-design for 5bv7 as a declared separate evaluation track (paper Table 2 protocol)

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| historical_stage_1 | masking + reference sealing (inherited from run_001 S1) | build_run.py (open_source) |
| historical_stage_2 | all-CDR generation | AbFlow (open_source) |
| historical_stage_3 | freeze before scoring | freeze_rankings.py (open_source) |
| historical_stage_4 | native-reference scoring | AbFlow evaluator (open_source) |
| historical_stage_5 | packaging | local python (open_source) |

## Configuration and results

[run.json](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_004_abflow_multi_cdr/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_004_abflow_multi_cdr/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
