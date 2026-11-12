# MD-PAPER-002 — 3CLpro conventional MD

| Path | Purpose |
|---|---|
| `TASK.md` | Agent-facing scientific task |
| `PAPER_REFERENCE.md` | Publication and protocol source |
| `inputs/` | Frozen PDB structure |
| `reference/` | Parameters and input hash |
| `configs/` | Reference, agent, alternative and perturbed setups |
| `evaluation/` | Independent validation output |
| `tests/` | Regression tests |

Run validation from the repository root:

```bash
python environments/md_paper_reproduction/tasks/md_paper_002/scripts/validate_inputs.py
python -m pytest -q environments/md_paper_reproduction/tasks/md_paper_002/tests
```

Current status is `REFERENCE_READY / REVIEW`; this does not claim production
trajectory reproduction.
