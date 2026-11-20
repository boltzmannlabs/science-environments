# Cetuximab CDR redesign and matched complex evaluation

**Task:** `task_008_egfr_scfv_design`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Prepared 1YY9 Fv and 613-residue EGFR construct. VH 119 aa, VL 107 aa; scFv linker `(G4S)3`. Editable variable-domain positions: VH 26–32, 52–56, 98–108; VL 24–34, 50–56, 89–97. Framework and linker are fixed.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare reference | PDB extraction; ANARCI Chothia numbering | Exact parent VH/VL sequence match |
| Generate sequences | AntiBMPNN; 20 samples; H/L CDR edits | 20 recorded candidates |
| Screen sequences | Mask, uniqueness, cysteine, glycosylation-sequon and sequence-property checks | 6 selected candidates |
| Evaluate complexes | Boltz2; same EGFR construct and conditions for designs and reference | 6 candidate models + native control |

## Measurements and outcome

Highest candidate ipTM: cet_008_r1_s15, 0.8549; matched native control 0.9065. No candidate improves the reference interface score.

See the [completed report](../../../results/task_008_egfr_scfv_design/run_001_antibmpnn_matched/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_008_egfr_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
