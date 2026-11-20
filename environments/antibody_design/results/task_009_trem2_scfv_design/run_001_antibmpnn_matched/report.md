# TREM2 reference-backbone AntiBMPNN redesign

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Saved reference scFv, prepared TREM2 construct and chain-local CDR mask. VH/VL framework residues and the scFv linker are protected; exact masks and numbering are retained in inputs/cdr_mask.json and inputs/imgt_numbering.json.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Verify reference | Saved structures, CDR numbering and TREM2 construct | Matched native control |
| Generate sequences | AntiBMPNN; 40 samples | 40 candidates |
| Apply sequence gates | CDR-only substitutions and identity checks | 40 pass; 39 unique sequences |
| Evaluate complexes | Boltz2, verified exact submitted VH/VL | 4 candidate predictions |

## Results

Candidate ipTM 0.3062–0.7969; matched native control 0.8987. cand13_T009-C13 is excluded from follow-up because of low interface confidence; its measured result is retained.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_009_trem2_scfv_design/run_001_antibmpnn_matched/workflow.md)
