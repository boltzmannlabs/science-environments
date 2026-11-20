# FXI AntiBMPNN fixed-backbone redesign

**Task:** `task_014_fxi_igdesign_cdr_redesign`  
**Run:** `run_001_antibmpnn_fixed_backbone`  
**Status:** completed

## Inputs and constraints

Osocimab Fv from 6HHC: VH 120 aa, VL 107 aa. Editable VH positions: 97–109 for HCDR3-only, or 26–33/51–58/97–109 for HCDR123. Framework and VL are fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; 20 per scope | 40 samples |
| Verify and deduplicate | VL identity, VH length, protected residues and mask checks | 40 pass; 11 HCDR3 + 15 HCDR123 unique sequences |
| Select panel | Five sequences per scope | 10 candidate sequence pairs |
| Evaluate geometry | Boltz2; exact sequence checks; Cα framework fit | 10 candidate models + native control |

## Measurements and outcome

Best recovery is 0.6923 (HCDR3) and 0.7241 (HCDR123). Geometry leader t014r001_hcdr123_scope_s05 has AAR 0.6897, nine substitutions, Fv deviation 0.3978 Å and HCDR3 deviation 1.3367 Å from the predicted native Fv.

See the [completed report](../../../results/task_014_fxi_igdesign_cdr_redesign/run_001_antibmpnn_fixed_backbone/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
