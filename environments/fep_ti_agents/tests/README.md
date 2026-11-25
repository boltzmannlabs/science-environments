# FEP validation tests

The tests validate task contracts, frozen input identity, endpoint artifacts,
provenance, configuration comparisons and conservative qualification rules.
They do not convert setup success into production FEP qualification.

Run from the repository root:

```bash
python -m pytest -q environments/fep_ti_agents/tests \
  environments/fep_ti_agents/tasks/fep_paper_001/tests \
  environments/fep_ti_agents/tasks/fep_paper_002/tests
```
