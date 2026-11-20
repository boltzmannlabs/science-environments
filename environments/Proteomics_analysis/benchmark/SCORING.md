# Benchmark scoring guide

This guide explains the existing proteomics evaluators, their reference methods, and how to evaluate either saved run. The evaluator and helper source files define the exact calculations, edge cases, and rounding behaviour.

## Files and run layout

| Location or file | Purpose |
| --- | --- |
| `tasks/<task>/task.md` | Analysis question, input description, required outputs, and constraints. |
| `tasks/<task>/<input>` | Measurements supplied to the agent and evaluator. |
| `results/<task>/run_1/` and `run_2/` | Agent-produced matrices or differential results, `run_manifest.json`, and optional `analysis_report.txt`. |
| `benchmark/<task>/evaluation.py` | Validation, scientific metrics, reference comparisons, and weighted score calculation. |
| `ground_truth_log2.csv` | True abundance matrices for Tasks 01, 02, and 04. |
| `ground_truth.csv` | Changed-protein labels and true fold changes for Task 03. |
| `meta.json` | Synthetic benchmark metadata, present for Tasks 01–04 and loaded where required by the evaluator. |
| `quant_methods.py` | Task 04 reference protein-quantification methods. |
| `reference_pipelines.py` | Task-specific reference analysis helpers for Tasks 05–07. |
| `faults.json` | Task 06 sample-fault metadata. |
| `benchmark_results_run_1.json` and `benchmark_results_run_2.json` | Saved evaluation outputs for the corresponding run of that task. |

Truth and reference assets are evaluation-only resources. Agents performing an analysis must follow their task's constraints on access to hidden evaluation material. Saved benchmark reports and the other run's outputs are not inputs to the reference pipelines.

## Scoring mechanism

1. Read the task input, submitted run outputs, and required truth assets.
2. Apply mandatory checks for required files, schemas, identifiers, and task-specific validity conditions. A failed gate returns an overall score of **0** before scientific components are calculated.
3. Measure the submitted output against ground truth. Run reference methods where needed and measure them against the same truth.
4. Convert measurements into component scores and combine them using task-specific weights.

Scores range from 0 to 1. Many components are clipped at 1: **a score of 1.0 can mean meeting or exceeding a reference standard, not necessarily perfect accuracy or complete detection**. QC, sample handling, and bookkeeping also contribute. Optional written analysis reports are recorded but not scored.

### Ground truth and references

Ground truth defines correctness: synthetic true values and changed-protein labels, or known species composition and concentration ratios. Reference methods define attainable performance standards on those data. The agent need not reproduce their exact output, and neither saved agent run serves as the reference for the other.

Several error-based components normally use:

```text
score = clip((baseline_error - agent_error) / (baseline_error - reference_error), 0, 1)
```

Matching the baseline earns 0; matching or beating the reference earns 1. Baselines and references differ by component. The source handles cases where their errors are indistinguishable.

Several detection components use:

```text
detection_score = clip(agent_recall / reference_recall, 0, 1) * fdr_score
```

Additional integrity checks apply in Tasks 05–07. Strong recall alone cannot earn full detection credit when false discoveries are excessive.

### Interpreting false discoveries

A true positive is a correctly called changed protein; a false positive is an unchanged protein called significant. Precision is `TP / (TP + FP)`. Recall is the fraction of eligible changed proteins found. Observed false-discovery proportion (FDP) is `FP / (TP + FP)`; false discovery rate (FDR) is its expectation across repeated experiments.

Tasks 03, 05, and 06 allow sampling variability around the declared FDR threshold, using a tolerance based on that threshold and the number of scored calls. Task 07 also allows the selected reference's FDP plus 0.05 when that is larger. Exceeding the tolerance progressively reduces FDR credit; this is not a universal pass/fail check at exactly 5% observed FDP.

Report raw metrics alongside scores. RMSE and observed FDP are better when lower; precision, recall, and ranking performance are better when higher. A full bookkeeping score confirms the implemented consistency checks, not every aspect of statistical correctness.

## Task weights

| Task | Contributions to the overall score |
| --- | --- |
| 01 — Imputation | Integrity 15%; bookkeeping 15%; QC 25%; imputation 45%. |
| 02 — Normalization | Alignment 30%; biological preservation 25%; accuracy 15%; integrity 10%; imputation 10%; bookkeeping 10%. |
| 03 — Differential expression | Detection 30%; FDR control 25%; ranking 15%; effect sizes 10%; bookkeeping 20%. |
| 04 — Protein quantification | Protein-profile accuracy 40%; fold-change accuracy 35%; bookkeeping 25%. |
| 05 — Mixed proteome | Cleaning 10%; detection 25%; FDR control 20%; ranking 15%; fold changes 15%; bookkeeping 15%. |
| 06 — Sample QC and differential analysis | Sample-fault handling 35%; detection 20%; FDR control 15%; ranking 10%; fold changes 10%; bookkeeping 10%. |
| 07 — Low-abundance spike-in | Combined contrast performance 85%; cleaning 5%; bookkeeping 10%. |

### Task 01: QC, log2 transformation, and imputation

[Evaluator](01_proteomics_synthetic_imputation/evaluation.py)

- Integrity measures preservation of observed cells after log2 transformation, with a `1e-6` alteration tolerance.
- QC averages exclusion recall for designated low-confidence spike rows and retention of adequately measured non-spike proteins with at least three observed values.
- Imputation RMSE uses originally missing cells with available truth in retained proteins. Column-median imputation defines the baseline; the best of column median, row mean, KNN with five neighbours, and deterministic downshift imputation defines the reference. References use the same truth-covered retained rows as the scored output.
- Bookkeeping checks statuses, exclusion reasons, retained IDs, and manifest counts.

### Task 02: normalization

[Evaluator](02_proteomics_synthetic_normalization/evaluation.py)

- One global offset is ignored when comparing abundances with truth, allowing zero-centred or intensity-level-centred outputs.
- Alignment measures residual sample offsets. Accuracy measures offset-free RMSE on observed cells. No normalization defines the baseline; the better of mean and median centering supplies the reference for each component. Quantile normalization is diagnostic, not a reference target for these components.
- Biological preservation measures systematic fold-change bias and protein-specific distortion on complete rows, using reference allowances and fixed tolerances.
- Integrity checks within-sample ordering of observed values using Spearman correlation of at least 0.999.
- Missing-cell accuracy is compared with column-median, row-mean, and KNN imputation on median-centred data. Manifest consistency is scored separately.

### Task 03: differential expression

[Evaluator](03_proteomics_synthetic_differential_expression/evaluation.py)

- Hidden labels define changed and unchanged proteins; hidden fold changes define effect-size truth.
- Detection is recall relative to the empirical-Bayes moderated t-test at the agent's valid declared FDR threshold, capped at 1 and multiplied by the FDR score. Student and Welch tests are also reported as diagnostics.
- Ranking is average precision from raw p-values relative to the moderated reference, capped at 1.
- Effect-size credit combines RMSE relative to the input's plain mean-difference estimate and direction accuracy among correctly called changed proteins. With no true changes called, only the RMSE component is used.
- Bookkeeping checks thresholds, adjusted versus raw p-values, significance flags, and counts. The detection reference does not apply the agent's optional fold-change cutoff.

### Task 04: peptide-to-protein quantification

[Evaluator](04_proteomics_synthetic_protein_quantification/evaluation.py) · [Reference methods](04_proteomics_synthetic_protein_quantification/quant_methods.py)

- Each protein's mean across samples is removed before profile RMSE is calculated; arbitrary absolute protein levels are ignored.
- Fold-change RMSE compares Treated-minus-Control estimates with truth.
- Both components use summation of all peptide intensities, including shared peptides, as the baseline. The better of unique-peptide median polish and MaxLFQ-style estimation supplies the reference error for each component. Other methods are reported for comparison.
- Bookkeeping checks peptide and protein counts and method descriptions.

### Task 05: mixed human/E. coli proteome

[Evaluator](05_proteomics_end_to_end_mixed_proteome/evaluation.py) · [Reference pipelines](05_proteomics_end_to_end_mixed_proteome/reference_pipelines.py)

- Human groups are unchanged; E. coli groups increase threefold in H versus L, corresponding to `log2(3)`. Mixed and other-species groups are omitted from species-based discovery scoring.
- The recall denominator includes unflagged E. coli groups with at least two positive LFQ measurements in each condition.
- References compare no normalization, all-protein median normalization, and human-anchor normalization with moderated tests, BH at 0.05, and absolute fold-change cutoffs of 0 or 1. Detection uses the highest reference recall among pipelines with FDP no greater than 0.1, then applies the agent's FDR penalty.
- Ranking is recall at 98% precision divided by the fixed published target of 0.72, capped at 1. Recall at 95% precision is also reported.
- Fold-change credit equally assesses the human baseline and species separation, allowing the expert reference's absolute errors before applying additional penalties.
- P-value integrity checks can suppress detection, FDR, and ranking credit. Cleaning and manifest consistency contribute separately.

### Task 06: sample faults and differential analysis

[Evaluator](06_proteomics_end_to_end_real_world_qc/evaluation.py) · [Reference helpers](06_proteomics_end_to_end_real_world_qc/reference_pipelines.py)

- Protein truth follows the constant-human/threefold-E. coli design. The evaluator reconstructs a clean design using sample-fault metadata.
- Fault handling checks the duplicate L1/L4 pair, failed H4 run, and L3/H3 label swap. Correct reassignment earns full swap credit; excluding both swapped samples earns partial credit. Omitting good samples incurs additional penalties.
- Detection is relative to the clean-design expert reference and multiplied by the FDR score. Ranking uses recall at 98% precision relative to 0.72. A blindly labelled eight-sample pipeline is reported only as a diagnostic.
- Fold-change credit assesses human baseline and species separation with reference allowances. P-value integrity checks can suppress FDR, detection, and ranking credit.
- Bookkeeping checks cleaning counts, significance, sample usage and exclusions, and notes for changed samples.

### Task 07: UPS1 low-abundance spike-in

[Evaluator](07_proteomics_end_to_end_spike_in_low_abundance/evaluation.py) · [Reference pipelines](07_proteomics_end_to_end_spike_in_low_abundance/reference_pipelines.py)

- UPS1 groups identified by `_UPS` in FASTA headers are changed; unflagged background groups are unchanged. The recall denominator includes unflagged UPS1 groups with at least two positive measurements at the higher amount.
- References use strict observed-value testing, strict testing with a fold-change cutoff, a presence/absence extension, and downshift imputation. The highest-F1 reference is selected per contrast to calibrate detection and the reference-based FDP allowance.
- Detection is relative recall multiplied by the FDR score. P-value integrity is checked on test-based rows.
- Fold-change credit compares median UPS1 changes with the known ratio, allowing the smallest reference median error, and checks the background median against zero. Presence/absence rows may omit statistics but still contribute to discovery counts.

| Contrast | Higher amount | Lower amount | Expected log2 change | Weight within contrast total |
| --- | --- | --- | --- | --- |
| C1 | 25000 amol | 2500 amol | 3.322 | 25% |
| C2 | 5000 amol | 500 amol | 3.322 | 40% |
| C3 | 2500 amol | 500 amol | 2.322 | 35% |

Within each contrast, detection contributes 50%, FDR control 30%, and fold-change accuracy 20%:

```text
contrast_score = 0.50 * detection + 0.30 * fdr + 0.20 * fold_change
overall_score = 0.85 * (0.25 * C1 + 0.40 * C2 + 0.35 * C3)
              + 0.05 * cleaning + 0.10 * bookkeeping
```

## Running an evaluation

Run from the repository root after installing the dependencies in [ENVIRONMENT_SPEC.md](../ENVIRONMENT_SPEC.md). Use a separate Python process per evaluator: Tasks 05–07 have different helpers sharing the import name `reference_pipelines`.

| Task directory | Input filename under `tasks/<task>/` | `--truth` required? |
| --- | --- | --- |
| `01_proteomics_synthetic_imputation` | `raw_protein_intensities.csv` | Yes: `benchmark/<task>` |
| `02_proteomics_synthetic_normalization` | `raw_protein_intensities.csv` | Yes: `benchmark/<task>` |
| `03_proteomics_synthetic_differential_expression` | `protein_log2_normalized.csv` | Yes: `benchmark/<task>` |
| `04_proteomics_synthetic_protein_quantification` | `peptide_intensities.csv` | Yes: `benchmark/<task>` |
| `05_proteomics_end_to_end_mixed_proteome` | `proteinGroups.txt` | No |
| `06_proteomics_end_to_end_real_world_qc` | `proteinGroups.txt` | Yes: `benchmark/<task>` |
| `07_proteomics_end_to_end_spike_in_low_abundance` | `proteinGroups.txt` | No |

For example, evaluate either saved run of Task 01 by setting `RUN` to `run_1` or `run_2`:

```bash
TASK=01_proteomics_synthetic_imputation
RUN=run_1
python3 -B "benchmark/$TASK/evaluation.py" \
  --input "tasks/$TASK/raw_protein_intensities.csv" \
  --results "results/$TASK/$RUN" \
  --truth "benchmark/$TASK"
```

Task 07 does not need a separate truth directory:

```bash
TASK=07_proteomics_end_to_end_spike_in_low_abundance
RUN=run_2
python3 -B "benchmark/$TASK/evaluation.py" \
  --input "tasks/$TASK/proteinGroups.txt" \
  --results "results/$TASK/$RUN"
```

These commands print JSON without saving reports. `-B` disables Python bytecode writes. To save a fresh report, append `--out /path/to/new_report.json`, choosing a new destination: `--out` overwrites an existing file at that path. Evaluators read completed outputs; they do not execute agent analysis scripts.

## Reading saved reports

Open `benchmark/<task>/benchmark_results_run_1.json` or `benchmark_results_run_2.json` for the corresponding run. Inspect:

- `gate.passed` and `gate.errors` before interpreting `score`.
- `sections` for component scores, raw errors, counts, and consistency checks.
- `contrasts` for Task 07's per-comparison results.
- `weights` for aggregation rules, and task-specific reference fields for calibration diagnostics.

Do not interpret a score as the percentage of proteins correctly analysed. Compare runs of the same task using the same evaluator and report relevant raw metrics alongside aggregate scores. F1 can be calculated from discovery counts as an additional descriptive metric, but does not replace the existing score or directly enforce the declared FDR threshold.
