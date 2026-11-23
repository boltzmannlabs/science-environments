# Published-result benchmark (descriptive, not recalled-lot validation)

Reproduce from repository root:

    python -m evaluation.check_primary_patent
    python -m cli benchmark --config configs/benchmark.yaml --track published
    python -m pytest -q

Two read-only coding-agent processes were started concurrently to audit the evidence and benchmark design. Their actual returned reviews are `data/processed/agent_evidence_review.txt` and `data/processed/agent_benchmark_review.txt`. Native SCI delegation and the external Boltzmann dissolution connector are not enabled, so no registered external dissolution service was run. Agent output is review, not laboratory measurement.

Published pH 6.8 profiles from Indian patent application 201741007784 (user-supplied transcriptions, QuickCompany URL 403 when checked): hold out each of Examples 3–8 as an entire curve and predict its seven nonzero time points with the arithmetic mean of the five remaining curves. Equal-formulation macro MAE = 7.580952380952381 percentage points; macro RMSE = 8.833409053609028 percentage points. The Ranexa 1 g reference is excluded from training and this primary score; comparing it to the six-example mean yields contextual MAE 6.404761904761904 and RMSE 8.527034505636614 percentage points. Example 8 has the largest error, MAE 13.114285714285714 and RMSE 17.466212280530986 percentage points. The underlying example strengths and individual units are not documented in this curated import, so these are within-publication summary-curve differences only. An in-sample first-order curve-fit reconstruction table is reported separately; its errors are not blind predictive performance.

Low-pH US6525057B2 Table 4, separately: fetched and hashed primary patent HTML `data/raw/US6525057B2-21d2090561d687d17c85cd2d3f1f3ba8ca171dd00899e55f9875b4778506b4cf.html`. The specified Table 4 numeric sequence matches the primary HTML; evidence in `data/raw/US6525057B2_source_check.json`. For SR A/B/C, leave-one-out within the source at seven reported time points yields macro MAE 12.733333333333334 and macro RMSE 14.63276182283762 percentage points. IR is excluded and the two media are never pooled. Strength, speed, temperature and unit variability remain unverified.

Prior 500 mg F8 research endpoint sanity check: author-reported 99.5% at 24 h versus saved assumption-scenario first-order median 89.3809057297187% and Weibull median 89.46928777886427%; absolute differences 10.119094270281295 and 10.03071222113573 percentage points. Not an untouched holdout or calibrated prediction.

Independent software verifier findings: none for pH 6.8 leave-one-out rows, training exclusions, metric recomputation and absent QC claims. Tests: 40 passed, 1 skipped. Files: `data/processed/published_benchmark/published_benchmark.json`, `published_profile_predictions.csv`, and `published_profile_scores.csv`. JSON includes hashes, each fold's training IDs, acid and scenario tracks, evidence caveats, and separate first-order fits.

No Ajanta 1000 mg lot DJ25134 measurements or approved QC limits have been provided. No independently verified pH 6.8 patent table, calibrated model, statistically independent source holdout, fully matched A–D arms, specification attainment, formulation improvement or root cause has been established. Next evidence request: approved dissolution method and limits; lot-level and appropriate comparator individual-unit profiles; verified formulation/process/storage and OOS records. Human approval and a verified backend are required before physical testing.
