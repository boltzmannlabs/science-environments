# Current Task001 benchmark audit

Run: 20261111_ref15_benchmark_audit; parent: 20261110_antibmpnn_her2_prodigy.

Only HER2/trastuzumab and the existing five shortlisted sequences were evaluated. No other tasks, new generation or Boltzmann submissions occurred.

Completed: archived benchmark/primary paper/SI retrieval; archive checksum validation; 16 published log endpoint extractions; six sequential CPU ABodyBuilder2 predictions; six PyMOL conformation checks; six successful ImmuneBuilder complex refinements; 15 sequential Prodigy runs; sequence/mask/geometry/interface audit.

A streaming archive probe stopped at its 240-second budget; the complete archive was then retrieved with verified byte ranges. SI direct fetches failed; the official ACS Figshare copy was retrieved and its MD5 matched the article metadata.

The first PyMOL pass exposed zero selected heavy-chain reference atoms because the released INPUT PDB numbers H sequentially108-227. Its values were discarded; the code now maps the native sequence to ANARCI Martin numbers and requires positive equal CA counts before scoring. Only the corrected pass is reported.

Blocked: Amber22/24 ff14SBonlysc/HMR/igb8 minimization and PyRosetta REF15. No proxy is labeled REF15. Initial full-Fab/full-ECD candidate estimates are reproducible but rejected as benchmark evidence because of malformed side chains and a mismatched construct.

Results: [report](../../../../results/task_001_her2_trastuzumab_interaction_optimization/20261111_ref15_benchmark_audit/report.md).
Configuration: configs/evaluation_config.json. Tool stdout and Prodigy commands: logs/. Exact code: configs/code_snapshot/.
