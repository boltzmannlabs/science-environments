# SynthChem remote-repository audit and local review copy

Audit date: 2026-10-27. Source: `boltzmann3@100.113.115.72:/home/boltzmann3/synthchem`.
Local copy: `/home/boltzmann6/synthchem-review/20261027/source`.
Scope at audit completion: inspection, selective copying and offline tests;
SRG-03 was paused. The user subsequently authorized selective reuse and resumed
SRG-03; see [the updated plan](OPTIMIZATION_PLAN.md) and [tracker](PROGRESS.md).

## Assessment

SynthChem is strongly related to this project. It is a broader process-research
application with route exploration, literature/source handling, process and
stereochemistry dossiers, local optimization, project storage and a browser UI.
SRG supplies the controlled action environment, main-profile-only Agent Scientist
execution and matched-comparison benchmark. The two projects are complementary.

The most useful imports are narrow scientific contracts and algorithms, not the
entire application. SynthChem's detailed reports preserve negative findings and
usually distinguish software checks, source recovery and experimental success.
It does **not** already establish our mandatory held-out new-model improvement or
matched-budget specialist advantage.

## What was copied

- 581 source/support files: application and selected vendor code, tests, scripts,
  docs, configurations, examples, benchmark definitions and five aggregate reports.
- Four catalog files: original CSV, legacy database, current versioned database
  and its selection/provenance metadata. The active database contains 38,753
  records; its metadata reports 38,029 valid structures and 38,115 usable price
  ranges. These prices are explicitly **unverified INR/kg estimates**. Current
  supply, purity and publication dates remain unknown.
- Total original-file payload: **585 files, 145,437,214 bytes**. Archive and
  per-file SHA-256 receipts are retained next to the copy. Both copied catalog
  databases passed SQLite integrity checks.

The source has no Git metadata, so there is no commit hash to pin. The file
manifest and archive hashes identify this snapshot. `.source_snapshot.json` and
`.catalog_snapshot.json` record the selection and hashes; the active catalog has
a separate transfer receipt.

The roughly 12 GB of model artifacts, virtual environments, raw/judge datasets,
most run histories, UI projects and vendor datasets/binaries were not copied.
One vendor-generated Python file above the initial 4 MB review limit was excluded
and recorded. This is a useful review snapshot, not a full-machine backup or a
ready-to-run replacement installation. Credential filenames and likely embedded
credential patterns were screened before the source archive was produced. The
SSH password was not stored in the workspace.

## Highest-value reuse candidates

Paths in this table are relative to the imported `source/` directory.

| Capability | Evidence in source | SRG use after resumption |
|---|---|---|
| Shared proposal pool, caching and source balancing | `planning/retrosynthesis.py`; `planning/search_portfolio.py` under `src/synthchem/` | SRG-04/05: stronger fixed baseline; SRG-07: bounded Strategist choices; SRG-12: search ablations. |
| MCTS and zero-heuristic A* | Native Syntheseus portfolio with shared calls/time policy | Compare on the same expansion backend and inventory. This is algorithmic search, not a learned feasibility model. |
| Recipe-bound DoE and response optimization | `planning/optimization.py`, `optimization/doe.py`, `optimization/response.py` | SRG-06/08/10: a fixed optimizer and Condition Scientist tools; factorial/LHS/composite designs and numeric GP/UCB proposals. |
| Feedback provenance and revision storage | `optimization/feedback.py`, `workflows/campaign_store.py` | SRG-03/11: persistence patterns, recipe binding and stale-result checks. |
| Structured condition predictions | `models/quarc.py` | SRG-04/08: preserve amount/temperature intervals, raw scores, unknowns and source identity. |
| Process cost and procurement contracts | `planning/process_comparison.py`, `route_economics.py`, `route_discovery.py`, `procurement.py` | SRG-09/10: comparable cost scenarios and separate verified quote records. |
| Impurity and stereochemical claim checks | `planning/impurities.py`, `chirality.py`, `stereo_success.py` | SRG-09/10/13: interpretable hypotheses and distinctions between encoded identity, source support and observations. |
| Research dossiers and browser UI | `ui/`, `workflows/process_campaign.py` | A possible later interface; not necessary to finish the benchmark environment. |

The numeric surrogate is fitted locally with a fixed RBF kernel. Its factors are
numeric; it is not directly interchangeable with our chemical-role condition
model. Bound its dense pure-Python computation and evaluate it on an appropriate
held-out decision task before crediting an improvement. No dedicated validated
biocatalytic model or retrieval workflow was identified; our biocatalysis lane
still needs its own work.

## What the reported experiments establish

These are findings in copied aggregate reports, **not scores reproduced during
this audit**. Source reports are under the imported `artifacts/` directory.

| Report | Recorded outcome | Interpretation |
|---|---|---|
| `workflows/process_v2/REPORT.md` | Agent-only 7/37 fields; retrieval 4/37; retrieval plus specialists 4/37. All arms 0/5 complete cases. | Negative result; extra specialist work makes compute unmatched. The evaluator explicitly records `matched_compute_budget=False`. |
| `workflows/hybrid_v1/REPORT.md` | Combined precursor rank 9 versus expanded agent-only rank 8; no top-five/full-route recovery. | No hybrid advantage. The earlier comparison used a smaller candidate library. |
| `benchmarks/retrosynthesis_portfolio_v1/IMPLEMENTATION_REPORT.md` | A*, MCTS and portfolio each found zero complete routes on the exposed development target. | Six supplied curated routes were comparators, not autonomous discoveries. |
| `workflows/quarc_architecture_v1/REPORT.md` | A small GP replay reports lower MAE, with a disclosed repeated train/test setting; GP and random search reach the same table-best outcome. | Does not establish general prediction or sequential-optimization superiority. |
| `benchmarks/process_20261020/REPORT.md` | Earlier 6/18 strict scoring was described as semantically defective; 13/18 supplemental AI review was post-hoc. | Neither is independent experimental validation or a clean confirmatory endpoint. |

The README's 313-test statement is a historical report. This audit selected a
different current subset and records its results below.

## Adaptations required before use in SRG

1. **Main-profile enforcement.** `ui/runtime_agents.py` defaults to `gpt-6.1-sol`
   and constructs Codex commands with `--ignore-user-config` and `--model`.
   A JSON adapter also exists, but returned model identity is not strictly
   checked. Retain SRG's Agent Scientist main-profile resolver and client for
   every live research role. Do not activate this default launcher unchanged.
2. **Host validation.** Convert returned routes to `RouteCandidate` and recompute
   graph, stock, quantity and constraint checks. Legacy scorecards trust submitted
   completion/stock booleans and bind some reviews to IDs rather than content.
   Search stock closure is not evidence-supported synthesis success.
3. **Inventory identity.** Some workflow code splits disconnected SMILES, while
   SRG can preserve a complete salt/material identity. Define the mapping and
   test it; do not silently change the available inventory. Catalog estimates
   require explicit units/currency/basis before any cost comparison.
4. **Shared budgets and cancellation.** A search deadline can be exceeded by an
   already-started blocking provider call. Reuse SRG's bounded worker execution
   and aggregate accounting. Cache keys must include input, model/configuration,
   stock and evidence versions.
5. **Evaluator isolation.** `BenchmarkWorkspace.assert_read_allowed()` is an
   optional check, not an enforced reader/sandbox; no production invocation was
   identified. Some reports disclose answer-bearing retrieval and exposed
   development cases. Keep our public-input/private-answer boundary authoritative.
6. **Model/tool output projection.** Proposal manifests can include full evidence
   and cached proposals. Surrogate serialization includes training/calibration
   rows. Keep host artifacts private and expose only allowed observations and
   predictions. Imported privileged seeds must not become free search evidence.
7. **Splitting and review.** Legacy split hashes use stripped reaction strings,
   missing canonical-equivalent cases. Retain SRG's connected-group audits and
   immutable review binding. Supplied reviewer names and hashes do not authenticate
   chemistry or make a review independent.
8. **Persistence scope.** Campaign revision storage does not yet preserve our
   consumed budgets, provider reservations, pending-action idempotency and
   cancellation state. It is a reusable pattern, not completed episode recovery.

## Local checks performed

Twenty selected core test modules were run against the copied source using the
existing chemistry Python environment. An audit-only pytest guard blocked network
connections and external subprocess launches. No live agent, scientific-model
inference, application server or heavy benchmark was started.

Initial run: **444 passed, 2 failed, 13 skipped** out of 459 collected tests.
Both failures required the configured default catalog snapshot, which was absent
from the initial source-only copy. Copying that exact catalog and its supporting
data resolved both failures in a targeted rerun without editing source code.
Combined result for the selected tests: **446 passed, 13 skipped, zero unresolved
failures**. This is not a full-suite or GPU-inference validation.

Four skips require `chemprop`; nine require `syntheseus`. Their absence means
QUARC backend details and native portfolio execution were not validated locally.
Other application tests require UI servers, remote-host interpreter paths or
artifacts not copied. The catalog's source CSV and databases were checksum-checked;
SQLite integrity was checked separately from price accuracy.

An automated scan checked 15,964 distinct literal strings from copied code,
structured files and text. It found zero exact canonical matches to our reserved
targets or reference-reaction strings. Raw judge and target-level route-result
datasets were not copied. This limited scan does not establish absence of
semantic, named-compound, template or model-pretraining overlap.

Receipts/logs live in `/home/boltzmann6/synthchem-review/20261027/`:
`transfer_receipt.json`, `catalog_transfer_receipt.json`,
`active_catalog_receipt.json`, `core-tests.xml`, `catalog-retest-complete.xml`,
`holdout_overlap.json` and `audit_receipt.json`. Earlier failed attempts remain
available instead of being overwritten.

## Recommended continuation

When the user resumes the environment work, inspect the campaign-store patterns
for SRG-03, then prioritize the proposal pool/search baseline and evidence/tool
contracts for SRG-04/05. Adapt the DoE/response tools and process contracts in
their planned stages. Each port needs SRG-specific tests and matched-budget
development evaluation; no imported specialist becomes enabled by default.

The 14-step plan remains at **2 accepted steps**. This side audit does not count
as completing SRG-03 or demonstrating new scientific performance.
