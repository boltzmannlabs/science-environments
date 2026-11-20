# TREM2 IgDesign heavy-CDR redesign

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_002_igdesign_local`  
**Status:** completed

## Inputs and constraints

Paired reference VH/VL and prepared TREM2 complex. The native heavy CDRs are redesigned while VL and VH framework are fixed. Exact regions, conditioning and sampling settings are retained in inputs/hcdr123_trem2.yaml.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare conditioning | Reference complex and heavy-CDR mask | Paired light-chain and antigen context |
| Generate sequences | IgDesign; 100 samples | 100 native candidate rows |
| Apply sequence gates | Protected-residue and sequence checks | 95 passing unique candidates |
| Evaluate complexes | Boltz2; exact model sequence verification | 4 accepted candidate predictions |

## Results

Best candidate cand067: ipTM 0.8618, pTM 0.9198; matched reference ipTM 0.8987. Four candidates span ipTM 0.7326–0.8618.

The [task benchmark](../../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/comparison.md) reports candidate-level values, controls, metric definitions and published comparison scope. These are computational measurements; affinity was not measured for the generated candidates.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_009_trem2_scfv_design/run_002_igdesign_local/workflow.md)
