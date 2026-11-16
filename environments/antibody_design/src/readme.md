# Antibody Design Source

Source packages retain the methods, code, prepared inputs and execution records associated with the completed runs in this collection. Each package is organized as `src/<task_id>/<run_id>/`, using the same identifiers as its agent settings and scientific results.

## Directory structure

```text
src/
├── readme.md
└── <task_id>/
    └── <run_id>/
        ├── workflow.md
        ├── run.yaml
        ├── code/
        ├── inputs/
        │   ├── saved_artifacts.csv
        │   └── execution_records/
        │       ├── full_config.json
        │       ├── tool_details.json
        │       ├── run_files.csv
        │       └── observable_events.jsonl
        └── logs/
            ├── agent_scientist_log.md
            └── execution_summary.md
```

| File or directory | Purpose |
| --- | --- |
| `workflow.md` | Method description, input preparation, constraints, stages, tool roles and selection criteria. |
| `run.yaml` | Task/run identity, recorded state, lineage, configuration paths and artifact-manifest metadata. |
| `code/` | Preparation, execution, analysis and result-processing code associated with the run. |
| `inputs/` | Original and prepared scientific inputs, mappings, controls, saved requests and supporting records. |
| `inputs/saved_artifacts.csv` | Package inventory with file paths, roles, sizes and SHA-256 hashes. |
| `inputs/execution_records/full_config.json` | Original configuration preserved as a provenance snapshot. |
| `inputs/execution_records/tool_details.json` | Detailed tool sources, inputs, settings and recorded output information. |
| `inputs/execution_records/run_files.csv` | Inventory of scientific inputs, code and results. |
| `inputs/execution_records/observable_events.jsonl` | Structured observable execution events. |

Input filenames and additional subdirectories reflect the material used by the calculation. Supporting historical records, where included, are stored under `inputs/execution_records/`.

## The two log files

Each `logs/` directory contains exactly two Markdown files:

| File | Contents |
| --- | --- |
| `agent_scientist_log.md` | Chronological observable activity, tool requests, returned information, progress and recorded decisions. |
| `execution_summary.md` | A readable summary of preparation, tool use, generated outputs, counts and selection decisions. |

## Related configuration and results

The Agent-Scientist settings are stored in `configs/<task_id>/<run_id>.json`. Its five keys describe delegation, model, version, token usage and time budget.

The scientific record is `results/<task_id>/<run_id>/run.json`. It records preparation, ordered stages and each tool's source, supplied inputs, parameter values and outputs. `@src/` and `@results/` resolve against its declared source and result paths. `value_ref` points to an exact detailed value in `tool_details.json`, and `by_record` records differences between related calls.

Scientific reports, candidate tables, sequences, metrics and native outputs are described in the [results guide](../results/README.md). The [task guide](../tasks/README.md) and [environment specification](../ENVIRONMENT_SPEC.md) explain the surrounding conventions.
