# Workflow — run_002_agcdr_antibmpnn

Task: `task_003_pd1_framework_guided_cdr_design`.

## Objective and inputs

Diversify CDR backbones on the fixed framework (agcdr_diff), redesign CDR sequences on each backbone (AntiBMPNN), enforce frozen gates, select 5 diverse candidates + H965 control, screen with Boltz2 and property predictors

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S1_backbone_diversification | Sample CDR backbone conformations with framework+antigen preserved | agcdr_diff (Antibody RFD3) (boltzmann) |
| S2_antibmpnn_on_backbones | Design CDR sequences on each diversified backbone | AntiBMPNN (boltzmann) |
| S3_selection | Select 5 diverse candidates for screening (frozen rule) | select_screening.py (open_source) |
| S4_boltz2_screening | Complex plausibility per selected candidate + H965 control | Boltz2 (boltzmann) |
| S5_properties | Thermal stability, solubility, CDR prediction on 5 candidates + H965 | Antibody_Prediction (AB_PROP) (boltzmann) |

## Configuration and results

[run.json](../../../results/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
