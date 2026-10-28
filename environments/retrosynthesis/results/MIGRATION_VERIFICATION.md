# Retrosynthesis migration verification

**Date:** 28 October 2026. **Status:** local preparation verified; GitHub update and post-publish verification pending.

Prepared on local branch `feat/retrosynthesis` against science-environments main commit `7d305586b92e6195e8a65856478b6ffcfaeb06ec`. No commit, push, pull request, merge or deployment was performed.

| Check | Observed result |
| --- | --- |
| Fresh isolated Python installation | `retrosynthesis` 0.1.0 installed from `environments/retrosynthesis` |
| Full regression | 2,650 passed, 13 skipped, 47 warnings in 208.41 seconds |
| Package statement/branch coverage | 94.57%, exceeding 80% threshold |
| Installed package and wheel | All 101 Python sources match tested source; required notices included |
| CLI compatibility | `retrosynthesis` and legacy `synthesis-route-gym` entrypoints work |
| Offline software demo and inventory replay | Passed; no experimental-validation claim |
| Actual Agent Scientist plugin discovery | Renamed plugin discovered in temporary homes; profile isolation verified |
| Actual chemistry bridge | BFS and SynthChem portfolio each generated drafts, imported, validated, ranked, explicitly submitted and closed |
| LocalRetro identity | Both workflows recorded checkpoint `0147fa71b0d1801f0c9843ce54c8a25f631f8a62cdd900583c49710211fd442c` |
| Dependency consistency and vulnerability audit | No broken requirements; 42 packages audited, zero known vulnerabilities at audit time |
| Migration review | No unresolved findings; historical STATUS preserved byte-for-byte |

The 13 skips cover absent archived Step 7/10/11 records, the archived measured portfolio and REBOLT excerpt, an opt-in ReactionT5 runtime, and opt-in native benchmark compatibility. Actual normal Agent Scientist discovery and LocalRetro integration were checked separately. Warnings comprise one Starlette test-client deprecation and 46 uncached test reaction-model warnings. No LLM/provider call or remote platform job was made; an autonomous model-driven research conversation and scientific benchmark are not claimed by these checks.

The first migration-suite launch was interrupted during collection to reinstall the final CLI display correction. Its log remains local; only the completed final run supplies acceptance counts. Main-profile configuration was not changed. Scientific model assets remain external and were already available on the test host.

## Reproduce locally

From `environments/retrosynthesis`, create a fresh Python environment and install `.[test,api,search]`, as in the README. Then:

```sh
python -m pytest -q -rs -p no:cacheprovider --cov=synthesis_route_gym --cov-report=term --cov-fail-under=80
python -I examples/base_demo.py
python -m pip check
retrosynthesis --help
synthesis-route-gym --help
```

Use the installed Agent Scientist Python to run `integrations/agent_scientist/verify_discovery.py --scientist-source /path/to/Agent-Scientist`. Actual chemistry workflows additionally require the separately configured LocalRetro source, checkpoint and runtime described in the integration guide. Discovery uses temporary homes and does not activate the plugin in the user's main profile.

Detailed install/build/test/runtime receipts and SHA-256 records are retained locally outside the repository payload in `retrosynthesis-validation/`. The small versioned summary here deliberately excludes full route traces, local paths, credentials and model assets.

## Publication gate

The owner requested review before updating GitHub. After approval, submit the focused branch through the repository's issue/PR/review workflow. Then test a fresh checkout of the exact published commit, including installation and Agent Scientist integration, and record that commit's results. This local report does not claim those future checks have happened. See [the post-publication checklist](README.md).

Full scientific benchmarking, specialist promotion, independent chemical review and comparisons with and without budgets remain deferred. The environment is Implemented; these software checks do not establish scientifically Validated status or close issue #14.
