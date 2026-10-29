# MD validation tests

The tests validate contracts, packet completeness, fixture materialization,
runtime behavior, and independent evaluator output.

```bash
python tests/validate_spec.py
python -m pytest -q tests
```

These checks establish software and harness correctness. They do not replace
production-length molecular-dynamics qualification or reference-data review.
