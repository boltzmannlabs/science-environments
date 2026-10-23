# GEOOPT-06-PILOT-001: Optimizer Selection Agent

Use only the supplied frozen input and declared tools. Choose BFGS, L-BFGS, trust-region, or another supported optimizer for the case.

Return a structured submission with a decision, evidence for every mandatory check, failure category when applicable, and wall time/retry/token provenance. Do not infer a minimum from energy alone.
