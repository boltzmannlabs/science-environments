# Task 005 execution record

Run ID: `20261110_cdrh3_boltz2_glycan_prodigy`
Task ID: `task_005_gal3bp_glycan_aware_interface_refinement`

## Final status

PARTIALLY COMPLETED. The candidate-generation, structure-prediction, interface-analysis, glycan-accessibility and Prodigy stages have retained artifacts. Platform AntiBMPNN approval, Antibody_Prediction, heated MD and like-for-like paper reproduction were not completed.

## Stage status

| Stage | Status | Retained evidence |
|---|---|---|
| Verify BDBV-43 and LGALS3BP inputs | COMPLETED | PDB 7KEW, prepared FASTAs, task report |
| Compare workflows | COMPLETED | `src/.../approaches.md`, `workflow.md`, original task workflow design |
| Platform AntiBMPNN generation | BLOCKED | Partial-validation approval prompt timed out; no job submitted |
| Local ProteinMPNN CDR-H3 generation | COMPLETED | `results/.../evidence/all_designs.fa`, `task005_cdrh3_designed.json` |
| Sequence filtering/top-3 selection | COMPLETED | `results/.../candidates.csv`, prepared candidate FASTAs |
| Boltz2 structure prediction | COMPLETED | `results/.../structures/` plus confidence JSON files |
| Interface metrics | COMPLETED | `../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/evidence/raw/task005_interface_metrics.json` |
| Glycan-aware accessibility | COMPLETED, APPROXIMATE | `../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/evidence/raw/glycan_aware_analysis.json` |
| Prodigy validation | COMPLETED | `../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/evidence/raw/prodigy_validation.json` |
| Antibody_Prediction developability | PENDING | No result artifact; do not infer property scores |
| Heated-MD interface stability | BLOCKED/PENDING | No replicas; 5 Å criterion not tested |
| Published benchmark reproduction | NOT COMPARABLE | Study-specific inputs unavailable |
| Final packaging | COMPLETED | `results/.../candidates.csv`, `report.md`, metrics and evidence |

## Executed candidate set

- Reference control: BDBV-43, CDR-H3 `ARDEIIGADS`.
- cand11: CDR-H3 `GLYPVPNSQT`.
- cand7: CDR-H3 `FLYPRPGSAT`.
- cand17: CDR-H3 `GVYPVPLGSS`.

The local ProteinMPNN design stage generated 20 designs, of which 17 were unique by CDR-H3 sequence. The three listed candidates were carried into structure prediction and evaluation.

## Evaluation settings

- Complex chains: A/B antibody, C LGALS3BP.
- Interface residue pair threshold: Cα-Cα < 8.0 Å.
- vdW atom threshold: < 4.5 Å.
- H-bond proxy: N/O heavy-atom pair < 3.5 Å.
- Glycan analysis: simplified 12-sugar model at Asn362; E1 approximated by BACK domain 260-360.
- Prodigy selection: antibody chains A,B versus antigen chain C.

## Results link

`../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/`

## Canonical scientific results

- [Scientific report](../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/report.md)
- [Candidate inventory](../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/candidates.csv)
- [Selection table](../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/shortlist.csv)

The source run and scientific results share run ID `20261110_cdrh3_boltz2_glycan_prodigy`.

## Later retained cross-check

The result report and `evidence/raw/biotite_sasa_crossvalidation.json` record failure of the original custom SASA method. Its glycan ΔSASA numbers remain historical, unreliable outputs; producing them did not complete a valid glycan-accessibility evaluation. The simplified Biotite model also does not reproduce the paper's conformational ensemble. The task remains partial. No glycan calculation was rerun during packaging.
