# FEP shared task and evidence contracts

This directory mirrors the shared `src/` layer used by the repository's
standard scientific environments. The reusable FEP specialist contracts remain
in `agents/`, problem-solving contracts remain in `problem_solving/`, and
executable adapters remain in `../scripts/`.

Read `TASK.md` for the common paper-reconstruction task contract and
`CONTRACTS.md` for evidence and qualification rules.

The runtime layer follows the repository's agent-environment pattern:

- `agents.py` selects specialist roles and records tool events.
- `structure_preparation.py` performs independent endpoint artifact checks.
- `assessment.py` evaluates the paper configuration matrix.
- `reporting.py` renders a conservative setup summary.
- `contracts.py` enforces status and missing-evidence rules.
