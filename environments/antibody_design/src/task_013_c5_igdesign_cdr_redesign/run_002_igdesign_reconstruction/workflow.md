# C5 IgDesign masked native reconstruction

**Task:** `task_013_c5_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Eculizumab VH/VL pair and heavy-chain edit masks as run_001. One sample and a separate 100-sample pool are generated for each scope; the raw CSVs and serialized sampling configurations are retained.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate HCDR3 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Generate HCDR123 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Measure native recovery | Position-aligned per-CDR AAR | 202 sample-level metric rows |
| Select shared evaluation panel | Four recorded designs | Boltz2 and ESMFold evaluation retained in run_001 |

## Measurements and outcome

HCDR3-only 1-shot AAR is 0.4667; the separate 100-sample pool has mean 0.5193 and maximum 0.6667. HCDR123 pool mean HCDR3 AAR is 0.5160; maximum 0.6667.

See the [completed report](../../../results/task_013_c5_igdesign_cdr_redesign/run_002_igdesign_reconstruction/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
