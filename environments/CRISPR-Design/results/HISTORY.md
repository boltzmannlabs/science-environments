# Execution history and evidence availability

## Run names

Run directories use `Run-<number>_<YYYY-MM-DD>`. Numbers identify the original
campaigns; moving files does not create a new execution or restart numbering.

| Original location | Current location | Evidence |
| --- | --- | --- |
| `results/002_knockout_gene_disruption/Run1_20261110/` | `results/002_knockout_gene_disruption/Run-1_2026-11-10/` | First knockout execution; retained stage-1 record. |
| `results/00N_<application>/Run-2_2026-11-12/` | Same location | Thirteen task reports, briefs and provenance records. |
| `benchmark/00N_<Model>/Run-4_2026-11-12/` | `results/benchmarks/00N_<Model>/Run-4_2026-11-12/` | Seven completed model benchmark packages. |
| Benchmark run `scripts/inference.*` | `scripts/benchmarks/00N_<Model>/inference.*` | Original execution scripts, preserved byte-identically. |
| `benchmark/PROVENANCE.{json,sha256}` | `results/benchmarks/PROVENANCE.{json,sha256}` | Source handles and hashes retained; destination paths updated. |

## Missing historical archive

Earlier documentation and recorded validation referred to 269 historical benchmark
files at `execution_history/before_completed_only_20261112T061830Z/`, including
Run-2/Run-3 comparisons, the campaign report, a coverage matrix and an archive
inventory. That directory and its reorganization pointer are absent from this
checkout. Their preservation cannot be verified here. Links to that missing archive
now resolve to this availability note; this note is not a replacement for the evidence.

The task documents retain historical descriptions with that limitation. The active
[benchmark registry](../benchmark/BENCHMARK_RUNS.md) contains the seven available
completed model evaluations. The historical archive check remains a failure until
the original archive and inventory are restored and verified. Three original source
handles in the active provenance manifest also point into the missing archive:
`Cas9_paired_differences.csv`, `specificity.json` and
`cas13_completion_verification.json`. Their destination copies still match the saved
hashes, but verification against those original sources cannot pass while the archive
is absent. The other 45 source files match their recorded hashes.

## Local artifacts and reproducibility

Lightweight task reports, provenance, actual input briefs and artifact indexes are
eligible for Git tracking. Large task outputs under `artifacts/`, raw references,
indexes and local runtime assets remain ignored. Some of these files exist only in
this working copy or at the absolute source paths recorded in provenance. A fresh
clone does not contain them. In particular, first-run stage-2 outputs are absent.

Benchmark predictions, metrics, logs and original inference scripts previously
tracked in Git are retained in the new locations. Moving them does not rerun the
models or establish new scientific validation. No model installation, inference,
guide generation or threshold change is part of this reorganization.
