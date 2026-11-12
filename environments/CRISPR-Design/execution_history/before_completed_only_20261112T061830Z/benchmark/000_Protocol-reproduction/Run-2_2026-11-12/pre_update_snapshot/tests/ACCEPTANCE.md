# Acceptance and validation plan

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory (stdlib only). It
records actual results to [validation.json](validation.json):

| # | Check | What it verifies |
| --- | --- | --- |
| 1 | `files` | core files present; 13 example briefs ↔ 13 task files, number-first naming aligned |
| 2 | `tasks` | 13 task MDs: house sections present (Description · Target · Design Constraints · Required Execution Steps · Expected Output · Constraints · Important Instructions), steps tables, task-index entries in tasks/README, per-task example-brief reference resolves |
| 3 | `schemas` | 2 JSON schemas well-formed; application enum = 12 modalities; weights have 4 bounded dimensions; candidate spacer pattern present |
| 4 | `examples` | all 13 example briefs validate against requirement_brief.schema.json (required fields, enums, weight ranges [0,1], additionalProperties) |
| 5 | `yaml_invariants` | environment.yaml: environment_id, 10 active applications, diagnostics review-only, plant inactive, draft-thresholds path resolves, 5 modes present |
| 6 | `thresholds` | draft gates carry provenance from the declared set; version is 0.1-draft; no_freeze_without calibration list present |
| 7 | `cross_references` | every relative markdown/JSON link in README, ENVIRONMENT_SPEC, MODELS_AND_TOOLS, tasks, benchmark docs resolves to a real file |
| 8 | `benchmark_docs` | benchmark/README anchor table + BENCHMARK_RUNS iteration structure; every Run slot explicitly `NOT_EXECUTED` (no claimed local result) |
| 9 | `honesty_markers` | no executed-result language: README/STATUS/spec declare runtime-pending; results/ contains no run directories |
| 10 | `runtime_probe` | probe_backends.py parses, BACKENDS map non-empty, stage dependency map consistent; probe runs without exception (findings are data) |

These checks validate **this specification package** on synthetic/structural fixtures
only. They do not validate external backends, model predictions, database access or
editing efficacy.

## Runtime behavior tests

Not yet applicable — the scoring runtime adapters arrive in the next phase
([STATUS](../STATUS.md)). The backend liveness probe
(`python3 runtime/probe_backends.py`) is the only executable component and reports
presence, never scores.

## Scientific validation status

- **Curation verification** — every tool/benchmark claim traced to a primary source
  during the 2026-11-10 sweep; misattributions corrected and recorded
  ([research notes](../../../research/CRISPR-Design/research-notes.md)).
- **Local backend evidence** — inherited from the prior KIF11 CRISPR-KO run (crisprScore
  stack installed; Lindel interface test PASS; Bowtie/GRCh38 index built), re-probed on
  demand by `runtime/probe_backends.py`.
- **No executed benchmark** — all Run slots NOT_EXECUTED by design; first executions are
  pre-registered in [BENCHMARK_RUNS.md](../benchmark/BENCHMARK_RUNS.md).
- For repository release: link the contribution issue and complete the PR/review process
  per [CONTRIBUTING](../../../CONTRIBUTING.md).
