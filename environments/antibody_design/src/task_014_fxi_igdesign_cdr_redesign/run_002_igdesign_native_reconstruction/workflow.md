# FXI IgDesign masked native reconstruction

**Task:** `task_014_fxi_igdesign_cdr_redesign`  
**Run:** `run_002_igdesign_native_reconstruction`  
**Status:** completed

## Inputs and constraints

Same Osocimab VH/VL and masks as run_001. The saved YAML configurations specify separate 1-shot and 100-sample executions for HCDR3 and HCDR123.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate samples | IgDesign; 1 + 100 samples per scope | 202 samples |
| Verify and deduplicate | Native framework/VL preservation and sequence identity | 158 unique sequences |
| Measure native recovery | Position-aligned designed-scope AAR | 1-shot and best-of-100 endpoints |
| Evaluate geometry | Five designs per scope; Boltz2; Cα framework fit | 10 candidate models + native control |

## Measurements and outcome

Designed-scope AAR is 0.6923/0.8462 for HCDR3 1-shot/best-of-100 and 0.7241/0.7931 for HCDR123. t014r002_hcdr3_best100_012 has HCDR3 deviation 1.3144 Å and Fv deviation 0.4382 Å from the predicted native Fv.

See the [completed report](../../../results/task_014_fxi_igdesign_cdr_redesign/run_002_igdesign_native_reconstruction/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
