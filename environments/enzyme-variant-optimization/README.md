# Enzyme Variant Optimization

[Task-specific benchmark reports](benchmark/README.md) contain predicted properties and ESM/Pythia scores, with published values and calculations in this work labeled separately.

An Agent-Scientist environment for improving an existing enzyme through actual tool-based generation, property screening, candidate-specific structural/chemical assessment, results-driven revision, re-evaluation and evidence review. Agent-alone and specialist-assisted runs follow the same scientific requirements. A completed workflow may find no supported improvement.

## Environment structure

```text
enzyme-variant-optimization/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── configs/
│   └── task_<id>_<case>/
│       ├── run_001_agent_alone.json
│       └── run_002_agent_with_specialist.json  # where executed
├── tasks/task_<id>_<case>.md
├── scripts/
├── src/
│   ├── evaluation.py
│   ├── benchmark_reports.py
│   ├── task_<id>_<case>/
│   └── shared/stability_predictions/
├── benchmark/
│   └── task_<id>/
│       ├── references.md
│       └── comparisions/benchmark_report.md  # available numerical results
└── results/
    └── task_<id>/
        ├── agent-alone/
        └── agent-with-specialist/  # four executed task groups
```

This naming pattern applies to all six tasks. There is no environment `tests/` directory. `comparisions/` uses the requested folder spelling. Hidden `.gitignore` rules protect local/private artifacts.

| Location | Information |
| --- | --- |
| [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) | Shared workflow stages, protected constraints, evidence, recovery, comparison protocol and completion criteria. |
| [STATUS.md](STATUS.md) | Implemented work, work in progress and future enhancements. |
| [MODELS_AND_TOOLS.md](MODELS_AND_TOOLS.md) | Required capabilities, method families, selection criteria and limitations. SCI discovery/contracts define current APIs. |
| [configs/](configs/README.md) | Compact actual-run records: specialist use, model/version, tokens and time budget. |
| [tasks/](tasks/README.md) | Numbered scientific assignments. |
| [scripts/](scripts/README.md) | Native launch preparation, resume instructions, offline evaluation and report generation. |
| [src/](src/README.md) | Actual agent-alone code and the retained offline evaluator. |
| [benchmark/](benchmark/README.md) | Published reference values and comparisons with agent-alone outputs. |
| [results/](results/README.md) | Agent-alone and specialist-assisted execution evidence. |

## Tasks and run configs

| ID | Case | Configuration |
| --- | --- | --- |
| `task_001_rml_stability` | [RML stability](tasks/task_001_rml_stability.md) | [Run configs](configs/task_001_rml_stability/) |
| `task_002_leh_stability` | [LEH stability](tasks/task_002_leh_stability.md) | [Run configs](configs/task_002_leh_stability/) |
| `task_003_bla_high_temperature` | [BLA high-temperature performance](tasks/task_003_bla_high_temperature.md) | [Run configs](configs/task_003_bla_high_temperature/) |
| `task_004_athol1_substrate` | [AtHOL1 substrate expansion](tasks/task_004_athol1_substrate.md) | [Run configs](configs/task_004_athol1_substrate/) |
| `task_005_sun_leh_pythia` | [Sun LEH / Pythia reproduction](tasks/task_005_sun_leh_pythia.md) | [Run configs](configs/task_005_sun_leh_pythia/) |
| `task_006_zhang_hydrolases` | [Zhang cellulase and β-glucanase reproduction](tasks/task_006_zhang_hydrolases.md) | [Run configs](configs/task_006_zhang_hydrolases/) |

Compact run configs follow the antibody-design format. BLA and AtHOL1 have agent-alone records only; the other four task groups also have assisted records. No unexecuted v1/v2 templates are included.

## Prerequisites and start

Use an available native SCI installation and access to the required scientific capabilities. Assisted runs additionally require the reviewed native saved `enzyme-variant-proposer` and `enzyme-variant-critic`; SCI owns their models, tools, permissions and lifecycle. Check current tool contracts and setup requirements before execution. Opening the environment does not authorize scientific submissions, installations or GPU work.

1. Read the chosen task and [shared specification](ENVIRONMENT_SPEC.md); choose and freeze settings for the intended approach.
2. Prepare and freeze the exact public parent, chemistry, mappings, protected features and final evaluation protocol. Record actual model/settings, explicit budget policies and authorized amendments in the run.
3. Start `sci` with this environment as its working directory. Use the corresponding prompt in `scripts/`, replace `RUN_ID` and select matching task/configs/input/output paths.
4. Keep approaches and repeats isolated, retain native artifacts/failures/unknown IDs, exclude MLDE, and seal selections before independent evaluation.

The JSON files in `configs/` are compact historical records, not SCI launch profiles. Fresh execution requires a separately supplied frozen settings file. Historical campaigns retain their original frozen settings and paths.

Keep large/private evidence in a dedicated workspace or ignored `results/local/`. Tracked results include separate agent-alone and specialist-assisted score tables, exact sequences and short usage summaries. Benchmark tables label published predictions and calculations in this work. Parent identity, methods and run status are explained in each results folder. Report generation does not restart historical campaigns.

## Offline comparison helper

Python 3.10+ and the standard library are sufficient for the retained helper. From the repository root:

```bash
python -B environments/enzyme-variant-optimization/scripts/evaluate_results.py --help
```

Input schemas and scientific limits are in the [common comparison protocol](ENVIRONMENT_SPEC.md#common-comparison-protocol). The helper compares already-reviewed measurements and sealed selections; it does not generate structures or establish experimental improvement.

Supporting literature remains in [research notes](../../research/enzyme-variant-optimization/research-notes.md). Repository [licensing](../../LICENSE) and external tool/data licenses continue to apply.

## Available agent-alone benchmarks

The [benchmark index](benchmark/README.md) and task-specific Markdown reports compare original published reference values with actual agent-alone outputs only. Each available task comparison has its own Markdown page with linked figures. RML and original LEH show changes from our selected parent. The other tasks also include reference-variant property predictions calculated in this work when available.

[Results](results/README.md) retain exact candidate sequences and full-precision values, including exploratory candidates lacking qualification. Historical runs have no assigned configuration version. Compact run configs summarize actual executions. No config-version comparison is presented.

[Source](src/README.md) retains actual agent-alone code with relocation provenance, and [scripts](scripts/README.md) provides launch/resume guidance and offline report commands. The working branch contains the available results and benchmark reports for review. The ten native arms are operationally closed, with unresolved scientific assessments recorded in results. The separate AtHOL1 reaction-site assessment and its descriptive comparison are complete. Original run workspaces are unchanged.

Specialist-assisted results are available for RML, original LEH, Sun LEH and Zhang hydrolases in the [results index](results/README.md). The existing benchmark reports retain their agent-alone scope.

New assisted executions use the reviewed enzyme-method, enzyme-recovery and enzyme-evaluator 1.2.0 packages and the environment-owned [enzyme-coordinator skill](src/skills/enzyme-coordinator/SKILL.md). See [startup instructions](scripts/README.md#assisted-workflow-startup) for explicit installation/version checks and native SCI goals with the retained 20-turn allowance. Historical results keep their original specialist setup.
