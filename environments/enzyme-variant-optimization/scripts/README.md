# Execution and report entry points

`launch_task.py` prepares a fresh native SCI prompt from a task/approach and an explicitly supplied frozen settings file (`--settings`); it starts SCI only with `--start` and rejects existing run workspaces.
Each task folder explains launch/resume use. SCI owns scientific execution, permissions, tools and saved-specialist lifecycle; JSON files do not configure SCI automatically.
`evaluate_results.py` is the existing sealed-endpoint helper. `build_reports.py` rebuilds a separate Markdown benchmark report for each completed task, with linked PNG figures (requires Matplotlib).
The original RUN_AGENT_ALONE.txt and RUN_WITH_SPECIALIST.txt remain available for the original full optimization workflow. Use task-specific reproduction scope for tasks005/006.

Compact JSON files under `configs/` document historical usage; they are not launch settings. Supply approved settings with `launch_task.py --settings /path/to/frozen_settings.json ...`.
