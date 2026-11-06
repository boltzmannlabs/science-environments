# Enzyme Variant Optimization

An Agent-Scientist environment for improving an existing enzyme through actual tool-based generation, property screening, candidate-specific structural/chemical assessment, results-driven revision, re-evaluation and evidence review. Agent-alone and specialist-assisted runs follow the same scientific requirements. A completed workflow may find no supported improvement.

## Environment structure

```text
enzyme-variant-optimization/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── config/
│   └── task_001_<case>/
│       ├── v1/
│       │   ├── agent_alone.json
│       │   └── agent_with_specialist.json
│       └── v2/README.md
├── tasks/task_001_<case>.md
├── scripts/
├── src/
│   ├── evaluation.py
│   └── skills/
├── benchmark/
│   └── task_001_<case>/comparisions/
└── results/
    └── task_001_<case>/v1/
```

This naming pattern applies to all five tasks. There is no environment `tests/` directory. `comparisions/` uses the requested folder spelling. Hidden `.gitignore` rules protect local/private artifacts.

| Location | Information |
| --- | --- |
| [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) | Shared workflow stages, protected constraints, evidence, recovery, comparison protocol and completion criteria. |
| [STATUS.md](STATUS.md) | Implemented work, work in progress and future enhancements. |
| [MODELS_AND_TOOLS.md](MODELS_AND_TOOLS.md) | Required capabilities, method families, selection criteria and limitations. SCI discovery/contracts define current APIs. |
| [config/](config/README.md) | Task/version/approach settings: LLM, parameters, budgets, concurrency, limits and exclusions. |
| [tasks/](tasks/README.md) | Numbered scientific assignments. |
| [scripts/](scripts/README.md) | Existing launch prompts and thin evaluation entry point. |
| [src/](src/README.md) | Reviewed generated workflow code/skills and the retained offline evaluator. |
| [benchmark/](benchmark/README.md) | Original paper values and comparisons between task/config versions, when verified. |
| [results/](results/README.md) | Reviewed original Agent-Scientist execution evidence. |

## Tasks and versions

| ID | Case | Configuration |
| --- | --- | --- |
| `task_001_est30_mhet` | [Est30 and MHET](tasks/task_001_est30_mhet.md) | [Versions](config/task_001_est30_mhet/README.md) |
| `task_002_rml_stability` | [RML stability](tasks/task_002_rml_stability.md) | [Versions](config/task_002_rml_stability/README.md) |
| `task_003_leh_stability` | [LEH stability](tasks/task_003_leh_stability.md) | [Versions](config/task_003_leh_stability/README.md) |
| `task_004_bla_high_temperature` | [BLA high-temperature performance](tasks/task_004_bla_high_temperature.md) | [Versions](config/task_004_bla_high_temperature/README.md) |
| `task_005_athol1_substrate` | [AtHOL1 substrate expansion](tasks/task_005_athol1_substrate.md) | [Versions](config/task_005_athol1_substrate/README.md) |

Each executable configuration version includes both approaches. A later version represents a deliberate settings change, such as a different LLM or budget. Repeated executions retain the version and get distinct run IDs. The v2 folders currently explain future contents rather than claiming selected settings. The three tasks without a selected LLM require that selection before launch.

## Prerequisites and start

Use an available native SCI installation and access to the required scientific capabilities. Assisted runs additionally require the reviewed native saved `enzyme-variant-proposer` and `enzyme-variant-critic`; SCI owns their models, tools, permissions and lifecycle. Check current tool contracts and setup requirements before execution. Opening the environment does not authorize scientific submissions, installations or GPU work.

1. Read the chosen task, [shared specification](ENVIRONMENT_SPEC.md) and configuration version/approach.
2. Prepare and freeze the exact public parent, chemistry, mappings, protected features and final evaluation protocol. Record actual model/settings, explicit budget policies and authorized amendments in the run.
3. Start `sci` with this environment as its working directory. Use the corresponding prompt in `scripts/`, replace `RUN_ID` and select matching task/config/input/output paths.
4. Keep approaches and repeats isolated, retain native artifacts/failures/unknown IDs, exclude MLDE, and seal selections before independent evaluation.

The JSON profiles document settings; they are not an automatic SCI configuration loader. Default prompts select task_002 RML/v1. Freeze the effective profile and actual SCI settings with each run. Current ongoing campaigns retain their original frozen environment and paths.

Keep large/private evidence in a dedicated workspace or ignored `results/local/`. Tracked results are reserved for reviewed shareable outputs. Benchmark and result READMEs explain future contents without inventing reference extraction, completed results or comparisons.

## Offline comparison helper

Python 3.10+ and the standard library are sufficient for the retained helper. From the repository root:

```bash
python -B environments/enzyme-variant-optimization/scripts/evaluate_results.py --help
```

Input schemas and scientific limits are in the [common comparison protocol](ENVIRONMENT_SPEC.md#common-comparison-protocol). The helper compares already-reviewed measurements and sealed selections; it does not generate structures or establish experimental improvement.

Supporting literature remains in [research notes](../../research/enzyme-variant-optimization/research-notes.md). Repository [licensing](../../LICENSE) and external tool/data licenses continue to apply.
