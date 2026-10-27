# KRAS evidence resolution and ranking sensitivity

## Decision
Retain the current conditional14-candidate research-review panel. Do not designate a single winner. The panel is justified as a mapped, operationally screened review set, not as biologically qualified siRNAs. Defer definitive potency ordering. Overall biology remains PARTIAL; shared-arm computational completion is preserved.

## Evidence boundaries and source verification
Source: /home/boltzmann13/IMRAN/OpenSource/Agent-RUNs/KRAS_siRNA_case_study/audit_20261021T071712Z. Prior output hashes and receipt binding verified. Input/output hashes and before/after source identity are retained. No generation, predictor inference, folding or transcriptome screening was run. The prior audit is computational verification, not biological validation.

## Candidate-level resolution
candidate_evidence_matrix.csv separates transcript coverage, exact findings, near matches, seeds, guide/passenger concerns, raw scores/statuses, extrapolation, required gaps and qualification. All14 cover the four declared RefSeq references and have no detected perfect outside-KRAS match on either strand in the preserved unambiguous transcript scope. That does not establish safety, absence of near/seed effects, all-mutant coverage, expression or knockdown.

## Extrapolation sensitivity
9 of14 are flagged Ridge extrapolations. Restricting to nominal0..100 leaves 5 candidates: NM_004985.5_site_1517, NM_004985.5_site_1912, NM_004985.5_site_2547, NM_004985.5_site_2875, NM_004985.5_site_4174. This numerical stratum is not a validated biological exclusion rule and being inside the nominal range does not establish calibration. Therefore it is not sufficient reason to discard the other candidates from computational review.

Ridge vs RN.Ai-Predict: Spearman -0.165 (n14) to -0.600 (restricted n5); top3 overlap 1 to 1.
Ridge vs RNAiSpline: Spearman 0.327 (n14) to -0.500 (restricted n5); top3 overlap 1 to 1.
Ridge vs OligoFormer_native: Spearman 0.446 (n14) to -0.600 (restricted n5); top3 overlap 1 to 1.
Ridge vs OligoFormer_corrected: Spearman 0.363 (n14) to -0.200 (restricted n5); top3 overlap 1 to 1.
Ridge vs siRNA-Bench: Spearman 0.380 (n14) to 0.500 (restricted n5); top3 overlap 1 to 2.
Ridge vs combined_frozen_v1: Spearman 0.420 (n14) to -0.300 (restricted n5); top3 overlap 1 to 2.

Full pairwise and same-method restriction results are in ranking_sensitivity.csv. Baseline statistics are reused, not relabelled as new inference. Spearman uses average tied ranks; Kendall uses tau-b. ExactK ties use literal IDs; fractional boundary memberships are also retained. K>n is NOT_APPLICABLE and K=n overlap is non-discriminating. The existing combined score remains normalized to its original20 cohort; weights and normalizations are not changed. No p-values, confidence intervals, calibration or efficacy accuracy estimates are invented. Native/eval OligoFormer share a checkpoint; composite priorities partly reuse their component evidence.

## Missing-output sensitivity
All14 have all seven preserved scores, so actual missing values do not require a smaller primary panel. The100-case compatible potency pool has five methods. Native Bench has81 available scores and19 missing scores tied to operational selection; adding Bench changes the cohort, not just the scoring method. The complete-case100-to81 comparisons expose membership and rank-position shifts for the same five methods; shifts are denominator/selection effects, not new biological results. No predictor scores are imputed; the combined priority is not extrapolated to81/100 and no new ensemble is formed.

## Specificity: exact transcript evidence and diagnostic scope
NM_004985.5_site_280; strand evaluated guide; KRASP1 ENST00000407852.2; transcript positions 90–108; length 19; mismatches 1; siRNA5to3 mismatch positions [18]; pattern =X=================.

No preserved full19nt HRAS/NRAS0–2-substitution match is present in this panel. RAS_family_seed_evidence.csv retains gene-level6/7/8nt motif opportunity counts; those do not establish repression. Full/near transcript identities, positions and patterns are retained in specificity_transcript_evidence.csv. Aggregated seed counts do not identify each positive transcript or seed location; that finer evidence is unresolved, not fabricated. The diagnostic is bounded by GENCODEv50 unambiguous forward transcript windows, no gaps/individual variants, and all annotated KRAS treated as on-gene. No new negative-window search was performed.

## Why retain rather than narrow or pick a winner
Ridge extrapolation is a predictor-scale warning, not observed biological failure. Excluding it changes a conditional cohort and does not measure what happens to any siRNA in cells. Current near/seed findings lack agreed tissue-specific risk tolerance and expression/loading data. Inventing thresholds or reweighting now would imply unsupported biological preference. Retain the14 with explicit warnings, while preserving the six exact-failure candidates only in the prior audit as flagged comparisons. No candidate is called safe, off-target-free or experimentally validated.

## Unresolved evidence and next actions
Required before biological qualification: accepted guide/passenger specificity criteria; relevant expression and loading; final chemistry/overhangs; delivery, dose/time and assay endpoints; immune evidence; exact-construct measured efficacy and independent validation. These are recorded candidate by candidate in unresolved_evidence.json. No repeated generation/inference is necessary. Any future context-dependent model or new screening is NOT_RUN here and requires appropriate inputs and authorization.

## Mutation-selective arm
BLOCKED_PENDING_MUTATION_SPECIFICATION. Exact mutation, transcript accession.version/context and wild-type-sparing objective must be supplied before construction or design. No hypothetical mutant was created.

## Provenance and verification
Baseline evidence citations: candidate_evidence.json, review_candidates14.csv, matched_pool_ranks.csv, rank_correlations.csv, topK_overlap.csv, reproduced_alignments.csv, family_seed_annotations_audited.csv, prediction_coverage.csv, exact_failure_alignments.csv and verification_receipt.json in the source directory. See input_hashes.json, tool_provenance.json, output_manifest.json and the new verification_receipt.json for execution and integrity scope.

Technical verification PASSED: source hashes unchanged, raw score/evidence preservation, independent rank/tie oracles and status boundaries checked. This does not change biological PARTIAL status. See verification_receipt.json.
