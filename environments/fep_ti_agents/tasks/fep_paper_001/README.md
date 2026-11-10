# FEP-PAPER-001 — CDK2 relative binding free energy

This is the first paper-derived FEP benchmark in the FEP/TI environment. It
reconstructs the CDK2 `17 -> 1h1q` transformation from the pinned Alchaware
source and evaluates whether the agent can build a traceable FEP setup.

## Task packet

| Path | Purpose |
|---|---|
| `PAPER_REFERENCE.md` | Publication/source protocol and scope |
| `TASK.md` | Agent-facing scientific task |
| `inputs/` | Frozen protein, ligand, mapping and source artifacts |
| `reference/` | Independently curated protocol values |
| `configs/` | Reference, agent, alternative and perturbed configurations |
| `execution/` | Parameterization, endpoint and smoke-run artifacts |
| `evaluation/` | Configuration, mapping and readiness reports |
| `expected_outputs/` | Machine-checkable acceptance requirements |
| `tests/` | Regression tests for the task packet |

## Run validation

```bash
python -m pytest -q environments/fep_ti_agents/tests \
  environments/fep_ti_agents/tasks/fep_paper_001/tests
```

The task validates protocol reconstruction, endpoint preparation and
provenance. It remains `REVIEW`: no production lambda trajectories, overlap,
convergence, uncertainty or paper-level free-energy reproduction is claimed.
