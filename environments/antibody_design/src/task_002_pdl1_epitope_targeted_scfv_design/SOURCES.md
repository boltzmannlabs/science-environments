# Task 002 sources and provenance

## Task definition

- Task specification: `tasks/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md`
- Benchmark specification and execution comparison: `benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md`

## Design source

- Germinal repository snapshot: `/home/boltzmann10/.sci/cache/scratch/germinal_repo`
- Repository source files copied into this task package:
  - `source/germinal_config.yaml`
  - `source/germinal_config_run_scfv_pdl1.yaml`
  - `source/germinal_config_target_pdl1.yaml`
- Generic parent framework: Germinal `pdbs/scfv.pdb`, represented locally by `inputs/framework_scfv_HL.pdb` and `source/framework_scfv.fasta`.
- Target construct: Germinal `pdbs/pdl1.pdb` chain A V-like domain, represented locally by `inputs/pdl1_vlike_A.pdb` and `source/pdl1_vlike.fasta`.

## Published/reference source

- Germinal paper: Nature Biotechnology, 2026, DOI `10.1038/s41587-026-03187-0`.
- Accessible manuscript: PMC article `PMC13366713`.
- H5 reference complex: PDB `35TL`, EMDB `EMD-77181`.
- H5 VH/VL sequences were retrieved from the 35TL polymer FASTA and retained as `source/h5_reference.fasta`. H5 was an evaluation reference, not a generation parent.

## Tool sources

- Boltzmann platform jobs are identified by their job name and doc_id in `runs/20261110_rf_antibody_boltz2/provenance.json` and `configs/platform_job_manifest.json`.
- Local open-source Boltz-2 was executed from the installed local environment using the command recorded in `code/boltz2_run_batch.sh`.
- Biopython was used for mmCIF/PDB parsing and coordinate-based interface analysis.
- StaBddG was inspected but not run because it requires a bound reference complex and predicts mutation delta-delta-G, not absolute binding of de novo candidates.

## Source/reference separation

The generic framework and PD-L1 V-like domain were design inputs. H5/35TL structures and sequences were evaluation-only references. Published Germinal metrics are not treated as measured properties of the newly designed candidates.
