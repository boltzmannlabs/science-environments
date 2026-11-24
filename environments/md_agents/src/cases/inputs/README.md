# MD input packets

Executable MD cases keep their request, runtime limits, source-file references
and expected outputs in a dedicated input directory. The canonical source
hashes remain recorded in the request and result JSON files.

```text
inputs/
├── MD-01/task.json
├── MD-02/task.json
├── ...
├── MD-10/task.json
├── MD-11/task.json
└── MD-62/task.json
```

The complete MD-01 through MD-62 registry is in `../cases/agent_inputs.json`.
Each registry entry is materialized as `inputs/MD-XX/task.json`. The two
executable packets additionally have descriptive directories
`MD-CORE-001-water-box/` and `MD-REC-001-recovery-fixtures/`.
