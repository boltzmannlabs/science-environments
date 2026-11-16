# Task - 02 results: ranolazine ER investigation and benchmark

## Outcome

The computational investigation completed. The literature-summary rerun reproduced the published LOFO baseline metrics and returned no verifier findings. A training-only model comparison found modest error reductions for pointwise median on the pH 6.8 group and Weibull on the separate HCl group. The candidate screen produced a higher arbitrary scenario score for `grid_C84_B42_H8.5` than F8 under the assumed 500 mg research scenario, but did not demonstrate a better median release profile or a closer match to the paper-reported F8 endpoint. Actual recalled-lot performance remains not evaluated.

## Data and result classes

- Literature-reported: published/patent summary curves and F8’s author-reported 99.5% at 24 h. No replicate-unit data were available.
- Derived: LOFO predictions and errors from those summaries, with entire profiles withheld.
- Synthetic: 24 fictional Weibull-generated batches for grouped software checks.
- Assumption-conditional predicted: 117 hypothetical research formulations evaluated under 256 invented parameter draws each.
- Measured Ajanta/Glenmark lot data: none available in this investigation.

## Key comparisons

- pH 6.8 mean baseline: MAE/RMSE 7.581/8.833 pp; pointwise median: 6.762/8.263 pp.
- HCl mean baseline: 12.733/14.633 pp; Weibull-on-training-mean: 12.544/14.449 pp.
- Selected scenario candidate vs F8 at matched assumed hardness: score 0.7280 vs 0.5122 and toy-goal fraction 86.72% vs 61.33%; simulated 2 h/24 h medians are 19.576%/90.986% vs 20.054%/91.355%.
- Synthetic fixture: Weibull test MAE/RMSE 1.63/1.84 pp vs first-order 3.18/3.67 pp; Weibull was the generating law.

All scientific caveats and full comparisons are in the [Task-02 benchmark report](../../benchmark/Task%20-%2002%20-%20Ranolazine%20ER%20Tablet%20Dissolution%20Investigation/README.md). Machine-readable outputs are adjacent in this folder. Global release/software validation receipts remain in [original validation JSON](../../../formulation_dissolution/results/validation.json) and [original validation log](../../../formulation_dissolution/results/validation.txt); historical test counts in those receipts describe their original execution environment.

## Files

- `literature_model_comparison.json` — fold-by-fold and nested model-selection output.
- `literature_model_comparison.csv` — macro metrics.
- `existing_lofo_rerun.json` — saved earlier rerun of the original published LOFO runner (not re-executed for this publication) and its verifier result.

## Publication provenance

The comparison JSON/CSV are preserved byte-for-byte from the earlier saved run. In `existing_lofo_rerun.json`, only three personal absolute output paths were replaced with `historical-run://published_benchmark_rerun/` locators; these are provenance identifiers, not downloadable files. All numerical values, input hashes and verifier findings are unchanged. Publication checks and the existing Task-01 test execution are recorded in [publication_validation.json](publication_validation.json) and [publication_tests.txt](publication_tests.txt). These checks do not rerun or independently validate the historical model-comparison study.

## Task-scoped structure validation

Dedicated configuration, source, scripts, tests, documentation, research and decision folders are now mapped in the task registry. [structure-v1 validation](structure-v1/repository_validation.json) records the actual integrated tests and Task-01 regression replay; [test log](structure-v1/repository_tests.txt), [Task-02 archive verification](structure-v1/verification.json) and [runner receipt](structure-v1/run_receipt.json) are separate from the earlier scientific outputs. The archive verifier checks saved hashes/arithmetic only; it does not reproduce fitting or validate a product.

## Decision boundary

This is an evidence-limited computational result. It does not establish that any candidate improves ranolazine ER dissolution experimentally, meets a regulated release specification, explains a recall, or is suitable for commercial manufacture. A product-level evaluation requires an authorized method/version and limits, source-linked unit profiles for the lot and appropriate comparators, plus prospective quality-reviewed testing.
