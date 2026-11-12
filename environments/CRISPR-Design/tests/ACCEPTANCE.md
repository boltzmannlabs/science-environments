# Acceptance and validation plan

Three validation layers: package validation (structure/links/schemas), executed-run
validation (Run1 artifacts), and completed-benchmark publication integrity. Active
benchmark evidence is the [completed-only registry](../benchmark/BENCHMARK_RUNS.md) —
seven completed native-model/endpoint evaluations; model benchmarks do not establish
full design-application validation, and older mixed evidence is retained as
[execution history](../execution_history/before_completed_only_20261112T061830Z/README.md).

## Specification-package checks

Run `python3 tests/validate_spec.py` from the environment directory (stdlib only). It
records actual results to [validation.json](validation.json):

| # | Check | What it verifies |
| --- | --- | --- |
| 1 | `files` | core files present; 13 example briefs ↔ 13 task files, number-first naming aligned |
| 2 | `tasks` | 13 task MDs: house sections present (Description · Target · Design Constraints · Required Execution Steps · Expected Output · Constraints · Important Instructions), steps tables, task-index entries in tasks/README, per-task example-brief reference and benchmark-status statement |
| 3 | `schemas` | 2 JSON schemas well-formed; application enum = 12 modalities; weights have 4 bounded dimensions; candidate spacer pattern present |
| 4 | `examples` | all 13 example briefs validate against requirement_brief.schema.json (required fields, enums, weight ranges [0,1], additionalProperties) |
| 5 | `yaml_invariants` | environment.yaml: environment_id, 10 active applications, diagnostics review-only, plant inactive, draft-thresholds path resolves, 5 modes present |
| 6 | `thresholds` | draft gates carry provenance from the declared set; version is 0.1-draft; no_freeze_without calibration list present |
| 7 | `cross_references` | every relative markdown/JSON link in README, ENVIRONMENT_SPEC, MODELS_AND_TOOLS, tasks, benchmark docs resolves to a real file |
| 8 | `benchmark_docs` | completed-only registry: completed_benchmarks.json has 7 COMPLETED entries, each report present, no heuristic/surrogate scores, no partial/planning placeholders in benchmark/README or BENCHMARK_RUNS |
| 9 | `honesty_markers` | README/STATUS/spec carry the maturity and boundary statements (partial workflows + executed model benchmarks; no wet-lab validation); results/ run dirs are Run-prefixed with hashed briefs |
| 10 | `runtime_probe` | probe_backends.py parses, BACKENDS map non-empty, stage dependency map consistent; probe runs without exception (findings are data) |

These checks validate **this specification package** on structural fixtures only. They
do not validate external backends, model predictions, database access or editing
efficacy.

## Runtime behavior tests

- **Executed-run validation:** `python3 tests/test_first_run.py [run_dir]` validates the
  Run1 task-002 artifacts — structure, coordinate integrity (independent re-extraction),
  scorer determinism, the Lindel regression anchor, off-target positive/negative
  controls, cross-endpoint sanity, DRAFT-gate conformance and provenance. Current state:
  stage-1 checks pass (coordinate integrity, Lindel anchor, cross-endpoint sanity); the
  stage-2-dependent checks fail on file presence because the stage-2 outputs were not
  retained in the repo copy (see [runtime contracts](../runtime/CONTRACTS.md)).
- **Liveness probe:** `python3 runtime/probe_backends.py` reports backend presence,
  never scores; run before every execution.
- **Publication integrity:** `python3 tests/test_completed_benchmarks.py` (requires
  pandas/scipy/sklearn and the indexed source data roots) — completed-only scope,
  copied-artifact hashes, fresh-native-inference verification, independent metric
  recomputation, active-link resolution and archived-history preservation; results to
  [completed_benchmarks_validation.json](completed_benchmarks_validation.json).

## Scientific validation status

- **Curation verification** — every tool/benchmark claim traced to a primary source
  during the 2026-11-10 sweep; misattributions corrected and recorded
  ([research notes](../../../research/CRISPR-Design/research-notes.md)).
- **Local backend evidence** — inherited from the prior KIF11 CRISPR-KO run (crisprScore
  stack installed; Lindel interface test PASS; Bowtie/GRCh38 index built), re-probed on
  demand by `runtime/probe_backends.py`; first end-to-end execution recorded in Run1.
- **Executed benchmarks are endpoint-level** — the completed-only registry validates
  model endpoints on public measured labels; it does not validate any full design
  application, and no wet-lab validation exists. Unexecuted evaluation slots remain
  `NOT_EXECUTED` by design; remaining benchmark arms are tracked as backlog in
  [STATUS](../STATUS.md).
- For repository release: link the contribution issue and complete the PR/review process
  per [CONTRIBUTING](../../../CONTRIBUTING.md).
