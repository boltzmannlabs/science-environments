# Audit, ranking sensitivity and independent experimental benchmarking

## Audit-only mode

Discover actual files and verify prior manifests/receipts. Hash source files before/after and write to a new sibling directory. Do not invoke an old report/verifier that writes into the original run. Reuse verified predictions, reference mappings and saved alignment windows. A saved match can be checked against its preserved reference window without a new transcriptome scan.

Separate the siRNA strand evaluated from transcript/genomic orientation; neither guide nor passenger designation proves loading. Preserve literal transcript IDs,1-based positions, match length, mismatch pattern and query-versus-siRNA positional conventions. Full match/exclusivity diagnostics are sequence observations, not demonstrated repression. Aggregated family seed counts cannot identify every positive transcript/site; mark unavailable detail rather than fabricate it.

## Ranking sensitivity

Prespecify matched cohorts, methods and K. Use average-tied Spearman and Kendall tau-b for descriptive agreement; unlike endpoints do not support direct percent-unit error comparisons. Specify exact-K tie-breaking and fractional boundary-tie sensitivity. K>n is NOT_APPLICABLE; K=n set overlap is non-discriminating, not evidence of robustness. Constant-score correlation is undefined/null.

Treat excluding Ridge extrapolations as a numerical sensitivity stratum, not automatic biological exclusion. Preserve raw estimates; being inside0..100 does not establish calibration. Do not silently reweight or renormalize an existing cohort-dependent composite on a restricted panel. No missing score, sentinel prediction or invented ensemble substitutes for an unavailable method. For complete-case restrictions compare available common methods and label rank-position/top-K shifts as membership/denominator changes, not biology.

A conditional multi-candidate review panel can remain useful even when potency ordering is unstable. Choose retain/narrow/defer with explicit evidence criteria; do not force a winner. Strong agreement of native/eval outputs sharing a checkpoint or a composite with its components is not independent confirmation. Do not invent p-values, confidence intervals, accuracy or precision from unmeasured candidate scores.

## Independent-data gate

Audit actual local experimental sequence/label data and official source archives before prediction. Record original-study/publication identifiers, target/accession, full sequence and core derivation, strand, assay endpoint, unit, dose/time/cell, chemistry, replicates, rights, source URL/version/time and hashes. Distinguish measured source %Inhibition, mRNA knockdown, protein knockdown, reporter signal and activity remaining.100 minus remaining is a documented arithmetic complement, not newly measured or harmonized mRNA knockdown. Do not average doses or pool native/reporter endpoints silently.

Check repeated/blank CSV headers before DictReader; assign documented positional surrogate names if needed and independently verify source counts. Create unique derived audit IDs from source row plus endpoint/dose/time/chemistry when these define separate measurements, retaining original IDs separately. Different labels with incomplete context do not establish data corruption. Quarantine proven corrupt blocks with provenance, never invented replacements. Git LFS pointer text is unavailable data. RNAseq gene counts and molecular coordinates are not automatically per-construct efficacy labels.

Audit exact full guides, reverse-complement equivalence, core/context matches and original-study exposure against actual training/development sources. Conservative19nt windows in20/21nt sequences may detect potential exposure but do not approve trimming for inference. Distinguish a known transparent baseline training partition from unknown pretrained final-checkpoint membership. No released-reference overlap is not proof of independence; a new publication can reuse old screens. Verify guide/context identity before comparing normalization factors, and never fit scale/calibration mappings on the test set.

If no auditable independent compatible cohort is established, stop with BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET. Deliver a dataset audit, row exclusions, model-specific blockers, split manifest with no claimed untouched test, an explicit empty independent-prediction schema and null metrics/zero attempts. Do not replace the blocked test with historical random-split/cross-study scores or claim zero performance. Domain-incompatible modified/asymmetric constructs require appropriate separate models/adapters, not arbitrary projection into an unmodified19nt model.

## If the gate passes

Freeze original-study/target/duplicate-connected grouping and train/development/test roles before test access. Purge related sequence components and resolve target aliases; a new split cannot erase pretrained development exposure. Compare same-successful-record intersections, preserve failures and justify label normalization using training/development only.

Use Spearman/Pearson where endpoint definitions support them; Precision@K with an assay-specific prespecified hit rule; NDCG@K with a justified relevance definition; MAE/RMSE only on valid shared scales; calibration only for matching class definitions. Use simple training-only mean/GC baselines and random ordering of real labels, never synthetic ground truth. Report by target/study and cluster uncertainty only when an adequate sampling design supports it. Missing structural/specificity/context domains block full-pipeline ranking validation, not license an efficacy-only replacement.

## Benchmark deliverables

benchmark_report.md; dataset_manifest.json; split_manifest.json; per_record_predictions.csv; metric_summary.csv; overlap_and_leakage_audit.json; record-level eligibility/duplicates/scale audits; source hashes; model/checkpoint provenance; failures/superseded roles; output_manifest.json and verification_receipt.json. Keep experimental efficacy prediction, ranking, unseen-study/target generalization, sequence specificity and exact-construct biological qualification distinct. No safety, delivery, immune-tolerance or mutation-selectivity inference from an efficacy benchmark.
