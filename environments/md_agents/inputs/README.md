# MD input packets

Executable MD cases keep their request, runtime limits, source-file references
and expected outputs in a dedicated input directory. The canonical source
hashes remain recorded in the request and result JSON files.

```text
inputs/
├── MD-CORE-001-water-box/task.json
└── MD-REC-001-recovery-fixtures/task.json
```

The complete MD-01 through MD-62 registry is in `../cases/agent_inputs.json`.
An input directory is added when its engine fixture is executable and versioned.
