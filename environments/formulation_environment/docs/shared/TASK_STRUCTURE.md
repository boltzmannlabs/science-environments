# Unified formulation task structure

Each task owns a folder under every task-related section. Use `task-NN-short-title` for configuration, documentation, scripts, task definitions, benchmark and results. Python source and tests use the exact same slug with hyphens replaced by underscores for valid imports and unittest discovery.

| Section | Task-01 | Task-02 |
| --- | --- | --- |
| config, docs, scripts, tasks, benchmark, results | `task-01-clarithromycin-ir-formulation-dissolution` | `task-02-ranolazine-er-dissolution` |
| src/formulation_environment, tests | `task_01_clarithromycin_ir_formulation_dissolution` | `task_02_ranolazine_er_dissolution` |

The [registry](../../config/shared/tasks.json) records each task's stable ID, full title, folder slug, Python package, ownership paths and entrypoint. The CLI selectors remain `Task - 01` and `Task - 02`.

## Shared files

- `config/shared/`: task registry.
- `scripts/shared/`: registry runner and environment validator.
- `docs/shared/`: environment specification, structure, status, models/tools and third-party provenance.
- `tests/shared/`: ownership, import and shared dispatch checks.

Section root READMEs provide navigation. The environment root contains only its README, packaging/dependency files and Git settings. Python package `__init__.py` files remain where imports or test discovery require them. Task-specific composition rules belong in the owning task source package.

## Adding a task

1. Assign the next task number and choose a short title, for example `task-03-short-title`.
2. Create matching task folders under config, docs, scripts, tasks, benchmark and results. Create corresponding Python source/test packages using underscores. Add a README that explains each folder's purpose.
3. Register all eight ownership paths and an importable entrypoint. Keep scientific contracts in config, work definitions in tasks, inputs/specifications in benchmark, implementation in source, and versioned outputs in results.
4. Extend the shared runner's explicit dispatch and add task-specific contracts. Task script wrappers select the registered task and reuse shared execution.
5. Run `python -m unittest discover -s tests -v`, both relevant task scripts and `python scripts/shared/validate_environment.py`. Use a fresh output directory for every real replay.

The shared structure check validates all ownership paths, imports, matching task numbers, unexpected section folders and loose files. External research and decision topics retain their established paths and are linked from task documentation.

## Preserving evidence

Keep old result versions and historical receipts, including paths recorded at execution time. Current contracts and manifests point to current locations. Scientific inputs, numeric outputs, reports and their hashes are preserved during structural changes. Record failed validation and known numerical discrepancies in status documentation; do not alter tolerances or scientific artifacts to make a folder cleanup pass.

Preserve citations and distinguish computed, literature-observed, planned and measured endpoints. Generated HTML/SVG artifacts retain their original bytes. Publication checks cover links, source hashes and accidental private data. A branch push does not imply scientific review or physical validation.
