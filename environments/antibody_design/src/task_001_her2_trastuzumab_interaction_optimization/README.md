# Task 001 source package

## Independent benchmark audit

Run: `runs/20261111_ref15_benchmark_audit/`.

- [Actual audit execution](runs/20261111_ref15_benchmark_audit/execution.md)
- [Audit provenance](runs/20261111_ref15_benchmark_audit/provenance.json)
- [Current benchmark report](../../results/task_001_her2_trastuzumab_interaction_optimization/20261111_ref15_benchmark_audit/report.md)

This run audits the existing five designs only, preserves the historical generation run, and does not claim missing Amber/PyRosetta calculations were executed. Its exact code, model hashes and settings are retained in the run's `configs/`.

Task: `task_001_her2_trastuzumab_interaction_optimization`
Target: human HER2 extracellular domain
Reference: trastuzumab Fab/HER2 PDB 1N8Z
Run record: `runs/20261110_antibmpnn_her2_prodigy/`

This folder is the source-side record for the executed AntiBMPNN all-CDR workflow.
It now follows the source-package layout used by the other antibody-design tasks.

## Package layout

```text
src/task_001_her2_trastuzumab_interaction_optimization/
├── README.md
├── approaches.md
├── workflow.md
├── WORKFLOW.md                 # detailed prior workflow snapshot
├── SOURCES.md                  # detailed paths and provenance
├── code/                       # runnable/local analysis scripts
├── inputs/                     # reference and prepared input records
├── configs/                    # effective workflow settings
├── sources/                    # source manifests and benchmark pointers
└── runs/20261110_antibmpnn_her2_prodigy/
    ├── execution.md
    ├── provenance.json
    ├── inputs/
    ├── configs/
    └── logs/
```

Scientific outputs remain in:

```text
results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/
```

The original execution additionally recorded this working-bundle location (historical execution-workspace path):

```text
science_env_results/her2_results/
```

## Counts and status

- AntiBMPNN generated 20 paired VH/VL candidates.
- All 20 passed framework and disulfide-preservation filtering.
- Five candidates were shortlisted: AB_13, AB_05, AB_20, AB_08 and AB_04.
- ProDIGy and clash analysis were completed for the reference and all five candidates.
- Candidate Boltz2 signed downloads failed after the 300-second URL lifetime; they are not treated as completed candidate structures.
- REF15/Rosetta was unavailable and was not fabricated.

## Canonical source and results

- [Recorded execution](runs/20261110_antibmpnn_her2_prodigy/execution.md)
- [Execution provenance](runs/20261110_antibmpnn_her2_prodigy/provenance.json)
- [Scientific report](../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/report.md)

Scientific artifacts are stored in the matching results run. Historical execution records are retained under the source run's `runs/20261110_antibmpnn_her2_prodigy/logs/packaging_history/`.

## Transferred package records

[Run register](runs.csv) · [Historical tool inventory](tool_catalog.json) · [Approaches](approaches.md) · [Workflow](workflow.md) · [Scientific results](../../results/task_001_her2_trastuzumab_interaction_optimization/20261111_ref15_benchmark_audit/report.md).

Run snapshots are retrospective records. Original absolute workspace paths and code hashes identify the historical execution; they are not a claim that this checkout can execute without dependencies or path configuration. See [shared dependency and transfer notes](../shared/README.md).
