# Tests

Run `python -m unittest discover -s tests -v` in the environment root with RDKit installed. Tests use tiny explicitly synthetic graph fixtures, confirm route IDs/target match, absent listed oxygen source flag, missing evidence gates, malformed input handling, and read-only source treatment. They do not validate chemistry or calculate experiment metrics.

Historical local integration exercise against *unpublished authorized raw exports*: A 12 routes/38 reaction nodes; M 7 routes/21 nodes; no complete literature-cited step procedures in either. Reproduction of those historical counts requires the original authorized exports; the repository ships only sanitized aggregates and a self-contained synthetic-fixture test suite.
