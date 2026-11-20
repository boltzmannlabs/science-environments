# IL-36R IgDesign HCDR3 reconstruction

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_001_igdesign_hcdr3_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Spesolimab Fv from 6U6U: VH 119 aa, VL 108 aa. Only VH 97–108 is editable; native VL, framework and HCDR1/2 remain fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate 1-shot | IgDesign; saved one-sample configuration | 1 sample |
| Generate 100-sample pool | IgDesign; separate saved configuration | 100 samples |
| Measure native recovery | Per-CDR position identity | HCDR3 AAR for 101 samples |
| Select evaluation entries | Ascending HCDR3 cross-entropy loss; distinct recorded sequences | 3 panel members evaluated in run_005 |

## Results

HCDR3 AAR: 1-shot 0.5833; maximum over the separate 100-sample pool 0.8333. Structural evaluation is retained in run_005.

The [task benchmark](../../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/comparison.md) reports candidate-level values, controls, metric definitions and published comparison scope. These are computational measurements; affinity was not measured for the generated candidates.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_015_il36r_igdesign_cdr_redesign/run_001_igdesign_hcdr3_native_reconstruction/workflow.md)
