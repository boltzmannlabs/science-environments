# Proteomics Analysis Benchmarks

A collection of seven label-free proteomics analysis tasks, their benchmark evaluators, and example analysis outputs. The tasks cover common steps in quantitative proteomics, from processing protein and peptide intensity tables to differential abundance analysis.

## Tasks

| Task | Analysis | Input data |
| --- | --- | --- |
| 01 | Synthetic LFQ quality control, log2 transformation, and missing-value imputation | Included in `tasks/01_proteomics_synthetic_imputation/` |
| 02 | Synthetic LFQ log2 transformation, sample normalization, and imputation | Included in `tasks/02_proteomics_synthetic_normalization/` |
| 03 | Differential abundance analysis of normalized synthetic LFQ data | Included in `tasks/03_proteomics_synthetic_differential_expression/` |
| 04 | Protein abundance estimation from peptide-level LFQ data | Included in `tasks/04_proteomics_synthetic_protein_quantification/` |
| 05 | Mixed human/*E. coli* benchmark: high versus low spike-in | Included in `tasks/05_proteomics_end_to_end_mixed_proteome/` |
| 06 | Real-world-style QC and differential abundance analysis, including sample issues | Included in `tasks/06_proteomics_end_to_end_real_world_qc/` |
| 07 | UPS1 low-abundance spike-in comparisons across three contrasts | Included in `tasks/07_proteomics_end_to_end_spike_in_low_abundance/` |

Each task directory contains a `task.md` describing the experiment, expected outputs, and analysis constraints. The benchmark directory contains evaluators, task-specific truth and reference assets, and benchmark reports for both runs. The results directory contains agent-produced analysis artifacts, manifests, and reports, separated by task and run.

## Repository layout

```text
tasks/<task>/
  task.md
  <input data>
results/<task>/
  run_1/                         Agent outputs for Run 1
  run_2/                         Agent outputs for Run 2
benchmark/
  SCORING.md                     Evaluation methods and scoring interpretation
  <task>/
    evaluation.py
    <truth and reference assets, depending on the task>
    benchmark_results_run_1.json
    benchmark_results_run_2.json
```

See [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) for the recommended Python environment and task-specific package requirements.

## Results

Run 1 (`run_1`) used **gpt-6-sol**, and Run 2 (`run_2`) used **discoveryrsi**, both with the same agent framework.

Each task was executed once per model. These results compare individual executions and should not be interpreted as a definitive model ranking.

Analysis outputs are organized under `results/<task>/run_1/` and `results/<task>/run_2/`. Depending on the task, these include processed log2 matrices, differential abundance tables, protein-level quantification matrices, quality-control tables, `run_manifest.json` metadata, and `analysis_report.txt` summaries.

The matching evaluator reports are stored separately as `benchmark/<task>/benchmark_results_run_1.json` and `benchmark_results_run_2.json`. These JSON files contain benchmark scores and diagnostics; they are evaluation outputs, not reference data used to score the other run.

The manifests record processing choices and bookkeeping counts. The reports describe key assumptions and limitations. Treat these as example analyses: they are not a substitute for reviewing the data, assumptions, and task-specific evaluation criteria.

## Reproducing or evaluating an analysis

There is no single project-wide runner or dependency lockfile. Work through one task at a time:

1. Read the task's `task.md` and check that its required input data are available.
2. Select `results/<task>/run_1/` or `results/<task>/run_2/` and check its required output files and manifest. Analysis scripts are not required to score completed outputs.
3. Install the evaluator dependencies described in [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md).
4. Run `benchmark/<task>/evaluation.py`, pointing `--results` at the selected run folder. Tasks 01–04 and 06 also require `--truth`; Tasks 05 and 07 derive truth from input annotations and experiment design. See [SCORING.md](benchmark/SCORING.md#running-an-evaluation) for commands and input paths.

All seven task input files are included in their respective task directories. A complete evaluation may still require evaluation assets specified by the evaluator. Follow the constraints in each `task.md` when using benchmark data.

## Scoring and interpretation

Each task receives a score between **0 and 1**. Evaluators first check required files, schemas, identifiers, and task-specific validity conditions. A mandatory validation failure produces an overall score of **0** before performance components are calculated. Outputs that pass are scored using a task-specific weighted combination of scientific performance and consistency checks.

Many scientific-performance components are **relative to reference methods or pipelines**. Both the agent output and reference outputs are assessed against ground truth: hidden values or labels for synthetic data, or known sample composition for the real-data benchmarks. The agent is then credited according to its performance relative to the reference standard; it does not need to reproduce the reference's exact output. Reference methods are computed during evaluation, rather than using the example agent outputs in `results/` as the standard.

For example, some error-based components use:

```text
component score = (baseline error - agent error) / (baseline error - reference error)
```

The result is clipped to the range 0–1. Other components compare detection or ranking performance with a reference, while format, bookkeeping, sample handling, and false-discovery checks use direct rules or tolerances. There is no single formula shared by every component.

**A score of 1.0 does not necessarily mean perfect accuracy or complete detection.** It can mean that an analysis matched or exceeded the reference standard. Excessive false discoveries can reduce both the false-discovery-control component and detection credit. Optional `analysis_report.txt` files are recorded but do not affect scores.

Read each `benchmark_results_run_1.json` or `benchmark_results_run_2.json` alongside its aggregate score: it records validation outcomes, component scores, weights, and task-specific diagnostics. Compare absolute metrics such as RMSE, precision, recall, and observed false-discovery proportion as well as the overall score.

See the [scoring guide](benchmark/SCORING.md) for benchmark file descriptions, task-specific metrics and weights, reference methods, and evaluation commands. The evaluator and helper code remain the source of truth for the exact calculations.

## Data and interpretation

These analyses use mass-spectrometry protein or peptide intensity measurements. Missing values may reflect nondetection, protein groups may map to multiple proteins, and small replicate counts limit statistical certainty. Normalization, filtering, and imputation choices can change results; consult each task's report and manifest before interpreting its output.
