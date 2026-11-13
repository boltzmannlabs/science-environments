# Task 001 code index

These scripts are the reproducible local copies used for sequence filtering, shortlist selection, payload preparation, fixed-pose reconstruction, clash analysis and result packaging.

| Script | Role |
|---|---|
| `00_verify_chain_mapping.py` | Verify candidate-to-1N8Z variable-domain sequence mapping |
| `01_filter_designs.py` | Check framework integrity, cysteine preservation and CDR edits |
| `02_select_shortlist.py` | Attach AntiBMPNN scores and select a diverse shortlist |
| `03_boltz2_payloads.py` | Build reference and candidate VH/VL/HER2 payload records |
| `04_reconstruct_fixed_pose.py` | Place designed CDR side chains on the fixed 1N8Z backbone |
| `05_compute_clashes.py` | Count approximate same-chain non-adjacent clashes |
| `06_run_prodigy.sh` | Run ProDIGy with Fab chains A+B versus HER2 chain C |
| `07_assemble_results.py` | Assemble result tables, FASTA, structures and evidence |
| `08_make_her2_bundle.py` | Create the task-spec `her2_results/` bundle |

The scripts preserve the absolute paths used during the original execution. They are an execution record and should be path-normalized before being treated as a portable package.
