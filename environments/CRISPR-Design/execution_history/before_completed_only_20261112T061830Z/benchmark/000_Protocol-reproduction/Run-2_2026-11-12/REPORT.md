# CRISPR task results and model-specific benchmark report

Run-2_2026-11-12: integration of genuine prior computational executions; no candidate redesign or new scientific inference during publication into this repository. The completed Cas13 run was independently audited before accepting its results.

## Repository structure and evidence classes

The sibling Gene-Silencing-RNA-Design layout is followed: tasks/ defines requirements, results/00N_application/Run-ID/ holds delivered example artifacts, benchmark/00N_application/Run-ID/ holds endpoint evidence; matching run IDs and provenance connect them. This shared campaign stores protocol manifests, scripts, primary numeric predictions and integrity checks once; task-specific folders reference it. Shared-model measurements are not thirteen independent validations.

Evidence classes: FRESH_INFERENCE; QUALIFIED_PROTOCOL_REIMPLEMENTATION; AUTHOR_SCORE_REPLAY; COMPONENT_ONLY; BLOCKED/NOT_RUN. None establishes experimentally validated designs. best_design=null throughout. Historical source inputs/weights are unchanged; prior documentation is snapshotted under pre_update_snapshot/. Large assets remain external and hash-indexed, so this is locally reproducible but not a standalone portable installation. Original scripts contain absolute paths and runtime/version dependencies; do not claim copy-and-run portability.

## 1. Cas9 accuracy

Source: DeWeirdt et al. RS3 (2022), https://europepmc.org/articles/PMC9448816 ; frozen author code gpp-rnd/rs_dev commit e92c3a8dc1d2452ffd979c094ec7d9e1f9b754e9. Correct30nt sequence and dataset-specific Hsu2013/Chen2013 tracr inputs, official processed labels, and exact20mer union exclusions across four models retained. This is RS3 Sequence, NOT Sequence+Target. CRISPRon v1 fresh inference is evaluated under this common-comparison protocol; its own v0 internal split and <=3mm exclusion protocol have not been reproduced. DeepSpCas9 and RuleSet2 are author-score replays, not freshly inferred baselines.

The23629 unique held-out contexts match the source. Source-table duplicate join keys produce27187 dataset observations; exact multiplicity and unmodified source bootstrap/rank-loss functions are retained for publication reproduction. Deduplicated26915-observation sensitivity is separate. Duplicate rows are not independent biological samples. The row-bootstrap intervals inherit source assumptions, not new-gene generalization guarantees.

| dataset | model | size | Spearman [95% CI] |
| --- | --- | --- | --- |
| Aguirre2016 | CRISPRon | 7828.0 | 0.5391 [0.5234, 0.5548] |
| Aguirre2016 | Rule Set 3 (sequence) | 7828.0 | 0.5505 [0.5330, 0.5662] |
| Behan2019 | CRISPRon | 7025.0 | 0.2237 [0.2025, 0.2475] |
| Behan2019 | Rule Set 3 (sequence) | 7025.0 | 0.2658 [0.2437, 0.2891] |
| Chari2015 | CRISPRon | 1130.0 | 0.4747 [0.4266, 0.5179] |
| Chari2015 | Rule Set 3 (sequence) | 1130.0 | 0.4356 [0.3872, 0.4856] |
| Kim2019_test | CRISPRon | 518.0 | 0.8970 [0.8766, 0.9139] |
| Kim2019_test | Rule Set 3 (sequence) | 518.0 | 0.7890 [0.7508, 0.8234] |
| Koike-Yusa2014 | CRISPRon | 6718.0 | 0.4219 [0.4001, 0.4409] |
| Koike-Yusa2014 | Rule Set 3 (sequence) | 6718.0 | 0.4141 [0.3949, 0.4350] |
| Shalem2014 | CRISPRon | 3968.0 | 0.2583 [0.2293, 0.2882] |
| Shalem2014 | Rule Set 3 (sequence) | 3968.0 | 0.2656 [0.2354, 0.2952] |


All four models, confidence intervals and original within-gene rank-loss are in evidence/reports/cas9_exact_published_protocol_metrics.csv and cas9_exact_source_within_gene_rank_loss.csv. Supplemental nDCG@20 uses within-gene percentile-rank relevance and is explicitly not the original RS3 endpoint. No pooled cross-assay accuracy headline or universal model superiority is claimed.

Historical Xiang2021 Day10+doxycycline results remain archived. Exact training-sequence overlap was not quantified there; the label condition differs from CRISPRon's establishment. D8/D10 correlation is NOT a mathematical predictor ceiling, and a degenerate binary-top-set nDCG is NOT solved by relabeling it as another metric.

## 2. Cas13 RFcombined

Source: Wessels et al.2020 https://europepmc.org/articles/PMC7294996 ; original source sanjanalab/cas13 commit c864b4f267e22e0ef1a9f28651744f6d04d58eaf. Published2918-row35-feature response table, recovered legacy R3.5 split-seed schedule, screen-balanced70/30 splits, training-only percentile scaling,2000trees/mtry12. All1000 corrected partitions and prediction files independently checked for disjointness and metric agreement. Rejected global-scaling pilot excluded.

Median Spearman 0.667308; 2.5–97.5% split/refit interval [0.629895, 0.700127], versus paper approximately0.67. This interval is a refit distribution, not an independent-target CI.

| screen | n | spearman |
| --- | --- | --- |
| CD46 | 704 | 0.618579017529186 |
| CD55 | 925 | 0.633169214767487 |
| CD71 | 890 | 0.623238787354509 |
| GFP | 399 | 0.294688479993955 |


The paper/final-model2000trees/mtry12 settings differ from comparative source randomForest defaults and final-CV source mtry10. This is a qualified reimplementation, not exact replay of all variants. Features were supplied, not reconstructed; global feature selection/label normalization is inherited. GFP transfer is substantially weaker. This does not validate TIGER, collateral cleavage or whole-transcriptome specificity.

## 3. Editing-outcome models

PRIDICT2.0: https://europepmc.org/articles/PMC7617539 ; source c133c35e205062e766bf515d1766169167e993b9. Native model-family ensemble within each correct held-out fold only; never average train-exposed folds. Source workbook test assignments independently match with zero fold mismatches for both cell types. Fresh intended-edit scores agree to less than0.00007 percentage points with published values. Full-pretraining overlap remains incompletely audited. Target-cluster intervals below supplement guide-row intervals.

| cell | endpoint | n | target_groups | spearman | target_cluster_ci_low | target_cluster_ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| HEK | averageedited | 22619 | 11863 | 0.9056291433786648 | 0.902677949436225 | 0.9083436791758532 |
| HEK | averageunintended | 22619 | 11863 | 0.31582255699226985 | 0.3027652826717942 | 0.32844919232048964 |
| K562 | averageedited | 22752 | 11886 | 0.8081186019351135 | 0.8029909405400116 | 0.8134774970388603 |
| K562 | averageunintended | 22752 | 11886 | 0.27408742976879114 | 0.26118492534648646 | 0.286806547853286 |


BE-Hive efficiency: https://europepmc.org/articles/PMC7384975 . HEK293T/BE4 external disease-focused library, n=9975; known training20mer/31nt contexts excluded. Spearman 0.165766,95% guide-bootstrap CI[0.145910,0.184578]; Pearson 0.176357. This weak transfer result is retained, not hidden. Endpoint is normalized logit ANY-edit efficiency, not intended correction or purity. BE4 is not BE4max; bystander-genotype evaluation remains NOT_RUN. Test-set probability calibration was not fitted.

DeepPrime: Yu et al.Cell2023, https://github.com/hkimlab/DeepPrime ; original base model commit99272383d1420576551d271d865b9972a63466c0. HEK293T/PE2/conventional-scaffold official fixed test n=28883,259910 training rows, zero exact-input/74nt-target overlap. Original74nt/24-numeric inputs, mean/std and five-weight ensemble used. Spearman 0.861474,target-cluster95%CI[0.856398,0.866396]. Other cells/editors and unintended outcomes are not validated by this one test.

## 4. Specificity and detection limits

WT SpCas9 CFD2016, study PMID28459459, HEK293 cellular targeted AmpliSeq, nominal0.1% detection threshold; hg38. Curated measured positives and assayed negatives from CRISPRoffT (https://ccsm.uth.edu/CRISPRoffT/). n=1684,9guides,108positives/1576negatives. V2 excludes3 explicitly annotated bulges and uses >=0.1% to match original Validation labels; earlier strict>0.1 V1 retained as sensitivity, not primary.

Average precision 0.186039; guide-cluster95%CI[0.088501,0.312278], trapezoid PR-AUC 0.178991.

| K | macro_recall | macro_precision | exhausted_guides |
| --- | --- | --- | --- |
| 1 | 0.021494708994708994 | 0.3333333333333333 | 0 |
| 5 | 0.08366402116402116 | 0.2888888888888889 | 0 |
| 10 | 0.14177489177489178 | 0.2111111111111111 | 0 |
| 20 | 0.2467231842231842 | 0.16666666666666666 | 0 |
| 50 | 0.3813431938431938 | 0.11555555555555556 | 0 |
| 100 | 0.6569264069264069 | 0.09727598566308243 | 1 |
| 500 | 1.0 | 0.08367046836774265 | 9 |


Recall@500=1 reflects exhaustion of all nine tested panels, NOT whole-genome nomination recall. Only23/108 positives meet the prior workflow's necessary NGG/<=3mm eligibility; this is search-policy coverage, not an executed genome-wide recall estimate. Assay negatives are below threshold in that experiment, not universally cleavage-free sites. Summary data lack per-site read-depth/LoD reconstruction. Population VCFs, haplotypes, ancestry representation, SVs and bulged alignment are not evaluated. No therapeutic safety conclusion follows.

## 5. Specialized modalities

CRISPRi: fixed TSS-window component only on3607 guides/307 held-out genes; precision0.254628,recall0.764172 for original normalized activity>=0.75, not75% knockdown. Full learned808-feature model and CRISPRa scoring remain NOT_RUN.

Epigenetic: context annotation is not durable repression/methylation efficacy. Matched CRISPRoff functional benchmark blocked; no nuclease surrogate.

Diagnostics: EasyDesign primary numeric-score replay is incomplete. Source columns cover differing numbers of rows; original attempt encountered nonnumeric dash tokens, and its edited script was not rerun. No final numeric diagnostic accuracy is accepted here. Prior synthetic primer-guide geometry is functionality only. Pathogen sequence design/scoring remains review-gated; no clinical sensitivity or assay LoD inferred.

Plant: source-score replay on52 N.benthamiana guides with actual in-planta InDel labels. Not fresh inference and not adapter validation; native plant DESIGN stays inactive. Source: https://doi.org/10.1007/s00299-026-03820-x .

Microbial: source-faithful MERF gene/dataset score replay median0.381385,95%gene-cluster bootstrap[0.337788,0.425000],642 comparisons; paper rounded0.396. Difference is retained unresolved. Not fresh bacterial inference or independent purine screen; CRISPRi depletion is not lacZ nuclease knockout. Source: https://europepmc.org/articles/PMC10782694 .

## 6. Per-task coverage matrix

| Task | Application | Evidence status |
| --- | --- | --- |
| 001 | general | SHARED_COMPONENT_BENCHMARKS |
| 002 | knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION |
| 003 | therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY |
| 004 | variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS |
| 005 | base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST |
| 006 | prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS |
| 007 | crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY |
| 008 | epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT |
| 009 | rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION |
| 010 | diagnostics_pathogen | REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY |
| 011 | library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION |
| 012 | plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY |
| 013 | microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY |


See task_execution_status.csv for precise findings, blockers and per-task result/benchmark paths. No complete application or clinical validation is claimed. Historical example artifacts are copies, not reruns. Weak results, failed pilots, unavailable stages and source discrepancies remain explicit.

## Reproducibility and verification

PROVENANCE.json/sha256 bind every copied artifact. EXTERNAL_ARTIFACT_INDEX.json indexes retained original datasets, checkpoints, runtime environments and RF partitions. evidence/protocols freezes exact features/splits/seeds; evidence/scripts contains the actually executed implementations. Some source manifests describe earlier/deduplicated pilot states: current authority is cas9_exact_source_replay.json, specificity_CFD_v2.json and corrected Cas13 source-audited-v2 completion verification. They must not be pooled with rejected variants.

Gates remain DRAFT; these model benchmarks did not freeze application ranking thresholds. No-tuning attestation is limited to the recorded individual evaluations, not an assertion of blinded label access across the whole historical campaign. Reproduction is not new independent experimental validation.
