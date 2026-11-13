# Protocol reproduction campaign

Start with [REPORT.md](REPORT.md), [task ledger](task_execution_status.csv), and [RFcombined independent completion verification](cas13_completion_verification.json).

Byte-identical scientific artifacts are hash-bound in PROVENANCE.json and PROVENANCE.sha256. Large datasets, model weights, environments and1000 RF partitions/predictions remain at absolute source paths in EXTERNAL_ARTIFACT_INDEX.json. This is a local reproducibility package, not a self-contained portable distribution. Source scripts retain their original absolute paths; inspect their protocol/environment manifests before rerunning.
