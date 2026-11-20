# Unified formulation task structure

Every formulation task must use the same `task-NN-short-title` folder name under `tasks/`, singular `benchmark/` and `results/`. Use lowercase words separated by hyphens, with a two-digit task number matching the registered ID. Full titles belong in the registry and task README.

| Task ID / CLI selector | Folder name in all three sections |
| --- | --- |
| `Task - 01` | `task-01-clarithromycin-ir-formulation-dissolution` |
| `Task - 02` | `task-02-ranolazine-er-dissolution` |

```text
tasks/
  task-01-clarithromycin-ir-formulation-dissolution/
  task-02-ranolazine-er-dissolution/
benchmark/
  task-01-clarithromycin-ir-formulation-dissolution/
  task-02-ranolazine-er-dissolution/
results/
  task-01-clarithromycin-ir-formulation-dissolution/
  task-02-ranolazine-er-dissolution/
```

Task README: title, overall task, objective, input provenance, actual execution, scope, acceptance and links to matching benchmark/results. Benchmark README: comparator eligibility, frozen bounds, source data, metrics and acceptance boundaries. Results README: versioned artifacts, actual findings, failures, limitations and links back.

To add a task:

1. Assign the next task number and choose one short title, for example `task-03-short-title`.
2. Create matching folders with a README under all three required sections. Keep inputs/specifications in benchmark, work definition in tasks, and versioned output artifacts in results.
3. Register the stable task ID, full title, `folder_slug`, `task_dir`, `benchmark_dir` and `results_dir` in [config/tasks.json](config/tasks.json). Add any extra task-specific ownership paths there too. The structure check requires matching numbered names and no unregistered task directories in the three sections.
4. Extend runner dispatch, implementation and scientific contracts as needed. Run tests, offline replay and publication validation before pushing.

[Task - 02](tasks/task-02-ranolazine-er-dissolution/README.md) also uses its slug under config/, scripts/ and docs/. Python source and tests use identifier-safe `ranolazine_task02` subpackages. Shared runners, indexes and reusable code stay at environment level. Existing root research/ and docs/decisions/ topics retain their names and are linked through the ownership map.

Keep old result versions; new runs need new directories. Historical execution receipts retain the paths recorded at execution time. Current registry paths, contracts and publication manifests point to the renamed folders; scientific inputs, numeric results, reports and artifact hashes remain unchanged.

Preserve source citations and distinguish computed, literature-observed, planned and measured endpoints. Generated HTML/SVG artifacts retain byte-identical Matplotlib formatting; scoped `.gitattributes` disable whitespace checks only for those generated artifacts. Publication checks cover links, source hashes and accidental private data. A branch push does not imply scientific review or physical validation.
