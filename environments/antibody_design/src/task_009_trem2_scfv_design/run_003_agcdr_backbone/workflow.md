# TREM2 AgCDR backbone diversification and inverse folding

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_003_agcdr_backbone`  
**Status:** completed

## Inputs and constraints

Prepared reference Fv and TREM2 antigen structures. AgCDR generates eight backbone samples; the evaluated sequence panel comes from sample 7. Framework and chain-local CDR constraints are checked before selection.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Diversify backbone | AgCDR; 8 samples, 10 steps | 8 backbone samples |
| Select backbone | Recorded sample-7 backbone | One backbone for sequence generation |
| Generate sequences | Local AntiBMPNN; 40 samples | 40 candidate sequences |
| Evaluate complexes | Boltz2; exact sequence identity check | 4 predictions; cand032 retained |

## Measurements and outcome

Best candidate cand032: ipTM 0.7413, pTM 0.8636; matched reference ipTM 0.8987. The full evaluated range is 0.3633–0.7413.

See the [completed report](../../../results/task_009_trem2_scfv_design/run_003_agcdr_backbone/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
