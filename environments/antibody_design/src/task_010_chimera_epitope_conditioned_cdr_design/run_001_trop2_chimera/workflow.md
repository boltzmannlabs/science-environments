# TROP-2 chimera epitope-conditioned CDR design

**Task:** `task_010_chimera_epitope_conditioned_cdr_design`  
**Run:** `run_001_trop2_chimera`  
**Status:** completed

## Inputs and constraints

Human TROP-2 reference complex `9pi9` (antigen chain F; antibody VH chain C, VL chain D). Only HCDR3 is redesigned: sequential VH positions 97–110 (14 residues), native `ARGGFGSSYWYFDV`. Framework and VL sequences remain fixed. The generator was conditioned on an existing predicted structural context, which did not recover native H3 contact pairs (not a guaranteed native antigen pose). Generated samples are sequences only in this package; structures and runnable workflow code are excluded.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Train RAAD H3 benchmark model | RAAD, CPU, 20 epochs, greedy one-design per complex | Best checkpoint epoch 18 |
| RAAD benchmark evaluation | 292 epitope-group test complexes, predicted H3 in native-framework context | AAR 0.368 ± 0.131; Cα RMSD 1.976 ± 0.829 Å; TM 0.200 ± 0.119 |
| AntiBMPNN H3 generation | 100 samples, nonduplicate generator-score ranking (ascending score, sample-number tie-break) | 70 unique VH/VL pairs |
| Multimer structure prediction | AlphaFold2-multimer/ColabFold, three-chain VH/VL/TROP-2, top unrelaxed model per candidate | 5 candidates modeled |
| Reference and interface assessment | Native-reference H3 AAR, 4.5 Å heavy-atom contact AAR, H3 RMSD, epitope F1, standard DockQ 2.1.3 | Rank 1: AAR 0.357, 4.5 Å contact AAR 0.167, RMSD 3.192 Å, DockQ 0.009 |
| Geometry validation | MolProbity, measurement-only, all five unrelaxed structures | Clashscores 50.67 / 38.85 / 51.52 / 32.24 / 44.47 (ranks 1–5) |

## Measurements and outcome

Benchmark comparison against CHIMERA-Bench Table 3 (292 complexes) is saved in `benchmark_comparison.csv`; the five-candidate table and limitations are in the run report. All five modeled shortlist candidates recovered 0/20 exact native H3–antigen contact pairs. No experimental affinity measurement was performed.

See the [completed report](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design/reference.md) for numerical tables and comparator definitions.

## Execution evidence

- [Run index](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/run.json)
- [Candidate inventory](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/candidates.csv)
- [Five-candidate metrics](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/metrics.csv)
- [Geometry review](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/geometry_review.md)
- [Source checksums](../../../results/task_010_chimera_epitope_conditioned_cdr_design/run_001_trop2_chimera/sha256_manifest.json)
