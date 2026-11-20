# PRIDICT2.0 — completed original-group-fold outcome benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Original Library-Diverse group-fold assignments,matching cell heads and missing-label exclusions;two source model families averaged within the single held-out fold only. Original workbook fold IDs independently matched with zero mismatches.

Source: https://europepmc.org/articles/PMC7617539

## Results

| cohort | endpoint | n | spearman | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- |
| Library-Diverse HEK | averageedited | 22619 | 0.9056291433786648 | 0.9026572394423762 | 0.9082425196866566 |
| Library-Diverse HEK | averageunintended | 22619 | 0.31582255699226985 | 0.3022793880998659 | 0.32918785178564897 |
| Library-Diverse K562 | averageedited | 22752 | 0.8081186019351135 | 0.8026675527350727 | 0.8132442162955482 |
| Library-Diverse K562 | averageunintended | 22752 | 0.27408742976879114 | 0.2612396110559815 | 0.2878322234978804 |


## Interpretation and scientific limits

Complete base-pretraining library overlap not audited. Intended and unintended edit fractions are separate endpoints; unintended-edit prediction is not purity validation. No PE3nick-design or all-editor transfer claim.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
