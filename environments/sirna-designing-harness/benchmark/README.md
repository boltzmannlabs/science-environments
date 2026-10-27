# Benchmark and case-study evidence

This folder contains **historical reports and selected result tables**, not a clean independent experimental performance benchmark or freshly executed scientific analyses.

Start with [KRAS evidence](KRAS/README.md).

The KRAS snapshot covers the shared-target design, candidate audit, ranking sensitivity, experimental-dataset audit and literature comparison. Original artifacts are copied byte-identically with explicit provenance; large/raw/restricted-source artifacts remain external and are indexed. Nothing was regenerated, inferred, folded or screened again.

- Shared-target computational arm: completed historically.
- Biological status: **PARTIAL**; no newly qualified construct.
- Independent experimental benchmark: **BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET**.
- Mutation-selective arm: **BLOCKED_PENDING_MUTATION_SPECIFICATION**.

From the environment root, run `python3 scripts/run.py verify-benchmark` to check the included frozen snapshot. That is file/evidence verification, not a scientific rerun. Preserve copied reports as historical originals; add future cases in separate versioned folders rather than overwrite them.
