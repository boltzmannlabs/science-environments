# IL-36R IgDesign HCDR123 reconstruction

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_hcdr123_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Spesolimab Fv. Editable VH positions 26–33, 51–58 and 97–108; VL and VH framework remain fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate 1-shot | IgDesign; saved one-sample configuration | 1 sample |
| Generate 100-sample pool | IgDesign; separate saved configuration | 100 samples |
| Measure recovery | Per-CDR position identity | 101 samples; separate per-CDR maxima |
| Select evaluation entries | Ascending summed CDR cross-entropy loss | 3 panel members evaluated in run_005 |

## Measurements and outcome

1-shot HCDR1/2/3 AAR: 0.7500/0.6250/0.5833. Per-CDR maxima over 100 samples: 1.0000/0.7500/0.8333; these maxima need not occur in one sequence.

See the [completed report](../../../results/task_015_il36r_igdesign_cdr_redesign/run_002_igdesign_hcdr123_native_reconstruction/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
