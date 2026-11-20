# IL-36R IgDesign HCDR123 reconstruction

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_hcdr123_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Spesolimab Fv. Editable VH positions 26–33, 51–58 and 97–108; VL and VH framework remain fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate 1-shot | IgDesign; saved one-sample configuration | 1 sample |
| Generate 100-sample pool | IgDesign; separate saved configuration | 100 samples |
| Measure recovery | Per-CDR position identity | 101 samples; separate per-CDR maxima |
| Select evaluation entries | Ascending summed CDR cross-entropy loss | 3 panel members evaluated in run_005 |

## Results

1-shot HCDR1/2/3 AAR: 0.7500/0.6250/0.5833. Per-CDR maxima over 100 samples: 1.0000/0.7500/0.8333; these maxima need not occur in one sequence.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_015_il36r_igdesign_cdr_redesign/run_002_igdesign_hcdr123_native_reconstruction/workflow.md)
