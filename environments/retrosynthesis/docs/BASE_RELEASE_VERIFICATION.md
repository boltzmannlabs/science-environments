# Base release verification — 0.1.0

Status: ready for owner review before a GitHub update. Prepared locally on 2026-10-28; no commit, push or deployment performed. Owner: environment/integration maintainer.

## Verified behavior

Normal Agent Scientist retains its existing tools and autonomous workflow selection. The optional `srg_action` plugin provides target/inventory sessions, local route generation, supported route import, validation, ranking and explicit submission. The controlled benchmark runner remains separate. Scientific LLM roles continue to use the main/default profile.

| Check | Result |
| --- | --- |
| Clean Python 3.11 source-release suite | 2,646 passed; 13 skipped; 47 warnings; 215.39 seconds |
| Package statement/branch coverage | 94.57%; required threshold 80% |
| Focused plugin/host/adapter checks | 134 passed; 94.99% coverage (overlaps full suite) |
| Actual Agent Scientist plugin discovery | Passed profile/session isolation checks |
| Actual chemistry bridge | BFS and SynthChem portfolio generated drafts, imported, validated, ranked and explicitly submitted |
| Actual LocalRetro identity check | Passed; four predictions; checkpoint SHA-256 `0147fa71b0d1801f0c9843ce54c8a25f631f8a62cdd900583c49710211fd442c` |
| Installed package and final wheel | All 101 Python sources match tested release; required third-party notices included |
| Offline installed demo / dependency consistency | Passed / no broken requirements |
| Clean dependency vulnerability audit | 42 packages checked; zero known vulnerabilities at audit time |
| Independent code review | No unresolved findings in reviewed changes |
| Previous acceptance receipts | 18 checked; none changed |

The 13 skips cover optional archival artifacts and explicitly configured external integration/scientific runtimes absent from the portable test setup. Actual normal Agent Scientist and LocalRetro checks were performed separately. Warnings comprise one Starlette test-client deprecation and 46 Syntheseus warnings about uncached test reaction models. Test success establishes software behavior, not chemical feasibility or research superiority.

## Reproduce

Install the source release with `pip install '.[test,api,search]'` in a fresh Python environment. From the release root:

```sh
python -m pytest -q -p no:cacheprovider --cov=synthesis_route_gym --cov-report=term --cov-fail-under=80
python -I examples/base_demo.py
python -m pip check
```

The accepted run used an isolated installation from `base-v0.1.0-rc3`, with bytecode writing and network package installation disabled. Every allowlisted working-tree file matched that tested copy before this report was added. The final export is verified against its own SHA-256 manifest; the external release receipt records manifest, archive and wheel hashes.

Detailed receipts remain local under `artifacts/releases/base-v1/`: `regression-clean-final.log`, `coverage-clean-final.json`, `plugin-focused-tests-v3.log`, `native-discovery.log`, `normal-runtime-smoke-v2.json`, `normal-runtime-smoke-v3.json`, `installed-wheel-verification.json`, `dependency-audit-clean-v1.json`, `review.md`, and `prior-receipts-verification.json`. These are excluded from the portable release to avoid bundling local research records. The v2 asset inventory is explicitly post-hoc; v3 verifies backend checkpoint identity directly.

Earlier failed/interrupted runs are retained locally. The first live smoke exposed timeout/worker-cleanup defects; these were fixed and checked with lifecycle tests and subsequent actual-runtime smokes. An earlier clean suite had five portability/fixture/timing failures; targeted fixes and the final full suite passed. Those earlier runs are not presented as successful acceptance results.

## Scope and remaining work

- No LLM/provider calls or remote platform jobs were used in these base-release checks. Full remote submit/download/import execution has not been verified.
- Scientific model assets and their separate runtimes are not bundled. Missing assets report unavailable status. The installed package alone is not a self-contained model distribution.
- Normal sessions are in memory and end when their host exits. Persistent benchmark episodes are separate.
- Asset identity is checked at host startup and backend response time; this is not continuous file-immutability enforcement or a complete transitive runtime pin.
- Linux parent-death cleanup covers the current direct scientific worker, not arbitrary future descendants or immediate termination during uninterruptible kernel I/O.
- Main-agent LLM use outside the environment is not fully accounted by the normal plugin. Matched comparisons use the dedicated benchmark runner.
- Full held-out scientific benchmarking, independent evidence-based chemical assessment, specialist promotion, and budgeted/unbudgeted comparisons remain deferred. This release does not establish improved synthesis outcomes or complete all 14 research steps; the existing scientific acceptance count remains 8/14.
- No new project license is assigned; third-party attribution is preserved. Release excludes credentials, profiles, checkpoints, evaluator answers and historical raw data.

See [base release contract](BASE_RELEASE.md) and [Agent Scientist integration](../integrations/agent_scientist/README.md) for setup and compatibility requirements.
