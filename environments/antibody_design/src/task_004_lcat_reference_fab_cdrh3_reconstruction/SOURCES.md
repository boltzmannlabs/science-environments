# Task 004 sources and provenance

## Task definition

- Task specification: `tasks/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md`.
- Benchmark task record: `benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md`.

## Biological and structural reference

- PDB reference used: `5BV7`.
- Local copied input for the run record: `runs/20261111_lcat_cdrh3_multworkflow/inputs/reference_5BV7.pdb`.
- Antibody and antigen preparation files originated from `/home/boltzmann10/.sci/cache/scratch/lcat_task/` and are retained in the scientific results/evidence package where applicable.
- Reference VH/VL input: `runs/20261111_lcat_cdrh3_multworkflow/inputs/reference_vhvl.fasta`.
- Native CDR-H3: `AREGAAVRSFYYSYYGMDV`.

## Boltzmann-platform workflows

The following platform tools were used or attempted, as recorded in the results report and execution record:

- AgCDR-Diff: target-aware CDR-H3 backbone generation.
- AntiBMPNN: sequence design on generated antibody backbones.
- CDR_Generator/EvoDiff: sequence-only HCDR3 generation.
- IG-Design: attempted; failed with internal `KeyError: 'aa_regions'`.
- Epitope AbGen: attempted/pending; no output produced.

The platform submission payloads and remote job logs were not saved as local Python source files. This package therefore records the platform tool names, stage, counts, status and resulting artifact paths without inventing unavailable commands or parameters.

## Open-source comparison workflow

- ProteinMPNN: prior fixed-framework sequence design; retained as the open-source sequence baseline.
- Boltz2: prior structure prediction of the top three ProteinMPNN variants.
- NumPy/Python analyses: RMSD, TM-score, AAR/CAAR, interface contacts and developability calculations.

## Local source-code origin

The Boltzmann-side analysis and preparation scripts were recovered from:

`/home/boltzmann10/.sci/cache/scratch/lcat_task/`

The prior open-source task scripts were recovered from:

`src/task_004_lcat_reference_fab_cdrh3_reconstruction/`

All copied source files are under this package's `code/` directory. Their SHA-256 values are recorded in `runs/20261111_lcat_cdrh3_multworkflow/inputs/sha256sums.txt`.

## Benchmark source

Published aggregate comparison values are preserved in:

- `results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/evidence/metrics.json`.
- `results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/benchmark_comparison.csv`.

The results report identifies the benchmark as the AbFlow KDD 2026 60-case RAbD aggregate and records the RMSD-definition discrepancy and single-case comparability limitation.

## Result artifact sources

- AgCDR-Diff generated PDBs: `results/.../structures/generated_sample_*.pdb`.
- ProteinMPNN/Boltz2 candidate structures: `results/.../structures/task004_sample*_complex.pdb`.
- Per-sequence AAR: `results/.../evidence/antibmpnn_aar.json` and `cdr_generator_aar.json`.
- Structural metrics: `results/.../evidence/agcdr_rmsd_correct.json` and prior `task004_struct_metrics.json`.
- Interface metrics: `results/.../evidence/interface_contacts.json`.
- Developability metrics: `results/.../evidence/developability_cdr_gen.json`.

## Identity reconciliation

The authoritative task definition and PDB 5BV7 header identify the target as human LCAT (L4F/N5D). Any DENV-2 wording found in inherited descriptions is a stale identity conflict and is not used for relabeling.
