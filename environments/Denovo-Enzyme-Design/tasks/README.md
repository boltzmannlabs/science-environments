# De novo enzyme-design tasks

This directory contains stable scientific task definitions. Each task has a unique `TASK-###` identifier, a descriptive directory, and a standard `task.md` definition. Execution records and outputs belong under `runs/` and `results/`, not in task directories.

## Task catalogue

| Task | Objective | Benchmark definition |
| --- | --- | --- |
| [TASK-001 — RFdiffusion2 retroaldolase](TASK-001-rfdiffusion2-retroaldolase/task.md) | Design and assess retroaldolase candidates around the supplied active-site motif. | [TASK-001](../benchmark/definitions/TASK-001.md) |
| [TASK-002 — RFdiffusion2 cysteine hydrolase](TASK-002-rfdiffusion2-cysteine-hydrolase/task.md) | Design and assess cysteine-hydrolase candidates. | [TASK-002](../benchmark/definitions/TASK-002.md) |
| [TASK-003 — Serine hydrolases](TASK-003-serine-hydrolases/task.md) | Design and assess serine-hydrolase candidates. | [TASK-003](../benchmark/definitions/TASK-003.md) |
| [TASK-004 — Riff-Diff retroaldolases](TASK-004-riff-diff-retroaldolases/task.md) | Scaffold and assess retroaldolase catalytic arrays. | [TASK-004](../benchmark/definitions/TASK-004.md) |
| [TASK-005 — Riff-Diff MBHases](TASK-005-riff-diff-mbhases/task.md) | Scaffold and assess Morita–Baylis–Hillmanase catalytic arrays. | [TASK-005](../benchmark/definitions/TASK-005.md) |
| [TASK-006 — Kemp eliminases](TASK-006-kemp-eliminases/task.md) | Assess substrate retention, productive orientation and reaction profiles. | [TASK-006](../benchmark/definitions/TASK-006.md) |
| [TASK-007 — Kemp QM/MM](TASK-007-kemp-qmmm/task.md) | Assess Kemp-elimination reaction free-energy surfaces. | [TASK-007](../benchmark/definitions/TASK-007.md) |

## Execution organization

For every execution, use the same stable task identifier throughout:

```text
runs/<task-id>/<run-id>/
results/<task-id>/<run-id>/
```

The task defines what must be done. Shared and task-specific configuration defines how it is done. A run records an execution, and its corresponding result directory stores the produced evidence and outputs.

Filenames listed in a task's expected-output section are logical output names. Newly generated scientific artifacts must use the repository's mandatory artifact filename convention, with the logical and stored names connected in result provenance.

Use the [environment specification](../ENVIRONMENT_SPEC.md), [model and tool inventory](../MODELS_AND_TOOLS.md), [runtime contracts](../src/CONTRACTS.md), and root repository contribution guidance when preparing a run.
