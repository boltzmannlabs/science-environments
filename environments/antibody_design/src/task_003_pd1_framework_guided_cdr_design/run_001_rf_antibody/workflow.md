# Workflow — run_001_rf_antibody

Task: `task_003_pd1_framework_guided_cdr_design`.

## Objective and inputs

Redesign the six CDRs on the fixed paper Table-1 humanized framework (IGHV3-23*01/IGKV1-5*01 + IGHJ4/IGKJ1) against the human PD-1 ligand-binding interface, using the staged 5GGS-derived Fv scaffold, and compare computational evidence with the published anti-PD-1-H965 design.

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S1_input_staging | Stage verified inputs (framework, PD-1 antigen, published panel, interface definition) | paper/supplement retrieval + parse_panel.py (open_source) |
| S2_design_rf_antibody | Generate CDR designs on the staged Fv scaffold | rfdiffusion_proteinmpnn (RF-Antibody) (boltzmann) |
| S3_gate_enforcement | Enforce frozen gates on RF-Antibody outputs | process_rf_align.py (open_source) |

## Configuration and results

[run.json](../../../results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
