# FEP-PAPER-004 — PTP1B 23477 → 23479

This task packet mirrors PTP1B FEP-PAPER-002 with a distinct ligand endpoint.
It includes frozen PDB/SDF inputs, source checksums, configurations,
independent validation and regression tests.

```bash
python environments/fep_ti_agents/tasks/fep_paper_004/scripts/validate_inputs.py
python -m pytest -q environments/fep_ti_agents/tasks/fep_paper_004/tests
```

Current status is `REVIEW`; the task is a validated published-input benchmark,
not a completed free-energy calculation.
