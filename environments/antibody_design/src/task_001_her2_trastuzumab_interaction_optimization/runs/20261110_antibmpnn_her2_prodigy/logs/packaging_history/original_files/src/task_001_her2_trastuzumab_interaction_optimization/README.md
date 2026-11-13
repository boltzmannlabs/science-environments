# Task 001 source package

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
├── outputs/                    # retained property outputs
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

The task-spec bundle is also retained in:

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
