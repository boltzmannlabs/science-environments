# Completed benchmark execution registry

Per-benchmark run registry for the active completed-only publication (program overview:
[README.md](README.md)). Only completed native-model/endpoint evaluations appear here;
each row's limitations are binding context for any use of the number. A completed model
benchmark is not validation of the full design application or experimental safety.

| ID | Model | Run | Report |
| --- | --- | --- | --- |
| 001 | RS3 Sequence held-out activity | Run-4_2026-11-12 | [Results](001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) |
| 002 | CRISPRon v1 external activity | Run-4_2026-11-12 | [Results](002_CRISPRon/Run-4_2026-11-12/REPORT.md) |
| 003 | CFD2016 experimentally assayed specificity | Run-4_2026-11-12 | [Results](003_CFD2016/Run-4_2026-11-12/REPORT.md) |
| 004 | BE-Hive BE4 any-edit efficiency | Run-4_2026-11-12 | [Results](004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) |
| 005 | PRIDICT2.0 published grouped OOF outcomes | Run-4_2026-11-12 | [Results](005_PRIDICT2/Run-4_2026-11-12/REPORT.md) |
| 006 | DeepPrime base fixed test | Run-4_2026-11-12 | [Results](006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) |
| 007 | RFcombined published-method refit evaluation | Run-4_2026-11-12 | [Results](007_RFcombined/Run-4_2026-11-12/REPORT.md) |

## Per-benchmark scope and limitations

**001 — RS3 Sequence held-out activity.** Six author-defined activity cohorts; native
30-nt context and Hsu2013/Chen2013 tracr features; exact-20mer four-model
training-union exclusions; 23,629 unique contexts / 26,915 deduplicated dataset
observations. Limits: RS3 Sequence only, not Sequence+Target; gene-cluster intervals
for genome-wide cohorts, guide-row intervals otherwise; original source duplicate-row
weighting is a separate retained reproduction, not extra independent observations.
Fresh native inference retry completed.

**002 — CRISPRon v1 external activity.** Completed native v1 inference on the same six
RS3-publication common-exclusion cohorts; exact 30-nt contexts and native thermodynamic
inputs. Limits: this is the RS3 comparative held-out protocol, not a CRISPRon_v0
internal-0.80 reproduction or its different ≤3-mm training-exclusion procedure; no
cross-assay universal superiority claim. Prior completed native execution retained, not
rerun in this retry.

**003 — CFD2016 experimentally assayed specificity.** Native WT-SpCas9 CFD2016 scores
joined to 1,684 explicitly assayed cellular sites: 108 positive, 1,576 negative across
9 guides; corrected indel ≥ 0.1%; 3 annotated bulges excluded. Limits: negatives mean
below the assay threshold in this condition, not universal non-cleavage; nominal 0.1%
AmpliSeq sensitivity without individual-site read-depth LoD; recall@500 saturates due to
panel exhaustion. Fresh native inference retry completed.

**004 — BE-Hive BE4 any-edit efficiency.** Native released HEK293T/BE4 regressor on
9,975 measured external-library any-edit efficiency labels; known training 20-mer/31-nt
contexts excluded; source-used 31-nt feature encoding independently matched to native
input. Limits: BE4, not BE4max; target is normalized logit any-edit efficiency, not
intended-edit purity or genotype distribution; original internal tuning
membership/whole-gene exclusion not fully available; weak transfer. Fresh native
inference retry completed.

**005 — PRIDICT2.0 published grouped OOF outcomes.** Original Library-Diverse
group-fold assignments, matching cell heads and missing-label exclusions; two source
model families averaged within the single held-out fold only. Limits: complete
base-pretraining library overlap not audited; intended and unintended edit fractions
are separate endpoints and unintended-edit prediction is not purity validation; no
PE3-nick-design or all-edit-genotype conclusion. Fresh native inference retry completed.

**006 — DeepPrime base fixed test.** Original HEK293T/PE2/conventional-scaffold fixed
test n=28,883 against 259,910 training rows; zero exact-input and 74-nt-target
overlaps; native 74-nt/24-numeric inputs, source mean/std and 5-checkpoint ensemble.
Limits: only this matched editor/cell/scaffold condition evaluated; author-provided
upstream DeepSpCas9 feature retained, not substituted; no unintended-edit or purity
conclusion. Fresh native inference retry completed.

**007 — RFcombined published-method refit evaluation.** Completed 1,000 native
randomForest (2,000-tree/mtry-12) fits using the published 2,918-row 35-feature matrix,
source R-3.5 seed schedule, screen-balanced 70/30 splits and training-only scaling; all
1,000 partitions/predictions independently verified train/test-disjoint. Limits: a
completed qualified published-method reimplementation, not an exact replay of
conflicting source variants (comparative code uses defaults/finalCV mtry 10); published
precomputed features and global feature selection inherited. Prior completed native
execution retained, not rerun in this retry.

## Governance

Exact input/model manifests are inside each completed run; all copied scientific files
are bound by [PROVENANCE.json](PROVENANCE.json)/[PROVENANCE.sha256](PROVENANCE.sha256).
Large datasets, weights and environments remain at indexed source locations. Integrity
is machine-checked by [tests/test_completed_benchmarks.py](../tests/test_completed_benchmarks.py)
(scope, hashes, fresh-inference verification, metric recomputation, link resolution).
No wet-lab validation or calibrated design-gate freeze is claimed.
