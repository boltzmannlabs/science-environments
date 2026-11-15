# Formulation Environment

**Status: In Progress / DESIGN_ONLY. No validated pharmaceutical product or recipe-to-release predictor.**

A reusable, evidence-gated task collection for formulation design, dissolution analysis and experimental planning. This addition preserves the separate [ranolazine-focused environment](../formulation_dissolution/README.md); it does not merge its synthetic scenarios with clarithromycin literature data.

## Current work

[Task - 01 — Clarithromycin 500 mg immediate-release formulation and dissolution investigation](tasks/Task%20-%2001/README.md).

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
.venv/bin/python scripts/run_task.py --task 'Task - 01' --out .runs/example-01
.venv/bin/python scripts/validate_environment.py
```

Run from this directory. `scripts/run_task.py` resolves checkout inputs independently of the working directory, refuses to overwrite nonempty runs, and records a receipt. No API credentials, network, LLM, GPU or physical laboratory backend is needed for Task 01. Tests do not manufacture synthetic experimental evidence.

## Unified structure

```text
formulation_environment/
  README.md  ENVIRONMENT_SPEC.md  STATUS.md  MODELS_AND_TOOLS.md
  config/          task registry and frozen benchmark contract
  tasks/Task - 01/  objective, overall work, execution and acceptance
  benchmark/Task - 01/  benchmark specification, numeric inputs and metric contract
  results/Task - 01/    curated v1/v2 results, reports and provenance
  scripts/         portable execution and publication checks
  src/             reusable implementation and hard constraints
  tests/           independent data/scientific-contract regression tests
```

Use the **same exact task ID** under all three task roots. [Task structure standard](TASK_STRUCTURE.md) explains adding Task - 02 without overwriting Task - 01.

## Navigation

[Specification](ENVIRONMENT_SPEC.md) · [Status](STATUS.md) · [Models/tools](MODELS_AND_TOOLS.md) · [Task index](tasks/README.md) · [Benchmark index](benchmark/README.md) · [Results index](results/README.md) · [Research](../../research/clarithromycin-ir-formulation/research-notes.md).

The repository [LICENSE](../../LICENSE) remains a no-license-grant status notice. Full third-party articles, SDKs, upstream tool archives and account-scoped logs are not published here.
