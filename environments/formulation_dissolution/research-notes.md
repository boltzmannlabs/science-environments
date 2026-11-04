# Formulation dissolution research notes

## Rationale and evidence boundary

The local formulation-optimization gym already implemented source-attested investigation state, constraint checks, bounded specialist functions and separate empirical/scenario benchmarks. The repository integration reuses those algorithms; it does not create a second dissolution simulator. Flat packages and configs/ were retained to preserve executable import and fixture contracts. See the [environment](../../environments/formulation_dissolution/README.md), [specification](../../environments/formulation_dissolution/ENVIRONMENT_SPEC.md) and [inventory](../../environments/formulation_dissolution/MODELS_AND_TOOLS.md).

Two distinct public FDA cases exist in the retained snapshots: Glenmark D-0092-2024, 500 mg, and Ajanta D-0010-2027, 1000 mg, lot DJ25134. Public recall reasons establish reported identity/failure context, not a numerical release profile, approved method or cause. DailyMed labels supply qualitative identity/ingredients, not the actual batch recipe. They are not merged into a fictional baseline.

## Scientific methods actually used

Six empirical kinetic forms were fitted through OpenPKFlow 2.9.0 / SciPy bounded least squares. Fitted kinetics can describe a curve but do not establish transport mechanism. Early-only Korsmeyer–Peppas fitting and unrestricted late extrapolation must be distinguished. The fixed 100% asymptote of several forms can mismatch reported >100% observations; observations were not clipped to improve fit.

The published benchmark separates pH 6.8 and HCl. The pH 6.8 table is a user-supplied patent transcription with an inaccessible original numerical table; independent verification remains outstanding. HCl Table 4 was sequence-checked against primary patent HTML in the source run; the check report/hash and small excerpts are retained, while full HTML stays local. Source verification is not evidence of cross-product applicability.

Synthetic batches use an invented Weibull law, seed 31415, and fixed whole-batch train/validation/test partitions. These verify reproducible software splitting, fitting, metric arithmetic and labeling. A Weibull result winning on a Weibull-generated fixture is not independent evidence of ranolazine predictive reliability. Four calibration batches cannot establish calibrated intervals.

The 500 mg research scenario uses 695 mg total tablets, literature-context recipe amounts and invented kinetic/coefficient ranges. Exhaustive feasible grid search, assumed uniform Monte Carlo scenarios, Pareto filtering, sensitivity and zero-effect controls test methodology. With rate effects zeroed, curve differences disappear while a lower-polymer preference can still rank candidates. This exposes imposed objective assumptions, not a learned improvement. The author-reported F8 endpoint is context already inspected, not a heldout validation label for a newly selected candidate.

Compatibility/stability triage filters supplied evidence only. Neither a molecular interaction predictor nor a stability/degradation/Arrhenius model has been trained or run. A nearest-mixture scalar baseline exists but has no eligible linked measured ranolazine training dataset. Mechanistic transport, PTCalc, GP/Bayesian optimization, RDKit screening and neural surrogates remain unimplemented/proposed.

## Source review and unresolved questions

References below are limited to retained source snapshots/reports, previously successful Zenodo metadata retrieval and installed software contracts. No new primary-PDF transcription audit or manufacturer-controlled record access occurred during packaging. Original PDFs, private datasets, credentials and model weights are not redistributed. Historical coding-agent reviews are source-indexed local artifacts, not measurements or a deployed agent framework.

Before scientific qualification, resolve:

1. Authorized product-specific method/version, QC limits and unit-level batch/comparator profiles.
2. Actual recipe, potency/material grades/attributes, manufacturing and storage history.
3. Primary numerical verification of the pH 6.8 transcription and curation of research-article graphs/tables.
4. Dose/method/formulation comparability and independent source/batch-aware heldout data.
5. Prespecified objectives, credible constraints, error tolerance, uncertainty calibration and approved experimental budget.
6. Prospective confirmatory dissolution, compatibility/stability and manufacturability evidence, plus scientific and maintainer review.

Passing software tests is not evidence of clinical equivalence, a resolved recall, validated formulation optimization or specialist superiority.
