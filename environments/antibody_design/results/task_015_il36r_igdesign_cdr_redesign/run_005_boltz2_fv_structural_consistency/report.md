# IL-36R shared Boltz2 Fv evaluation

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_005_boltz2_fv_structural_consistency`  
**Status:** completed

## Inputs and constraints

Twelve fixed sequence pairs from runs 001–004, three per generation run, plus the unmodified Spesolimab VH/VL reference. All modelled chains were checked against the supplied sequences.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Assemble panel | Saved boltz2_panel.json; 12 designs + reference | 13 exact sequence pairs |
| Predict Fv structures | Matched Boltz2 settings | 13 accepted models |
| Verify model identity | Exact VH and VL sequence checks | All 13 panel members verified |
| Measure structure and confidence | Framework Kabsch fit; N/Cα/C/O backbone vs experimental 6U6U | 12 ranked candidates and native control |

## Results

Lowest candidate Fv deviation is antibmpnn_hcdr3_top3, 0.4022 Å; native control 0.3178 Å. Lowest candidate HCDR3 deviation is igdesign_hcdr123_top2, 0.6926 Å. The AntiBMPNN subsets are the fixed recorded panels, selected in descending NLL order.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_015_il36r_igdesign_cdr_redesign/run_005_boltz2_fv_structural_consistency/workflow.md)
