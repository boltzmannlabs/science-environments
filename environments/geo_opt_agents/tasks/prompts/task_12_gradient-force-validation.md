# GEOOPT-12-PILOT-001: Gradient and Force Validation Agent

Use only the supplied frozen input and declared tools. Validate gradient shape, finite values, signs, units, and consistency with energy changes.

Return a structured submission with a decision, evidence for every mandatory check, failure category when applicable, and wall time/retry/token provenance. Do not infer a minimum from energy alone.
