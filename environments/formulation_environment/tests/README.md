# Tests

From the environment root:

```bash
python -m unittest discover -s tests -v
```

- [Shared](shared/README.md): folder ownership, registry/import consistency and portable dispatch.
- [Task-01](task_01_clarithromycin_ir_formulation_dissolution/README.md): composition, scientific records, metrics, source hashes and reports.
- [Task-02](task_02_ranolazine_er_dissolution/README.md): archive integrity, arithmetic and portable execution.

Folders use the registered Python package names so unittest discovery traverses them. Full Task-01 replay runs separately through its task script.
