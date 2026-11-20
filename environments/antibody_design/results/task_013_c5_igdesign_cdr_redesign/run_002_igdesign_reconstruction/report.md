# C5 IgDesign masked native reconstruction

**Task:** `task_013_c5_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Eculizumab VH/VL pair and heavy-chain edit masks as run_001. One sample and a separate 100-sample pool are generated for each scope; the raw CSVs and serialized sampling configurations are retained.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate HCDR3 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Generate HCDR123 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Measure native recovery | Position-aligned per-CDR AAR | 202 sample-level metric rows |
| Select shared evaluation panel | Four recorded designs | Boltz2 and ESMFold evaluation retained in run_001 |

## Results

HCDR3-only 1-shot AAR is 0.4667; the separate 100-sample pool has mean 0.5193 and maximum 0.6667. HCDR123 pool mean HCDR3 AAR is 0.5160; maximum 0.6667.

The [task benchmark](../../../benchmark/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign/comparison.md) reports candidate-level values, controls, metric definitions and published comparison scope. These are computational measurements; affinity was not measured for the generated candidates.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_013_c5_igdesign_cdr_redesign/run_002_igdesign_reconstruction/workflow.md)
