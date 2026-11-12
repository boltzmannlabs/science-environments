# Task 001 executed workflow

## Workflow graph

```text
PDB 1N8Z reference complex
        |
        v
AntiBMPNN, chains A+B designed; chain C fixed
        |
        v
20 paired VH/VL candidates
        |
        v
Framework + cysteine + pairing checks
        |
        v
AntiBMPNN score + CDR-edit diversity shortlist
        |
        v
5 candidates: AB_08, AB_20, AB_04, AB_05, AB_13
        |
        +--> Antibody_Prediction: thermal stability + solubility
        |
        +--> Boltz2 reference/candidate payloads
        |       reference retained; candidate downloads failed
        |
        v
Fixed 1N8Z backbone + designed CDR side-chain reconstruction
        |
        v
ProDIGy Fab(A,B) versus HER2(C) + clash analysis
        |
        v
Ranked results and her2_results bundle
```

## Actual stage status

| Stage | Status | Evidence |
|---|---|---|
| Reference/chain verification | complete | `code/00_verify_chain_mapping.py`, `inputs/1N8Z_deposited_complex.pdb` |
| AntiBMPNN generation | complete | `runs/.../inputs/antibmpnn_results.csv`, `configs/antibmpnn_run_manifest.json` |
| Sequence filtering | complete | `code/01_filter_designs.py`; 20/20 passed framework/disulfide checks |
| Shortlist selection | complete | `code/02_select_shortlist.py`; five candidates |
| Antibody_Prediction | complete | `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/raw/task001_antibody_pred_output.csv` and `task001_props_parsed.csv` |
| Boltz2 reference | complete | results `evidence/boltz2_confidence.json` and retained reference archives |
| Boltz2 candidate downloads | failed/incomplete | signed URL lifetime was exceeded; no candidate Boltz2 structures claimed |
| Fixed-pose reconstruction | complete | `code/04_reconstruct_fixed_pose.py`; five PDBs in results |
| ProDIGy | complete | `code/06_run_prodigy.sh`; `results/.../evidence/prodigy_results.csv` |
| Clash analysis | complete | `code/05_compute_clashes.py` and ProDIGy evidence table |
| REF15/Rosetta | pending/unavailable | Rosetta not installed; no REF15 result claimed |

## Ranking rule

The final table ranks candidates primarily by fixed-pose ProDIGy ΔG relative to the reference, with AntiBMPNN score, stability and clash count used as supporting evidence. The best computational candidate is AB_13: ΔG −10.9 kcal/mol versus reference −9.9, predicted KD 9.4e−9 M versus 5.6e−8 M, and 27 versus 26 clashes.

## Resource policy

GPU-backed Boltzmann jobs were submitted through the platform. Local structure/property analyses were run with the conda base Python. The local GPU was not used for the ProDIGy or Biopython steps. No OOM event was recorded for this task.
