# IL-36R AntiBMPNN HCDR3 redesign

**Task:** `task_015_il36r_igdesign_cdr_redesign`  
**Run:** `run_003_antibmpnn_hcdr3_redesign`  
**Status:** completed

## Inputs and constraints

Prepared Spesolimab–IL-36R complex from 6U6U. Editable VH positions 97–108; native light chain, framework and HCDR1/2 remain fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare complex | Saved H/L/antigen structure and declared edit mask | Exact native-chain mapping |
| Generate sequences | AntiBMPNN; 40 samples | 40 native output rows |
| Record evaluation panel | Three sequences selected in descending reported score order | Fixed panel; lower NLL is preferred |
| Evaluate panel | Shared Boltz2 evaluation | See run_005 |

## Measurements and outcome

Three recorded sequence pairs were evaluated in run_005. The selection used descending AntiBMPNN score, while the tool score is a negative log likelihood for which lower is preferred. Historical panel identifiers are retained; they do not indicate best-likelihood sequences.

See the [completed report](../../../results/task_015_il36r_igdesign_cdr_redesign/run_003_antibmpnn_hcdr3_redesign/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
