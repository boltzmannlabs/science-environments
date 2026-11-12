# Task 001 approaches

## Target and objective

Design paired trastuzumab-derived VH/VL variants against human HER2 while preserving the reference binding region, antibody pairing, framework and required disulfides.

## Considered approaches

| ID | Approach | Status | Suitability | Limitation |
|---|---|---|---|---|
| W1 | AntiBMPNN all-CDR -> filtering -> fixed-pose reconstruction -> ProDIGy | Selected and executed | Highest suitability: structure-conditioned on 1N8Z, all six CDRs editable, reference pose retained | Side-chain reconstruction is approximate; ProDIGy is not REF15 |
| W2 | ProteinMPNN CDR-H3-only -> Boltz2 -> downstream scoring | Historical comparison | Fast and simple CDR-H3 baseline | Only one CDR is optimized; historical run is not the primary result |
| W3 | De novo/random sequence generation -> Boltz2 -> scoring | Considered, not selected | No starting structure required | Does not preserve the reference binding region and depends on unreliable de novo VH-HER2 interface placement |

## Selection decision

W1 was selected because it directly conditions sequence design on the experimentally deposited 1N8Z complex and allows all six CDRs to change while the framework and disulfide positions remain protected. Boltz2 showed strong reference VH-VL confidence but weak VH-HER2 interface confidence, so fixed-pose reconstruction was used for the matched binding comparison.

## Historical distinction

The existing `code/retained_root_scripts/design_cdrh3.py` and the files under `results/.../evidence/historical_proteinmpnn_cdrh3/` belong to the earlier W2-style ProteinMPNN CDR-H3 run. They are retained as historical evidence and are not relabeled as the selected AntiBMPNN run.
