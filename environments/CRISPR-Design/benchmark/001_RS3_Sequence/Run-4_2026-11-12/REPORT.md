# RS3 Sequence — completed held-out benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Six author-defined activity cohorts; native30nt context and Hsu2013/Chen2013 tracr features. Exact20mer four-model training-union exclusions;23629unique contexts/26915deduplicated dataset observations.

Source: https://europepmc.org/articles/PMC9448816

## Results

| cohort | n | spearman | ci_low | ci_high |
| --- | --- | --- | --- | --- |
| Aguirre2016 | 7716 | 0.5510310865290882 | 0.5357642343253478 | 0.5664983374381501 |
| Behan2019 | 6974 | 0.2659086085019047 | 0.24187312910415937 | 0.2872178667124398 |
| Chari2015 | 1129 | 0.4361937896843572 | 0.38608134442540015 | 0.4816613447959462 |
| Kim2019_test | 518 | 0.7889820078972705 | 0.7505639813159306 | 0.8241350961724466 |
| Koike-Yusa2014 | 6666 | 0.4160398463171475 | 0.3955612730716287 | 0.43671327964116896 |
| Shalem2014 | 3912 | 0.26576445855825026 | 0.2375494934768222 | 0.2954364602852762 |


## Interpretation and scientific limits

RS3 Sequence only, not Sequence+Target. Gene-cluster intervals for genomewide cohorts, guide-row intervals otherwise. Original source duplicate-row weighting is a separate retained reproduction, not extra independent observations.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
