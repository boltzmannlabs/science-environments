# Optimization execution tracker

Current local route-generation work after the base release makes SynthChem
portfolio the preferred default and adds metered one-step hypotheses plus
intermediate grafting. This user-directed product choice does not change the
historical accepted-step count or establish a search or specialist win.

Scope: local work, using Agent Scientist's main-profile LLM for every research
role. The user has prioritized a usable base release before the full benchmark.
No commit, push or deployment is authorized by local release preparation. The working MVP and the completed optimization program are different
milestones. **8 of 14 steps are accepted under the revised Step 6 scope;
the full program is not complete.** Custom-model development is deferred at
the user's request; its original scientific improvement gate has not passed.

| Step | Work | Status |
|---|---|---|
| SRG-01 | Preserve baseline and define success | Accepted |
| SRG-02 | Curate benchmark and isolate final evaluation | Accepted |
| SRG-03 | Execution efficiency, budgets and reliable submission | Accepted |
| SRG-04 | Scientific tools and evidence contracts | Accepted |
| SRG-05 | Stronger fixed-search baseline | Accepted: implementation and pilot; no promotion |
| SRG-06 | Existing pretrained model integration (user-revised scope) | Accepted locally; custom-model development deferred; superiority unproven |
| SRG-07 | Retrosynthesis Strategist | Implementation and matched development pilot complete; scientific promotion gate open |
| SRG-08 | Condition Optimisation Scientist | Implementation and 96-episode development comparison complete; scientific promotion gate open |
| SRG-09 | Route Critic | Implementation and 48-episode development comparison complete; scientific promotion gate open |
| SRG-10 | Integrate five application workflows | Accepted for local integration; scientific measurement gates remain unvalidated |
| SRG-11 | Adaptive orchestration and Small Molecule handoff | Accepted for local integration; ten-episode pilot and code/execution audits passed; scientific gain unproven |
| SRG-12 | Development ablations and configuration freeze | Partial; remaining comparisons and final freeze deferred for the base release. Both regimes implemented; 24 fixed budgeted runs and three unbudgeted fixed runtime checks completed. |
| SRG-13 | Locked benchmark and blinded source review | Deferred until after the base release; final outcomes remain sealed |
| SRG-14 | Measured performance optimization and full local verification | Essential base-release checks in progress; full optimization/reproducibility and scientific-report gate remain open |

The [implementation plan](OPTIMIZATION_PLAN.md) defines each step's dependencies
and acceptance gate. Existing MVP implementations are starting points, not
automatic completion of their optimization tickets.

## Base release priority (user amendment, 2026-10-28)

Prepare the working software for review before a GitHub update, while deferring
full scientific benchmarking. Preserve existing Agent Scientist retrosynthesis
tools and skills. Normal usage keeps Agent Scientist responsible for workflow
selection; the environment provides local search, a common route workspace,
constraints/evidence checks and feedback. The restricted runner remains a
separate benchmark entry point, not the default for every Agent Scientist task.

The base-release gate requires normal-session integration, supported route
imports, compatibility/portability fixes, clean-package verification, appropriate
third-party notices and explicit exclusion of credentials, private evaluators,
checkpoints and nonredistributable research data. See [BASE_RELEASE.md](BASE_RELEASE.md).
Local preparation is not permission to push; the user must approve that action.

The completed Stage B screen is 24/24 submitted runs on eight inventory inputs
from four target groups. Inventory-compliant reference recovery was 2/8 for
breadth-first, 0/8 for best-first and 2/8 for SynthChem portfolio. The predeclared
tie-break chose SynthChem portfolio using additional inventory-closed tasks;
it did not change the CLI default. All three separate unbudgeted fixed-policy
checks completed naturally. These are development/runtime results, not a final
Agent Scientist versus specialist comparison or a chemical-feasibility verdict.
Remaining Stage C/D/E/F comparisons and the final configuration freeze are deferred.

Historical acceptance sections below describe their frozen versions. Their
file hashes, results and step counts are not rewritten by base-release changes.
The recorded Step 12 regression was 2,586 passing tests and 94.60% branch-inclusive
coverage; the prepared release requires its own verification after new edits.

## Final evaluation requirement (user amendment, 2026-10-27)

Evaluate fixed workflow, main Agent Scientist and specialist-enabled Agent
Scientist **both with matched budgets and without research-budget limits**.
The unbudgeted track must allow natural completion, without a hidden model-call,
token, action, expansion or episode-time cap. Record actual resources, failures
and external interruptions, and report the two tracks separately. Keep inputs,
scientific constraints, tools, evidence rules and the main-profile LLM consistent.
Commit decisions from both tracks before opening final answers.

Both execution regimes have been implemented and exercised locally, including
three naturally completed unbudgeted fixed-policy runtime checks. This does not
satisfy the remaining comparative scientific evaluation. Earlier pilot results
and acceptance receipts remain historical. Details are in
[the final evaluation plan](OPTIMIZATION_PLAN.md#13-run-the-locked-benchmark-and-blinded-source-review).

## SRG-11 orchestration and local handoff execution

One main conversation can now receive eligible, tool-free advisor consultations
under a versioned host policy and shared resource ledger. Default adaptive mode
enables no advisors; explicit experimental policies control admission. Typed
Small Molecule handoffs preserve candidate identity and upstream provenance,
return evidence gaps and resource accounting, and persist success/failure and
resume receipts. The single-main role-prompt control is implemented, but context,
timing and conversation isolation differ from separate advice.

The frozen local diagnostic completed **10/10 route submissions and 8/8 native
conversations**: two reused public development cases × five arms × one repeat.
Direct tools, main, role-prompt main, all-eligible-advisors main and default
adaptive main selected the same route in each case. All-advisors admitted two
critic requests, one accepted and one contract-rejected; no Strategist or
condition consultation was eligible. Default adaptive admitted none. The
same-pool feedback comparison changed candidate selection in **0/5 arms**.
These are integration outcomes, with no specialist benefit or cross-pod gain.

- **31 model requests, 249,723 confirmed tokens and 60,420 reservation units.**
  Main recovered from two provider failures; their usage remains unsettled.
  Exact total tokens and monetary cost are unknown. The 310,143 charged units
  must not be described as measured tokens. There were 62 environment actions.
- **2,315 tests passed; 24 warnings; 95.04% branch-inclusive coverage.** The
  package build and separate code review passed. The native interface smoke used
  no model calls; the eight native pilot conversations are separate evidence.
- All 1,623 frozen files passed the pilot integrity check. Public development
  inputs were reused, synthetic upstream provenance was retained, and private
  and reserved final labels remained closed.

The separate execution accounting/source audit verified all ten event chains,
candidate/source bindings, resource receipts and feedback comparisons. This is
automated source-consistency review, not external chemist or experimental
validation. **Step 11 is accepted for local integration: 8/14 steps are accepted.**
Main-only remains default and Steps 7–9's scientific promotion gates stay open.
**Step 12, development ablations and configuration freeze, is next.**
Matched-budget and genuinely unbudgeted final evaluation remain outstanding.

Evidence: [orchestration and handoff guide](ORCHESTRATION_HANDOFF.md),
[actual pilot summary](../artifacts/steps/srg-11/pilot-v1/summary.json),
[decision commitments](../artifacts/steps/srg-11/pilot-v1/commitments.json),
[integrity receipt](../artifacts/steps/srg-11/pilot-v1/integrity.json),
[separate code review](../artifacts/steps/srg-11/review-code-final.md),
[execution audit](../artifacts/steps/srg-11/review-execution.json),
[acceptance receipt](../artifacts/steps/srg-11/acceptance.json).

## SRG-10 integration acceptance and local execution (historical)

All five application workflows are callable through the same environment using
stored routes and step references. The host binds source access, condition
observations and impurity predictions to those exact records, preserves evidence
authority and shares action, observation and retrieval budgets across APIs.
Revisions remain separate records; configuration changes reject checkpoint resume.

The frozen five-lane replay completed **five reports and five submissions, with
zero failed/unavailable actions or truncated episodes**. It used 24 actions,
two retrospective condition observations, one actual existing impurity-checkpoint
request and one biocatalysis source retrieval. There were no LLM calls, new model
training, deployments or reserved final-label access. All 377 frozen files passed
preflight and postflight checks.

- Inventory/process examples test declared flows and illustrative cost accounting.
  The process alternatives cost 51 and 80 USD on the supplied basis; the third
  retained unknown total cost. No chemical-feasibility or savings claim follows.
- Conditions reuse previously public Step 8 measured development records; no new
  experiment or untouched held-out decision improvement is claimed.
- Impurity inference succeeded, but no measured impurity labels were available.
  Its outputs included an unsupported C6 polyol and two unchanged inputs. They
  remain hypotheses; partial annotations do not create negative labels.
- Biocatalysis uses Rhea/IUBMB reaction identity, with omitted acetate/proton
  coproducts and unknown activity retained. No enzyme process is validated.
- **2,092 tests passed; 24 warnings; 94.95% branch-inclusive coverage.** Separate
  code and runner reviews left no unresolved HIGH/MEDIUM findings. Their selected
  test sets overlap the full regression and are not additional unique tests.
- Separate source review verified all five event chains, source/step bindings
  and declared quantity/cost calculations. This is AI source-consistency review,
  not external chemist sign-off or new experimental validation.

**At Step 10 acceptance, the accepted count became 7/14.**
Scientific measurement gates remain unvalidated. Step 11's subsequent execution
is recorded above. Steps 7–9's scientific promotion gates
remain open; main-only remains default. Final evaluation with and without
research budgets remains required in Steps 12–13.

Evidence: [application guide](APPLICATION_WORKFLOWS.md),
[execution summary](../artifacts/steps/srg-10/execution-v1/runs/summary.json),
[completion manifest](../artifacts/steps/srg-10/execution-v1/runs/execution-complete.json),
[source audit](../artifacts/steps/srg-10/review-source.md),
[final code review](../artifacts/steps/srg-10/review-code-final.json),
[runner review](../artifacts/steps/srg-10/review-code-examples.json).

## SRG-09 implementation and development result

Implemented shared `review_routes` and optional `main_route_critic`. The host
binds stored routes, deterministic facts, retrieved sources and scientific-tool
results. One tool-free main-profile consultation returns typed advice within the
shared ledger; main owns checks, revisions and final submission.

The frozen comparison completed **48 episodes: eight three-candidate shortlists
× two repeats × three arms**. Every arm made the exact expected selection in
**16/16 trials**, retained **24/24 controls**, and submitted **zero invalid or
unsupported records**. All 32 main-agent conversations completed normally. There
were no manual interruptions. All decisions preceded private label scoring;
reserved final data remained closed.

- The assisted arm tied main in all sixteen comparisons. Direct tools reached
  the same ceiling without LLM requests. No critic benefit was demonstrated.
- Critic: **3 accepted, 8 rejected reports, 5 provider stream idle timeouts**.
  Rejections were route/step fact-citation mismatches. Failed advice stayed
  consumed. Three completed rechecks were main-initiated; no accepted critic
  report recommended one.
- Main used **52 requests**, 441,229 confirmed tokens and 20,321 reservation
  units. Assisted used **71 requests**, 588,650 confirmed tokens and 214,000
  reservation units. Exact total tokens remain unknown: one and six requests,
  respectively, have unsettled usage. Both main-request timeouts recovered.
- **1,767 tests passed; 94.44% branch-inclusive coverage.** Separate source
  review verified 24 records and all 48 selection scores. Separate accounting
  review verified event chains, ledgers, advice delivery and aggregate results.
  These are AI source-consistency checks, not external chemist or lab validation.

The cases reuse PaRoutes/Doyle development records with controlled errors.
They are not untouched held-out synthesis problems. Main-only remains default;
the critic remains experimental. At this historical Step 9 gate, **6/14 steps were fully accepted**. Step 10
application integration and its acceptance are recorded above. Final evaluation with and without research
budgets remains required in SRG-12/13.

Evidence: [guide](ROUTE_CRITIC.md),
[summary](../artifacts/steps/srg-09/pilot-v1/summary.json),
[source audit](../artifacts/steps/srg-09/review-source.md),
[ledger audit](../artifacts/steps/srg-09/review-final.json),
[acceptance](../artifacts/steps/srg-09/acceptance.json).

## SRG-08 implementation and development result

Implemented a persistent finite condition-study environment with inspect,
observe, cached public-yield prediction and observed-candidate submission.
The optional `main_condition_scientist` advisor uses the main profile, zero
tools and one request within the main episode's shared ledger. Host validation
binds predictions and measurements to exact candidate chemistry and preserves
observation charges, deadlines and failed consultations across resume.

The frozen comparison ran **96 episodes: eight studies × two repeats × six
methods**. Every arm used the same 24 candidates, two initial measurements,
four additional observations and 192 shared ReactionT5 predictions. All 96
submitted selections and all 32 main-agent conversations finished normally.
All decisions were committed before retrospective scoring. Final data stayed closed.

- Mean submitted regret in yield percentage points, lower is better:
  **7.9752 fixed order, 7.2725 random, 4.5699 public-model ranking,
  6.0064 GP expected improvement, 4.7498 main, 4.2315 assisted**.
- Assisted versus main: **two wins, thirteen ties, one loss**. Both wins occurred
  where the specialist request failed. The fourteen accepted recommendations
  yielded thirteen ties and one loss. This post-hoc breakdown supplies no
  evidence that successfully delivered advice improved the result; it is not
  evidence that failures caused improvement. Public-model ranking also slightly
  outperformed main without LLM requests.
- Main used 112 requests and 3,010,400 settled tokens. Assisted used 128 requests,
  with 3,219,754 recorded tokens and 60,759 retained reservation units for two
  advisor stream timeouts. Exact total assisted token use is unknown; the
  budget-accounting charge is 3,280,513. Failed advice stayed consumed, and
  main continued. Resource reservations are not monetary cost estimates.
- **1,514 tests passed; 93.97% branch-inclusive package coverage.** Independent
  runner review passed 20 synthetic end-to-end cases. Separate source review
  verified all 192 recipes/predictions, 96 selections and 576 observation
  instances with no discrepancies. This is source consistency verification,
  not new experiments or external chemist validation.

The studies share five products, three scaffolds and one previously used
development publication. These results do not close the held-out improvement
gate. **SRG-08 remains scientifically open, default remains main-only, and
6/14 steps were fully accepted at that gate.** The subsequent Route Critic implementation
is recorded above. Final evaluation with and without research-budget limits remains
required in SRG-12/SRG-13.

Evidence: [Condition Scientist guide](CONDITION_SCIENTIST.md),
[frozen summary](../artifacts/steps/srg-08/pilot-v1/summary.json),
[individual source review](../artifacts/steps/srg-08/review-source.md),
[accounting review](../artifacts/steps/srg-08/review-final.json) and
[acceptance status](../artifacts/steps/srg-08/acceptance.json).

## SRG-07 implementation and development result

Implemented optional `--method main_strategist`: one host-triggered consultation,
one model request, zero specialist tools, a typed bounded plan and the shared
main-profile ledger. The host validates advice and main chooses ordinary
environment actions; inventory, evidence authority and final submission remain unchanged.
Interrupted or rejected advice is recorded and cannot silently obtain a retry.

The frozen development pilot ran **12 actual executions: four targets × fixed
best-first, main-only and main-plus-Strategist**, with equal resource ceilings.
The agent arms used the same main-profile `gpt-6-sol` through `openai-codex`.
All decisions were committed before selected development-reference scoring;
reserved final labels stayed closed.

- Inventory-compliant reference-route retrieval within the submitted top three:
  **0/4 fixed, 0/4 main-only, 1/4 assisted**; one paired win and three ties.
  All top-1 reference-hit counts are zero; the assisted match was ranked second.
- Deterministically accepted submitted routes: **3, 5 and 5**, respectively.
  These are not experimentally validated or independently solved routes.
- Main-only versus assisted: **32 versus 30 model requests**, **373,923 versus
  291,814 recorded tokens**, and **13 versus 13 expansion requests**. All token
  usage was settled; tokens are not a USD cost estimate.
- Three advisor consultations produced valid plans; one task did not trigger
  advice. All 12 runs submitted, including empty shortlists. Four main-only and
  three assisted model conversations were incomplete at their request limits;
  their submitted routes remain scored rather than being discarded.
  Only one consultation had later expansion overlap with a recommended target;
  neither that overlap nor the retrieval result establishes a causal benefit.
- A pre-outcome correctness amendment reserves an advisor call, main action
  round and submission. The three actual admissions had three, four and five
  calls remaining, so the recorded guard audit found them compatible. Original
  frozen execution and the source amendment are both retained.
- Final configured regression: **1,155 tests passed, 93.24% branch-inclusive
  package coverage**, including the explicitly enabled existing model-runtime
  test. Separate review verified execution provenance, all eight agent ledgers,
  advice delivery and reported totals.
- A separate individual source review checked all **13 submitted route
  instances**, their assessments and recorded prediction provenance against the
  four selected references, finding no discrepancies. This is source verification,
  not an external chemist review or experimental validation.

This four-target, single-run comparison is descriptive and underpowered for
promotion. It establishes an executable specialist and a measured pilot,
not general scientific benefit. **SRG-07's scientific gate remains open, the
default stayed main-only, and the accepted count was 6/14 at that gate.** SRG-08's
subsequent implementation and comparison are recorded above.

Evidence: [Strategist guide](STRATEGIST.md),
[development summary](../artifacts/steps/srg-07/development-v1/summary.json),
[guard compatibility](../artifacts/steps/srg-07/development-v1/guard-compatibility.json),
[final review](../artifacts/steps/srg-07/review-final.json),
[individual route review](../artifacts/steps/srg-07/review-routes.md),
[test log](../artifacts/steps/srg-07/pytest-configured.log) and
[acceptance status](../artifacts/steps/srg-07/acceptance.json).

## SRG-06 scope amendment and acceptance

The user requested an existing model now, with their own replacement later.
The revised completion gate is a pinned, replaceable, locally executed public
predictor with contract tests and an honest development diagnostic. The original
SRG-06 acceptance receipt and negative experiment remain unchanged historical
records; references below to 5/14 describe those earlier decisions.

- Integrated `ReactionT5v2-yield`, reusing verified cached REBOLT weights, as
  `predict_reaction_yield` in the environment, API, CLI and agent tool schema.
  It requires explicit host configuration and supplied reaction recipes.
- Pinned checkpoint/runtime identities, safe inference, strict used-weight
  loading, bounded requests/timeouts, explicit abstentions and resume checks.
  The coordinating LLM remains the Agent Scientist main-profile model.
- All **96 development recipes** received actual predictions in **31.88 seconds**.
  Top-1 hit selection tied fixed ordering at **2/12** products; top-3 was
  **7/12 versus 6/12**. This small reused-development CAD-hit diagnostic does
  not establish yield accuracy, held-out superiority or agent advantage.
- **1,030 tests passed; 93.26% branch-inclusive package coverage.** Separate
  review verified all 96 source records and ranking decisions and resolved the
  CLI failure-reporting issue. No remaining HIGH/MEDIUM code finding.
- Exact output parity with the publisher's reference class was confirmed.
  The model-card example's printed number remains unreproduced for the pinned
  checkpoint/runtime and is retained as a known discrepancy.
- The replacement protocol supports a later custom predictor. Generic yield
  scoring does not automatically rank incomplete SynthChem routes; explicit
  decision policies remain in Steps 7–8. The final three-arm benchmark is pending.

See [model usage and limits](PUBLIC_YIELD_MODEL.md) and the
[acceptance addendum](../artifacts/steps/srg-06/public-model-v1/acceptance.json).

## SRG-01 acceptance

- Preserved 1,567 files (1,017,638,000 bytes), including all 152 inventoried
  pre-change package files, checkpoint assets, historical successes/failures,
  external source references and four runtime dependency inventories.
- Added a reusable, tested snapshot creator/verifier with an externally recorded
  SHA-256 manifest anchor. It refuses overwrite and detects tampering.
- Recorded [protocol v1](PROTOCOL_V1.md): four distinct research questions,
  metric denominators, evidence rules, budget fairness, missingness rules,
  multiplicity-aware promotion criteria and explicit final-seal prerequisites.
- Added 25 preservation/integrity/CLI tests. Full suite: **280 passed, 90.34%
  branch-inclusive coverage**. One upstream Starlette/httpx deprecation warning.
- Separate-context code/protocol review found two verifier issues; both were
  reproduced with failing tests and fixed. No remaining SRG-01-level blockers.

Evidence: [acceptance receipt](../artifacts/steps/srg-01/acceptance.json),
[snapshot guide](BASELINE_PRESERVATION.md),
[protocol hash receipt](../artifacts/protocols/srg-protocol-v1-receipt.json).

The snapshot is locally read-only and checksum-verified, not owner-proof immutable
storage. Version inventories do not guarantee offline dependency installation.
Final benchmark authorization remains false because data, sample design,
configurations and budgets still require completion in later steps. No new
scientific improvement is claimed by this preservation work.

## SRG-02 acceptance

- Curated 80 route targets: 10 smoke, 20 development and 50 candidate final,
  with two inventory variants each; shared stock has 13,432 identities.
- Added 15 development condition tasks from 3,955 previously seen Doyle rows
  and 15 reserved condition tasks from 5,760 fresh Suzuki rows. **190 tasks total**.
  The fresh condition source is one product/publication, not 15 independent groups.
- Excluded 4,491 references with available-training-corpus overlaps, plus
  connected groups. Kept target, intermediate, reaction, scaffold and source
  links together. No detected cross-partition group leakage.
- Audited all 10,000 source references against deterministic environment rules;
  all selected 80 pass with full stock. Resolved the selected 80 documents to
  80 distinct Google Patents displayed families; no cross-partition conflict.
- Added hashed, write-once public/private bundles and explicit public projection.
  Submissions are committed before development scoring. Final scoring refuses.
- **449 tests passed; 90.98% package branch-inclusive coverage.** Actual local
  task materialization/commit/scoring-gate smoke passed with zero model calls.
  Separate-context review found no remaining HIGH blockers in this scope.

Evidence: [data guide](BENCHMARK_DATA.md),
[acceptance receipt](../artifacts/steps/srg-02/acceptance.json),
[curation receipt](../artifacts/steps/srg-02/curation-v1/curation.json),
[family audit](PATENT_FAMILY_AUDIT.md).

Acceptance covers the candidate cohort and tested access boundary. The statistical
design, final budgets/configurations and independent source-review phase remain
unsealed. No new chemistry-model improvement or agent superiority was claimed.
Checkpoint training completeness and independent DOCDB/INPADOC family validation
remain unknown. Broader condition inference requires more independent sources.

## SRG-02 implementation sequence (completed)

1. Research and pin eligible PaRoutes/source-reviewed route data and measured
   condition records; record provenance, license, missing fields and known model
   training overlap. Keep the already inspected Doyle outcomes in development.
2. Define task, inventory, source, candidate and grouping manifests. Keep target
   analogues, source families and repeated inventories in the same partition.
3. Write failing tests for deduplication, leakage, inventory semantics, outcome
   redaction and reproducible partition generation before implementing loaders.
4. Implement task curation and evaluator-only outcome access. Separate reference
   recovery, source-supported planning and measured-condition tracks.
5. Validate actual eligible counts and audit overlap; do not present the proposed
   10/20/50 task counts as already curated or statistically sufficient.
6. Save hashes and an acceptance receipt. Data isolation is established here;
   final configuration/resource sealing follows development selection.

Each later step follows the same research → tests → implementation → review →
acceptance sequence. Retain unsuccessful experiments and source uncertainty.

## SRG-03 acceptance (2026-10-27)

- Updated the existing plan with the approved SynthChem component mapping.
  Adapted its revision-store pattern without importing its LLM launcher.
- Added request-level usage settlement, conservative unknown reservations,
  retry admission guards and configurable finalization allowances. Conversation
  completion is distinct from actual agent submission; no host fallback invents
  a shortlist.
- Added durable environment/runtime checkpoints, action IDs, stale-writer checks,
  cancellation and resume preserving resources and deadlines. CLI supports
  `--episode-dir` and `--resume`; changed task/tool/model settings reject resume.
- Added compact specialist reports and bounded inventory/evidence inspection.
  One public smoke task with 13,432 stock identities used 1,342 prompt bytes
  versus 1,766,971 bytes for its full task JSON. This is a serialized-byte
  measurement, not measured provider-token savings or scientific improvement.
- Full regression: **533 passed, 91.98% branch-inclusive package coverage**;
  one upstream Starlette/httpx deprecation warning. Separate review identified
  and verified fixes for resume bindings, finalization reserves, evidence access
  and expired-episode execution; no remaining HIGH blocker in this scope.
- Reproducible offline smoke passed: interrupted-stage recovery retained usage
  and unknown reservations, completed specialists were not repeated, main made
  an explicit empty submission, duplicate actions consumed no new resources,
  and cancellation discarded late output. **Zero live LLM/model inference calls.**

Evidence: [runtime guide](RUNTIME_RECOVERY.md),
[acceptance receipt](../artifacts/steps/srg-03/acceptance.json),
[smoke receipt](../artifacts/steps/srg-03/smoke-v1/receipt.json).

This accepts local runtime reliability, not live-provider compatibility, improved
route feasibility or specialist benefit. Arbitrary external jobs still require
adapter-owned cancellation; orphaned revisions fail closed. External tool/weight
version pinning remains part of SRG-04. The 7.23-second smoke and prior 183-second
whole-bundle workflow cover different work and are not a speedup comparison.
Final evaluation remains unauthorized under the unchanged protocol.

## SRG-04 acceptance (2026-10-27)

- Added eight versioned scientific capabilities with typed requests/data/results,
  canonical aliases, explicit availability, declared versions, ownership, timeout
  and accounting contracts. Reused existing adapter callbacks and adapted audited
  SynthChem contract ideas; no imported launcher or upstream code dependency.
- Added strict source claims and separate content-bound host attestations, stale
  review checks and default closed-information policy. Frozen retrieval checks
  corpus identity and requested reaction participants; predictions cannot become
  measured evidence by supplying backend metadata.
- Connected environment, Agent Scientist schemas, local API and host-only
  `--science-config`. Public candidate pages omit outcomes; observation and shared
  retrieval budgets persist. Ranking predictions use one metered contract batch.
- Added version-2 scientific checkpoint identity/history checks. Changed configuration,
  rollback inconsistencies and legacy checkpoints reject instead of resetting
  resources. Late source results cannot retain discarded record IDs.
- Full regression: **698 passed; 92.71% branch-inclusive package coverage**.
  One existing Starlette/httpx deprecation warning. Separate review reproduced
  and verified fixes for replay allowance, source snapshot/query mismatches,
  discovery, counter history, multiplicity and quote dates; no remaining blocker
  identified in the reviewed scope.
- Actual offline smoke passed all eight configured fixture capabilities and five
  unavailable cases. Exported the versioned JSON tool/API contract. Network and
  subprocess operations were blocked inside the smoke. **Zero live LLM calls,
  model inference or new experimental measurements.**

Evidence: [contract and usage guide](SCIENTIFIC_TOOL_CONTRACTS.md),
[acceptance receipt](../artifacts/steps/srg-04/acceptance.json),
[smoke receipt](../artifacts/steps/srg-04/smoke-v2/receipt.json),
[exported tool contract](../artifacts/steps/srg-04/smoke-v2/tool-contract.v1.json).

Acceptance covers local software contracts, not predictor accuracy, comprehensive
source authentication, specialist benefit or new scientific improvement. Host
curation remains trusted; external weight/dependency identities may be unknown
until explicitly pinned and verified for a run. Full application workflows and
condition optimization policies remain later work. Final benchmark authorization
remains false under the unchanged protocol.

## SRG-05 acceptance (2026-10-27)

- Preserved the legacy breadth-first search and added an explicit best-first
  policy with shared-intermediate reuse, complete precursor obligations,
  directed-cycle checks, bounded deduplication and versioned prediction caches.
  Invalid candidates cannot fill the new policy's accepted-route quota.
- Added lightweight host status/cache identity accessors and local CLI policy
  selection. Submission actions are reserved; wall admission guards cannot
  guarantee submission after an in-flight timeout, which stays explicit.
- Full regression: **767 passed; 93.04% branch-inclusive package coverage**.
  Tests cover deeper/convergent synthetic graphs, missing branches, multiplicity,
  exclusions, quantities, cache identity/tampering, CLI execution and accounting.
- Completed 32 matched episodes: 8 development tasks (4 targets, both inventories)
  × 2 fixed policies × cold/shared-precomputed conditions. Both policies used
  48 admitted expansions per condition and found **0 accepted routes out of 8**.
  The predeclared rule therefore **retains breadth-first as the default**.
- All 96 real LocalRetro comparison calls succeeded. The frozen pool contained
  52 distinct query keys, with no conflicts, replay misses or late calls. No LLM
  calls, model training, private outcome reads or final evaluation occurred.
- Separate review checked all episode/decision hashes, aggregate metrics,
  selected inputs, source hashes and 24 model-related assets. Fixed late-call
  accounting, failure retention and deduplication-memory issues before freezing.
  No remaining blocker was identified for this implementation/pilot scope.

Evidence: [implementation and result guide](FIXED_SEARCH.md),
[acceptance receipt](../artifacts/steps/srg-05/acceptance.json),
[development comparison](../artifacts/steps/srg-05/development-v1/summary.json),
[default-selection decision](../artifacts/steps/srg-05/selection.json).

This is an accepted software and comparison deliverable, **not demonstrated
route-retrieval improvement**. Empty submissions cannot establish empirical
inventory compliance or chemical feasibility. The new policy remains explicitly
available, while broader performance and scientific model gains remain unproven.
Repeated public-bundle validation caused substantial common preparation overhead;
batch validation of a frozen snapshot is recorded for SRG-14. Earlier acceptance
receipts and the final-evaluation protocol remain unchanged.

## SRG-06 result (2026-10-27)

- Built a source-specific C–N screening-hit model, safe JSON artifact and optional
  `score_cn_conditions` tool with local CLI/API/environment integration. It ranks
  explicit candidate tuples; it does not predict isolated yield or full feasibility.
- Audited 11,328 source records and froze product-scaffold-separated training,
  development, calibration and assessment partitions before fitting. Seven
  configurations were compared; decisions were saved before assessment scoring.
- **885 tests passed; 93.34% branch-inclusive package coverage.** Real-model
  dispatch, abstention, CLI replay and checkpoint accounting passed. A separate
  source-record audit verified every assessment candidate and both sets of choices.
- The new Random Forest's primary top-1 regret was **32.24% versus 28.50%** for
  the selected ExtraTrees baseline: 3.74 pp worse, with gain interval
  [-9.35, +0.93] pp. Top-5 regret and Brier score improved, but the primary
  improvement gate **failed**. No default was replaced and no retuning followed.
- Source-specific evaluation and implementation are complete. **Scientific
  acceptance remains open; the accepted-step count remains 5/14.** The final
  benchmark, route-search gains and agent/specialist superiority remain unproven.

Evidence: [model card and failure analysis](CN_CONDITION_MODEL.md),
[step receipt](../artifacts/steps/srg-06/acceptance.json),
[aggregate experiment](../artifacts/steps/srg-06/experiment-v1/summary.json).

SRG-07 (Retrosynthesis Strategist) is the next implementation ticket. Its software
dependencies are available, but it must retain the baseline and cannot treat
this experimental model as scientifically promoted. Closing SRG-06's improvement
gate requires a new frozen study with untouched assessment evidence.

## User-directed SynthChem search integration (2026-10-27)

Implemented native Syntheseus A*, MCTS and the shared-proposal portfolio from
the audited SynthChem approach, with explicit local CLI/Python access. Existing
LocalRetro and AiZynthFinder bindings are selectable. This does not import the
original RetroChimera/template ensemble or enable a new LLM model.

**944 tests passed, 93.57% combined coverage.** The real AiZynthFinder pilot
generated three two-step inventory-complete predicted routes for each of two
hand-selected tasks. The existing best-first comparator also found three per
task and used fewer calls, so the legacy default remains unchanged. These
results demonstrate local multi-step generation, not independent chemical
validation, held-out superiority or closure of SRG-06's model gate.

See [integration, usage and results](SYNTHCHEM_SEARCH.md). Earlier step receipts
remain historical and unchanged; the accepted-step count stays 5/14. SRG-07 can
now use the native controller when implementing bounded Strategist orchestration.
