# Acceptance and validation plan

## Specification-package checks (11 checks)

Run `python3 tests/validate_spec.py` from the environment directory (stdlib only). It records actual results to [validation.json](validation.json):

| # | Check | What it verifies |
|---|---|---|
| 1 | `files` | 17 core files present; config↔tasks example-JSON byte identity |
| 2 | `application_tasks` | 10 task MDs: house sections, steps tables, task-index entries, example-request alignment with schema enum, weight ranges [0,1], organism=human, review_window bounds, benchmark-status stated; results-tree number-first naming |
| 3 | `schemas` | 2 JSON schemas well-formed; 10-app enum; 5-dim weights; organism/guide-pattern/required-fields constraints |
| 4 | `examples` | 2 general example briefs: all required fields + 5-dim weights + illustrative markers |
| 5 | `yaml_invariants` | environment.yaml policy tokens; 10 frozen gates with provenance tags from the declared set; YAML contract paths point to real files |
| 6 | `benchmarks` | All 10 case-folder metric values match published numbers; 19 provenance SHA-256 hashes verified |
| 7 | `runtime_import` | All 3 runtime scripts (immune_scan, rank_by_requirements, explore_design) import; immune-scan motif behaviors; ranking veto/ordering/stability; explore has v1.2.1 `target_gene` param |
| 8 | `cross_references` | Every relative markdown/JSON link in all READMEs, spec, tasks, benchmark docs resolves to a real file |
| 9 | `benchmark_readmes` | Every benchmark case README has Published reference + Run configuration + Benchmark metrics sections with tables |
| 10 | `benchmark_runs_structure` | BENCHMARK_RUNS.md has the iteration pattern (published/config/results, Run-1/Run-2, FUTURE slots); published sources cited; none-exists markers present |
| 11 | `results_tree` | Results/README + PROVENANCE present; application dirs number-first; no empty run folders |

## Runtime behavior tests (11 unit tests)

Run `python3 -m unittest discover -s tests -p 'test_*.py'`:

| Test class | Tests | What they verify |
|---|---|---|
| `TestImmuneScan` | 6 | UGUGU motif detection; clean 19-mer no flags; TLR3 ≥21-nt class; invalid-char rejection; both-strand flag propagation; DNA T→U silent conversion |
| `TestRequirementRanking` | 3 | Hard-veto removes UGUGU + min-standard filters low RN.Ai; stability report present with disclosure text; panel respects max size |
| `TestExploreDesign` | 3 | Module importable; `target_gene` parameter present (v1.2.1 scope-explicit); required signature parameters |

These checks validate this specification package and runtime-script behavior on synthetic fixtures only. They do not validate external backends, model predictions, database access or biological efficacy.

## Scientific validation status

- **Component-level backend validation** (liveness audit: mutation tests, label separation, positive/negative controls, live-API round-trip; e2e: 11/12 pass + integration micro-run reproducing known values exactly; E4e RNAhybrid defect documented) — executed 2026-11-04/05, summarized in [STATUS](../STATUS.md).
- **Computational benchmarks on public data** — included in [benchmark/](../benchmark/) with no-tuning attestation; they are not biological validation.
- **Head-to-head manual-vs-sub-agent** — definitive large-pool comparison in [benchmark/001_HeadToHead-LargePool](../benchmark/001_HeadToHead-LargePool/README.md) with run-iteration structure in [BENCHMARK_RUNS.md](../benchmark/BENCHMARK_RUNS.md).
- For repository release: link the contribution issue and complete the applicable PR/review process; owner/reviewers currently pending.
