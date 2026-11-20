# TREM2 AgCDR backbone diversification and inverse folding

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_003_agcdr_backbone`  
**Status:** completed

## Inputs and constraints

Prepared reference Fv and TREM2 antigen structures. AgCDR generates eight backbone samples; the evaluated sequence panel comes from sample 7. Framework and chain-local CDR constraints are checked before selection.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Diversify backbone | AgCDR; 8 samples, 10 steps | 8 backbone samples |
| Select backbone | Recorded sample-7 backbone | One backbone for sequence generation |
| Generate sequences | Local AntiBMPNN; 40 samples | 40 candidate sequences |
| Evaluate complexes | Boltz2; exact sequence identity check | 4 predictions; cand032 retained |

## Results

Best candidate cand032: ipTM 0.7413, pTM 0.8636; matched reference ipTM 0.8987. The full evaluated range is 0.3633–0.7413.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_009_trem2_scfv_design/run_003_agcdr_backbone/workflow.md)
