# Workflow — run_002_rf_antibody

Task: `task_002_pdl1_epitope_targeted_scfv_design`.

## Objective and inputs

framework-conditioned, epitope-directed design of paired VH/VL candidates (scFv output) against human PD-L1 with H5/35TL as comparator only

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| W3_generation_and_evaluation | RF-Antibody generation, excluded outputs | rfdiffusion_proteinmpnn (boltzmann) |

## Configuration and results

[run.json](../../../results/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
