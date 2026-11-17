# Antibody Design

A scientific environment for antibody discovery, design, optimization and evaluation with Agent-Scientist. It combines explicit scientific tasks, task-specific benchmarks and a common structure for implementations, scripts, specialized skills and reproducible results.

The development scope covers **monoclonal, bispecific and multispecific antibodies**, including **de novo design and optimization of existing antibodies**. The current task collection is organized under monoclonal antibody design; the [environment specification](ENVIRONMENT_SPEC.md) defines the shared conventions.

## Scientific scope

| Area | Design focus |
| --- | --- |
| Monoclonal antibody design | Target-directed design, reference-guided refinement, epitope recognition and structural assessment. |
| Bispecific antibody design | Two binding specificities, assessed individually and in the assembled molecule. |
| Multispecific antibody design | Three or more binding specificities, including component compatibility and molecular architecture. |
| De novo design | Candidate discovery from a defined target and objective, with an optional framework or scaffold. |
| Antibody optimization | Interaction quality, specificity, humanization, developability and architecture within declared constraints. |
| Reconstruction and benchmarking | Controlled sequence-recovery, structural-agreement and task-defined endpoint comparisons. |

## Repository structure

```text
antibody_design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── MODELS_AND_TOOLS.md
├── status.md
├── tasks/
│   ├── README.md
│   └── monoclonal_antibody_design/
│       ├── README.md
│       └── <task_id>.md
├── benchmark/
│   ├── README.md
│   └── monoclonal_antibody_design/
│       ├── README.md
│       └── <task_id>/
├── configs/
│   └── <task_id>/<run_id>.json
├── src/
│   ├── readme.md
│   └── <task_id>/<run_id>/
├── results/
│   ├── README.md
│   ├── <task_id> — Results.md
│   └── <task_id>/<run_id>/
├── scripts/
├── skills/
└── tests/
```

| Location | Contents |
| --- | --- |
| [tasks/](tasks/README.md) | Scientific objectives, supplied inputs, design constraints and evaluation requirements. |
| [benchmark/](benchmark/README.md) | Task-matched reference documents, calculated comparisons and PNG figures. |
| [configs/](configs/) | Compact Agent-Scientist settings, organized by task and run ID. |
| [src/](src/readme.md) | Per-run methods, metadata, code, prepared inputs, supporting records and two Markdown logs. |
| [results/](results/README.md) | Per-run scientific configuration, reports, tables and native outputs, plus standalone task summaries. |
| [scripts/](scripts/readme.md) | Location for shared utilities; run-specific code is stored under `src/`. |
| [skills/](skills/readme.md) | Location for reusable agent instructions. |
| [tests/](tests/README.md) | Location for environment validation resources. |

## Finding the right files

Start with the [task catalog](tasks/monoclonal_antibody_design/README.md) and its matching [benchmark catalog](benchmark/monoclonal_antibody_design/README.md). A task uses the same `<task_id>` in every directory. For a recorded run, follow the same `<run_id>` across `configs/`, `src/` and `results/`.

`configs/<task_id>/<run_id>.json` stores the Agent-Scientist settings. `results/<task_id>/<run_id>/run.json` records scientific tool sources, inputs, parameters and outputs. The corresponding source directory explains the methods and preparation; the result report explains the calculated findings. Task-level `comparison.md` documents bring related results together with benchmark references and figures.

The [environment specification](ENVIRONMENT_SPEC.md) defines the directory and file conventions. [MODELS_AND_TOOLS.md](MODELS_AND_TOOLS.md) describes the model and tool landscape.
