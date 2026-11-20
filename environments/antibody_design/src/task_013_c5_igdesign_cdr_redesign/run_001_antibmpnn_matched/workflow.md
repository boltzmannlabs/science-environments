# C5 AntiBMPNN redesign and shared structural evaluation

**Task:** `task_013_c5_igdesign_cdr_redesign`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Eculizumab Fv from 5I5K: VH 122 aa, VL 107 aa. Editable VH positions are 97–111 for HCDR3-only, or 26–33/51–58/97–111 for HCDR123. VL and VH framework are fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; temperature 0.1; 100 per scope | 200 generated sequences |
| Assemble evaluation panel | 2 AntiBMPNN designs + 4 designs imported from run_002 + native control | 7 fixed sequence pairs |
| Predict structures | Boltz2 Fv and ESMFold VH–linker–VL | 14 accepted models |
| Measure recovery and geometry | Native AAR; Cα scRMSD after framework fit | Candidate consistency vs same-predictor native model; native control vs 5I5K crystal |

## Measurements and outcome

AntiBMPNN maximum HCDR3 AAR is 0.4000 in each 100-sample scope. The closest candidate Fv is ig_hcdr3_s002 for Boltz2 (0.371 Å) and ig_hcdr3_s031 for ESMFold (0.139 Å).

See the [completed report](../../../results/task_013_c5_igdesign_cdr_redesign/run_001_antibmpnn_matched/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
