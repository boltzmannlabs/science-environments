# FEP-PAPER-005 — force-field sensitivity

| Path | Purpose |
|---|---|
| `PAPER_REFERENCE.md` | Publication and selected system |
| `TASK.md` | Agent-facing sensitivity task |
| `inputs/` | Frozen CDK2 protein and ligand structures |
| `reference/` | Independently extracted paper fields and hashes |
| `configs/` | Reference, agent, alternative and perturbed setups |
| `evaluation/` | Input and configuration validation |
| `tests/` | Regression tests |

Run from the repository root:

```bash
python environments/fep_ti_agents/tasks/fep_paper_005/scripts/validate_inputs.py
python -m pytest -q environments/fep_ti_agents/tasks/fep_paper_005/tests
```

Current status is setup validation and `REVIEW`; no production sensitivity
result is claimed.
