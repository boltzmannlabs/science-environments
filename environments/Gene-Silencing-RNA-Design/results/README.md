# Results — delivered designs and run outputs, by application

Parallel to `tasks/00N_*` (workflows) and `benchmark/00N_*` (evaluation evidence), this tree
holds **what each run delivered**: candidate panels, ranked tables, pool summaries. Structure:

```
results/00N_<application>/<RunID>_<date>/artifacts...
```

- **Run IDs match `../benchmark/BENCHMARK_RUNS.md`** — a result folder and its benchmark row
  share the Run ID, so design ↔ evaluation ↔ config are one click apart.
- Artifacts are **copies** (hash-bound in PROVENANCE.sha256); full pools/campaign trees stay in
  the source workspace (`~/IMRAN/NOV26/siRNA-Design-Task-Specific`), indexed by path here.
- New runs land in a new `<RunID>_<date>` folder — never overwrite a prior run.
- Applications without results yet (004 allele, 006 LNP, 007 neuro, 008 inflammation,
  011 DTV) get folders when a governed run delivers designs for them.

| Folder | Contents |
|---|---|
| 001_general | head-to-head Run-2: both arms' 24-candidate panels (4 genes) |
| 002_oncology | HPSE/HK2 sub-agent panels + formal battery deliverables (Run-2) |
| 003_genetic-disease-total-lowering | TTR Run-1: validation panel (6), top-20 same-side candidates, pool top-25 |
| 005_metabolic-liver-galnac | HIF1A Run-1 explorer consensus panel (mechanism demo caveat) + Run-1b corrected battery deliverable |
| 009_functional-genomics | panel-construction outputs (3 pools) |
| 010_gene-regulation | MYC sub-agent panel |

## Run-3_2026-11-11

New execution artifacts are under `results/00N_<application>/Run-3_2026-11-11/` for all 11 task IDs. Nine application frames have computational panels (51 rows / 31 unique guides); 004 and 007 contain published-reporter EVALUATE results, not new designs. The 120 target candidates were freshly evaluated; HK2/MYC generation pools were reused and TTR/PCSK9/TNF generation was fresh. Application context/annotation gaps are explicit: no fully complete application task or experimental validation is claimed.

Start with the [campaign report](../benchmark/011_Campaign-reproduction/Run-3_2026-11-11/REPORT.md) and [task-status ledger](../benchmark/011_Campaign-reproduction/Run-3_2026-11-11/task_execution_status.csv). Each task folder contains `REPORT.md` and provenance; panel-bearing tasks also contain gate decisions, independent endpoint values, and post-diversity weight-stability reports. Historical artifacts and frozen gates are unchanged.

