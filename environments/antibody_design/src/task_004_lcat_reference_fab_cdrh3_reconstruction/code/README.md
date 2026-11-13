# Task 004 code map

The code is grouped by execution role, not by scientific result.

- `boltzmann/preparation/`: input normalization, chain extraction and CDR-H3 numbering.
- `boltzmann/analysis/`: AAR, CAAR, RMSD/TM-score and developability calculations.
- `boltzmann/interface/`: epitope and antigen-contact calculations.
- `open_source/`: prior ProteinMPNN/Boltz2 preparation and evaluation scripts.

The Boltzmann generation stages themselves were remote platform-tool executions. Their local reproducible records are the workflow, execution and provenance files; no fabricated local wrapper is supplied for a remote call whose original payload was not archived.

All scripts are preserved with their original filenames. Use the run's `inputs/sha256sums.txt` to identify the exact copied versions used in this package.
