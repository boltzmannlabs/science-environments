# Task 002 code inventory

| File | Role | Execution status |
|---|---|---|
| `boltz2_run_batch.sh` | Runs local Boltz-2 predictions sequentially for the selected 10-candidate panel. | Executed |
| `analyze_interface.py` | Reads Boltz-2 confidence JSON and mmCIF structures; measures confidence, contacts, hotspot engagement, minimum distance and clashes. | Executed |
| `compute_novelty.py` | Recomputes full VH/VL and CDR3-H sequence identity against H5. | Added as reproducible reconstruction of the executed analysis. |
| `rank_and_package.py` | Recomputes the composite ranking and writes the candidate table and FASTA package. | Added as reproducible reconstruction of the executed packaging step. |
| `retained_root_scripts/h5_rmsd.py` | H5 prediction/reference C-alpha RMSD comparison. | Existing task script; executed in the prior H5 benchmark run. |

The Boltzmann generation and property stages were remote platform jobs. Their local record is the job manifest, uploaded input CSV, doc_ids and status in the run package; no private backend implementation code is available locally and none is invented here.
