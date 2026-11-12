# Antibody Design Source

This directory contains workflow planning, implementation and execution records for antibody design and evaluation. It documents the approaches explored, the methods selected and the work actually performed. Scientific outputs are stored in the corresponding `results/` package.

## Directory Structure

```text
src/
├── readme.md
├── shared/
│   ├── reusable_helpers.py
│   └── validation/
└── <task_id>/
    ├── README.md
    ├── tool_catalog.json
    ├── approaches.md
    ├── workflow.md
    ├── runs.csv
    ├── code/
    └── runs/
        ├── <run_id_A>/
        │   ├── execution.md
        │   ├── inputs/
        │   ├── configs/
        │   │   └── workflow_snapshot.md
        │   ├── provenance.json
        │   └── logs/
        └── <run_id_B>/
```

The tree defines the shared organization. Helper filenames depend on the implementation; each run retains the inputs, configurations and records applicable to its execution. Additional source references and historical snapshots may be retained with their purpose clearly identified.

## File Contents

| File or directory | Purpose |
| --- | --- |
| `shared/` | Reusable preparation, orchestration, evaluation and packaging helpers, together with dependency and transfer records where applicable. |
| `shared/validation/` | Package-wide organization and integrity reports. These checks are separate from scientific evaluation. |
| `<task_id>/` | Groups planning, implementation and executions under the exact task identifier. |
| Task `README.md` | Identifies source entry points, dependencies, workflow records and corresponding scientific reports. |
| `tool_catalog.json` | Records tool identifiers, versions, capabilities, input/output contracts and resource requirements. Distinguishes verified current contracts from historical inventories. |
| `approaches.md` | Describes explored approaches, their suitability, strengths, limitations and selection rationale. |
| `workflow.md` | Defines the selected workflows, stage dependencies, constraints, budgets, evaluation requirements, shortlisting strategy and stopping conditions. |
| `runs.csv` | Registers execution attempts, run IDs, workflow scope, parent relationships, statuses, scientific coverage and result locations. |
| `code/` | Contains the preparation, execution and analysis implementations used, with entry points, dependencies and revision or checksum information. |
| Run `execution.md` | Records the work actually performed, stage outcomes, tools used, deviations, failures and links to scientific outputs. |
| Run `inputs/` | Preserves exact supplied and prepared inputs, including sequences, structures, masks, mappings and evaluation datasets. Held-out references remain separate from generation inputs. |
| Run `configs/` | Stores effective tool settings and the workflow/code snapshot used by the execution, including runtime overrides. |
| Run `provenance.json` | Records task/run identities, lineage, tools and model versions, commands or job IDs, parameters, seeds, timestamps, statuses, counts, artifact hashes and path bases. |
| Run `logs/` | Retains execution logs, stdout/stderr, warnings, failure evidence and clearly labelled historical records. |

## Workflow Planning and Execution

The agent determines workflow count, methods, execution order and shortlisting strategy from the task requirements, available capabilities and resource budget. Planning documents describe the intended approach; execution records describe what occurred.

Each independent workflow execution, repeat or retry receives a distinct run ID. Follow-up work records its parent run and identifies reused inputs or artifacts. Considered approaches remain in planning records. An unsuccessful attempt retains its status and available evidence without claiming completed scientific stages or creating placeholder results.

Task-level plans may evolve. Each run preserves the configuration and code revision it used. Clearly label retrospective snapshots and recovered records, and preserve the original identity of historical workflow bundles.

## Reproducibility and Results Links

Use matching task and run IDs across source and results:

```text
src/<task_id>/runs/<run_id>/
results/<task_id>/<run_id>/
```

Link each execution record to its scientific report and link the report back to the execution record. Declare path bases, input sources, software/model versions and artifact hashes. External dependencies require source/version information and any restoration or path configuration needed for reproduction.

Store generated sequences, predictions, evaluated structures, measurements and benchmark comparisons in `results/`. Preserve commands, configurations and execution logs here. Report execution status, scientific coverage and packaging validation separately.

See the [environment specification](../ENVIRONMENT_SPEC.md) for the shared execution contract, the [results guide](../results/README.md) for scientific output definitions and [shared documentation](shared/README.md) for implementation and dependency records.
