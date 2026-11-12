# Executed publication-label benchmarks — Run-3_2026-11-12

## What executed

This run genuinely recomputed measured-label accuracy, paired comparisons and1000-resample uncertainty estimates using the retained native model predictions from Run2. It did NOT rerun model inference or generate designs. Original fresh native predictions, weights, training exclusions and published splits remain traceable in Run2. This is computational metric replication, not a new blinded or independent biological experiment.

The previously incomplete diagnostic analysis was completed as numeric-only author-score review; no source target/guide sequence columns were loaded, no pathogen sequence inference or design was performed.

## Sources and comparability

[Publication-by-publication comparability ledger](publication_comparability.csv) separates matched protocol reproductions, external transfer tests, source-score replays, component tests and true blockers. Publications: RS3/PMC9448816, Cas13/PMC7294996, BE-Hive/PMC7384975, PRIDICT2/PMC7617539, DeepPrime official hkimlab/DeepPrime source, specificity studyPMID28459459, Horlbeck/PMC5094855, CRISPRoff/PMC8376083, EasyDesign/PMC11316927, plant doi10.1007/s00299-026-03820-x, microbial/PMC10782694. Source data and execution scripts are hash-bound in input_provenance.json and scripts/.

## 1. Measured-label model accuracy

Intervals use1000percentile resamples with seed20261112; gene/target clusters are sampled where defined, otherwise guide rows. The original duplicate-weighted RS3 source protocol remains inRun2. This run's Cas9 numbers use the deduplicated common prediction-key panel, so they must not be silently substituted into the source-row replay table.

| model | cohort | endpoint | n | Spearman [95% CI] |
| --- | --- | --- | --- | --- |
| RS3 Sequence | Aguirre2016 | official processed sgRNA activity | 7716 | 0.5510 [0.5358, 0.5665] |
| CRISPRon v1 | Aguirre2016 | official processed sgRNA activity | 7716 | 0.5390 [0.5225, 0.5537] |
| RS3 Sequence | Behan2019 | official processed sgRNA activity | 6974 | 0.2659 [0.2419, 0.2872] |
| CRISPRon v1 | Behan2019 | official processed sgRNA activity | 6974 | 0.2228 [0.2002, 0.2466] |
| RS3 Sequence | Chari2015 | official processed sgRNA activity | 1129 | 0.4362 [0.3861, 0.4817] |
| CRISPRon v1 | Chari2015 | official processed sgRNA activity | 1129 | 0.4754 [0.4255, 0.5219] |
| RS3 Sequence | Kim2019_test | official processed sgRNA activity | 518 | 0.7890 [0.7506, 0.8241] |
| CRISPRon v1 | Kim2019_test | official processed sgRNA activity | 518 | 0.8970 [0.8774, 0.9132] |
| RS3 Sequence | Koike-Yusa2014 | official processed sgRNA activity | 6666 | 0.4160 [0.3956, 0.4367] |
| CRISPRon v1 | Koike-Yusa2014 | official processed sgRNA activity | 6666 | 0.4237 [0.4028, 0.4432] |
| RS3 Sequence | Shalem2014 | official processed sgRNA activity | 3912 | 0.2658 [0.2375, 0.2954] |
| CRISPRon v1 | Shalem2014 | official processed sgRNA activity | 3912 | 0.2593 [0.2318, 0.2869] |
| BE-Hive efficiency | HEK293T BE4 external disease library | normalized logit any-edit efficiency Y | 9975 | 0.1658 [0.1461, 0.1855] |
| DeepPrime base | HEK293T PE2 conventional scaffold fixed test | measured PE efficiency | 28883 | 0.8615 [0.8568, 0.8661] |
| PRIDICT2.0 | Library-Diverse HEK | averageedited | 22619 | 0.9056 [0.9027, 0.9082] |
| PRIDICT2.0 | Library-Diverse HEK | averageunintended | 22619 | 0.3158 [0.3023, 0.3292] |
| PRIDICT2.0 | Library-Diverse K562 | averageedited | 22752 | 0.8081 [0.8027, 0.8132] |
| PRIDICT2.0 | Library-Diverse K562 | averageunintended | 22752 | 0.2741 [0.2612, 0.2878] |


PRIDICT2 published intended-edit values round to0.91HEK293T/0.81K562. The current matching OOF values agree. Correct fold assignments are independently checked against the published workbook, but complete pretraining-overlap auditing remains incomplete. Unintended-edit prediction is clearly weaker and is NOT a purity endpoint.

BE-Hive's weak external BE4 any-edit efficiency is retained. It is not comparable to the headline internal bystander-genotype accuracy, and cannot validate BE4max intended-correction ranking. DeepPrime is limited to its testedHEK293T/PE2/conventional-scaffold system. No universal Cas9 winner is claimed.

## 2. Paired Cas9 comparison

RS3 minus CRISPRon Spearman on the SAME labels and sampled guide/gene clusters. Intervals are exploratory, not multiplicity-adjusted superiority tests across assays.

| cohort | n | delta_RS3_minus_CRISPRon | paired_ci_low | paired_ci_high | resampling_unit |
| --- | --- | --- | --- | --- | --- |
| Aguirre2016 | 7716 | 0.01206189546828218 | 0.004298781658019268 | 0.019451937922698653 | gene |
| Behan2019 | 6974 | 0.043072006272359936 | 0.024051817011178672 | 0.06339438650374364 | gene |
| Chari2015 | 1129 | -0.039232757074915414 | -0.06575127781478222 | -0.01242644841580521 | guide |
| Kim2019_test | 518 | -0.10802555594668029 | -0.13336590124143952 | -0.08200237445599819 | guide |
| Koike-Yusa2014 | 6666 | -0.007698688877977977 | -0.01709470172864393 | 0.001620936526552481 | gene |
| Shalem2014 | 3912 | 0.006475087848830163 | -0.005561645786599629 | 0.018623668839242588 | gene |


## 3. Cas13

The1000completed, independently verified RFcombined refits give medianSpearman0.667308; split/refit2.5–97.5percentiles[0.629895,0.700127], consistent with publishedapprox0.67. This is NOT an independent-target confidence interval. Native paper2000tree/mtry12 settings differ from source comparative defaults/finalCVmtry10; source-method reproduction remains qualified. GFP leave-screen-out transfer is only0.294688; source-screen performance is not universal transfer.

## 4. Specificity

Corrected WTSpCas9 assay panel:1684sites,108positives/1576negatives,9guides. Averageprecision0.186039,guide-clusterCI in reports/specificity.json. Nominal0.1%AmpliSeq threshold; individual-site raw-read detection limits unavailable. Assay-matched negatives are not universal genomewide negatives. Existing recall@K curves are retained inRun2; recall@500=1 only because all panels are exhausted. No matched comparison to Kaufmann's genomewide77%top500 is valid; no population/haplotype/SV coverage claim.

## 5. Diagnostics: missingness changes the comparison

The six author score columns have unequal coverage. Available-case CNN12ae givesrho0.812438 on1358rows; the all-model common subset contains859rows. All-model common rows, not unequal denominators, support the paired numerical comparison below. Dash placeholders were treated as missing predictions, never zeros. Numerical author-score replay does not independently verify model inference or the original train/test partition, clinical sensitivity or detection limits.

| model | cohort | endpoint | n | Spearman [95% CI] |
| --- | --- | --- | --- | --- |
| CNN12ae | all_six_models_common | original measured fluorescence activity | 859 | 0.6724 [0.6243, 0.7129] |
| CNN12a | all_six_models_common | original measured fluorescence activity | 859 | 0.6573 [0.6103, 0.6985] |
| CNND | all_six_models_common | original measured fluorescence activity | 859 | 0.6206 [0.5704, 0.6616] |
| Transformer12ae | all_six_models_common | original measured fluorescence activity | 859 | 0.4676 [0.4087, 0.5224] |
| Transformer12a | all_six_models_common | original measured fluorescence activity | 859 | 0.5430 [0.4894, 0.5896] |
| TransformerD | all_six_models_common | original measured fluorescence activity | 859 | 0.5337 [0.4784, 0.5834] |


See diagnostic_metrics.csv for both per-model available-case and common-row results and diagnostic_missingness.csv for exact coverage. Common-subset CNN12ae rho0.672393 is lower than its1358-row headline; do not present these as the same test cohort or a new independent validation.

## 6. Remaining modality scope

CRISPRi window: component-only phenotypic test, not the full learned CRISPRi/a model. Plant and microbial measurements are published author-score replays, not newly executed adapters. Plant design remains inactive. MicrobialCRISPRi phenotype cannot validate nucleaseKO. Library guide scores are not essentialgene-screen validation. Epigenetic durable repression remains blocked by missing matched functional data/model binding. No suitable alternate endpoint is invented to clear a blocker.

## Reproducibility

Run script: scripts/publication_label_benchmark.py. Exact input file SHA256s: input_provenance.json. Frozen procedure: protocols/evaluation.json. Execution output: logs/attempt_2.log. Initial serialization failure is recorded and was not accepted. All source datasets/predictions are unchanged. Large native model assets remain inRun2's external index; this is a local, not standalone portable, reproducibility package. Design thresholds are stillDRAFT, no experimental validation, best_design=null. Repeated evaluation of the same labels is not an independent replication.
