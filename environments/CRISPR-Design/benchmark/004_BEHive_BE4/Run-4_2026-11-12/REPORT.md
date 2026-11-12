# BE-Hive BE4 — completed measured-label efficiency transfer benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Native released HEK293T/BE4 regressor;9975measured external-library any-edit efficiency labels;known training20mer/31nt contexts excluded. Source-used31nt feature encoding independently matched to native featurizer without fabricated flanks.

Source: https://europepmc.org/articles/PMC7384975

## Results

| n | spearman | ci_low | ci_high |
| --- | --- | --- | --- |
| 9975 | 0.16576576051572114 | 0.14610144283899645 | 0.1855116466834055 |


## Interpretation and scientific limits

BE4,notBE4max. Target is normalizedlogit any-edit efficiency,not intended-edit purity or genotype distribution. Original internal tuning membership/whole-gene exclusion not fully available. Weak transfer performance is retained.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
