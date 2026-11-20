# IL-36R AntiBMPNN HCDR3 redesign

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_003_antibmpnn_hcdr3_redesign`  
**Status:** completed

## Inputs and constraints

Prepared Spesolimab–IL-36R complex from 6U6U. Editable VH positions 97–108; native light chain, framework and HCDR1/2 remain fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare complex | Saved H/L/antigen structure and declared edit mask | Exact native-chain mapping |
| Generate sequences | AntiBMPNN; 40 samples | 40 native output rows |
| Record evaluation panel | Three sequences selected in descending reported score order | Fixed panel; lower NLL is preferred |
| Evaluate panel | Shared Boltz2 evaluation | See run_005 |

## Results

Three recorded sequence pairs were evaluated in run_005. The selection used descending AntiBMPNN score, while the tool score is a negative log likelihood for which lower is preferred. Historical panel identifiers are retained; they do not indicate best-likelihood sequences.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_015_il36r_igdesign_cdr_redesign/run_003_antibmpnn_hcdr3_redesign/workflow.md)
