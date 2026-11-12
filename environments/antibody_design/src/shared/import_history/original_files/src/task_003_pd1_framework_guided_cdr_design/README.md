# Task 003 source package

This directory contains the organized source-side record for
`task_003_pd1_framework_guided_cdr_design`.

## Contents

- `approaches.md` — considered workflows, selection and applicability.
- `workflow.md` — selected ordered workflow, protected regions, gates and ranking.
- `code/` — preparation code and preserved legacy local-run code.
- `sources/` — framework, target, H965 control, epitope and provenance.
- `inputs/` — exact prepared PDB inputs for the selected platform workflows.
- `workflow/workflow_design.md` — detailed Boltzmann workflow comparison.
- `workflow/execution_status.md` — actual completed, pending and blocked stages.
- `runs/20261110_pd1_framework_stage0_pending/` — machine-readable execution record
  for the verified stage-0 preparation and pending platform submission.
- `runs/20261110_local_proteinmpnn_boltz2/` — matching source record for the historical
  local ProteinMPNN/Boltz2 comparison result under the same run ID.

## Scientific inputs

1. Framework: humanized IGHV3-23/IGKV1-5 FR sequences from Table 1 of the tFold
   paper, with IGHJ4/IGKJ1 assignments.
2. Target: human PD-1 PDB 4ZQK chain B construct, 106 aa.
3. Epitope: PD-1 residues contacting PD-L1 in 4ZQK, using a 6.0 Å heavy-atom cutoff.
4. H965: comparison control only; not the design parent or candidate input.

## Code used

- `code/stage0_prepare_framework_pd1.py`: verifies the staged H965 reference sequence,
  extracts exact framework atoms, creates the PD-1 target PDB and computes the epitope.
- `code/legacy_local_run/prepare_struct.py` and `design_cdrh3.py`: preserved code from
  an earlier local CDR-H3-only ProteinMPNN/Boltz2 attempt. It is historical comparison
  evidence, not the selected six-CDR Boltzmann workflow.

## Platform workflow

Primary: `rfdiffusion_proteinmpnn` in antibody mode.
Comparison: `epitope_abgen` PDB branch followed by
`Antibody_Backbone_to_Sequence_Generation`.
Downstream planned stages: `Boltz2`, `ipsae-protein`, `Antibody_Prediction`,
`stability-binding-ddg`, `Antibody_Numbering` and `tm_align`.

## Status boundary

Stage-0 preparation completed. The first Boltzmann PDB upload passed syntax checks but
returned partial validation because chain selection and scientific suitability required
explicit approval. The approval prompt timed out. No Boltzmann design job was submitted,
and no candidate-level platform metrics or final shortlist are claimed.

Scientific results, when executed, belong under the matching `results/<task_id>/<run_id>/`
directory. The historical local result is paired with
`results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/`.
It is not silently relabeled as the pending platform run.

## Canonical source and results

- [Recorded execution](runs/20261110_local_proteinmpnn_boltz2/execution.md)
- [Execution provenance](runs/20261110_local_proteinmpnn_boltz2/provenance.json)
- [Scientific report](../../results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/report.md)

Scientific artifacts are stored in the matching results run. Historical execution records are retained under the source run's `runs/20261110_local_proteinmpnn_boltz2/logs/packaging_history/`.
