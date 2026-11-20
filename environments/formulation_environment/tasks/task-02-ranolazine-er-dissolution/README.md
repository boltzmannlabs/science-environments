# Task - 02: Ranolazine ER Tablet Dissolution Investigation and Literature Benchmark

Status: computational investigation and retrospective comparison completed; recalled-product prediction and experimental validation not evaluated.

## Objective

Investigate whether available public and literature information can explain or quantify the reported ranolazine extended-release dissolution concern, assess which empirical dissolution approaches perform better on the available literature summaries, and document whether an assumption-conditional 500 mg research-formulation screen supports a candidate for future testing.

The task must keep separate: (1) public recall identity/reason, (2) literature-reported summary curves/endpoints, (3) synthetic software fixtures, and (4) predictions from assumed scenario parameters. It must not infer the Ajanta lot’s dissolution values, approved specification, causal failure mechanism, or a validated product improvement without controlled records and measured data.

## Overall task and scope

Public recall reporting identifies Ajanta ranolazine ER lot DJ25134 (1000 mg) as below specification, but the available record does not provide individual-unit dissolution data or the approved method and acceptance limits. A separate Glenmark 500 mg recall is a different product/lot and is not used as a proxy. The investigation therefore examined what can be learned from public-literature curve summaries and reproducible simulations while explicitly abstaining from lot-level QC conclusions.

This Task-02 record covers the work already run: source/evidence inventory, method-separated published-summary benchmarking, empirical kinetic-model checks, a synthetic grouped-holdout software exercise, and a bounded 500 mg research-prototype formulation grid with matched scenario controls. It does not authorize physical experiments, batch changes, or a manufacturing recommendation.

## Questions addressed

1. What quantitative recall-lot measurements and controlled specifications are available? (None of the required unit-level Ajanta data were obtained.)
2. How do simple and empirical curve estimators compare when a whole literature summary formulation is withheld?
3. Does model choice differ between the pH 6.8 patent-example group and the separate HCl sustained-release group?
4. How did the hypothetical research grid rank its candidate, and do matched F8/F1 and zero-effect controls support interpreting that ranking as release improvement?
5. Which computations are reproducible software demonstrations versus evidence of product performance?

## Approach actually followed

1. Preserve the inherited formulation implementation and source records; do not replace missing values with synthetic values.
2. Keep literature groups stratified by method/source. Withhold complete curves and score their nonzero shared timepoints using per-profile MAE, RMSE, and signed bias.
3. Compare pointwise mean/median baselines and zero-order, Higuchi, first-order, and Weibull curves fitted only to the training-profile mean. Also run nested grouped model selection using only each outer training set.
4. Separately report the existing six-model in-sample reconstruction and Weibull-generated synthetic batch holdout. Do not treat same-curve fit error or a Weibull-generated fixture score as external ranolazine prediction accuracy.
5. Review the 117 feasible 500 mg research-prototype candidates under 256 assumed draws each, then compare the selected candidate and literature F8/F1 at matched assumed hardness using shared draws. Include sign sensitivity and the zero-effect negative control.
6. Record evidence limitations and software test results; do not extrapolate the 500 mg research case to Ajanta’s 1000 mg lot.

## Main outputs

- The pH 6.8 median baseline yielded LOFO MAE/RMSE 6.762/8.263 pp versus the pointwise mean’s 7.581/8.833 pp. The source transcription remains independently unverified.
- The HCl Weibull-on-training-mean estimator yielded MAE/RMSE 12.544/14.449 pp versus mean 12.733/14.633 pp across only three related patent summaries. The Table 4 sequence was checked against primary patent HTML; full method details and unit variability remain absent.
- Nested selection results were pH 6.8 MAE/RMSE 7.307/8.668 pp and HCl (inner-RMSE selection) 12.329/14.395 pp. These are small same-publication samples, not independent validation.
- The assumed-scenario winner was `grid_C84_B42_H8.5`; the toy-goal fraction was 86.72% versus 61.33% for research F8 under shared invented draws. These are not tablet pass rates. At the compared scenario settings, the selected mixture’s median release was slightly below F8 at both 2 h and 24 h; its predicted F8 24 h endpoint also differed from the literature-reported 99.5% by about 10 pp at the paper-reported hardness.
- The synthetic batch experiment favored Weibull on data generated from a Weibull law; this validates computation contracts only.

Detailed side-by-side fold/model values are in [Task-02 benchmark](../../benchmark/task-02-ranolazine-er-dissolution/README.md); saved output and evidence labels are in [Task-02 results](../../results/task-02-ranolazine-er-dissolution/README.md).

## Completion criteria and limitations

Completed for this computational task: source groups and evidence labels retained; literature benchmark rerun and independently checked; candidate ranking compared under matched assumptions; negative controls documented; tests executed in the available base environment.

Not completed / not evaluated: controlled Ajanta method and limits; lot DJ25134 individual-vessel curves; matched passing-lot controls; independent-source holdout; prospective experiment; predictive calibration; compatibility/stability testing; causal attribution; product QC attainment; validated formula improvement.

References and provenance: [research notes](../../../formulation_dissolution/research-notes.md), [reference list](../../../formulation_dissolution/references.md), and [original implementation provenance](../../../formulation_dissolution/SOURCE_PROVENANCE.json).

## Publication and execution status

The investigation remains archived. `scripts/shared/run_task.py --task "Task - 02"` now dispatches a task-specific archive verifier: it checks hashes and saved aggregate arithmetic, not new fitting or product performance. Original ranolazine algorithms and historical evidence remain in [formulation_dissolution](../../../formulation_dissolution/README.md), unchanged. Tracking: [issue #197](https://github.com/boltzmannlabs/science-environments/issues/197).

## Task-owned folders throughout the repository

- [Configuration](../../config/task-02-ranolazine-er-dissolution/README.md)
- [Source package](../../src/formulation_environment/task_02_ranolazine_er_dissolution/README.md)
- [Scripts](../../scripts/task-02-ranolazine-er-dissolution/README.md)
- [Tests](../../tests/task_02_ranolazine_er_dissolution/README.md)
- [Documentation and ownership map](../../docs/task-02-ranolazine-er-dissolution/README.md)
- [Research notes](../../../../research/Task%20-%2002%20-%20Ranolazine%20ER%20Tablet%20Dissolution%20Investigation/research-notes.md) and [references](../../../../research/Task%20-%2002%20-%20Ranolazine%20ER%20Tablet%20Dissolution%20Investigation/references.md)
- [Architecture decision](../../../../docs/decisions/Task%20-%2002%20-%20Ranolazine%20ER%20Tablet%20Dissolution%20Investigation/README.md)

The benchmark and results folders retain the same descriptive task name. Python source/tests use `task_02_ranolazine_er_dissolution` for valid imports and discovery; the registry maps this name explicitly. Task-01 content is not moved or pooled.
