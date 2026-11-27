# Enzyme Variant Optimization

Scientific assignments and recorded workflows for six enzyme case studies. Agent-alone and specialist-assisted executions retain their own models, tools, sequences, measurements and reviews. A completed computational workflow can find no qualifying candidate.

## Structure

```text
enzyme-variant-optimization/
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── tasks/<task-id>/task.md
├── config/tasks/<task-id>/<config-id>.json
├── runs/<task-id>/<native-logical-run-id>/
├── results/<task-id>/<same-run-id>/
├── benchmark/
├── scripts/
└── src/
```

| Location | Contents |
|---|---|
| [Tasks](tasks/README.md) | Stable assignments, scientific constraints and acceptance criteria. |
| [Configuration](config/README.md) | Recovered or frozen task settings, with unknown historical fields explicit. |
| [Runs](runs/README.md) | Each independent execution, native continuation identity, inputs, usage, calls and status. |
| [Results](results/README.md) | Per-run workflow, reports, sequences, predictions and specialist reviews. |
| [Benchmarks](benchmark/README.md) | Published references and explicitly identified historical comparisons. |
| [Source](src/README.md) | Retained implementation and environment coordinator skill. |
| [Scripts](scripts/README.md) | Native launch preparation, evaluation and offline report tools. |

## Recorded workflows

- [task_001_rml_stability](results/task_001_rml_stability/README.md)
- [task_002_leh_stability](results/task_002_leh_stability/README.md)
- [task_003_bla_high_temperature](results/task_003_bla_high_temperature/README.md)
- [task_004_athol1_substrate](results/task_004_athol1_substrate/README.md)
- [task_005_sun_leh_pythia](results/task_005_sun_leh_pythia/README.md)
- [task_006_zhang_hydrolases](results/task_006_zhang_hydrolases/README.md)

The registry includes 23 native workflow starts: ten historical campaigns, nine later Codex/DiscoveryRSI starts (including interrupted preparation), and four HY4 assisted executions. Native continuation sessions stay within the same logical run. Controlled software fixtures are excluded. All six tasks have specialist-assisted evidence; incomplete starts are never presented as complete scientific results.

## Execution

Read the [environment specification](ENVIRONMENT_SPEC.md), select a task, and supply explicit frozen settings to [launch_task.py](scripts/launch_task.py). Historical configuration summaries are incomplete where stated; they are not drop-in replay profiles. Use native SCI resume for an existing run and reconcile accepted or unknown jobs before any retry. MLDE remains excluded. No scientific job was replayed by this migration.

## Provenance and migration

[Migration notes](MIGRATION.md) and [path mapping](migration_map.json) preserve prior identifiers and evidence. Each result package links its run record and configuration. Large/private artifacts and complete native transcripts remain in retained private archives; public activity logs contain metadata only. Missing original settings or artifact naming components are reported, not invented. No empty tests directory is added; environment-owned validation is available through `python scripts/validate_run_records.py`.

Benchmark reports retain their documented legacy `benchmark/<task>/comparisions/` layout and historical agent-alone scope. They do not silently combine later model runs.
