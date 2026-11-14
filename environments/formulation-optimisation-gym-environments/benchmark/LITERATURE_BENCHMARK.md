# Literature benchmark of the exploratory ranolazine ER simulation

Status: external literature sanity check only; NOT empirical validation, calibration, or a Glenmark-product prediction.

## Question and benchmark rule

Does the existing, unfitted scenario model reproduce published ranolazine research-tablet observations? Only directly reported values from the identified papers are considered. Do not digitize questionable graphs or fit/relabel generated curves as measurements. Report absolute endpoint discrepancy for the single usable numerical endpoint, but do not report R², RMSE, or calibrated uncertainty from n=1. Literature tests here are independent source comparisons, not an authorized QC acceptance test.

## Evidence reviewed

1. Alladi Saritha and Rebecca Sanjana, “Formulation Development and Invitro Evaluation of Ranolazine Extended Release Tablets,” Indo American Journal of Pharmaceutical Sciences 5(1), 682–687 (2018), DOI: [10.5281/zenodo.1170150](https://doi.org/10.5281/zenodo.1170150). Zenodo metadata identifies open access and CC BY 4.0. The original PDF downloaded for this check had SHA-256 `3619141b00d0bd7e895cfa452ecba94554ea37bdf8724b24bdd1c296eed9c706`, matching the project catalog. The paper reports F8 99.5% release at 24 h in the abstract; its F8 composition is 500 mg API, 105 mg Compritol, 35 mg Carbopol 934, 25 mg Avicel PH101, 10 mg Povidone K30, 5 mg Aerosil, and 15 mg titanium dioxide (695 mg total). Reported F8 hardness is 9.3 ± 0.04 kg/cm². The dissolution method is described as 900 mL 0.1 N HCl for 2 h, then pH 6.8 phosphate buffer, 37 ± 0.5 °C, 50 rpm to 24 h, with absorbance at 271 nm. These are authors' reported research-study details—not controlled Glenmark records. The paper's own model-fit reporting is internally inconsistent: Table 4 gives F8 Higuchi R² 0.976 and Peppas 0.986, while later prose reports Higuchi 0.989 and Peppas 0.991. Do not treat the reported similarity-factor claim as independently reproduced.

2. Bharathi Arigela et al., “Formulation and Evaluation of Ranolazine Extended Release Tablets,” Indo American Journal of Pharmaceutical Sciences 5(7), 6445–6453 (2018), DOI: [10.5281/zenodo.1311884](https://doi.org/10.5281/zenodo.1311884). The Zenodo record reports CC BY 4.0 and the locally checked PDF hash matches `a1b666d1c6ef13c3519c778ecb977001e5936389f796067aede0534ec0ec39c7`. Its Table 6 extraction has inconsistent/missing entries across time rows and a nonmonotonic reported profile. Without independently checking the original table's cell alignment/underlying data, no Table 6 values were admitted to numeric scoring, fitting, or holdout evaluation. This is an explicit curation exclusion, not evidence that the study failed.

## Quantitative endpoint comparison (study 1, F8 only)

Existing OpenPKFlow 2.9.0 scenario output at the literature recipe and literature-reported F8 hardness gives:

| Quantity at 24 h | First-order scenario | Weibull scenario |
|---|---:|---:|
| Scenario median (% released) | 89.3809 | 89.4693 |
| Scenario 5th–95th percentiles (%) | 78.7397–96.4847 | 79.7971–96.5522 |
| Published F8 abstract claim (%) | 99.5 | 99.5 |
| Absolute median-to-claim difference (percentage points) | 10.1191 | 10.0307 |
| Claim outside scenario 5th–95th spread? | Yes | Yes |

These percentiles are Monte Carlo quantiles over stipulated, unverified parameter ranges, not confidence or predictive intervals. Both central scenario curves under-shoot the single author-reported endpoint by about 10 percentage points; even their simulated 95th percentiles remain below 99.5%. This is a mismatch that should reduce confidence in the current assumptions—not a reason to tune to that point, assert literature error, or claim model failure. The manuscript does not provide the replicate-level numerical curves needed to independently adjudicate the point.

The current top-ranked hypothetical composition (C84/B42/Avicel39 mg at assumed hardness 8.5) is NOT a paper's published F8 recipe. It was ranked against invented goals and assumed coefficients; it is not shown to outperform the published F8 tablet experimentally or to meet a real release specification. Do not select it as an improved product formulation.

## What the benchmark supports—and does not

Supported: the scenario generator is deterministic/reproducible under its stated seed; recipe mass balance can be checked; one available literature endpoint exposes a meaningful model/assumption discrepancy; the internal F8 kinetic-fit numbers should be treated cautiously; the second paper's extracted profile is not fit-ready.

Not supported: measured-curve accuracy, comparative predictive performance of first-order versus Weibull (their errors differ by only ~0.09 percentage point at one point, with no replicates), calibrated uncertainty, causal excipient effects, rank confidence, or any conclusion about Glenmark lot 17230388. Since the benchmark is n=1 numerical endpoint from a different research formulation, it is NOT a holdout dataset and does not change the product benchmark status from `not_evaluated`.

## Recommended next benchmark gate

Obtain author/repository-authorized replicate-level dissolution values or manually curate the original graph/table with two independent reviewers, preserving medium changes, time points, replicate count, SD, formulation identity, and PDF/page coordinates. Resolve source contradictions before analysis. Fit models on other formulation groups and evaluate this F8 profile as a group-held-out case, then repeat with the second paper only after its Table 6 is correctly curated. Report per-timepoint MAE/RMSE, bias, profile similarity with a preregistered method, calibration/coverage only with enough independent groups, and external validation by study. Never pool these research tablets with recalled lots or treat the paper method as Glenmark's approved QC method.

## Reproducible input/output

Input: `../scripts/formulation-optimization-gym/data/processed/ranolazine_research_scenario_results.json`, source configuration `../scripts/formulation-optimization-gym/configs/exploratory_ranolazine_500.json`; structured extract: `../results/processed/literature_benchmark_summary.json`. Literature sources and hashes are listed in `../../research/formulation-optimisation-gym-environments/references.md` and `../scripts/formulation-optimization-gym/data/processed/public_literature_catalog.json`. The original PDFs were used for verification and are not redistributed in this package.
