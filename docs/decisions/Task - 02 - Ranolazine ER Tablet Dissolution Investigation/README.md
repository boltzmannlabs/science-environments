# Decision: separate ranolazine Task-02 throughout the repository

## Context

Ranolazine Task-02 and clarithromycin Task-01 have different APIs, methods, data and scientific limitations. Keeping only a task brief separate is insufficient for maintainable ownership.

## Decision

Use dedicated Task-02 config, task, benchmark, results, scripts, docs and root research folders. Use identifier-safe `ranolazine_task02` Python source/test packages, mapped explicitly in the registry. Keep common navigation/runner shared. Preserve the original ranolazine implementation and evidence in place instead of duplicating raw archives or completing an unrelated migration.

## Consequences

Task-01 stays unchanged except permitting additional registry tasks. Task-02 execution verifies archived integrity/arithmetic only; it does not refit models or establish pharmaceutical performance. All new validation outputs stay within Task-02. See the [folder map](../../../environments/formulation_environment/docs/task-02-ranolazine-er-dissolution/README.md).

## Complete environment ownership (2026-11-20)

Both tasks now own configuration, documentation, scripts, source and tests as well as tasks, benchmark and results folders. The registry lives under `config/shared/`; common execution tools live under `scripts/shared/`. Source/test packages now use the complete numbered task slug with hyphens replaced by underscores. The earlier `ranolazine_task02` package name is superseded.
