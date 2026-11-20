# IL-36R shared Boltz2 Fv evaluation

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_005_boltz2_fv_structural_consistency`  
**Status:** completed

## Inputs and constraints

Twelve fixed sequence pairs from runs 001–004, three per generation run, plus the unmodified Spesolimab VH/VL reference. All modelled chains were checked against the supplied sequences.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Assemble panel | Saved boltz2_panel.json; 12 designs + reference | 13 exact sequence pairs |
| Predict Fv structures | Matched Boltz2 settings | 13 accepted models |
| Verify model identity | Exact VH and VL sequence checks | All 13 panel members verified |
| Measure structure and confidence | Framework Kabsch fit; N/Cα/C/O backbone vs experimental 6U6U | 12 ranked candidates and native control |

## Measurements and outcome

Lowest candidate Fv deviation is antibmpnn_hcdr3_top3, 0.4022 Å; native control 0.3178 Å. Lowest candidate HCDR3 deviation is igdesign_hcdr123_top2, 0.6926 Å. The AntiBMPNN subsets are the fixed recorded panels, selected in descending NLL order.

See the [completed report](../../../results/task_015_il36r_igdesign_cdr_redesign/run_005_boltz2_fv_structural_consistency/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
