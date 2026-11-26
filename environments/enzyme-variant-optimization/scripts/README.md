# Execution and report entry points

`launch_task.py` prepares a fresh native SCI prompt from a task/approach and an explicitly supplied frozen settings file (`--settings`); it starts SCI only with `--start` and rejects existing run workspaces.
Each task folder explains launch/resume use. SCI owns scientific execution, permissions, tools and saved-specialist lifecycle; JSON files do not configure SCI automatically.
`evaluate_results.py` is the existing sealed-endpoint helper. `build_reports.py` rebuilds a separate Markdown benchmark report for each completed task, with linked PNG figures (requires Matplotlib).
The original RUN_AGENT_ALONE.txt and RUN_WITH_SPECIALIST.txt remain available for the original full optimization workflow. Use task-specific reproduction scope for tasks005/006.

Compact JSON files under `configs/` document historical usage; they are not launch settings. Supply approved settings with `launch_task.py --settings /path/to/frozen_settings.json ...`.

## Assisted workflow startup

Install enzyme-method, enzyme-recovery and enzyme-evaluator 1.2.0 through SCI's reviewed catalog installer in a dedicated execution profile. Copy the reviewed src/skills/enzyme-coordinator directory into that profile's skills directory. Existing conversations keep their snapshots; start a new task only after verifying installed versions. The launcher verifies all three package versions and the coordinator before execution.

Use launch_task.py with explicit --profile, --sci-source and --sci-python from the reviewed installation, plus --task, --settings, --approach and --run-dir. Its default prepares the request and prints the command. --start requires an interactive terminal. start_goal.py queues a plain native /goal command, so SCI persists the goal and handles continuation. Query-file prompts alone bypass slash handling. Confirm /goal status reports active and the retained 20-turn allowance. Use /goal resume in the same session after that allowance is exhausted, and SCI's native /background for persistent execution. Reuse accepted job IDs and native assignment IDs after interruptions.

The specialist definitions are distributed in Agent Scientist's subagent catalog. Public source searches require task approval, and no new scientific service credentials are copied by these scripts. Existing runs must use their saved native resume identities rather than this fresh-workspace launcher.
