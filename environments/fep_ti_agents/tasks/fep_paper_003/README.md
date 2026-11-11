# FEP-PAPER-003 — SAMPL6 host–guest relative binding

| Path | Purpose |
|---|---|
| `PAPER_REFERENCE.md` | Source and reference definition |
| `TASK.md` | Agent-facing reconstruction task |
| `inputs/` | Frozen complex and solvent PDB inputs |
| `reference/` | Checksums, identities and evaluator-only target |
| `configs/` | Reference, agent, alternative and fault configurations |
| `evaluation/` | Independent input validation output |
| `tests/` | Task packet regression checks |

Run validation from the repository root:

```bash
python environments/fep_ti_agents/tasks/fep_paper_003/scripts/validate_inputs.py
python -m pytest -q environments/fep_ti_agents/tasks/fep_paper_003/tests
```

Current qualification is `REVIEW`: source inputs and protocol reconstruction
are implemented, but no host/guest parameterization, alchemical topology,
lambda trajectory or estimator evidence is claimed.
