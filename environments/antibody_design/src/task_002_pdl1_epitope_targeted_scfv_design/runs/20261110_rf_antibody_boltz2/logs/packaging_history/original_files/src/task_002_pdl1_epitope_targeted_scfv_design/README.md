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

Its main files are `report.md`, `candidates.csv`, `shortlist.csv`, `designed_sequences.fasta`, `structures/`, and `evidence/`. The former `src/outputs/` records were relocated into `evidence/raw/platform_outputs/`; the old source path is retained only as a historical relocation record.

## Count semantics

- 20 candidates were returned by the RF-Antibody generation output.
- 10 candidates were explicitly included in the retained local Boltz-2 batch.
- 5 candidates received Antibody_Prediction property analysis.
- 4 candidates are epitope-engaged recommendations; `rf0_d0` is a high-confidence off-epitope contrast.
- The epitope-abgen branch was submitted but produced no output and has no fabricated downstream artifacts.
