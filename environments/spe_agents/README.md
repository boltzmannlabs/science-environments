# SPE Agents Environment

**Status:** Validated (benchmark harness and recorded qualification evidence)

This environment contains the specialist single-point-energy (SPE) agent
contracts, frozen task packets, evaluators, benchmark reports, and reproducible
examples. It is organized as a scientific environment under the repository
layout defined in `CONTRIBUTING.md`.

## Scope

- 18 specialist SPE agent contracts and task definitions.
- Frozen benchmark cases and evaluator rules.
- General, specialist-assisted, and conditional-routing evidence where available.
- Reproducibility metadata, failure categories, runtime, and token-cost fields.

## Validation

Run the environment tests from this directory:

```bash
pytest -q tests
```

The reports distinguish observed engine results from deterministic fixture
checks. They do not claim execution for a backend or agent runtime that was
not available.

## Deliverables

- [`ENVIRONMENT_SPEC.md`](ENVIRONMENT_SPEC.md)
- [`REFERENCES.md`](REFERENCES.md)
- [`tasks/`](tasks/)
- [`results/`](results/)
- [`reports/`](reports/)
