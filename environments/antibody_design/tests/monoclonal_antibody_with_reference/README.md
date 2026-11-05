# Reference-Guided Monoclonal Test Suite

The DENV prompt variants referenced by these regression checks are retired fixtures under `tests/fixtures/retired_tasks/`. The active monoclonal tasks are the five documents in `tasks/monoclonal_antibody_design/`; this suite does not establish their scientific performance.

This is the environment's only scenario test directory. The tested scenario requires **both a supplied antigen and a supplied paired heavy/light-chain monoclonal reference antibody**. The existing DENV example is a profile of this scenario.

Target-only design, bispecific design, and bispecific assessments have no scenario suites here. Tests that reject those modes within a reference-guided request protect this suite's boundary; they do not test those other workflows. Task instructions remain under `tasks/`, and configuration contracts remain under `config/`.

Reference-guided test code, synthetic fixtures, validation and acceptance documentation live in this directory. Historical prompt fixtures are stored separately in `../fixtures/retired_tasks/`. The shared helpers one level above serve multiple task families: schema loading, file integrity, configuration checks, and the package runner. They do not establish scientific capability.

| File | Purpose |
| --- | --- |
| `validation.py` | Monoclonal preflight, result-bundle, and assay-record contract validation. |
| [ACCEPTANCE.md](ACCEPTANCE.md) | Acceptance requirements for the reference-guided monoclonal suite. |
| [COVERAGE.md](COVERAGE.md) | Implemented coverage and remaining scientific gaps. |
| `test_reference_guided.py` | Reusable request/preflight and result checks: reference identity, lineage, protocol, provenance, and exports. |
| `test_denv_reference.py` | DENV reference-guided regressions: evidence integrity, cutoff, resource limits, qualification, and failure statuses. |
| `test_task_variants.py` | Parity between the general and capability-detailed DENV prompts. |
| `test_mab_testing_criteria.py` | Declared mAb criteria, endpoint distinctions, catalog coverage, and output requirements. |
| `contract_fixtures.py` | Shared synthetic fixtures for the contract tests. |
| [MONOCLONAL_ANTIBODY_TEST_CASES.md](MONOCLONAL_ANTIBODY_TEST_CASES.md) | Scientific criteria and planned cases; not an executable assay suite. |
| `make_needs_input_example.py` | Testing helper that regenerates the DENV example's preflight result. |

Run from the environment directory:

```bash
# All reference-guided monoclonal tests
python3 -m unittest discover -s tests/monoclonal_antibody_with_reference -t tests -p 'test_*.py' -v

# Reusable contract tests only
python3 -m unittest discover -s tests/monoclonal_antibody_with_reference -t tests -p 'test_reference_guided.py' -v

# Full package checks, including this suite
python3 tests/validate_spec.py
```

These tests use synthetic records or inspect specifications. They do not generate antibodies, predict binding, or establish biological activity. See [coverage and remaining gaps](COVERAGE.md).

## Input and evidence boundary

- An absent or null antigen/reference declaration fails schema validation. A missing antigen sequence, construct sequence, or reference chain file returns `NEEDS_INPUT`.
- A complete paired reference remains the baseline for identity and lineage checks. Contract readiness does not demonstrate improvement over that reference.
- Binding, specificity, physicochemical quality, and biological function require appropriate independent evidence. A predicted score is not an experimental measurement.

The scientific distinction follows the [EMA monoclonal-antibody characterisation guideline](https://www.ema.europa.eu/en/scientific-guidelines/development-production-characterisation-specifications-monoclonal-antibodies-related-products), which treats antigen binding and biological activity as characterisation questions. That guideline informs the evidence categories; these software tests do not establish regulatory compliance or experimental validation.
