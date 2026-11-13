# Execution record — 20261110_pd1_framework_stage0_pending

Task: `task_003_pd1_framework_guided_cdr_design`
Status: `PENDING_PLATFORM_APPROVAL`
Scientific results for this pending run: none; candidate generation was not submitted.

Historical local results: [report.md](../../../../results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/report.md).

## Completed stages

1. Retrieved and parsed the study full text through NCBI eutils.
2. Extracted the Table 1 framework sequences and CDR-length rules.
3. Verified PDB 4ZQK chain identities and target sequence.
4. Verified the H965 reference complex artifact and framework identity.
5. Computed the PD-1 ligand-binding contact surface.
6. Generated `inputs/framework.pdb`, `inputs/pd1_target.pdb` and the epitope JSON.

## Platform attempt

The first `boltzmann_upload` attempt targeted `rfdiffusion_proteinmpnn` and
`antibody_pdb_path`. Coordinate syntax passed. The connector returned partial
validation because chain selection and scientific suitability were unchecked.

The required approval prompt timed out. Therefore:

- no `allow_partial_validation=true` retry was made;
- no Boltzmann design job was submitted;
- no job ID, experiment ID or platform candidate artifact exists for this run.

## Planned but not executed

- `rfdiffusion_proteinmpnn`
- `epitope_abgen`
- `Antibody_Backbone_to_Sequence_Generation`
- candidate-level `Boltz2` and `ipsae-protein`
- `Antibody_Prediction`
- `stability-binding-ddg`
- open-source validation for newly generated candidates
- final platform shortlist

## Historical comparison

An earlier local CDR-H3-only ProteinMPNN/Boltz2 attempt is retained under the task
results evidence and `code/legacy_local_run/`. It is not this run and is not used to
claim completion of the selected six-CDR platform workflow.
