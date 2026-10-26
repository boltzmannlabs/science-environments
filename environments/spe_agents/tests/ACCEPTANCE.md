# Acceptance and validation plan

The package is accepted when each case records its exact input, method, basis,
charge, multiplicity, engine/version, output units, convergence evidence,
failure category and provenance hash. The independent evaluator must recompute
the reported arithmetic and reject unsupported claims.

Validation evidence is case-specific; benchmark summaries belong in the
`science-benchmarking` repository. Missing engine access or reference data is a
documented limitation, not a pass.
