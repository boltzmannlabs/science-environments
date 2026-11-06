# Retro Environment — target-specific route audit

Research-prototype environment for auditing computational retrosynthesis of the target
`CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`.

This package contains a sanitized, reproducible analysis of 16 model-generated routes and a three-step review of `top0`. Start with the [achieved numbers and literature comparison tables](results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md), [paper catalog](benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md), [metric definitions](benchmark/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json), and [task objectives with actual outcomes](tasks/README.md). The catalog distinguishes papers, an inspected experimental reference for a different substrate, and non-matching patent hits.

It does **not** contain an experimentally validated synthesis, a transferable API credential, or the original account-scoped service export. For scientific interpretation see [research notes](../../research/retro_environment/research-notes.md), [references](../../research/retro_environment/references.md), [benchmark methodology](benchmark/README.md), and [status](STATUS.md).

## Unified task layout

```text
tasks/task-01-fluorinated-quinoline-retrosynthesis/       # overall objective, inputs, expected outcomes and phase documents
benchmark/task-01-fluorinated-quinoline-retrosynthesis/   # papers, source links, metric definitions and comparison evidence
results/task-01-fluorinated-quinoline-retrosynthesis/     # observed model outputs, numerical tables and DOCX
```

Use the same `task-NN-descriptive-topic` name in all three sections for each future study. The existing three phase documents belong to task-01-fluorinated-quinoline-retrosynthesis, not three separate target tasks.

## Structure

- `ENVIRONMENT_SPEC.md`, `MODELS_AND_TOOLS.md`, `STATUS.md`: scope, tool limits, and actual readiness.
- `results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json`: all 16 generated route trees represented as precursor-to-product steps and model-only yield fields.
- `results/task-01-fluorinated-quinoline-retrosynthesis/top0_validation.json`: selected-route forward/mapping/condition review, **not** experimental measurements.
- `results/task-01-fluorinated-quinoline-retrosynthesis/retro_benchmark_report.docx`: public report generated from the sanitized data, with structure images and evidence tiers.
- `scripts/derive_routes.py`: rebuild sanitized route summary from a separately authorized local raw JSON (never commit raw account data).
- `scripts/build_report.py`: reproduce the public DOCX using `python-docx` and `rdkit` if installed.
- `tests/test_results.py`: validate JSON and numerical consistency with standard-library unittest.

## Run

From the repository root:

```sh
python -m unittest discover -s environments/retro_environment/tests -v
python environments/retro_environment/scripts/derive_routes.py --input /path/to/authorized-scored-paths.json --output /path/to/derived-summary.json
```

The raw export is intentionally excluded. To rebuild the report, create an isolated Python environment and install `python-docx` and `rdkit` there; then run:

```sh
python environments/retro_environment/scripts/build_report.py
```

No live Boltzmann job is run by these scripts. See [specification](ENVIRONMENT_SPEC.md) and [tasks](tasks/README.md) for input expectations and reproducibility limits.
