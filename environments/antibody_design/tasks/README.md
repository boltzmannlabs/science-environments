# Antibody Design Tasks

Task definitions describe the scientific objective, starting information, design constraints, evaluation requirements and expected deliverables. The current collection is stored under [monoclonal_antibody_design/](monoclonal_antibody_design/README.md).

## Directory structure

```text
tasks/
├── README.md
└── monoclonal_antibody_design/
    ├── README.md
    └── <task_id>.md
```

| Location | Contents |
| --- | --- |
| [monoclonal_antibody_design/README.md](monoclonal_antibody_design/README.md) | Task catalog and links to matching benchmark references. |
| `monoclonal_antibody_design/<task_id>.md` | Target and antibody context, supplied inputs, editable/protected regions, objective, evaluation endpoints and output requirements. |

The task filename supplies the `<task_id>` used throughout the collection. Its reference document is `benchmark/monoclonal_antibody_design/<task_id>/reference.md`. Related source, agent-setting and result directories retain that same identifier; `<run_id>` identifies an individual recorded calculation within the task.

See the [benchmark guide](../benchmark/README.md) for reference and comparison documents, the [source guide](../src/readme.md) for methods and inputs, and the [results guide](../results/README.md) for scientific outputs.
