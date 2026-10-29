# HOMO–LUMO validation tests

Run the package checks with:

```bash
python tests/validate_spec.py
python -m pytest -q tests
```

These tests verify contracts and prototype behavior; they do not replace
independent QM reference calculations or experimental excitation data.
