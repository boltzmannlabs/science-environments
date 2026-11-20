# C5 AntiBMPNN redesign and shared structural evaluation

**Task:** `task_013_c5_igdesign_cdr_redesign`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Eculizumab Fv from 5I5K: VH 122 aa, VL 107 aa. Editable VH positions are 97–111 for HCDR3-only, or 26–33/51–58/97–111 for HCDR123. VL and VH framework are fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; temperature 0.1; 100 per scope | 200 generated sequences |
| Assemble evaluation panel | 2 AntiBMPNN designs + 4 designs imported from run_002 + native control | 7 fixed sequence pairs |
| Predict structures | Boltz2 Fv and ESMFold VH–linker–VL | 14 accepted models |
| Measure recovery and geometry | Native AAR; Cα scRMSD after framework fit | Candidate consistency vs same-predictor native model; native control vs 5I5K crystal |

## Results

AntiBMPNN maximum HCDR3 AAR is 0.4000 in each 100-sample scope. The closest candidate Fv is ig_hcdr3_s002 for Boltz2 (0.371 Å) and ig_hcdr3_s031 for ESMFold (0.139 Å).

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

[Scientific run record](run.json) · [Workflow](../../../src/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/workflow.md)
