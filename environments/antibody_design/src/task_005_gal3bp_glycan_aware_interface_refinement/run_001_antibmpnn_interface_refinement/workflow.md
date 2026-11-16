# Workflow — run_001_antibmpnn_interface_refinement

Task: `task_005_gal3bp_glycan_aware_interface_refinement`.

## Objective and inputs

Glycan-aware interface refinement benchmark task: refine/design BDBV-43-derived antibody interface against Gal-3BP (LGALS3BP, UniProt Q08380) following the published study's workflow shape (ref complex -> CDR redesign -> matched evaluation -> interface sampling), using verifiable public inputs

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| W1_ref_complex | W1_ref_complex | Boltz2 (boltzmann platform) (boltzmann); Multimer_Structure_Prediction (colabfold_multimer, AF2-Multimer v3) (boltzmann); interface_map.py, interface_chemistry.py, glycan_dsasa.py (skill script), Prodigy (conda base) (open_source) |
| W2_cdr_design | W2_cdr_design | AntiBMPNN (boltzmann platform) (boltzmann) |
| W3_candidate_eval | W3_candidate_eval | Multimer_Structure_Prediction (boltzmann); ANARCI (igdesign env) (open_source); glycan_dsasa.py (skill script, open_source) (open_source); candidate_persistence.py (local) (open_source) |
| W4_interface_sampling | W4_interface_sampling | w4_interface_sampling.py (local) (open_source); Protenix local (protenix_base_default_v1.0.0) (open_source); Boltz2 (aux evidence) (boltzmann) |

## Configuration and results

[run.json](../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/run.json) records each tool's supplied inputs, parameter values, execution source and output files. [report.md](../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/report.md) presents the performed methods, result tables and candidate highlights.

The source `logs/` folder contains the two execution records: [activity](logs/agent_scientist_log.md) and [execution summary](logs/execution_summary.md). Input hashes and the current artifact inventory are saved in `inputs/`.
