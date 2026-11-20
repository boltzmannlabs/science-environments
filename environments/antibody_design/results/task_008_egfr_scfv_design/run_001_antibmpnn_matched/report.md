# Cetuximab CDR redesign and matched complex evaluation

**Task:** `task_008_egfr_scfv_design`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Prepared 1YY9 Fv and 613-residue EGFR construct. VH 119 aa, VL 107 aa; scFv linker `(G4S)3`. Editable variable-domain positions: VH 26–32, 52–56, 98–108; VL 24–34, 50–56, 89–97. Framework and linker are fixed.

## Executed steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare reference | PDB extraction; ANARCI Chothia numbering | Exact parent VH/VL sequence match |
| Generate sequences | AntiBMPNN; 20 samples; H/L CDR edits | 20 recorded candidates |
| Screen sequences | Mask, uniqueness, cysteine, glycosylation-sequon and sequence-property checks | 6 selected candidates |
| Evaluate complexes | Boltz2; same EGFR construct and conditions for designs and reference | 6 candidate models + native control |

## Results

Highest candidate ipTM: cet_008_r1_s15, 0.8549; matched native control 0.9065. No candidate improves the reference interface score.

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

[Scientific run record](run.json) · [Workflow](../../../src/task_008_egfr_scfv_design/run_001_antibmpnn_matched/workflow.md)
