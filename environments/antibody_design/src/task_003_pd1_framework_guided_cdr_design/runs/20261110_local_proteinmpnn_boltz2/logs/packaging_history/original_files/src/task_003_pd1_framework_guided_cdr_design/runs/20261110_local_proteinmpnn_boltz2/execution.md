# Execution record — 20261110_local_proteinmpnn_boltz2

Task: `task_003_pd1_framework_guided_cdr_design`
Status: `COMPLETED_HISTORICAL_LOCAL_RUN`

ProteinMPNN redesigned the 10-residue H965 CDR-H3 while protecting the framework, light chain and PD-1 target. Twenty designs were generated, 17 were unique by CDR-H3 sequence, and candidates 2, 9 and 11 were structure-predicted with Boltz2. The pending platform run `20261110_pd1_framework_stage0_pending` is separate and produced no candidate-level platform output.

Retained commands:
- `python code/legacy_local_run/prepare_struct.py`
- `python code/legacy_local_run/design_cdrh3.py`
- Boltz2 prediction for H965 reference and candidates 2, 9 and 11
- confidence extraction and candidate comparison

Results: `../../../../../results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/`
