# Workflow — run_003_antibmpnn_native_backbone

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`.

## Objective and inputs

Fixed-backbone CDR-H3 sequence design via Boltzmann AntiBMPNN

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| historical_stage_1 | input preparation | local python (open_source) |
| historical_stage_2 | AntiBMPNN design (Boltzmann) | AntiBMPNN (boltzmann) |
| historical_stage_3 | freeze | local python (open_source) |
| historical_stage_4 | scoring | AbFlow evaluator (open_source) |
| historical_stage_5 | packaging | local python (open_source) |

## Configuration and results

[run.json](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
