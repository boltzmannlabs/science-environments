# Executed workflows and published-target comparisons — Run-6_2026-11-16

Status: runnable benchmark workflows completed; full application design tasks remain partial. No new training, generation, relaxed gates or substituted challenger models.

## What ran

Fresh RN.Ai source-guide and core19 inference, RNAiSpline core19 inference, and native OligoFormer paired inference were executed on all 322 measured human pairs. OligoFormer also freshly scored all 598 TTR windows, in seven verified native jobs total. Identical TTR C00/C01 guide inputs explicitly share one identical RN.Ai score vector. Four RNAduplex settings and three missing-context controls used the 26 HTT reporters; the unchanged immune motif rule was freshly evaluated on eight retained examples.

There are 35 task/config bundles across nine task frames, plus the auxiliary immune-rule result in task 008. Shared task frames are not independent model fits. PCSK9 and TNF target-specific efficacy benchmarks remain unavailable. Allele/CNS design requirements remain unresolved. SiaRNA, ENsiRNA and BERT-siRNA remain blocked as documented in Run-5; no performance values are assigned to them.

## Fresh measured-cohort performance

| Config | HIF1A n=100 | HPSE n=106 | HK2 n=95 | Full Simone n=322 | Strict >0.7 full AUC |
|---|---:|---:|---:|---:|---:|
| C00_rnai_native21 | 0.7803 | 0.6366 | 0.7176 | 0.7021 | 0.6960 |
| C01_rnai_core19 | 0.7709 | 0.6671 | 0.7229 | 0.7056 | 0.6989 |
| C02_rnaispline_core19 | 0.7791 | 0.6452 | 0.6656 | 0.6769 | 0.6763 |
| C03_oligoformer_core19 | 0.7394 | 0.5943 | 0.6438 | 0.6355 | 0.6426 |

Measured target labels derive from the Sciabola cohort; they are experimental reference outcomes, not model-specific published AUC targets.[2] MYC has seven rows and one positive: its numerical AUC is descriptive and excluded from the primary macro comparison.

C01 has the highest observed three-target macro AUC, 0.7203, versus baseline 0.7115. Selection using only the other two target genes yields 0.7102, not an improvement over baseline. No production default was changed. All cohorts were examined previously; this is not an untouched prospective validation. Row-bootstrap intervals in measured_metrics.json are exploratory because shared/overlapping sites violate independence.

## Comparison with published model targets

SiaRNA reports AUC 0.7586 on 322 Simone pairs.[5] This run evaluates different executable models, not that blocked checkpoint pipeline. Four local labels are exactly 0.7; both >=0.7 and >0.7 AUCs are saved. Exact published-protocol equivalence is not established and no superiority delta is asserted.

OligoFormer reports average Mixset AUC 0.8163 and PCC 0.5879 in inter-dataset validation.[1] Our fresh evaluation uses Simone, not Mixset; these values are contextual targets, not like-for-like comparisons. The native inference CLI leaves training/dropout mode active. Fixed seed and coordinate order are recorded, but subset/order differences can change scores relative to prior full-pool generation. No changed checkpoint or model improvement is inferred from that variation.

published_target_comparison.csv/JSON records actual local values, primary reference IDs, cohort/endpoint mismatches and null matched-protocol deltas. Public-measurement evaluation is complete for the eligible cohorts; published model performance has not been reproduced as a matched protocol.

## Drug-core and reporter outcomes

| Endpoint | Fresh result | Interpretation |
|---|---|---|
| TTR patisiran | rank 107/598 | Fresh native OligoFormer; projected unmodified core only, not clinical potency |
| TTR vutrisiran | rank 62/598 | Fresh native OligoFormer; projected unmodified core only, not clinical potency |
| HTT allele reporters | Spearman -0.3080; n=21 uncensored | Four physical settings rerun; no patient allele-design validation |
| HTT efficacy control | Spearman 0.2630; n=26 | Genuine flanks absent; not CNS validation |
| Immune motif rule | sensitivity 0.1429, specificity 1.0000 | Eight examples, only one negative; not immune safety |

The HTT evaluations use the same published reporter set and retain censoring rather than treating bounds as exact outcomes.[3] Thermodynamic margins are not measured cellular allele selectivity. Immune activation is sequence-dependent; a single unchanged motif rule is not a validated safety classifier.[4] Drug-site identities and their derivation are inherited from hash-verified Run-3 primary-source anchor records; clinical outcomes are never treated as candidate efficacy labels.

## Files and limitations

Task outputs: results/<task>/Run-6_2026-11-16/. Frozen configs: config/<task>/Run-6_2026-11-16/. Each executed configuration has predictions.csv, metrics.json, benchmark_config.json and provenance.json. No panels were reranked and no new candidate generation or battery was claimed.

Open performance_overview.png for actual measured-cohort, target-selection, TTR anchor and HTT physical-model trajectories. Native OligoFormer execution logs, model hashes, coordinate/sequence mappings and completion records are in native_oligoformer/. Disposable execution trees were removed only after output validation; original sources/checkpoints stayed unchanged.

The cached initial-stage OligoFormer reference is explicitly named and is not used in final comparisons. Fresh native outputs cover all 322 pairs, whereas the historical cache covered 308; prior replay comparisons use only identical paired rows. See paired_prior_replay_checks.json.

Validation passed: all 11 package checks and all 53 runtime/artifact tests succeeded. Ten unique generated figures decoded successfully and passed nonblank-image checks; new documentation links and all five evidence-backed citations verified. All historical Run-3, Run-4 and Run-5 manifest entries remained unchanged, and the independently checked Run-6 manifest covers 395 entries. See validation_summary.json, unittest.log, citation_verification.log and PROVENANCE.sha256. Software tests and readable plots do not establish biological efficacy, clinical equivalence or complete task acceptance.

## Sources

[1] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11494384 — OligoFormer: an accurate and robust prediction method for siRNA design
[2] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3561943 — Improved nucleic acid descriptors for siRNA efficacy prediction
[3] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2746439 — Five siRNAs targeting three SNPs in Huntingtin may provide therapy for three-quarters of Huntington’s disease patients
[4] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2724479 — Sequence determinants of innate immune activation by short interfering RNAs
[5] https://pmc.ncbi.nlm.nih.gov/articles/PMC13488420 — SiaRNA: a siamese neural network with bidirectional cross-attention for pairwise siRNA-mRNA efficacy prediction
