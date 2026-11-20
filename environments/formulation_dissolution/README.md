# Formulation Dissolution

**Lifecycle: In Progress — executable software, not experimentally validated.** This integrates the existing evidence-first ranolazine ER investigation, dissolution-model comparison and explicitly synthetic formulation scenarios. It does not establish a recalled lot's formula, cause, approved QC limits or validated replacement formulation.

Tracking: [issue #51](https://github.com/boltzmannlabs/science-environments/issues/51). Maintainer and scientific reviews remain outstanding. Repository license selection is pending.

## Implemented

- Persistent episode state, typed actions/observations, provenance, budgets and deterministic composition/dose/unit/process validation.
- Six bounded local specialist functions; an approved-callable registry with no live scientific backend configured. Compatibility/stability preserve supplied findings or abstain.
- OpenPKFlow 2.9.0 fits: Weibull, first-order, zero-order, Higuchi, Korsmeyer–Peppas and Hixson–Crowell. Same-curve literature fits are reconstruction only; separate synthetic batches exercise grouped holdout.
- A 500 mg / 695 mg research-prototype grid, Monte Carlo assumptions, Pareto analysis, sensitivity and zero-effect controls. A bounded wrapper records every feasible candidate and refuses to overwrite runs.
- Context/time/unit-gated comparison of supplied predictions and experimental profiles, with MAE/RMSE/bias and conditional mathematical f1/f2. No regulatory similarity decision or actual measured-profile evaluation is claimed.

## Install and execute

From this directory, use a dedicated virtual environment. Python >=3.10 is declared; integration checks ran on Python 3.14.7, Linux, CPU only. No GPU, credentials or LLM is needed locally.

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[simulation,test]'
.venv/bin/python -m pytest -q
.venv/bin/python scripts/run_simulation.py --config configs/environment.yaml --out .runs/example
.venv/bin/python scripts/evaluate_results.py --run .runs/example
.venv/bin/python -m evaluation.six_model_pipeline --literature data/processed/literature_profiles.json --out .runs/six-model
.venv/bin/python -m evaluation.six_model_verifier --result .runs/six-model/six_model_results.json --fixture .runs/six-model/synthetic_batch_fixture.json --out .runs/six-model/verification.json
.venv/bin/python scripts/evaluate_results.py --six-model .runs/six-model
```

Use a new output directory on each run. The default configuration preserves missing experimental observations as null. Quantiles and optimized scores are conditional on invented parameter ranges; they are not measured release values or calibrated predictive intervals.

To exercise the inherited selection benchmark and commercial-lot abstention:

```bash
.venv/bin/python -m evaluation.exploratory_selection_benchmark --config configs/exploratory_ranolazine_500.json --scenario .runs/example/scenario.json --out .runs/example/selection.json
.venv/bin/python -m cli solve --config configs/task.yaml --mode predict
.venv/bin/python -m cli benchmark --config configs/benchmark.yaml --track published
```

The commercial prediction command should report `insufficient_data`. The published benchmark writes into `data/processed/published_benchmark/`, not a laboratory record. `import-history` is an optional networked operation that writes processed history and may fetch openFDA; it is not part of the offline quickstart. Its archive roots are null until explicitly configured for authorized local files.

Installed commands: `formulation-gym` (legacy triage), `formulation-history` (history CLI), `formulation-simulate` (bounded scenario runner). The wheel contains code; configs/data/schemas/tasks remain checkout assets. Pass explicit paths outside this directory. Base-package operation uses the standard library; `python -m unittest discover -s tests -v` explicitly skips simulation-only tests when OpenPKFlow is absent.

## Layout

```text
formulation_dissolution/
  README.md  ENVIRONMENT_SPEC.md  STATUS.md  MODELS_AND_TOOLS.md
  pyproject.toml  SOURCE_PROVENANCE.json  THIRD_PARTY_NOTICES.md
  environment/   state, actions, observations, budgets
  agents/        bounded local specialist functions
  models/        nearest-mixture baseline, ranker, uncertainty helpers
  tools/         composition checks, history, callable registry, fixture controller
  evaluation/    dissolution fits, scenarios, benchmarks and auditors
  configs/       real task/scenario/benchmark configurations
  schemas/       JSON record contracts
  scripts/       simulation, evaluation and release checks
  tasks/         task definitions and acceptance criteria
  benchmark/     benchmark track configuration
  data/          public-source snapshots and bounded regression artifacts
  results/       executed integration receipt and historical summary
  tests/ docs/ skills/
  run.py  cli.py  simulation.py  import_fda.py  import_dailymed.py
```

The proposed src layout is adapted to reuse the original flat packages. Do not install these generic `agents`, `tools`, `models`, `environment` and `evaluation` package names alongside unrelated same-name packages; use an isolated virtualenv. No duplicate modeling engine or empty compatibility/stability/PDE module is added. Native Agent-Scientist plugin registration is not implemented.

## Documentation and evidence

- [Specification](ENVIRONMENT_SPEC.md), [model/tool inventory](MODELS_AND_TOOLS.md), [status](STATUS.md).
- [Tasks](tasks/README.md), [benchmarks](benchmark/README.md), [tests](tests/README.md), [results](results/README.md).
- [Research notes](../../research/formulation_dissolution/research-notes.md), [references](../../research/formulation_dissolution/references.md).
- Historical investigation notebooks remain in `docs/` and the pre-existing report files. Their old paths, access statements and test counts describe the source run; current status/specification supersede them. Agent-review transcripts remain local-only and are indexed by source hashes, not bundled as datasets.

Public FDA/DailyMed records establish identity context, not unit-level dissolution. The pH 6.8 transcription remains independently unverified; the separate HCl patent Table 4 had a primary-HTML sequence check. Neither is the Ajanta controlled QC method. Do not pool methods, transfer a 500 mg research result to a 1000 mg recalled lot, or infer physical mechanism from empirical fit. Independent measured data, calibration, confirmatory experiments and domain review remain necessary.
