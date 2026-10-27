# KRAS case study — historical reports and results

## What this snapshot is

A bounded, source-hash-verified copy of the KRAS work developed with Agent Scientist: **85 selected report/result/provenance files** from five historical runs. All selected originals remain byte-identical; no candidate generation, model inference, folding, transcriptome screening or experimental measurement was rerun. `copy_provenance.json` maps every copied file to its original case directory/path, source hash and copied hash.

**This is not an independently validated experimental benchmark.** The folder name groups case-study/benchmark evidence; the independent-data workstream remains explicitly blocked.

## Browse the reports

| Stage | Report | Important results |
|---|---|---|
| 1. Shared-target design | [Scientific report](01_shared_design/scientific_report.md) | [20 investigated core designs](01_shared_design/top20_sequences.csv), [full selected evidence](01_shared_design/top_shared_candidates.csv), [conditional 14 subset](01_shared_design/reference_exact_exclusivity_subset.csv), [qualification](01_shared_design/qualification_results.json) |
| 2. Candidate audit | [Audit report](02_candidate_audit/audit_report.txt) | [Candidate evidence table](02_candidate_audit/candidate_evidence_flat.csv), [six exact-failure alignments](02_candidate_audit/exact_failure_alignments.csv), [rank correlations](02_candidate_audit/rank_correlations.csv), [top-K overlap](02_candidate_audit/topK_overlap.csv) |
| 3. Ranking sensitivity | [Evidence-resolution report](03_ranking_sensitivity/evidence_resolution_report.md) | [14-candidate evidence matrix](03_ranking_sensitivity/candidate_evidence_matrix.csv), [sensitivity results](03_ranking_sensitivity/ranking_sensitivity.csv), [unresolved evidence](03_ranking_sensitivity/unresolved_evidence.json) |
| 4. Experimental-data eligibility | [Benchmark report](04_experimental_dataset_audit/benchmark_report.md) | [Dataset manifest](04_experimental_dataset_audit/dataset_manifest.json), [split status](04_experimental_dataset_audit/split_manifest.json), [null metrics](04_experimental_dataset_audit/metric_summary.csv), [training/leakage audit](04_experimental_dataset_audit/overlap_and_leakage_audit.json) |
| 5. Literature comparison | [Workflow comparison report](05_literature_comparison/comparison_report.md) | [Workflow comparison table](05_literature_comparison/workflow_comparison.csv), [literature-to-harness crosswalk](05_literature_comparison/literature_to_harness_crosswalk.csv), [compatible score comparison](05_literature_comparison/candidate_score_comparison.csv), [qualification gaps](05_literature_comparison/qualification_and_gaps.json) |

## Interpretation boundaries

The historical shared arm generated 5,288 unique cores, deeply assessed 100, investigated 20 and retained a conditional 14 with no detected perfect outside-KRAS match under the stated scope. Six perfect-match warnings, residual near/seed concerns and Ridge extrapolation flags are retained. None is declared safe, off-target-free or newly experimentally validated.

The literature comparison recovered two source-supported shared-KRAS paired cores already present in the full generated pool but absent from the selected panel. One had an inherited palindrome-heuristic flag. These are separately labelled comparator cores, not an automatic merged qualified shortlist or proof of superiority. Published pooled endpoint ranges were not converted into individual efficacy labels.

Experimental-data independence was not established. `04_experimental_dataset_audit/per_record_predictions.csv` is intentionally **header-only** and `metric_summary.csv` contains null results with zero test/prediction counts. These are blocked outputs, not zero performance or a successful validation benchmark.

Biology remains **PARTIAL**. The mutation arm remains **BLOCKED_PENDING_MUTATION_SPECIFICATION**; no hypothetical mutant was constructed.

## Provenance and verification

- [Copy provenance](copy_provenance.json): selected source paths, exact source/copied hashes and historical receipt identities.
- [Source-preservation receipt](source_preservation.json): the 85 selected source files remained unchanged during copying.
- [External artifact index](external_artifact_index.json): 207 original artifacts not copied, with location/size/reason. These are preserved externally, not deleted or treated as unavailable in the original run.
- `snapshot_manifest.json` and `snapshot_verification.json`: current frozen snapshot integrity, created by the packaging verifier after checking copied bytes and key row/status semantics.

Historical receipts/manifests are renamed `source_verification_receipt.json`, `source_verification_report.json`, `source_output_manifest.json` or `source_reproducibility_manifest.json`. They describe the original runs, **not a complete portable copy** of those runs. Their original file lists can include artifacts intentionally excluded from this snapshot. Do not run an old scientific verifier against this partial snapshot or reinterpret a historical PASSED receipt as fresh biological validation.

Original generated reports may mention originating-host paths or files excluded from the snapshot. They are intentionally not rewritten, so copied bytes can be checked against their original hashes. Use the copy/external indexes to locate those dependencies. No raw full-text publication archives, model weights, full reference assets or raw experimental datasets are bundled. Scientific references remain centralized in [the research reference list](../../../../research/sirna-designing-harness/references.md).

## Reproduce the integrity check

From `environments/sirna-designing-harness/`:

```bash
python3 scripts/run.py verify-benchmark
```

No original host paths, scientific packages, network access, GPU or model assets are needed to verify copied files. File checksums establish byte consistency, not clinical or biological qualification.
