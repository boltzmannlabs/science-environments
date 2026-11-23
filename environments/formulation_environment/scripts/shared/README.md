# Shared execution tools

From the environment root:

```bash
python scripts/shared/run_task.py --task 'Task - 01' --out .runs/task-01/new-run
python scripts/shared/run_task.py --task 'Task - 02' --out .runs/task-02/new-run
python scripts/shared/validate_environment.py
```

The runner loads [the registry](../../config/shared/tasks.json). Validation discovers all task and shared tests, checks Markdown links and source hashes, and writes fresh receipts under `.runs/validation/`. Add `--run <fresh-task-01-output>` to compare a real replay against archived metrics.
