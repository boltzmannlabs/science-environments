# SPE validation tests

Run the specification and contract checks with:

```bash
python tests/validate_spec.py
python -m pytest -q tests
```

These tests validate package contracts and do not by themselves establish
scientific accuracy of every quantum-chemistry calculation.
