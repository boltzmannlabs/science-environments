# Shared qualification gate

This small standard-library utility provides the common scientific evidence
gate used by environment integrations. It prevents adapter success from being
reported as scientific success.

```python
from environments.shared_qualification import qualify

decision = qualify(
    evidence,
    required_evidence=["trajectory", "reference"],
    required_checks=["finite_energy", "converged"],
)
```

The gate returns `PASS` only when required evidence exists, all required
checks are true, the adapter passed, and an independent evaluator is present.
Incomplete evidence returns `REVIEW`; explicit adapter or scientific failures
return `FAIL`.
