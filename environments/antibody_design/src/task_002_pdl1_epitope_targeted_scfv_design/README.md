# Task 002 source package

This folder contains the source-side record for `task_002_pdl1_epitope_targeted_scfv_design`.

## Package layout

```text
src/task_002_pdl1_epitope_targeted_scfv_design/
├── README.md
├── approaches.md                 # workflows considered and selection rationale
├── workflow.md                   # executed stage graph and ranking rule
├── SOURCES.md                    # source, reference and tool provenance
├── workflow_design.md            # original planning snapshot
├── code/
│   ├── README.md
│   ├── boltz2_run_batch.sh       # executed local Boltz-2 batch
│   ├── analyze_interface.py      # executed interface analysis
│   ├── compute_novelty.py       # reproducible novelty analysis
│   └── rank_and_package.py       # reproducible ranking/package reconstruction
├── inputs/                       # prepared design inputs and one Boltz-2 example
├── source/                       # Germinal configs and source/reference sequences
└── runs/20261110_rf_antibody_boltz2/
    ├── execution.md              # actual run, deviations and status
    ├── provenance.json            # machine-readable run record
    ├── inputs/                    # copied exact run inputs and references
    ├── configs/                   # effective source configs and job manifest
    └── logs/                      # local Boltz logs and platform-log note
```

## Results link

The paired scientific package is:

`results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/`

Its main files are `report.md`, `candidates.csv`, `shortlist.csv`, `designed_sequences.fasta`, `../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/structures/`, and `../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/`. The former `src/outputs/` records were relocated into `../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/evidence/raw/platform_outputs/`; the old source path is retained only as a historical relocation record.

## Count semantics

- 20 candidates were returned by the RF-Antibody generation output.
- 10 candidates were explicitly included in the retained local Boltz-2 batch.
- 5 candidates received Antibody_Prediction property analysis.
- 4 candidates are epitope-engaged recommendations; `rf0_d0` is a high-confidence off-epitope contrast.
- The epitope-abgen branch was submitted but produced no output and has no fabricated downstream artifacts.

## Canonical source and results

- [Recorded execution](runs/20261110_rf_antibody_boltz2/execution.md)
- [Execution provenance](runs/20261110_rf_antibody_boltz2/provenance.json)
- [Scientific report](../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/report.md)

Scientific artifacts are stored in the matching results run. Historical execution records are retained under the source run's `runs/20261110_rf_antibody_boltz2/logs/packaging_history/`.

## Transferred package records

[Run register](runs.csv) · [Historical tool inventory](tool_catalog.json) · [Approaches](approaches.md) · [Workflow](workflow.md) · [Scientific results](../../results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/report.md).

Run snapshots are retrospective records. Original absolute workspace paths and code hashes identify the historical execution; they are not a claim that this checkout can execute without dependencies or path configuration. See [shared dependency and transfer notes](../shared/README.md).
