# Workflow — run_001_antibmpnn_matched

Task: `task_001_her2_trastuzumab_interaction_optimization`.

## Objective and inputs

Reference-guided interaction optimization of trastuzumab Fv against HER2 ECD

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S0_prep | fetch/verify/split 1N8Z; build correctly numbered design input | stage0_fetch_verify.py (open_source); stage0b_fix_numbering.py (open_source) |
| S1_design | CDR-only fixed-backbone redesign of trastuzumab Fv | AntiBMPNN (boltzmann) |
| S2_verify | edit-mask verification, dedupe, candidate table | stage2_verify_mask.py (open_source) |
| S3_structure | matched Boltz2 complex prediction: reference + top-8 candidates | Boltz2 (boltzmann) |
| S4_affinity | Prodigy binding-affinity on Boltz2 structures (both records per construct) | Prodigy (boltzmann) |
| S5_evaluation | consolidated metrics + artifacts | stage4_extract_confidence.py (open_source); stage6_evaluate.py (open_source); clash scan (open_source); stage7_artifacts.py (open_source) |

## Configuration and results

[run.json](../../../results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
