# FEP runtime contracts

The FEP environment uses the following evidence contract:

- `tasks/` contains immutable task definitions and permitted inputs.
- `config/` contains shared schemas and policy.
- `scripts/` contains executable preparation, validation and comparison tools.
- `execution/` and `evaluation/` inside a task contain generated artifacts and
  reports, each bound to input hashes and commands.
- `benchmark/` contains publication-facing comparison criteria.
- `results/` indexes completed evidence without changing task inputs.

`PASS` means the stated check passed. `REVIEW` means scientific evidence is
incomplete. `FAIL` means a required check failed. A successful process exit or
valid standalone topology is not sufficient for production FEP qualification.

Agent-generated configurations must not read evaluator-only reference values.
Every tool call must be recorded with its command, input/output artifacts and
software identity. If the run uses a deterministic harness rather than an LLM,
that limitation must be stated explicitly.
