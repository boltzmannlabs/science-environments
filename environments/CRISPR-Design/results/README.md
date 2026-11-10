# Results

Run outputs land here per application, one directory per run:
`00N_<application>/<RunID>_<date>/` (number-first, mirroring the task numbering). Run IDs
match [benchmark/BENCHMARK_RUNS.md](../benchmark/BENCHMARK_RUNS.md) rows.

**Current state: empty by design.** No executed run exists yet — the scoring runtime and
frozen gates arrive in the next phases. Nothing in this environment claims an executed
result; published anchors live in [benchmark/](../benchmark/README.md) and are labeled
as published, not as our runs.

When runs begin: each run directory carries `requirement_brief.json` (hashed), per-stage
outputs with `NOT_RUN(reason)` transparency, the ranked deliverable, and a provenance
block (tool versions, engine stamp, threshold version). Superseded runs are archived with
dated notes, never deleted.
