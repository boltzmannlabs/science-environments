# Executed EvoEF1 comparison code

These are the actual agent-generated driver and identity/energy parser used for the retrospective folding-stability comparison. EvoEF1 remains an external dependency; its pinned version, commit and binary hash are recorded in each task’s reference-comparison method file.

The driver expects its original reviewed execution layout: `local_evoef/PLAN.json`, exact parent PDBs, mutation files, and the pinned external binary. Those large/private operational inputs remain in the assessment archive. It validates their hashes and complete sequences before execution and refuses an existing execution-intent file.

`python scripts/run_evoef_panel.py --validate-only` checks a restored workspace without executing predictions. `--run` executes a fresh reviewed panel once. Outputs include matched WT and mutant structures, native energy logs and decimal energy differences. Do not use it to replay existing jobs.
