# ESMFold and ProteinMPNN evaluation of the fixed EGFR panel

**Task:** `task_008_egfr_scfv_design`  
**Run:** `run_002_esmfold_proteinmpnn_evaluation`  
**Status:** completed

## Inputs and constraints

The six selected sequences from run_001 and its native reference, each a 241-residue VH–linker–VL scFv. This run evaluates the supplied panel without generating new designs.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare panel | Saved FASTA and run_001 shortlist | 7 sequences |
| Predict scFv structures | ESMFold | 7 accepted single-chain models |
| Score sequences | ProteinMPNN score-only on each sequence’s own ESMFold backbone | Negative log likelihood; lower is preferred |
| Summarize | Whole-scFv confidence and sequence properties | Seven-row metrics table |

## Measurements and outcome

Candidate ESMFold pLDDT 85.07–85.84; reference 85.40. Lowest candidate own-backbone ProteinMPNN NLL: cet_008_r1_s18, 1.4510; reference 1.4692.

See the [completed report](../../../results/task_008_egfr_scfv_design/run_002_esmfold_proteinmpnn_evaluation/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_008_egfr_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
