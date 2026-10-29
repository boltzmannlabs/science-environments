# Tasks

The working input is a JSON object following `enzyme-research-task/1`, implemented in `enzyme_research.contracts.task_contract`. The specification documents its fields. Task definitions never contain account credentials or protected assay answers.

Create a fully executable synthetic example from the installed package:

```bash
.venv/bin/python tasks/examples/create_synthetic_task.py --output .runs/task-example
.venv/bin/enzyme-research start --task .runs/task-example/task.json --state .runs/task-example/state --arm base
```

The creator writes a toy structure, computes its actual SHA-256, and creates a matching task JSON. This avoids a placeholder structure path/hash. The coordinates and results are only parser/research-loop fixtures and are not valid scientific structures or model predictions. The example performs no scientific submissions.

Real computational tasks supply their own reviewed sequence, structure, substrate, catalytic mappings, evidence, allowed jobs, and limits. For `protected_measured_library`, supply public member IDs/sequences and their membership hash, while storing experimental answers with a separate evaluator. The environment enforces declared membership but does not itself establish operating-system isolation for an unrestricted agent session.
