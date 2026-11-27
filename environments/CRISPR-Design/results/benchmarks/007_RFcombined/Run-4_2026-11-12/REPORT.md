# RFcombined — completed 1000-refit published-method benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Completed1000native randomForest2000tree/mtry12fits using published2918row35feature matrix,sourceR3.5seed schedule,screen-balanced70/30splits and training-only scaling. All1000partitions/predictions independently verified.

Source: https://europepmc.org/articles/PMC7294996

## Results

MedianSpearman=0.667308;2.5–97.5%split/refitinterval=[0.6298954555379912, 0.7001266891035433]. The separate leave-screen-out measurements are retained in leave_screen_out.csv.

## Interpretation and scientific limits

Completed qualified published-method reimplementation,not exact replay of conflicting source variants:comparative code uses defaults/finalCVmtry10. Published precomputed features/globalfeatureselection inherited. Refit percentile spread is not independent-targetCI. GFPLOSO0.294688 limits transfer.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
