# RML stability — execution entry point

From the environment directory, prepare this assignment with explicitly selected settings:

```bash
python scripts/launch_task.py \
  --task task_001_rml_stability \
  --settings /path/to/frozen_settings.json \
  --approach agent_with_specialist \
  --profile your-dedicated-profile \
  --run-dir /path/to/empty-run-directory \
  --sci-python /path/to/reviewed-sci-python \
  --sci-source /path/to/reviewed-agent-scientist
```

Use `agent_alone` to run without specialists. Run the printed command in an interactive terminal; confirm SCI saved an active goal with the retained 20-turn allowance. For an existing run, use its original profile and native session ID through SCI resume instead of launching again.

[Task assignment](../../tasks/task_001_rml_stability/task.md) · [Full script instructions](../README.md) · [Recorded workflows](../../results/task_001_rml_stability/README.md).
