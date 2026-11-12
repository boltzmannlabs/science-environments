# CFD2016 — completed assay-matched specificity benchmark

Execution status: COMPLETED for the explicitly defined model/endpoint benchmark. This does not establish full application or experimental validation.

## Published protocol and executed scope

Native WTSpCas9 CFD2016 scores joined to1684explicitly assayed cellular sites:108positive,1576negative across9guides;correctedindel>=0.1%,3annotatedbulges excluded.

Source: Study PMID28459459; curated data https://ccsm.uth.edu/CRISPRoffT/

## Results

Average precision=0.186039;95%guide-clusterCI=[0.08740410244460901, 0.30826662003630484];trapezoidPR-AUC=0.178991. Recall@K is in recall_at_K.csv.

## Interpretation and scientific limits

Negatives mean below the assay threshold in this condition, not universal noncleavage. Nominal0.1%AmpliSeq sensitivity, no individual-site read-depthLoD. Recall@500saturates due to panel exhaustion and is not genomewide recall. No variant/haplotype/SV evaluation.

No heuristic scores, missing-feature imputation or synthetic sequence context was introduced. Existing native source/model features were retained. This rerun uses previously observed labels and is not a new blinded biological validation.

Exact inputs, model identities, splits and native code are recorded in the copied protocol files; large assets remain at the absolute source paths. Copies are SHA256-bound in ../../PROVENANCE.json.
