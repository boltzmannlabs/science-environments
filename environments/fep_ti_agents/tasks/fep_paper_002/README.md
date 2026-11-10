# FEP-PAPER-002 — PTP1B public benchmark edge

This task is the second paper-derived FEP benchmark. It uses the PTP1B
`23477 -> 23482` edge from the public binding free-energy benchmark released
with Ross et al., *The maximal and current accuracy of rigorous protein-ligand
binding free energy calculations* (Communications Chemistry, 2023).

The task evaluates whether an agent can reconstruct a protein–ligand RBFE
environment from a public paper/dataset source. It is intentionally separate
from the CDK2/Alchaware task and does not reuse its answer files.

Run:

```bash
python scripts/validate_inputs.py
python -m pytest -q tests
```

The current result is `REVIEW`: input identity, ligand extraction and the
published experimental edge are validated, but the source paper does not
provide a complete open alchemical trajectory bundle for this edge.
