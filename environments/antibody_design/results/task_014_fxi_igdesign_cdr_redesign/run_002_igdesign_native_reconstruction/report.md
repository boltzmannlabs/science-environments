# FXI IgDesign masked native reconstruction

**Task:** `task_014_fxi_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Osocimab VH/VL and masks as run_001. The saved YAML configurations specify separate 1-shot and 100-sample executions for HCDR3 and HCDR123.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate samples | IgDesign; 1 + 100 samples per scope | 202 samples |
| Verify and deduplicate | Native framework/VL preservation and sequence identity | 158 unique sequences |
| Measure native recovery | Position-aligned designed-scope AAR | 1-shot and best-of-100 endpoints |
| Evaluate geometry | Five designs per scope; Boltz2; Cα framework fit | 10 candidate models + native control |

## Results

Designed-scope AAR is 0.6923/0.8462 for HCDR3 1-shot/best-of-100 and 0.7241/0.7931 for HCDR123. t014r002_hcdr3_best100_012 has HCDR3 deviation 1.3144 Å and Fv deviation 0.4382 Å from the predicted native Fv.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_014_fxi_igdesign_cdr_redesign/run_002_igdesign_native_reconstruction/workflow.md)
