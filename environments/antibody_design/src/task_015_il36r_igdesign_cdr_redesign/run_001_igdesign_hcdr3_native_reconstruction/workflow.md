# IL-36R IgDesign HCDR3 reconstruction

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_001_igdesign_hcdr3_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Spesolimab Fv from 6U6U: VH 119 aa, VL 108 aa. Only VH 97–108 is editable; native VL, framework and HCDR1/2 remain fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate 1-shot | IgDesign; saved one-sample configuration | 1 sample |
| Generate 100-sample pool | IgDesign; separate saved configuration | 100 samples |
| Measure native recovery | Per-CDR position identity | HCDR3 AAR for 101 samples |
| Select evaluation entries | Ascending HCDR3 cross-entropy loss; distinct recorded sequences | 3 panel members evaluated in run_005 |

## Measurements and outcome

HCDR3 AAR: 1-shot 0.5833; maximum over the separate 100-sample pool 0.8333. Structural evaluation is retained in run_005.

See the [completed report](../../../results/task_015_il36r_igdesign_cdr_redesign/run_001_igdesign_hcdr3_native_reconstruction/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
