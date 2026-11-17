# Workflow — run_002_diffab_local

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`.

## Objective and inputs

DiffAb in-context CDR-H3 co-design comparator for 5bv7

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| historical_stage_1 | DiffAb in-context H3 generation | DiffAb (open_source); graft_diffab.py (open_source) |
| historical_stage_2 | freeze ranking | local python (open_source) |
| historical_stage_3 | scoring | AbFlow evaluator (open_source) |
| historical_stage_4 | packaging | local python (open_source) |

## Configuration and results

[run.json](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_002_diffab_local/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_002_diffab_local/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
