# SRG-07 Retrosynthesis Strategist

The optional `main_strategist` method adds an isolated, metered advisory context
to the main Agent Scientist session. It is intended to help when observed
search behavior stalls, repeats equivalent proposals or leaves inventory
obligations unresolved. Main-only remains the default. The legacy `specialists`
method remains a separate comparison and is not silently replaced.

Creating a specialist does not establish that delegation improves route decisions.

## Research basis

[Syntheseus](https://microsoft.github.io/syntheseus/stable/cli/search/) provides
fixed Retro* and MCTS search configurations for comparison. The
[RetroAgent paper](https://arxiv.org/abs/2607.14512) investigates structured
search memory containing explored routes and available alternatives. These
motivate testing a bounded advisor grounded in observed search state. They do
not establish an advantage for our implementation or authorize changing the
user's main-profile model. Our experiment isolates the advisory context while
preserving the main conversation and tool schemas.

## Local use

Use the same main profile, task, inventory and chemistry runtime as main-only.
Change only `--method`:

```bash
.venv/bin/python -m synthesis_route_gym agent \
  --task PATH_TO_TASK.json \
  --method main_strategist \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci \
  --model-calls 24 --episode-dir artifacts/reproduction/strategist-episode \
  --output artifacts/reproduction/strategist.json
```

Runtime variables are defined in the [README](../README.md). The task file
supplies shared action, expansion, wall-time and token limits. Scientific model
flags, including `--reaction-yield-model`, work as before and do not change
the coordinating LLM.

Resume using the same command with `--resume`. Changing method, main profile,
scientific configuration, budgets or implementation identities refuses
incompatible resume. Use a new episode directory for a new experiment.

## Advice and authority

The host observes the main session's allowed tool results. Its deterministic
trigger and bounded context use those observations, not hidden answers. The
advisory context receives relevant frontier/proposal information, route
identities, inventory observations, prior failures, constraints and remaining
resources. Incomplete observations remain incomplete; the specialist gains no
filesystem, terminal, web or evaluator access.

Triggers cover two consecutive failed/repeated/no-new expansion outcomes,
equivalent inspected routes after expansion, or an observed inventory gap
(a missing-material assessment after expansion, or checked missing frontier
stock after at least two expansions). Bounded expansion observations made before
the first inspection are retained and replayed once the host target is known.
Unknown or exhausted expansion allowances suppress consultation. The state and
context are limited to 20 KB, with explicit truncation and saturation handling.

Advice must parse as the declared typed plan. The host checks identities,
context binding, allowed expansion targets and the bounded action allowance.
Malformed, stale or unauthorized plans are recorded as rejected proposals.
Advice returns to main in `strategist_advice` alongside the original tool
observation. Main chooses and executes ordinary environment actions. Advice
does not automatically create a route or submission, and main can ignore it.

The `srg-strategist-plan-v1` record contains `context_sha256`,
`candidate_route_ids`, `next_expansion_targets`, `alternative_disconnection_ids`,
`relevant_constraint_keys`, `action_allowance`, `rationale` and
`evidence_status: agent_proposal`. Its allowance permits at most two recommended
expansions, within remaining resources; it grants no additional budget. Empty
advice with zero allowance is valid. JSON must be an object without duplicate
keys, extra fields or surrounding prose/code fences.

The specialist cannot edit stock, relax constraints, introduce trusted outcomes
or assert experimental success. Suggestions retain `agent_proposal` status.
Route validation, scientific prediction and source evidence remain separate.
A useful explanation alone is not a benchmark success.

## Model, budget and persistence

One consultation is allowed per episode, with one model request and zero tools.
It uses the resolved main-profile model and provider. Existing request fences
block routing changes and fallbacks; there is no `--strategist-model` option.
The specialist cannot recursively delegate or execute its suggestions.

Calls share the main ledger and deadline. Admission requires at least
`max(3, finalization_model_calls + 2)` remaining model calls: one for advice,
one for the main action round and the configured submission reserve. It also
requires the finalization-tool reserve plus two tool calls, conservative
prompt/output token capacity and the wall-time reserve.
Resource accounting includes successful, failed and interrupted advice.

The `srg-agent-runtime-strategist-v1` checkpoint contains `strategist` state with
schema `srg-strategist-runtime-v1`: observer, consultation, runs and delivery
state. Consultation
status is `pending`, `accepted`, `rejected`, `failed`, `interrupted` or
`skipped_budget`; observer failures can produce `disabled_observation` without
interrupting the main session. Admission is persisted before the request. A pending
consultation is consumed as interrupted on resume, with no automatic retry;
completed advice can be redelivered through later observations.

Advice is delivered once during an uninterrupted session. On resume, accepted
or interrupted advice may be delivered once again without another specialist
request. Durable advisor records retain bounded context, its prompt hash and
bounded response rather than raw conversation messages.

Results retain main-stage `runs` and add `strategist_runs` and
`strategist_state`. Aggregate usage includes advisor usage separately, avoiding
double settlement. Main's conversation, prompt and tool schema remain stable;
the treatment adds the validated advisory observation.

## Why the existing metered runner is retained

The Agent Scientist checkout was audited at commit
`062351dd048c142840f78ea198f22417d983ccda`. Its public native lifecycle lacks
the profile/provider, executor and shared-ledger injection required here. It
also rejects some per-launch timeout/tool controls and uses process-local
handles. Hermes' advanced-delegation registration interface is absent.

This feature therefore uses `NativeAgentBackend` for an isolated role context
under verified model and accounting fences. It is not Hermes cross-profile
delegation or a completed native-lifecycle migration. See the
[delegation compatibility audit](DELEGATION_COMPATIBILITY.md).

## Development comparison and acceptance

The [frozen plan](../artifacts/steps/srg-07/development-v1/plan.json) selected
the four smallest full-stock development targets by heavy-atom count, with a
task-ID hash tie-break and no reference-answer inspection. Each target receives
fixed best-first search, main-only and main-plus-Strategist, one run per arm.
Agent order alternates by task. Each arm has the same 40-action, six-expansion,
240-second, 200,000-token and top-three-route caps; the agent arms share an
eight-model-call cap. LocalRetro is the common proposal source, with no shared
cross-run proposal cache. Recorded agent calls use main-profile `gpt-6-sol`
through `openai-codex`; these are frozen observed values, not new model overrides.

All decisions are committed before source scoring. The evaluator verifies the
commitment and reads only the selected development task's private reference;
final labels remain sealed. Deterministic graph/inventory acceptance, exact
reference-route recovery and independently supported chemistry remain separate.
Actual resource use differs despite equal caps. Wall time is descriptive because
host load is not isolated. Tokens are recorded usage, not a monetary cost claim.

The original execution used a two-remaining-call advisory guard. A correctness
amendment declared before outcome scoring raised it to the three-call minimum
described above. All three observed admissions had three, four or five calls
remaining, so the correction changes none of those eligibility decisions. The
one remaining task did not invoke the advisor. The
[compatibility audit](../artifacts/steps/srg-07/development-v1/guard-compatibility.json)
preserves the original source, hashes and actual contexts. It does not attribute
any performance improvement to the correction or claim all unobserved behavior
is equivalent.

The 12 runs completed their environment submissions, including empty shortlists.
Their [recorded comparison](../artifacts/steps/srg-07/development-v1/summary.json)
is:

| Metric across four targets | Fixed best-first | Main-only | Main + Strategist |
|---|---:|---:|---:|
| Inventory-compliant reference-route retrieval in top 3 | 0/4 | 0/4 | 1/4 |
| Deterministically accepted submitted routes | 3 | 5 | 5 |
| Model requests | 0 | 32 | 30 |
| Recorded/charged tokens | 0 | 373,923 | 291,814 |
| Expansion requests | 20 | 13 | 13 |
| Environment actions | 27 | 48 | 41 |
| Total elapsed seconds | 199.13 | 415.96 | 384.00 |

The paired retrieval comparison has one win and three ties. All arms had zero
top-1 reference hits; the assisted match appeared at rank 2. The evaluator's
general cutoff is five, but this pilot submitted at most three routes, so no
fourth/fifth candidate contributed. The advisor was invoked three times and
returned three valid plans; one of the four targets did not trigger it.
The token difference is 82,109 fewer in the assisted arm, with no
unsettled token reservations. These are observations from this pilot, not an
established efficiency or scientific advantage. Main-only also had five
deterministically accepted routes, and the fixed workflow used no LLM tokens.
Only one consultation was followed by expansion of a recommended target. That
request overlap does not establish causality, and the one recovered reference
route does not prove that its consultation caused the retrieval difference.

The summary's `failed_runs` field counts incomplete **model conversations**:
four main-only and three assisted conversations reached their request allowance
without a normal final narrative. It does not mean missing environment
submissions; all 12 runs submitted, and submitted routes remain in scoring.
No submitted route is marked scientifically solved. Reference connectivity alone
does not establish chemical feasibility, and no independent experimental
validation was performed.

A separate [individual route/source review](../artifacts/steps/srg-07/review-routes.md)
checked all 13 submitted route instances against the four selected references,
reran their assessments and verified every claimed expansion against recorded
predictions. It found no identity, assessment or prediction-provenance
discrepancies. This verifies source connectivity and evidence labels; it is not
an external chemist review or an exact patent/procedure validation. Nonreference
alternatives remain unverified rather than disproved.

Four selected targets with one run per arm are insufficient to establish broad
superiority, equivalence or a causal effect of advice. The promotion gate remains
open; main-only stays the default, and the Strategist stays experimental.
Step 7 implementation and this development pilot are complete, but the program
still has **6/14 accepted steps**. Step 8 is the next implementation ticket.

Final configured regression: **1,155 tests passed**, with **93.24% branch-inclusive
package coverage** and 24 recorded warnings. This run explicitly enabled the
existing scientific runtime test through `SRG_YIELD_TEST_PYTHON`; see
[the test log](../artifacts/steps/srg-07/pytest-configured.log) and
[coverage](../artifacts/steps/srg-07/coverage-configured.json). The separate
[final review](../artifacts/steps/srg-07/review-final.json) verified execution
provenance, all eight agent ledgers, advice delivery and reported score totals.

## Reproduction and evaluator separation

The CLI example above reproduces the current implementation into a fresh
episode. The three-arm launcher is
[run-development.py](../artifacts/steps/srg-07/run-development.py); its `--plan`,
`--output-dir` and optional `--freeze` arguments support new bounded comparisons.
Freeze current implementation and asset identities before treating a rerun as a
new benchmark. The historical v1 freeze intentionally detects the documented
source amendment; do not overwrite that freeze or its completed runs.

To recheck the committed v1 outcomes, run this host-only evaluator locally:

```bash
.venv/bin/python artifacts/steps/srg-07/evaluate-development.py
```

This evaluator is never exposed as an agent tool. It checks frozen commitments
and the recorded amendment before reading selected development references; it
does not open every private label or score the final cohort. See
[summary.json](../artifacts/steps/srg-07/development-v1/summary.json),
[the code review](../artifacts/steps/srg-07/review-code.json) and
[the acceptance receipt](../artifacts/steps/srg-07/acceptance.json).

Owner: specialist/controller maintainer owns triggers, plans and runtime;
benchmark maintainer owns comparisons/scoring; environment maintainer owns
action validation and evidence boundaries.
