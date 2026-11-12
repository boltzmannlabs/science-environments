# Task 001 execution record

Run ID: `20261110_antibmpnn_her2_prodigy`
Task: `task_001_her2_trastuzumab_interaction_optimization`
Date represented by retained artifacts: November 10, 2026.

## Actual execution

1. Used PDB 1N8Z as the trastuzumab/HER2 reference complex.
2. Verified chain mapping: A=VL, B=VH, C=HER2; variable-domain positions map 1:1 to the first standard residues of the corresponding chains.
3. Ran AntiBMPNN with chains A and B editable and chain C fixed. The run manifest records model `antibmpnn_020`, 20 generations, temperature 0.1, backbone noise 0.0 and seed 37.
4. Filtered 20 paired outputs for framework integrity and required cysteine preservation. All 20 passed.
5. Selected five candidates using AntiBMPNN score and CDR-edit diversity: AB_08, AB_20, AB_04, AB_05 and AB_13.
6. Ran Antibody_Prediction on the reference plus five shortlisted candidates.
7. Submitted Boltz2 payloads for the reference and five candidates. The reference confidence was retained. Candidate signed downloads expired, so no candidate Boltz2 structures are claimed.
8. Reconstructed candidate CDR side chains on the fixed 1N8Z backbone using the original CA-to-CB direction and approximate ideal side-chain geometry.
9. Ran ProDIGy with Fab chains A+B versus HER2 chain C, then computed approximate clashes.
10. Packaged the results under `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/` and `science_env_results/her2_results/`.

## Counts

| Quantity | Count |
|---|---:|
| AntiBMPNN generated candidates | 20 |
| Framework/disulfide-eligible candidates | 20 |
| Shortlisted candidates | 5 |
| ProDIGy-evaluated candidates | 5 + reference |
| Result structures | 5 reconstructed candidates + reference |
| REF15 results | 0; unavailable |

## Stage status

| Stage | Status | Evidence |
|---|---|---|
| Workflow design | complete | `../../workflow.md`, `../../approaches.md` |
| AntiBMPNN generation | complete | `inputs/antibmpnn_results.csv`, `configs/antibmpnn_run_manifest.json` |
| Sequence filtering | complete | `../../code/01_filter_designs.py` |
| Shortlist selection | complete | `../../code/02_select_shortlist.py` |
| Antibody_Prediction | complete | [property output](../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/raw/task001_antibody_pred_output.csv) and the paired results evidence |
| Boltz2 reference | complete | paired results `../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/boltz2_confidence.json` |
| Boltz2 candidate downloads | failed/incomplete | signed URL lifetime exceeded |
| Fixed-pose reconstruction | complete | paired results `../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/structures/` |
| ProDIGy | complete | paired results `../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/evidence/prodigy_results.csv` |
| Clash analysis | complete | paired results evidence |
| REF15 | pending/unavailable | Rosetta not installed |

## Deviations and limitations

- The scientific result package is stored under the matching run directory `results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/`.
- The fixed-pose side-chain reconstruction is an approximation, not full rotamer optimization.
- ProDIGy is not comparable to REF15 Rosetta REU and does not establish experimental affinity.

## Canonical scientific results

- [Scientific report](../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/report.md)
- [Candidate inventory](../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/candidates.csv)
- [Selection table](../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261110_antibmpnn_her2_prodigy/shortlist.csv)

The source run and scientific results share run ID `20261110_antibmpnn_her2_prodigy`.
