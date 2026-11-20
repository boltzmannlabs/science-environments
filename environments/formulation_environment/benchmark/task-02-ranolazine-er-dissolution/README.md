# Task - 02 benchmark: literature-summary curve comparison

This benchmark compares descriptive whole-profile holdouts within two source/method groups. Lower error is better. MAE, RMSE, and bias are percentage points (pp), macro-averaged over profile-level scores. Zero-time anchors are excluded. These are not independent-study validations and do not predict Ajanta lot DJ25134.

## pH 6.8 group — six related patent-example summaries

| Training-only estimator | Macro MAE (pp) | Macro RMSE (pp) | Macro bias (pp) |
|---|---:|---:|---:|
| Pointwise arithmetic mean | 7.581 | 8.833 | 0.000 |
| Pointwise median | 6.762 | 8.263 | +0.905 |
| Zero-order fit to training mean | 14.985 | 16.772 | −9.688 |
| Higuchi fit to training mean | 6.933 | 8.271 | −0.812 |
| First-order fit to training mean | 9.900 | 11.694 | −3.381 |
| Weibull fit to training mean | 7.195 | 8.596 | −0.134 |

The pointwise median was best on this small LOFO set: approximately 10.8% lower MAE and 6.5% lower RMSE than the pointwise-mean baseline. Higuchi was close, but the median had slightly lower RMSE (8.263 vs 8.271 pp). The numeric pH 6.8 table was transcribed from a supplied specification and has not been independently verified; all examples share one patent source.

## HCl group — three SR summaries from US6525057B2 Table 4

| Training-only estimator | Macro MAE (pp) | Macro RMSE (pp) | Macro bias (pp) |
|---|---:|---:|---:|
| Pointwise arithmetic mean / median | 12.733 | 14.633 | 0.000 |
| Zero-order fit to training mean | 24.046 | 27.484 | −15.864 |
| Higuchi fit to training mean | 12.582 | 15.397 | −2.329 |
| First-order fit to training mean | 15.033 | 17.055 | −1.279 |
| Weibull fit to training mean | 12.544 | 14.449 | −0.479 |

The Weibull grid fit was best in un-nested LOFO, with about 1.5% lower MAE and 1.3% lower RMSE than the mean baseline. The numeric Table 4 sequence was checked against primary patent HTML, but unit variability and several method/strength details are unavailable. This HCl track is not pooled with pH 6.8.

## Nested model-selection check

| Group / policy | Outer-fold MAE (pp) | Outer-fold RMSE (pp) | Selected model behavior |
|---|---:|---:|---|
| pH 6.8, choose by inner RMSE | 7.307 | 8.668 | Higuchi in 5 of 6 outer folds; median in 1 |
| pH 6.8, choose by inner MAE | 7.307 | 8.668 | Same selections on these data |
| HCl, choose by inner MAE | 12.582 | 15.397 | Higuchi in all 3 outer folds |
| HCl, choose by inner RMSE | 12.329 | 14.395 | Weibull in 2 folds; mean in 1 |

Selection is confined to each outer training set. With only 6 and 3 source-related profiles, nested results remain unstable exploratory estimates, not a qualified model-selection policy.

## Research formulation scenario — separate from literature curve benchmark

| Comparison | Selected C84/B42/H8.5 | F8 at same assumed hardness | Interpretation |
|---|---:|---:|---|
| Weighted toy score | 0.7280 | 0.5122 | Arbitrary configured score, not release accuracy |
| Assumed draws meeting 2 h/24 h toy goals | 222/256 (86.72%) | 157/256 (61.33%) | Synthetic scenario fraction, not QC pass probability |
| Simulated median release at 2 h | 19.576% | 20.054% | Selected lower by 0.478 pp |
| Simulated median release at 24 h | 90.986% | 91.355% | Selected lower by 0.369 pp |

At the paper-reported F8 hardness, simulated 24 h medians were 89.381% (first-order) and 89.469% (Weibull), compared with the literature-reported F8 endpoint of 99.5%. The endpoint was already inspected, there is no underlying replicate curve in the benchmark, and the scenario inputs are assumed. Thus the score-selected candidate does not demonstrate a closer literature match or improved measured formulation performance. In the zero-effect control, compared candidate profiles and toy-goal fractions became identical; the arbitrary mass preference could still change scores.

## Reproducibility and source files

- [literature_model_comparison.json](../../results/task-02-ranolazine-er-dissolution/literature_model_comparison.json): per-profile folds, metrics, nested model selections, and source hash.
- [literature_model_comparison.csv](../../results/task-02-ranolazine-er-dissolution/literature_model_comparison.csv): compact macro comparison table.
- [existing_lofo_rerun.json](../../results/task-02-ranolazine-er-dissolution/existing_lofo_rerun.json): rerun of the existing published LOFO runner with verifier findings.
- Existing kinetic fit, synthetic holdout, and candidate artifacts remain under [the original ranolazine data folder](../../../formulation_dissolution/data/processed/README.md) with their source labels and hashes.
- Published references and source-verification details: `../../../formulation_dissolution/references.md`.

Scientific boundary: no measured unit-level dissolution dataset or approved Ajanta QC procedure was available. Do not interpret scenario fractions, literature summary curves, or synthetic fixture errors as product performance.
