# Retro Environment — task-scoped route audits

Research-prototype workspace for two retrosynthesis tasks and a separate forward-prediction task. Task 01 audits the target
`CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`.

This package contains a sanitized, reproducible analysis of 16 model-generated routes and a three-step review of `top0`. Start with the [achieved numbers and literature comparison tables](results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md), [paper catalog](benchmarks/task-01-fluorinated-quinoline-retrosynthesis/papers.md), [metric definitions](benchmarks/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json), and [task objectives with actual outcomes](tasks/README.md). The catalog distinguishes papers, an inspected experimental reference for a different substrate, and non-matching patent hits.

It does **not** contain an experimentally validated synthesis, a transferable API credential, or the original account-scoped service export. For scientific interpretation see [research notes](../../research/retro_environment/research-notes.md), [references](../../research/retro_environment/references.md), [benchmark methodology](benchmarks/README.md), and [status](STATUS.md).

## Unified task layout

```text
tasks/task-01-fluorinated-quinoline-retrosynthesis/       # objectives and target structures
benchmarks/task-01-fluorinated-quinoline-retrosynthesis/  # linked benchmark evidence
results/task-01-fluorinated-quinoline-retrosynthesis/     # route outputs and comparisons
tasks/task-02-impurity-retrosynthesis/
benchmarks/task-02-impurity-retrosynthesis/
results/task-02-impurity-retrosynthesis/
tasks/task-03-indole-forward-prediction/
benchmarks/task-03-indole-forward-prediction/
results/task-03-indole-forward-prediction/
tasks/task-04-pdnhc-suzuki-miyaura-optimization/
benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/
results/task-04-pdnhc-suzuki-miyaura-optimization/
```

Use the same `task-NN-descriptive-topic` name in all three sections. `benchmarks/` is the sole benchmark directory; source catalogs and metrics were moved there from the former singular directory, and maintained scripts and internal links now use the new path. See the [task-folder standard](TASK_STRUCTURE.md). The three Task 01 phases are not separate target tasks.

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

## Task 02 — Impurity retrosynthesis and literature benchmarking

[Task definition](tasks/task-02-impurity-retrosynthesis/README.md), [literature and metrics](benchmarks/task-02-impurity-retrosynthesis/README.md), [results](results/task-02-impurity-retrosynthesis/README.md), and [gaps to outperform literature](results/task-02-impurity-retrosynthesis/gaps_and_improvement_plan.md). This case is separate from Task 01's target; matching task folder names link their respective evidence.

## Task 03 — Indole forward prediction

[Task and supplied inputs](tasks/task-03-indole-forward-prediction/README.md) · [Literature benchmark](benchmarks/task-03-indole-forward-prediction/README.md) · [Saved results](results/task-03-indole-forward-prediction/README.md). This is a forward-reaction evaluation, not a retrosynthesis run. Candidate files are transcribed derivatives, not original machine-readable service outputs.

## Task 04 — Pd-NHC Suzuki–Miyaura blind optimization

[Task](tasks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Benchmark](benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Results](results/task-04-pdnhc-suzuki-miyaura-optimization/README.md). Multi-tool blind product prediction, Pd-NHC-constrained design and loading-aware frozen-yield analysis; no experimental validation.
