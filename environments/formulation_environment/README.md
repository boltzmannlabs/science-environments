# Formulation Environment

**Status: In Progress / DESIGN_ONLY. No validated pharmaceutical product or recipe-to-release predictor.**

A reusable, evidence-gated task collection for formulation design, dissolution analysis and experimental planning. Task-02 has dedicated folders for its [ranolazine investigation](tasks/task-02-ranolazine-er-dissolution/README.md), including configuration, source, scripts, tests, documentation, research, benchmark and results. The original [ranolazine implementation/evidence](../formulation_dissolution/README.md) remains unchanged; its synthetic scenarios are not pooled with clarithromycin literature data.

## Current work

[Task - 01 — Clarithromycin 500 mg immediate-release formulation and dissolution investigation](tasks/task-01-clarithromycin-ir-formulation-dissolution/README.md).

- Fixed 500 mg API in an assumed 800 mg finished coated tablet; eight specified excipients only.
- Original 24 valid recipes, expanded to 28; nine matched CP/PVP designs support future interaction/curvature estimation.
- Actual archived PTCalc analysis plus portable SciPy held-out-timepoint comparisons on published comparator means.
- No measured candidate dissolution, stability, compatibility or manufacturing results; no demonstrated superiority over a literature product.

## Setup and run

Tested on Python 3.13.7 with NumPy 2.2.4, pandas 3.0.3 and SciPy 1.15.3. Other supported-version claims require validation.

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/shared/run_task.py --task 'Task - 01' --out .runs/example-01
.venv/bin/python scripts/shared/validate_environment.py
```

Run from this directory. `scripts/shared/run_task.py` resolves checkout inputs independently of the working directory, refuses to overwrite nonempty runs, and records a receipt. No API credentials, network, LLM, GPU or physical laboratory backend is needed for Task 01. Tests do not manufacture synthetic experimental evidence.

## Task - 02: separate ranolazine folders

[Ownership map](docs/task-02-ranolazine-er-dissolution/README.md). Run archive verification from this environment:

    python scripts/shared/run_task.py --task "Task - 02" --out .runs/task02/new-run

This verifies archived hashes and arithmetic only. It does not rerun model fitting or demonstrate product improvement.

## Unified structure

```text
formulation_environment/
  README.md
  pyproject.toml
  requirements.txt
  config/
    shared/tasks.json
    task-01-clarithromycin-ir-formulation-dissolution/contract.json
    task-02-ranolazine-er-dissolution/contract.json
  docs/
    shared/                  specification, structure, status, models and provenance
    task-01-clarithromycin-ir-formulation-dissolution/
    task-02-ranolazine-er-dissolution/
  scripts/
    shared/                  registry runner and environment validator
    task-01-clarithromycin-ir-formulation-dissolution/run.py
    task-02-ranolazine-er-dissolution/verify_archive.py
  src/formulation_environment/
    task_01_clarithromycin_ir_formulation_dissolution/
    task_02_ranolazine_er_dissolution/
  tests/
    shared/                  ownership and dispatch checks
    task_01_clarithromycin_ir_formulation_dissolution/
    task_02_ranolazine_er_dissolution/
  tasks/                     one folder per task
  benchmark/                 matching task folders with inputs and specifications
  results/                   matching task folders with versioned outputs
```

Every task has dedicated folders in config, docs, scripts, source, tests, tasks, benchmark and results. Use the same `task-NN-short-title` slug; Python source/test packages replace hyphens with underscores. The [registry](config/shared/tasks.json) records every path. Common infrastructure belongs in `shared/`.

The root keeps the README, package/dependency metadata, `.gitignore` and `.gitattributes`. Section READMEs provide navigation; package `__init__.py` files support imports and test discovery. The [task structure standard](docs/shared/TASK_STRUCTURE.md) explains how to add future tasks.

## Navigation

[Specification](docs/shared/ENVIRONMENT_SPEC.md) · [Status](docs/shared/STATUS.md) · [Models/tools](docs/shared/MODELS_AND_TOOLS.md) · [Task index](tasks/README.md) · [Benchmark index](benchmark/README.md) · [Results index](results/README.md) · [Research](../../research/clarithromycin-ir-formulation/research-notes.md).

The repository [LICENSE](../../LICENSE) remains a no-license-grant status notice. Full third-party articles, SDKs, upstream tool archives and account-scoped logs are not published here.
