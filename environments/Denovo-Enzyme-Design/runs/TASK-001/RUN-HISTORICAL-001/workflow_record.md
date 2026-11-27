# Task 1 — RFdiffusion2 Retroaldolase Design (Run Record)

Non-executable workflow summary for canonical run `RUN-HISTORICAL-001` and historical campaign label `GLP1_p03_variable_s02`.
This document indexes the task definition, benchmark material, and result directory.
It does NOT specify a procedure for generating or modifying protein sequences and is not a runnable workflow.

## Task identity
- Task ID: `TASK-001`
- Run ID: `RUN-HISTORICAL-001` (assigned during repository migration; no verified original run ID or execution timestamp was retained)
- Campaign label: `GLP1_p03_variable_s02`
- Target: Retroaldolase (GLP1 p03 variable scaffold)

## Artifact index
| Artifact | Path |
|----------|------|
| Task definition | `tasks/TASK-001-rfdiffusion2-retroaldolase/task.md` |
| Benchmark definition | `benchmark/definitions/TASK-001.md` |
| Benchmark reference | `benchmark/reference_data/TASK-001/reference.md` |
| Configuration availability | `runs/TASK-001/RUN-HISTORICAL-001/configuration.json` |
| Input availability manifest | `runs/TASK-001/RUN-HISTORICAL-001/input/manifest.json` |
| Aggregate metrics | `results/TASK-001/RUN-HISTORICAL-001/metrics.csv` |
| Run report | `results/TASK-001/RUN-HISTORICAL-001/REPORT.md` |
| Benchmark comparison | `results/TASK-001/RUN-HISTORICAL-001/benchmark_comparison.csv` |
| Shortlist | `results/TASK-001/RUN-HISTORICAL-001/shortlist.csv` |
| Candidate properties | `results/TASK-001/RUN-HISTORICAL-001/candidate_properties.json` |
| Historical SHA-256 manifest | `results/TASK-001/RUN-HISTORICAL-001/historical_sha256_manifest.json` |
| Result provenance | `results/TASK-001/RUN-HISTORICAL-001/provenance.json` |
| Run record | `runs/TASK-001/RUN-HISTORICAL-001/run.json` |

## Excluded from this package
- Generated sequences (FASTA files)
- 3-D structures (PDB / CIF files)
- Runnable design-generation workflows (RFdiffusion2 scripts, model weights, audit scripts)
- Raw per-candidate assessment files (kept in `raw/` for audit but not part of the reviewable package)

## Notes
- This summary was assembled during repository repackaging and is not an original execution output.
- The configuration and complete input snapshots were unavailable in the retained records; their availability records do not supply assumed values.
- This record is not evidence of experimental validation.
- The archived files are the record of what was evaluated; they do not constitute a rerunnable pipeline.
