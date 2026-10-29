# FEP/TI validation tests

Run:

```bash
python tests/validate_spec.py
python -m pytest -q tests
```

These tests validate contracts, toy TI behavior, and manifest integrity. They
do not replace production molecular FEP trajectories or reference comparison.
