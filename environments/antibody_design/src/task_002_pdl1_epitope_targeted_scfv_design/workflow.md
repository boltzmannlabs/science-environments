# Task 002 executed workflow

## Objective
Design VH-first scFv candidates against the human PD-L1 V-like domain, prioritizing contact with PD-L1 residues I37, Y39, E41, R96 and M98 while preserving the generic Germinal scFv framework and G4S x3 linker.

## Executed path

```text
Germinal framework + PD-L1 V-like target
        |
        v
Boltzmann rfdiffusion_proteinmpnn
        |
        v
20 generated RF-Antibody candidates
        |
        v
10 candidates selected by the explicit local Boltz-2 batch list
        |
        v
Local open-source Boltz-2 complex prediction, sequentially
        |
        v
Biopython interface analysis: contacts, hotspot pairs, minimum distance, clashes
        |
        v
Post-hoc epitope filter and composite ranking
        |
        v
5 candidates submitted to Boltzmann Antibody_Prediction
        |
        v
Final shortlist: rf1_d5, rf1_d2, rf1_d3, rf0_d5, rf0_d0 contrast
```

## Platform jobs

| Stage | Job | ID | Status | Output |
|---|---|---|---|---|
| Design-selected branch | `epitope_abgen` | `6af33484b2d9f21f0dc8d50e` | pending/no output | no backbone or sequence output |
| Executed generation | `rfdiffusion_proteinmpnn` | `68d12a5de5b6a2fdc0e3c443` | completed | 20 candidate records |
| Properties | `Antibody_Prediction` | `6af36e74d982f81aac5b4ec8` | completed | 5 candidates; thermal stability, solubility and CDR annotations |

## Local commands actually retained

- `code/boltz2_run_batch.sh`: sequential Boltz-2 prediction with three recycling steps and MSA server enabled.
- `code/analyze_interface.py`: extracts confidence fields and computes interface/hotspot/clash measurements.
- `code/retained_root_scripts/h5_rmsd.py`: H5 reconstruction comparison against the 35TL reference.
- `code/rank_and_package.py`: reproducible reconstruction of the candidate table and FASTA package.
- `code/compute_novelty.py`: reproducible VH/VL and CDR3-H identity comparison against H5.

## Ranking rule

The executed composite score was:

```text
score = ipTM + 0.08 * number_of_hotspots_touched
        - 0.03 * ipDE - 0.01 * clash_count
```

The ranking was applied only to the 10 locally structure-evaluated candidates. Candidates touching all five hotspots were preferred. `rf0_d0` was retained only as a contrast because it had high ipTM but zero declared-hotspot engagement.

## Resource policy

Boltz-2 models were run sequentially on the RTX 3090 (24 GB VRAM). No OOM event occurred. The platform property job was run once for the five-candidate shortlist; no duplicate or top-up job was submitted.
