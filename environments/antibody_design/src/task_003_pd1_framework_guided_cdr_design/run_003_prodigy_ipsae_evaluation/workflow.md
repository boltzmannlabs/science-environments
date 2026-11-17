# Workflow — run_003_prodigy_ipsae_evaluation

Task: `task_003_pd1_framework_guided_cdr_design`.

## Objective and inputs

Quantify interface quality of run_002_agcdr_antibmpnn's 6 Boltz2 models (5 candidates + H965 control) with Prodigy (predicted binding affinity, KD) and ipSAE (interface PAE score) under Boltzmann tooling

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S1_prodigy_per_model | Prodigy binding-affinity prediction on each of the 12 PD1:VH / PD1:VL models | Prodigy (Binding Affinity) (boltzmann) |
| S2_ipsae_interface_scoring | ipSAE interface score on models+PAE bundle | ipsae-protein (ipSAE Generation) (boltzmann) |

## Configuration and results

[run.json](../../../results/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
