# SPE Agent Scientist environment

This directory contains the runnable SPE environment adapters, schemas, and
Agent Scientist bridge entry points. It is the implementation-side companion
to the benchmark package in `science-benchmarking/benchmarks/spe`.

## Reproducible local check

```bash
python -m pip install -e .
pytest -q tests/test_adapters.py tests/test_evaluation.py
```

The bridge requires an explicitly configured Agent Scientist provider. No
credentials are committed here.

## Scope

This release packages the tested SPE implementation and its interfaces. It
does not claim that every agent is production-qualified; qualification results
and limitations are maintained in the benchmarking repository.
