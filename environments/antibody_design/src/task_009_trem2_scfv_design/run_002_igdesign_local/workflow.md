# TREM2 IgDesign heavy-CDR redesign

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_002_igdesign_local`  
**Status:** completed

## Inputs and constraints

Paired reference VH/VL and prepared TREM2 complex. The native heavy CDRs are redesigned while VL and VH framework are fixed. Exact regions, conditioning and sampling settings are retained in inputs/hcdr123_trem2.yaml.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare conditioning | Reference complex and heavy-CDR mask | Paired light-chain and antigen context |
| Generate sequences | IgDesign; 100 samples | 100 native candidate rows |
| Apply sequence gates | Protected-residue and sequence checks | 95 passing unique candidates |
| Evaluate complexes | Boltz2; exact model sequence verification | 4 accepted candidate predictions |

## Measurements and outcome

Best candidate cand067: ipTM 0.8618, pTM 0.9198; matched reference ipTM 0.8987. Four candidates span ipTM 0.7326–0.8618.

See the [completed report](../../../results/task_009_trem2_scfv_design/run_002_igdesign_local/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
