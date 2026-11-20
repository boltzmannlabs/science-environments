# ESMFold and ProteinMPNN evaluation of the fixed EGFR panel

**Task:** `task_008_egfr_scfv_design`  
**Run:** `run_002_esmfold_proteinmpnn_evaluation`  
**Status:** completed

## Inputs and constraints

The six selected sequences from run_001 and its native reference, each a 241-residue VH–linker–VL scFv. This run evaluates the supplied panel without generating new designs.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare panel | Saved FASTA and run_001 shortlist | 7 sequences |
| Predict scFv structures | ESMFold | 7 accepted single-chain models |
| Score sequences | ProteinMPNN score-only on each sequence’s own ESMFold backbone | Negative log likelihood; lower is preferred |
| Summarize | Whole-scFv confidence and sequence properties | Seven-row metrics table |

## Results

Candidate ESMFold pLDDT 85.07–85.84; reference 85.40. Lowest candidate own-backbone ProteinMPNN NLL: cet_008_r1_s18, 1.4510; reference 1.4692.

The [task benchmark](../../../benchmark/monoclonal_antibody_design/task_008_egfr_scfv_design/comparison.md) reports candidate-level values, controls, metric definitions and published comparison scope. These are computational measurements; affinity was not measured for the generated candidates.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation/workflow.md)
