# IL-36R AntiBMPNN HCDR123 redesign

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_004_antibmpnn_hcdr123_redesign`  
**Status:** completed

## Inputs and constraints

Same Spesolimab–IL-36R prepared complex. Editable VH positions 26–33, 51–58 and 97–108; light chain and VH framework remain fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare complex | Saved H/L/antigen structure and declared edit mask | Exact native-chain mapping |
| Generate sequences | AntiBMPNN; 40 samples | 40 native output rows |
| Record evaluation panel | Three sequences selected in descending reported score order | Fixed panel; lower NLL is preferred |
| Evaluate panel | Shared Boltz2 evaluation | See run_005 |

## Results

Three recorded sequence pairs were evaluated in run_005. AntiBMPNN selection used descending negative log likelihood, so the fixed panel is not a best-likelihood selection from the generation pool.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_015_il36r_igdesign_cdr_redesign/run_004_antibmpnn_hcdr123_redesign/workflow.md)
