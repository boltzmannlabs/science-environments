# TREM2 epitope-conditioned backbone design and inverse folding

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_004_epitope_abgen_local`  
**Status:** completed

## Inputs and constraints

Saved reference framework, TREM2 antigen and 20-residue epitope. The accepted prepared-feature generation uses explicit local masks: H 28–35, 53–60, 99–112 on the 123-residue H chain; L 27–32, 50–52, 89–97 on the 107-residue L chain. The actual input mask and protected cysteine were verified before generation.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare features | Explicit chain-local CDR masks; saved epitope and feature tensors | 10/10 recorded mask checks |
| Generate backbones | epitope_abgen local core; 4 samples; seed 2026; max_tokens 384 | 4 finite backbone samples |
| Generate sequences | Local AntiBMPNN; 40 sequences per backbone | 160 sequences; 94 pass gates (0/25/32/37) |
| Evaluate complexes | Matched Boltz2; exact sequence identity check | 3 accepted predictions; s2_cand13 retained |

## Measurements and outcome

Best candidate s2_cand13: ipTM 0.6039 vs matched reference 0.8987. Sample-0 designs fail the CDR cysteine gate. The evaluated panel has one replacement for an unverified prediction, so only the three saved verified models enter the benchmark.

See the [completed report](../../../results/task_009_trem2_scfv_design/run_004_epitope_abgen_local/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
