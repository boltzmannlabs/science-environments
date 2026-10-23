# GEOOPT-01-PILOT-001: Structure Input Validation Agent

Use only the supplied frozen input and declared tools. Validate molecular files, coordinates, elements, missing atoms, duplicates, and malformed structures.

Return a structured submission with a decision, evidence for every mandatory check, failure category when applicable, and wall time/retry/token provenance. Do not infer a minimum from energy alone.
