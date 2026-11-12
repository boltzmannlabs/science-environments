# Acceptance and validation

Run `pytest -q environments/md_agents/tests` for package tests and
`python tests/validate_spec.py` for specification validation. Tests verify
contracts, packet coverage, schemas, and bounded execution invariants; they do
not establish scientific reproduction.
