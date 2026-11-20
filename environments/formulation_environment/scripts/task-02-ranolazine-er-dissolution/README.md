# Task - 02 scripts

Run from the environment root:

    python scripts/shared/run_task.py --task "Task - 02" --out ".runs/task02/new-run"

Or call [verify_archive.py](verify_archive.py) with --out from any directory. Both use the same task-scoped implementation, require a new/empty output directory and check saved evidence only. Fresh outputs belong under `.runs/task02/`, not in Task-01 results.
