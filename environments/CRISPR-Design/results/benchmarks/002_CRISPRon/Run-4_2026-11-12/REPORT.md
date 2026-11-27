# CRISPRon v1 — completed comparative-cohort benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Completed native v1 inference on the same six RS3-publication common-exclusion cohorts; exact30nt contexts and native thermodynamic inputs.

Source: https://europepmc.org/articles/PMC8163799 ; comparator protocol https://europepmc.org/articles/PMC9448816

## Results

| cohort | n | spearman | ci_low | ci_high |
| --- | --- | --- | --- | --- |
| Aguirre2016 | 7716 | 0.538969191060806 | 0.5225393821557369 | 0.5537245089571844 |
| Behan2019 | 6974 | 0.22283660222954474 | 0.20015739595515425 | 0.24659931017200923 |
| Chari2015 | 1129 | 0.4754265467592726 | 0.4255156898205781 | 0.5219478301834674 |
| Kim2019_test | 518 | 0.8970075638439508 | 0.8774039473981581 | 0.9131665736643461 |
| Koike-Yusa2014 | 6666 | 0.4237385351951255 | 0.4028429281864194 | 0.44316752642588014 |
| Shalem2014 | 3912 | 0.2592893707094201 | 0.231812564799139 | 0.28693845402768514 |


## Interpretation and scientific limits

This is the RS3 comparative held-out protocol, not CRISPRon_v0 internal0.80 reproduction or its different<=3mm training-exclusion procedure. No cross-assay universal superiority claim.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
