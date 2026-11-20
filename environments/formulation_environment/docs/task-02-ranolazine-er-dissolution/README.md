# Task - 02 documentation

## Layout and ownership

The stable ID is Task - 02. Its folder slug is `task-02-ranolazine-er-dissolution` across this environment's task-specific sections.

Task-owned material has dedicated folders in config/, tasks/, benchmark/, results/, scripts/, docs/, and root research/. Executable Python code and tests use `src/formulation_environment/task_02_ranolazine_er_dissolution/` and `tests/task_02_ranolazine_er_dissolution/` so imports and unittest discovery work. The [contract](../../config/task-02-ranolazine-er-dissolution/contract.json) and [registry](../../config/shared/tasks.json) provide the canonical path map.

The original ranolazine implementation/data remain in [formulation_dissolution](../../../formulation_dissolution/README.md) as immutable historical evidence, not copied into Task-01 or silently relabeled as measured data. Shared indexes and dispatch stay at environment level; task-specific details do not belong in shared files. No unrelated environment is reorganized.

## Execution boundary

Task-02 now has explicit archive-verification dispatch. It checks saved artifact integrity and arithmetic only, not fresh model fitting, lab results, calibrated product prediction or prospective improvement. Earlier publication receipts are retained unchanged; new structure-verification receipts are versioned separately under this task.
