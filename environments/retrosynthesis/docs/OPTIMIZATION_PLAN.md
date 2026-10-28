# Next-phase implementation and benchmark plan

Status: **execution started; per-step acceptance is tracked in [PROGRESS.md](PROGRESS.md)**.
Baseline: local package 0.1.0, 255 passing tests, 90.86% coverage.
Scope: local execution; all research LLM roles use Agent Scientist's main-profile
model/provider. Existing chemistry models and new trained scientific predictors
remain permitted tools. No replacement LLM is introduced.

**Step 6 scope amendment (user request, 2026-10-27):** use an existing
pretrained scientific model now; the user will build a replacement later.
Completion of revised SRG-06 requires a versioned, replaceable local predictor,
actual inference through environment contracts, an honest development diagnostic
and independent implementation review. New-model training and its improvement
gate are deferred, not passed. The historical C–N negative result and original
acceptance receipt remain intact. The full held-out three-arm benchmark remains
in Steps 12–13. See [the public-model guide](PUBLIC_YIELD_MODEL.md).

Before changing delegation, complete the native-lifecycle compatibility gate
in [DELEGATION_COMPATIBILITY.md](DELEGATION_COMPATIBILITY.md). The new upstream
Hermes Advanced Delegation plugin depends on hooks absent from the inspected
Agent Scientist checkout; named role presets and full profile routing are
different implementation choices.

The requested outcome is an integrated, reproducible environment whose useful
improvements are demonstrated under declared constraints. Completing software
and demonstrating scientific improvement are separate acceptance decisions.
A specialist that does not help remains disabled. Missing measurements remain
a data limitation, not a successful validation.

## Approved SynthChem reuse plan (2026-10-27)

The user approved selective reuse of the audited local SynthChem snapshot and
resumed SRG-03. The fourteen tickets and their scientific acceptance gates remain
unchanged. Source hashes, exclusions and negative results are recorded in
[EXTERNAL_SYNTHCHEM_AUDIT.md](EXTERNAL_SYNTHCHEM_AUDIT.md). The source has no Git
revision; use the per-file SHA-256 manifest to pin the snapshot.

| SRG tickets | Selected source component | Adaptation and acceptance | Owner |
|---|---|---|---|
| 03, 11 | Campaign revision store and feedback provenance | Adapt atomic revisions and stale-write checks; add budgets, reservations, action IDs, deadlines and cancellation. Test interrupted writes, duplicates and restart without resource reset. | Runtime/integration maintainer |
| 04, 05, 07 | Shared proposal pool and search portfolio | Wrap behind our expansion contract; version caches by model/config/stock/evidence. Recompute validity and compare fixed search before Strategist use. | Tool/search maintainer |
| 04, 08, 10 | QUARC output normalization | Preserve intervals, scores, unknowns and provenance. Validate mock and real adapter contracts separately; prediction is not measurement. | Condition/tool maintainer |
| 06, 08, 10 | DoE and numeric GP/UCB response optimization | Bound compute and use eligible numeric factors. Keep training observations private, charge replay queries and evaluate held-out decisions before crediting improvement. | Scientific-model/condition maintainer |
| 09, 10 | Process comparison, route economics and procurement | Preserve units, scale, currency, timestamp and uncertainty. Catalog prices remain unverified estimates. Test declared quantity/cost scenarios. | Process maintainer |
| 09, 10, 13 | Impurity, chirality and stereochemical checks | Produce typed hypotheses bound to route content; measure false rejections as well as errors detected. Review supporting evidence separately. | Critic/validation maintainer |
| 12, 14 | Aggregate reports and reusable test cases | Preserve negative findings; rerun our own matched comparisons. Imported scores are not our results. | Benchmark maintainer |

Keep the copied source isolated. Adapt selected contracts or algorithms with
provenance and component-specific tests. Preserve SRG molecular identities and
evaluator isolation. Exclude answer-bearing retrieval, private training rows and
supplied route seeds from observations. Check license/attribution before copying
implementation text. Retain the main-profile resolver; SynthChem's hard-coded
LLM launcher is not used. Specialists require measured benefit before promotion.
The new scientific-model improvement and biocatalysis deliverable remain required.

User-directed update: native SynthChem A*/MCTS/portfolio controllers are now
implemented through SRG's environment boundary. See [the integration guide and
real two-step route pilot](SYNTHCHEM_SEARCH.md). One configured LocalRetro or
AiZynthFinder backend is used per run; the original dual-backend ensemble is not
reproduced. The Strategist can build on this controller without changing the
main-profile rule or treating graph completion as experimental success.

## 1. Preserve the baseline and define success

Owner: environment and benchmark maintainers. Dependency: none.

Save an immutable snapshot of current source, dependency versions, task inputs,
checkpoints, prompt versions and results. Preserve failures and the existing
Doyle evaluation. Do not overwrite earlier artifacts or disturb unrelated
working-tree changes.

Implementation: [baseline preservation](BASELINE_PRESERVATION.md) and
[protocol v1](PROTOCOL_V1.md). The local snapshot is checksum-anchored and
read-only by default, not storage that even its owner cannot alter.

Separate four questions: condition-choice quality, ranking a fixed candidate
pool, search from inventory to target, and the value of agent orchestration.
Record which changes affect which question. A yield predictor feeding a
heuristic is not a learned general feasibility model.

Write a versioned protocol before tuning: metrics, budgets, failure rules,
source-access rules, review rubric, test split and promotion criteria.

**Gate:** every later result identifies the exact baseline and protocol; no
experiment can change its primary objective after seeing final outcomes.

## 2. Curate a larger benchmark and seal the final evaluation

Owner: benchmark/data maintainer. Depends on 1.

Implemented candidate-cohort/data-isolation deliverable:
[BENCHMARK_DATA.md](BENCHMARK_DATA.md). The 10/20/50 route-target allocation now
exists with two inventory variants per target and separate condition cohorts.
Full final-run sealing still depends on development-selected configurations,
resource limits, statistical adequacy and review preparation in later steps.

Initial planning target: 10 smoke targets, 20 development targets and 50 locked
test targets. These are proposed sizes, not existing curated counts or a power
guarantee. Include short and multi-step routes, distinct reaction families,
convergent branches, stereochemistry and varied inventory restrictions.

Keep target analogues, source/patent families and repeated inventory versions
together when assigning partitions. Deduplicate reaction records and examine
overlap with known chemistry-model training sets. If checkpoint training data
are unavailable, report overlap as unknown. No claim that targets were absent
from the LLM's pretraining is possible from this audit alone.

Use separate evaluation tracks:

- Public reference-route recovery, with a pinned PaRoutes subset and stock.
- Source-reviewed inventory planning, with each step and its evidence scope
  independently checked. Alternative routes can be unresolved rather than wrong.
- Measured condition decisions, grouped by independent substrate/product and
  experimental source. This is not the same test as route discovery.

[PaRoutes](https://github.com/MolecularAI/PaRoutes) provides routes, stock and
route-quality/diversity evaluation. Its top-k metric measures reference-route
recovery; it does not by itself establish chemical feasibility.

The already inspected Doyle test is **development/regression evidence for
future optimization**, not a new untouched final test. Obtain a separate
audited dataset or source group for the next confirmatory claim. Inspect suitable
measured records in [ORD](https://docs.open-reaction-database.org/en/latest/),
whose schema represents inputs, conditions, workups, outcomes and provenance;
membership in a database does not guarantee complete labels for a chosen task.

Inventory perturbations need precise labels. Removing a required stock item
may invalidate a reference route without proving no alternative synthesis exists.
Use explicitly bounded synthetic fixtures to test guaranteed infeasibility;
label real searches without a recovered route as unsolved under the budget.

**Deliverables:** task manifest, source/label manifest, split checksums, overlap
report, expected constraints and a sealed evaluator directory/process.
**Gate:** no test labels in agent observations, retrieval indexes, caches or
training inputs; group leakage checks pass. Insufficient data reduces the claim,
not the quality requirements.

## 3. Fix execution efficiency and protect final submission

Implemented local runtime gate: [RUNTIME_RECOVERY.md](RUNTIME_RECOVERY.md), with
acceptance evidence in [PROGRESS.md](PROGRESS.md). Live-provider and scientific
performance validation remain distinct later gates.

Owner: Agent Scientist integration maintainer. Depends on 1; test with smoke data.
Files: `agent_runner.py`, `agent_bridge.py`, `environment.py`, persistence helpers,
CLI entry points and their tests. Adapt the SynthChem revision-store pattern
without importing its launcher or benchmark labels.

The observed specialist failure is a priority: it consumed substantial tokens
but did not submit. Implement request-level settlement against confirmed provider
usage without double counting; retain conservative reservations for unresolved
requests. Validate bookkeeping on completed, failed and retried calls.

Use compact structured specialist reports and state deltas instead of copied
conversation histories. Reserve a configurable portion of the shared allowance
for the main decision and final submission; select the reservation on development
tasks. Stop admitting optional work when the remaining budget cannot cover it.
Do not secretly give the specialist arm extra resources or fabricate an agent
submission through an unreported host fallback.

Use the same scoped timeout/retry policy for comparable arms. Add local persistent
episode storage, idempotent action IDs, bounded cancellation and restart/resume.
Resuming preserves consumed resources and the declared deadline policy.

**Gate:** no budget reset on resume; no duplicate side effects; every failure is
recorded; resource limits remain enforced; a selected end-of-run policy behaves
as specified in integration and end-to-end failure tests.

## 4. Standardize scientific tools and evidence contracts

Implemented local contract gate: [SCIENTIFIC_TOOL_CONTRACTS.md](SCIENTIFIC_TOOL_CONTRACTS.md).
Acceptance receipts and limitations are tracked in [PROGRESS.md](PROGRESS.md).

Owner: environment/tool maintainers. Depends on 2–3.
Reuse existing adapters and REBOLT workers before adding model implementations.

Create a capability registry describing input/output schema, applicable chemistry,
evidence type, version, timeout and usage accounting. Extend environment actions
for the tools actually supported: bounded source retrieval, forward consistency,
condition observation, impurity hypotheses, process comparison and biocatalytic
retrieval. Unsupported tools return an explicit unavailable result.

Separate ordinary tool output from host-verified evidence. Source records include
document identity, exact location, reaction participants, stereochemistry,
conditions scope and retrieval timestamp. Use atom mapping and forward predictions
as checks, never as experimental proof. Full atom balance can remain unknown
when datasets omit coproducts; record that rather than assuming a balance.

Define source-access protocols before evaluation. In a closed-information track,
reference answers and outcome labels are hidden. In an evidence-retrieval track,
all methods receive the same frozen searchable corpus and retrieval allowance;
report retrieval-assisted performance explicitly.

**Gate:** uniform result/error contracts; model scores cannot become measured
evidence; aliases, invalid structures, malformed results and stale evidence are
covered by contract tests. No arbitrary evaluator-file access is available.

## 5. Build a stronger fixed-search baseline

Implemented and validated: [FIXED_SEARCH.md](FIXED_SEARCH.md). The declared
development pilot found zero accepted routes for either policy; no promotion
occurred. The legacy default and explicitly selectable new policy are both retained.

Owner: search maintainer. Depends on 2 and 4. Extend `planning.py`.

Retain the current breadth-first search as a regression baseline. Add a bounded
best-first or beam-search policy with an explicit scoring rule, shared intermediate
reuse, route deduplication, full precursor obligations and inventory-aware pruning.
Invalid proposals must not fill the search's successful-route quota.

Cache deterministic expansion results by chemical identity and relevant model,
template and configuration versions. Include stock/evidence snapshots when the
tool result depends on them. Compare identical cold-cache and shared-precomputed
conditions separately; account for precomputation and cache hits consistently.

The primary fixed/main/specialist comparison uses the same expansion backend,
tools and checkpoints. Keep AiZynthFinder as an additional reference baseline
when its expansion policy differs; do not attribute generator differences to
agent reasoning.

**Gate:** deeper and convergent fixtures pass; no accepted stock/quantity
violations; a development comparison reports quality, duplicate work, expansions
and elapsed time for old and new fixed policies. Keep the stronger honest baseline.

## 6. Improve and validate the scientific model

Current source-scoped experiment and pre-fitting decisions:
[CN_CONDITION_MODEL.md](CN_CONDITION_MODEL.md). The existing Doyle artifact and
reserved final source remain unchanged; internal assessment is development evidence.

Execution result (2026-10-27): implementation and fixed evaluation complete;
the candidate failed the primary improvement gate (top-1 regret 32.24% versus
28.50% baseline). Preserve the negative result and baseline. Scientific acceptance
remains open; no secondary metric substitutes for this gate.

Owner: scientific-model maintainer. Depends on 2 and 5.
Files: existing `ranking.py`, `model_training.py`, `condition_domain.py` plus
source-specific `cn_data.py`, `cn_model.py`, `cn_training.py` and tool integration.

Start with the observed gap: top-1 improved slightly while top-5/top-10 worsened.
Choose the decision objective before fitting. Compare simple condition means,
the current ExtraTrees model and a small, bounded set of justified alternatives.
Use separate training, development and calibration groups where data support it;
reserve new final groups for one confirmatory evaluation.

Expand yield prediction only to reaction domains with audited measured labels.
Keep domain-specific models or abstention when pooling is unjustified. Evaluate
decision regret, top-k selection, yield error, calibration and performance on
unseen components. Predicted bands need coverage tests; ensemble variation alone
is not calibrated uncertainty.

If sufficient labels support a new route-ranking model, define its target first:
reference-route retrieval, reviewed route preference or a measured decision
outcome. Train on decision-time features only. Missing literature support is not
a failed-reaction label. Plausible unreviewed alternatives remain unlabeled;
synthetic corruptions test constraint rejection, not experimental feasibility.

Evaluate model-on/model-off on identical candidate pools before changing search.
Then separately test the best eligible model in route search. Export a safe local
artifact, data/split hashes, model card and versioned callable contract.

**Gate:** improvement on the preregistered held-out decision metric, with losses
and uncertainty reported; correct abstention outside scope. If no improvement is
demonstrated, retain the earlier model and state the negative result.

## 7. Implement a purposeful Retrosynthesis Strategist

Owner: specialist/controller maintainer. Depends on 3–6.

Trigger it when search stalls, repeats equivalent routes, or cannot resolve
inventory obligations. Inputs are the frontier, unresolved materials, prior
failed branches, evidence gaps and remaining resources. Return a typed plan:
candidate route IDs, next expansion targets, alternative disconnections, relevant
constraints and a bounded action allowance.

The main controller validates and executes allowed actions. The strategist must
not edit inventory, supply trusted outcomes or relax constraints. Preserve both
successful and failed alternatives. Cheap deterministic decisions should stay in
the search policy rather than requiring another LLM call.

**Gate:** main-plus-strategist versus main-only on paired development tasks.
Retain it only if it improves supported route retrieval or reaches comparable
quality with fewer resources. Fluent explanations are not a success metric.

**Execution status:** the optional trigger-based implementation and the frozen
four-target, three-arm development pilot are complete. The assisted arm retrieved
one inventory-compliant reference route versus none for main-only, with lower
aggregate recorded token use. Four targets and one run per arm do not establish
the promotion gate. Main-only remains the default; SRG-07 remains scientifically
open, with [results, limits and reproduction](STRATEGIST.md) retained. SRG-08's
subsequent comparison is recorded below; this does not waive the later specialist
ablation, repeated-run and final benchmark requirements.

## 8. Implement a purposeful Condition Optimisation Scientist

Owner: condition workflow/specialist maintainer. Depends on 4 and 6.

Trigger it for a route step with an applicable prediction model or a measured
condition-study task. It returns allowed candidate conditions, cited support,
predictions with domain/uncertainty labels and the next observation request.

Expose an ask/observe/update loop through the environment. A measured-data replay
reveals only the queried records; unqueried yields and the best possible answer
remain evaluator-only. An unmeasured combination cannot be assigned a synthetic
experimental outcome. Charge every observation to a separate declared budget.

Compare fixed/random selection, a competent fixed optimization policy, main-only
and main-plus-condition-scientist with identical starting observations, candidate
space, predictor and observation count. Keep predictions and measured replay
observations distinct throughout.

**Gate:** lower held-out decision regret or a better observed outcome at the
same observation budget across independent groups; appropriate abstention on
unrelated chemistry. Otherwise the specialist remains experimental.

**Execution status:** local implementation and a frozen 96-episode comparison
are complete. All runs submitted, and all 32 main-agent conversations finished
normally. Mean regret was 4.7498 percentage points for main and 4.2315 for the
assisted arm, but both paired assisted wins occurred where the advisor failed.
The fourteen successfully delivered consultations produced thirteen ties and
one loss. This post-hoc result does not establish benefit from valid advice.
Public-model ranking scored 4.5699 without LLM requests. Two failed consultations
retain unconfirmed token reservations; exact assisted token use is unknown.
The guide records every arm, failure, resource total and individual source
review. The studies share one reused development publication, so the specialist
remains experimental and its scientific gate stays open. See
[implementation, results and reproduction](CONDITION_SCIENTIST.md).
SRG-09 execution is recorded below; the accepted count was 6/14 at this gate.

## 9. Implement a purposeful Route Critic

Owner: validation/specialist maintainer. Depends on 4 and 7–8.

Give it route structure, tool findings and accessible sources. It returns typed
findings with route/step ID, category, severity, source and requested revision.
Categories include unsupported transformations, missing materials, stereochemistry,
quantity conflicts, incomplete conditions and model-domain mismatch.

Deterministic errors can block acceptance. Evidence uncertainty requests review
or abstention; it is not automatically proof of impossibility. The critic may
request a bounded recheck or revision, and the controller records its effect.
Invoke it on a shortlist or specific uncertainty rather than on every expansion.

Test it with known-valid controls and deliberately corrupted records. Measure
both errors caught and valid candidates incorrectly rejected. Its opinions never
become the independent benchmark labels.

**Gate:** fewer invalid/unsupported submissions without an unacceptable loss of
source-supported routes, under the same shared budget as main-only.

**Execution status:** implemented locally with shared `review_routes`, typed
main-profile advice, bounded rechecks and persistent shared accounting. The
frozen 48-episode comparison completed: all three arms achieved 16/16 exact
selections, retained 24/24 controls, and submitted zero invalid/unsupported
records. Assisted tied main in all sixteen pairs while increasing model requests
from 52 to 71. Only three critic reports were accepted; eight were rejected for
fact route/step mismatches and five hit provider stream timeouts. Main completed
all conversations. Seven request usages remain unsettled across the two agent
arms; retained reservations remain charged. No selection improvement was shown.

Independent source and ledger audits passed; 1,767 tests passed with 94.44%
coverage. The critic remains experimental and main-only stays default. Future
work must improve report binding/delivery under a new frozen diagnostic and
establish value on broader independent problems. The original pilot remains
immutable. See [implementation, results and reproduction](ROUTE_CRITIC.md).
The accepted count was 6/14 at this gate. SRG-10 integration acceptance is recorded below.

## 10. Integrate all five application workflows

Owner: portfolio maintainers. Depends on 4; domain implementations can proceed
alongside 6–9. Extend `portfolio.py`, adapters, schemas and environment actions.

| Application | Required improvement | Evidence/measurement gate |
|---|---|---|
| Inventory planning | Multi-step, convergent, quantity-aware alternatives and explicit restrictions | Source-reviewed top-k routes, inventory/quantity compliance and search cost |
| Conditions | Stateful observation loop tied to route steps | Group-held-out measured decisions at equal observation budgets |
| Impurities | Route-step hypothesis generation with source-matched measured annotations | Precision/recall only where annotation coverage supports them; concentrations require quantitative measurements |
| Process selection | Common production scale, amounts, dated prices/currency, uncertainty and equipment constraints | Audited cost calculations and multiobjective comparisons; no savings claim from illustrative numbers |
| Biocatalysis | Documented transformations linked to substrate, enzyme, cofactors and available conditions | Exact versus analogue retrieval; measured activity/yield claims only with matching evidence |

Incomplete impurity annotation is not an exhaustive negative set. Document
detection/reporting limits. Preserve the current T5 negative finding.

[Rhea](https://www.rhea-db.org/) supplies curated biochemical reaction records.
Use those to locate evidence; a reaction entry alone does not establish operating
conditions or a suitable enzyme preparation. Biocatalysis here concerns benign
small-molecule transformation selection, not biological agent engineering.

For process yield, do not average step yields or multiply arbitrary branch
predictions. Compute material balances only with the required quantities and
stoichiometry, and clearly distinguish estimates from measured route outcomes.

**Gate:** each path is callable through the same local environment, has an
end-to-end test and its own result/evidence report. An application lacking required
measurements remains scientifically unvalidated, even when its integration passes.

**Execution status: accepted for local integration.** All five paths now use
stored routes and exact route-step references through `application_report` and
metered observation, prediction and source-retrieval actions. The frozen example
pack produced five reports and submissions with 24 successful actions, no
truncation and zero LLM calls. It included two reused public Doyle observations,
one successful existing impurity-checkpoint inference and one Rhea/IUBMB source
retrieval. All 377 frozen inputs passed preflight/postflight checks.

Full regression passed **2,092 tests, 24 warnings, 94.95% branch-inclusive
coverage**. Separate code, runner and source audits passed with no unresolved
HIGH/MEDIUM code findings. Source review verified bindings and declared quantity/
cost calculations; it is not external chemist or experimental validation.

The inventory/process examples remain illustrative; condition records are reused
development evidence; no measured impurity assay supports the model outputs;
biocatalytic identity does not establish activity or process feasibility.
Scientific measurement gates remain unvalidated. Step 10 satisfies its separate
integration gate, historically bringing accepted steps to **7/14**. Steps
7–9's promotion gates remain open and main-only remains default. See the
[application guide](APPLICATION_WORKFLOWS.md),
[actual execution summary](../artifacts/steps/srg-10/execution-v1/runs/summary.json)
and [source audit](../artifacts/steps/srg-10/review-source.md).

## 11. Implement adaptive orchestration and the Small Molecule handoff

Owner: controller/integration maintainer. Depends on 3 and 7–10.

Use structured shared state. The main agent chooses among deterministic search,
an eligible specialist, further evidence gathering and submission. Triggers,
budgets, stop conditions and reports are explicit and versioned. Specialist use
must depend on a measured need, not a mandatory three-session chain.

Connect the existing typed Small Molecule handoff to complete local episodes.
Preserve candidate identity and upstream provenance. Return route availability,
evidence gaps and costs to candidate selection. Evaluate this feedback with and
without route information on the same candidate set and budget; if no independent
downstream labels exist, report only integration behavior, not cross-pod gains.

**Gate:** every action and specialist call is attributable and metered; callbacks
cannot modify hidden data or reset budgets; candidate provenance survives the
full handoff; a predictable final report is produced for success and failure.

**Execution status: accepted for local orchestration and handoff integration.**
Versioned host policies, shared
main/advisor accounting, recovery bindings and durable candidate handoff feedback
are implemented. The pilot completed ten route submissions and eight native
conversations across two reused public development cases and five arms. All arms
selected the same route per case; candidate feedback changed selection in none
of the five same-pool comparisons. Two critic consultations yielded one accepted
and one rejected report. Other advisors were ineligible, and default adaptive
main admitted none. This supports integration, not advisor or cross-pod gains.

Full regression passed 2,315 tests with 24 warnings and 95.04% branch-inclusive
coverage; the build and separate code review passed. Pilot accounting records
31 requests, 249,723 confirmed tokens, 60,420 reservation units and two unsettled
requests after recovered provider failures. Exact total usage and monetary cost
remain unknown. All 1,623 frozen files passed integrity verification; private and
final labels remained closed. The role-prompt arm shares substantive role
instructions but differs in context and timing, so it is not an exact causal
control for delegation. The separate execution audit verified all ten event
chains, candidate/source bindings, resource receipts and feedback comparisons;
it is automated source-consistency review, not external chemist validation.
**8/14 steps are accepted and Step 12 is next.** Main-only remains default. See the
[orchestration and handoff guide](ORCHESTRATION_HANDOFF.md) and
[pilot summary](../artifacts/steps/srg-11/pilot-v1/summary.json),
[execution audit](../artifacts/steps/srg-11/review-execution.json) and
[acceptance receipt](../artifacts/steps/srg-11/acceptance.json).

## 12. Run development ablations and freeze the chosen configuration

Owner: benchmark maintainer. Depends on 5–11.

Compare the strong fixed workflow, main-only, main-plus-strategist,
main-plus-condition-scientist, main-plus-critic, all specialists and adaptive
specialist selection. Add a single-agent control with equivalent role instructions
and resource allowance, so extra prompting is not mistaken for a multi-agent gain.
Use staged screening to avoid spending the full budget on every weak variant.

Compare the learned model on/off using the same candidate pools and then the same
search tasks. Keep tools, evidence corpus, inventory, runtime settings and aggregate
caps matched. All specialist messages and retries count. Do not require a
deterministic baseline to burn unused LLM tokens merely to equalize consumption.

**Gate:** select configurations from development results only. Freeze prompts,
models, data, cache policy, timeouts and resource limits before opening final
test outcomes. Main-only remains default if specialists provide no justified gain.

User-directed final-evaluation amendment (2026-10-27): prepare and test both
budgeted and unbudgeted execution during development. Unbudgeted execution must
actually disable research-budget admission and budget-triggered finalization;
setting a larger finite call limit is not an unbudgeted implementation. Verify
natural submission, search exhaustion and interrupted-run reporting before
freezing either configuration.

## 13. Run the locked benchmark and blinded source review

Owner: benchmark/review maintainers. Depends on 12.

Required final arms: strongest fixed workflow, main Agent Scientist and the
frozen specialist-enabled configuration. Initial plan: 50 locked targets × 3
runs × 3 arms × 2 resource regimes = **900 episodes** if that sample size is
retained: 450 budgeted and 450 unbudgeted. Independent group count and final sample size
must be decided from the development variance and available curated evidence,
before examining final outcomes. Repeated seeds are not independent new chemistry.
Record seeds where the tools support them and explicit repeat identifiers for
LLM calls without reproducible seed control. Randomize arm order within task
blocks to reduce time-of-day/provider-load effects. Match hardware allocations,
thread limits and predictor settings, and record actual resource use.

**Both resource regimes are required by the user (2026-10-27):**

| Regime | Execution and comparison |
|---|---|
| Budgeted | Give all three approaches matched research-resource ceilings; include every specialist call and retry in the shared allowance. |
| Unbudgeted | Remove research caps on model calls, tokens, environment actions, expansions and episode wall time. Let the policy reach its declared natural stopping condition, including submission or exhausted search. Record actual use throughout. |

Keep targets, inventory, scientific constraints, allowed evidence, tool/model
availability, output top-k, hardware allocation and source-review rules identical
across regimes. Every LLM role continues to use Agent Scientist's main profile.
Run each episode in isolation; do not carry decisions or hidden-answer feedback
between regimes. Commit all final decisions in both regimes before opening any
final evaluation answers.

Report the two regimes separately and compare their quality/resource tradeoffs.
Unbudgeted runs are not equal-compute comparisons. Record declared per-tool
timeouts and infrastructure/provider restrictions in both regimes. An external
interruption or imposed resource ceiling must be recorded as an interrupted or
censored run, not as natural completion or a completed unbudgeted run. Report
nontermination and failures; do not silently replace them with successful retries.

For the budgeted regime only, at the existing 600-second cap, 450 episodes have a worst-case serial episode
allowance of **75 hours**, excluding setup/review. For two LLM arms at the existing
200,000-token cap, 300 runs permit up to **60 million tokens**. These are caps,
not forecasts or an instruction to spend them. Run a small smoke pilot, measure
actual use, bound concurrency and freeze feasible budgeted limits. The unbudgeted
regime has no finite worst-case runtime/token forecast; record actual consumption
and any externally imposed campaign interruption explicitly.
Development ablations, model training and evaluation overhead are counted separately.

Save ordered decisions before evaluating hidden outcomes. Blind source reviewers
to arm/score, randomize review order and deduplicate by chemical content. Use the
same main-profile model in isolated review contexts with independently retrieved
source records. Check all steps of every submitted top-k route. Unknown support
remains unresolved; a reference mismatch is not a negative chemistry label.
Record disagreements and audit a preselected sample of rejections as well as
acceptances. This is automated source review, not human review or an independent
model family. Its systematic uncertainty remains part of the report.

| Metric | Required interpretation |
|---|---|
| Inventory-closed targets | Structural availability only, separate from quantities and feasibility |
| Evidence-supported targets at k | At least one route passes declared gates and all step-level support requirements; no new experiment claimed |
| Reference top-1/top-5 | Recovery of a known reference route, separate from support for alternatives |
| Validity and quantity compliance | Report violations and unknown quantities separately |
| Ranking quality | Rank of supported/reference candidates; judged coverage and unresolved alternatives disclosed |
| Condition decision regret | Difference from best recorded candidate within the measured evaluation set |
| Search efficiency | Expansions and scientific calls to a qualifying route; unsuccessful runs remain in accounting |
| Resources | CPU/GPU allocation and usage, wall time, calls, actual/reserved tokens, retries, cache behavior and review overhead |
| Cost | Only comparable sourced estimates; no invented prices or free inference assumptions |

Report paired changes, group-level confidence intervals, quality-versus-resource
curves, timeouts, empty submissions and negative results. Cluster uncertainty by
independent target/source family, not correlated rows or repeated seeds.

Proposed promotion rule to freeze before final testing: a practically useful
increase in source-supported top-5 rate (initial proposal: at least 5 percentage
points with a paired interval excluding zero), **or** at least 20% fewer scientific
expansions at non-inferior quality (initial tolerance: 5 percentage points).
No increased hard-constraint violations are allowed; report other resource
tradeoffs rather than calling fewer expansions universally cheaper. These are
proposed decision thresholds, not expected results or guaranteed statistical power.
If intervals are inconclusive, report that or use a separately prespecified new
cohort; do not tune and repeatedly retest the same sealed set.

## 14. Optimize measured bottlenecks and verify the full local release

Owner: environment and release maintainers. Depends on 12; final scientific
claims must correspond to the frozen version evaluated in 13.

Profile development runs for repeated expansions, model loading, serialization,
unnecessary context, evidence retrieval and scheduler overhead. Optimize measured
bottlenecks through model reuse, bounded batching, caching and compact observations.
Show output-equivalence checks for optimizations intended to preserve decisions.
Any decision-changing optimization requires a new evaluation version, not a silent
replacement of the already tested system.

Run unit, integration and end-to-end tests with at least 80% coverage. Exercise
malformed chemistry, cycles, missing co-reagents, evidence spoofing, domain errors,
deadlines, provider failures, shared budgets, resume and unavailable predictors.
Verify clean-environment reproduction, plugin discovery, CLI workflows, local API,
all five applications and handoff behavior.

Produce a local release manifest, benchmark table, reviewed route cases, model
card, failure analysis, ownership/version records and reproducible commands.
Label each capability as implemented, execution-tested, scientifically evaluated
or supported by measured improvement. Those labels must not collapse into one
generic "complete" flag.

## One-week execution sequence

| Day | Main deliverables |
|---|---|
| 1 | Freeze baseline/protocol; audit and partition data; measure smoke-run resource use |
| 2 | Fix accounting/context/finalization; strengthen tools, evidence contracts and fixed search |
| 3 | Develop the scientific model and structured specialist contracts on development data |
| 4 | Integrate application loops and handoffs; test failure handling and domain limits |
| 5 | Run development ablations, profile bottlenecks and freeze the final configuration |
| 6 | Run locked comparisons and separate source review with bounded concurrency |
| 7 | Finish evaluation, reproduce, test and issue the evidence-qualified local release |

This is a scheduling target, conditional on usable data, runtime capacity and
LLM access. Data curation, experimental labels and statistical confidence cannot
be guaranteed by a calendar deadline. If a lane lacks measurements, finish and
test its implementation while explicitly leaving its scientific gate open.

## Ordered implementation tickets

Statuses are tracked in [PROGRESS.md](PROGRESS.md): SRG-01 through SRG-05 are
accepted within their documented scopes; revised SRG-06 is accepted for existing
pretrained-model integration. Custom-model development is deferred and the
original improvement gate has not passed. SRG-07 implementation and its small
development pilot are complete, with its scientific promotion gate still open.
SRG-08 implementation and the 96-episode development comparison are also
complete; scientific promotion remains open. SRG-09 implementation and its
48-episode development comparison are complete without a demonstrated specialist
benefit. SRG-10 is accepted for five locally executed application integrations;
its scientific measurement gates remain unvalidated. SRG-11 is accepted for local
orchestration and candidate handoff integration after the native pilot and code/
execution audits. The accepted-step count is **8/14** and SRG-12 is next.
Ownership refers to responsibilities, not newly created
research agents or assumed staffing.

| Ticket | Work | Depends on | Completion artifact |
|---|---|---|---|
| SRG-01 | Baseline and protocol freeze | — | Baseline manifest and preregistered metrics |
| SRG-02 | Benchmark curation and leakage audit | 01 | Split/source manifests and sealed evaluator |
| SRG-03 | Runtime, budgets and recovery | 01 | Accounting/failure tests and smoke receipts |
| SRG-04 | Tool and evidence contracts | 02,03 | Capability registry and integration tests |
| SRG-05 | Strong fixed search | 02,04 | Search comparison and regression cases |
| SRG-06 | Existing pretrained model integration (revised scope) | 02,05 | Pinned replaceable predictor, real inference, diagnostic, model card and review; custom model deferred |
| SRG-07 | Strategist contract | 03–06 | Implemented typed plan and completed development comparison; promotion remains open |
| SRG-08 | Condition scientist loop | 04,06 | Implemented measured-feedback loop and 96-episode comparison; promotion remains open |
| SRG-09 | Critic contract | 04,07,08 | Implemented typed critic and 48-episode comparison; promotion remains open |
| SRG-10 | Five integrated applications | 04 | Accepted: five actual local reports, regression and source review; scientific measurement gates remain open |
| SRG-11 | Adaptive controller and candidate handoff | 03,07–10 | Accepted: metered orchestration, ten-episode pilot, regression and code/execution audits; scientific gain unproven |
| SRG-12 | Development ablations and selection | 05–11 | Frozen configuration and negative findings |
| SRG-13 | Locked comparison and source review | 12 | Paired results, intervals and reviewed cases |
| SRG-14 | Performance verification and local release | 12,13 | Reproducibility/acceptance manifest |
