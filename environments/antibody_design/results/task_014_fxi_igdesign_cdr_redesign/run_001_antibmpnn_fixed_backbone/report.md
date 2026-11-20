# FXI AntiBMPNN fixed-backbone redesign

**Task:** `task_014_fxi_igdesign_cdr_redesign`  
**Run:** `run_001_antibmpnn_fixed_backbone`  
**Status:** completed

## Inputs and constraints

Osocimab Fv from 6HHC: VH 120 aa, VL 107 aa. Editable VH positions: 97–109 for HCDR3-only, or 26–33/51–58/97–109 for HCDR123. Framework and VL are fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; 20 per scope | 40 samples |
| Verify and deduplicate | VL identity, VH length, protected residues and mask checks | 40 pass; 11 HCDR3 + 15 HCDR123 unique sequences |
| Select panel | Five sequences per scope | 10 candidate sequence pairs |
| Evaluate geometry | Boltz2; exact sequence checks; Cα framework fit | 10 candidate models + native control |

## Results

Best recovery is 0.6923 (HCDR3) and 0.7241 (HCDR123). Geometry leader t014r001_hcdr123_scope_s05 has AAR 0.6897, nine substitutions, Fv deviation 0.3978 Å and HCDR3 deviation 1.3367 Å from the predicted native Fv.

The [task benchmark](../../../benchmark/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign/comparison.md) reports candidate-level values, controls, metric definitions and published comparison scope. These are computational measurements; affinity was not measured for the generated candidates.

## Saved artifacts

| Artifact | Contents |
| --- | --- |
| [candidates.csv](candidates.csv) | Generated candidates or supplied evaluation entries, with source linkage |
| [shortlist.csv](shortlist.csv) | Recorded selection and evaluated identifiers |
| [sequences.fasta](sequences.fasta) | Saved sequences; paired chains are labelled |
| [metrics.csv](metrics.csv) | Calculated values and stated measurement scope |
| [benchmark_comparison.csv](benchmark_comparison.csv) | Machine-readable comparison with stated reference scope |
| [structures/](structures/) | Accepted structural models, where this run predicts structures |
| [raw/](raw/) | Native generation and prediction products |

[Scientific run record](run.json) · [Workflow](../../../src/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone/workflow.md)
