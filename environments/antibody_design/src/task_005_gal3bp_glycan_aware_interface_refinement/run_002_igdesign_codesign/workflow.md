# Workflow — run_002_igdesign_codesign

Task: `task_005_gal3bp_glycan_aware_interface_refinement`.

## Objective and inputs

glycan-aware interface refinement of BDBV-43-derived candidates on Gal-3BP E1-window; second design engine (antigen-conditioned LM codesign) beyond fixed-backbone AntiBMPNN

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S1_generation | Local IgDesign generation | IgDesign (open_source) |
| S2_sequence_checks | Recorded sequence/framework gates and candidate inventory | Saved stage analysis artifacts |
| S3_matched_prediction | Three completed AF2-Multimer candidate predictions | Multimer_Structure_Prediction (boltzmann) |
| S4_evaluation | Interface chemistry, predicted energy, glycan and model-persistence analyses | Saved stage analysis artifacts |

## Configuration and results

[run.json](../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
