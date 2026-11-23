# ACVR2B / Bimagrumab — IgDesign reference-backbone CDR redesign

**Task:** `task_12_acvr2b_igdesign_cdr_redesign`  
**Run:** `run_001_igdesign_hcdr_redesign`  
**Status:** completed

## Inputs and constraints

Bimagrumab Fv from PDB 5NGV (chain H = VH 113 aa, chain L = VL 111 aa) and the exact supplied ACVR2B fragment (chain A, human ACVR2B UniProt Q13705 mature residues 25–117, 93 aa, verified 93/93). CDR windows (0-indexed): HCDR1 24:32, HCDR2 49:57, HCDR3 95:103. Scopes: HCDR3-only and HCDR123; the light chain and all framework/protected VH residues are preserved. Generation yielded 200 samples; deduplication retained 133 unique (44 HCDR3-only, 89 HCDR123).

[Saved inputs](inputs/) include the reference PDB, sequences, edit masks and the published benchmark CSV. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration; tool and job records are in [execution_records](inputs/execution_records/).

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate HCDR3-only pool | IgDesign; ACVR2B-holdout + ProteinMPNN holdout; reference-backbone conditioning; 100 samples, T=0.5, seed 0 | 44 unique |
| Generate HCDR123 pool | IgDesign; same conditioning; 100 samples | 89 unique |
| Measure native recovery | Position-aligned per-CDR AAR (1-shot, best-of-100, mean) | 4 CDR × 3 summary rows |
| Select evaluation panel | Top 10 per scope by summed independent CE loss | 20 candidates (T12-C001–C020) |
| Predict structures | AlphaFold2-Multimer v3 (Boltzmann Multimer_Structure_Prediction), rank-1 | native + 20 candidates |
| Measure scRMSD | Whole-Fv (224 C-alpha) Kabsch onto 5NGV; regional C-alpha RMSD | 17/20 beat native HCDR123 |

## Measurements and outcome

HCDR3-only HCDR3 AAR is 0.875 (1-shot) and 0.875 (best-of-100), mean 0.750. HCDR123 AAR (1-shot / best-of-100 / mean): HCDR1 0.750 / 1.000 / 0.897, HCDR2 0.750 / 0.875 / 0.703, HCDR3 0.750 / 1.000 / 0.757.

Native scRMSD (executed): HCDR1 0.2347, HCDR2 0.6304, HCDR3 0.3705, HCDR123 0.4434, Fv 1.2140 A. Best HCDR3-only T12-C008 (ARGSEFDY): 0.3803 A (−0.0631). Best HCDR123 T12-C011: 0.3879 A (−0.0555). Fv spans 1.13–1.24 A across the panel, i.e. assembly is essentially unperturbed.

See the [completed report](../../../Results/task_12_acvr2b_igdesign_cdr_redesign/run_001_igdesign_hcdr_redesign/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_12_acvr2b_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
