# Workflow — run_001_abflow_h3_reconstruction

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`.

## Objective and inputs

Antigen-conditioned CDR-H3 sequence/structure reconstruction for 5BV7 under the AbFlow RAbD benchmark protocol

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| historical_stage_1 | input masking + reference sealing | build_run.py (open_source) |
| historical_stage_2 | CDR-H3 co-design generation | AbFlow (open_source) |
| historical_stage_3 | freeze rankings before native scoring | freeze_rankings.py (open_source) |
| historical_stage_4 | native-reference evaluation | AbFlow evaluator (open_source) |
| historical_stage_5 | packaging + benchmark comparison | package_results.py (open_source) |

## Configuration and results

[run.json](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_001_abflow_h3_reconstruction/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_001_abflow_h3_reconstruction/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.

## Saved input format

`inputs/masked_input_5bv7_x32.json` retains AbFlow's line-delimited dataset format: 32 JSON records, one per line. The filename and input bytes match the saved generation input.
