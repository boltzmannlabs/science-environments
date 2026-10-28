# SRG-09 Route Critic

Step 9 adds a shared shortlist-review tool and an optional Route Critic inside
Agent Scientist's main conversation. The host assembles stored routes,
deterministic checks and already accessible source records. The critic returns
bounded, typed advice; main decides whether to recheck, revise or submit.
Both LLM roles use Agent Scientist's main-profile model and provider.

**Status: implementation, 48-episode development comparison and independent
reviews complete; scientific promotion remains open.** All three arms tied.
Only three of sixteen critic reports were accepted. Main-only remains the
default. Everything remains local; no model or service was deployed.

## Research basis and scope

The [RDKit Book](https://rdkit.org/docs/RDKit_Book.html) describes encoded molecular
stereochemistry and the toolkit's supported representations. The critic's host
checks compare encoded identities; they do not establish whether an actual
reaction preserves or produces a stereoisomer. Missing stereochemical evidence
therefore remains a review issue unless an explicit target identity conflicts.

[AiZynthFinder's scoring documentation](https://molecularai.github.io/aizynthfinder/scoring.html)
describes route scores based on stock availability, route size, prices and other
criteria. These provide useful computational comparisons. The environment keeps
those scores separate from source support and experimental validation; a good
route score alone does not certify a synthesis.

Step 9 reuses the existing route environment, validator, immutable revision
store, source projections, recorded scientific-tool envelopes and shared LLM
ledger. It adds an explicit review point before final submission, rather than
asking the critic to inspect every expansion. It does not combine all three
specialists into one automatic pipeline; later orchestration remains separate.

## Shared host review tool

All comparison arms receive the same callable contract:

```json
{"action":"review_routes","arguments":{"route_ids":["stored-route-id"]}}
```

The action accepts one to three unique, already stored route IDs. It consumes an
ordinary environment action and returns a `srg-route-review-v1` packet. The
packet contains:

- The task identity, target, declared scale and constraints.
- Canonical stored routes and their current deterministic assessments.
- Relevant inventory identities and their available amounts, where supplied.
- Public source projections already retrieved within the episode's authorized
  source-access mode; review does not retrieve additional records.
- Relevant recorded forward-check, condition and yield-prediction requests/results, bound
  to the route step inputs rather than accepted solely by matching an arbitrary
  candidate ID.
- Stable, content-bound facts and a host-defined recheck menu.

Agent-authored route arguments are not a substitute for stored routes. The
builder rechecks deterministic assessment consistency against the supplied task
and route. It preserves source claims as public source claims, with no hidden
reviewer labels or host attestations. A claimed reviewer name or route-authored
yield cannot manufacture source or model authority.

The packet is bounded to three routes, twelve steps per route, sixty relevant
sources, twelve relevant scientific records and 100,000 serialized bytes.
Ambiguous duplicate step IDs and oversized packets are rejected; proof is not
silently truncated. Other schema-valid graph errors can remain in the packet as
explicit findings. `review_routes` does not change a route, reject a candidate,
submit a shortlist or call an LLM by itself.

## Finding categories and authority

| Category | Example interpretation |
|---|---|
| `route_structure` | Wrong target, disconnected graph, cycle, duplicate producer or acquisition-only route. |
| `constraint_violation` | Explicit step, material, operation or equipment restriction. |
| `unsupported_transformation` | Missing/unavailable source, source participant mismatch or limited forward-model evidence. |
| `missing_materials` | Required external material missing from the declared stock. |
| `stereochemistry` | Encoded target mismatch, source stereochemistry mismatch or unreported stereochemistry. |
| `quantity_conflict` | Insufficient declared quantities or missing scale information. |
| `incomplete_conditions` | Missing condition information or an unmet explicit complete-conditions requirement. |
| `model_domain_mismatch` | Unverified route-authored yield, bound model abstention or uncertain model transfer. |

Host facts carry `deterministic`, `source_consistency` or `uncertainty` authority
and `error`, `review` or `info` severity. Only a deterministic violation can
supply error authority. Incomplete conditions are normally a review issue;
violating an explicit task condition requirement can be an error. Encoded target
stereochemistry may give a definite identity conflict, while a source mismatch
still does not prove a transformation chemically impossible.

Unknown atom balance, missing yields and unsupported alternatives must not
become automatic chemical rejection. Conversely, a source connectivity match
alone does not verify full operating conditions, stoichiometry, safety or
experimental reproducibility. The critic's prose remains `agent_proposal` even
when it cites a correct deterministic finding.

## Optional specialist and report contract

With `--method main_route_critic`, the first eligible successful `review_routes`
result can trigger one tool-free consultation. It is not triggered by an
expansion or after submission. Main-only uses the same task prompt and tool
schema and can inspect the same review packet directly.

The `srg-route-critic-context-v1` context binds the complete public packet and
remaining shared resources. The specialist receives the main profile's resolved
model/provider, zero tools and at most one model request. The response contract
is `srg-route-critic-report-v1`:

```json
{
  "schema_version":"srg-route-critic-report-v1",
  "context_sha256":"<hash of exact host context>",
  "findings":[],
  "recommended_recheck_id":null,
  "evidence_status":"agent_proposal"
}
```

Each finding names a route, optional step, category, severity, supporting fact
IDs, source-record IDs, requested revision and a rationale of at most 600
characters. The report permits at most eight findings; empty findings are valid.
Requested revision is `revise_route`, `recheck`, `retain_uncertainty` or `none`.
The optional recheck ID must name one existing host-menu action, currently a
`validate` request for a reviewed route. This recommendation does not grant an
extra action or additional budget.

The parser rejects duplicate JSON keys, extra fields, nonfinite values, stale
context hashes, unknown identities and cross-route/cross-step fact citations.
An `error` finding requires a cited deterministic host error for the same route,
step and category. Source-only citations and uncited concerns can support
`review` or `info`, never new blocking authority. The host attaches exact cited
fact/source records and recheck arguments after validation; it does not accept
invented evidence objects from the model.

Advice or its failure status is returned to main as `route_critic_advice`.
Main may use normal metered tools to inspect evidence, validate again or propose
a revision with a new `route_id` and an existing `parent_route_id`. It then
submits through the ordinary environment contract. The critic cannot directly
edit routes or veto submission. Deterministic acceptance remains host-owned.

## Resource accounting and recovery

Main and critic share request, token, tool and wall-time limits. Admission
protects an advisor call, a subsequent main action round and finalization:
`max(3, finalization_model_calls + 2)` model calls must remain, alongside the
configured tool, token and time reserves. A budget skip is recorded explicitly.

The controller checkpoints consultation admission before the external request.
An interrupted pending consultation stays consumed on resume and is not
silently retried. Saved accepted reports, contexts and hydrated recommendations
are revalidated. Changes to task, source/tool configuration, implementation,
profile, mode or budget refuse incompatible runtime resume.

Malformed output, provider errors and missing token confirmations remain
separate outcomes. Main may continue after failed advice. Unknown request usage
retains its reservation; a zero-valued failure report must not be interpreted as
zero actual cost. Report confirmed usage, unsettled reservations and unknown
full totals explicitly. No monetary cost is inferred from token counts alone.

## Local usage

Run from the repository root using its existing chemistry environment:

```bash
cd /home/boltzmann6/server3_data/boltzmann3/joel/REBOLT-FEATURES/synthesis-route-gym
export REBOLT_ROOT=/home/boltzmann6/server3_data/boltzmann3/joel/REBOLT-FEATURES
export REBOLT_PYTHON=/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python
export SRG_SCIENTIST_SOURCE=/home/boltzmann6/Agent-Scientist
export SRG_SCIENTIST_PYTHON=/home/boltzmann6/.sci/tools/python-3.14.7+20260901-linux-x64/bin/python3

.venv/bin/python -m synthesis_route_gym agent \
  --task examples/aspirin_task.json \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci --method main_route_critic \
  --model-calls 24 \
  --episode-dir artifacts/reproduction/route-critic-episode \
  --output artifacts/reproduction/route-critic.json
```

This is a normal route-planning episode, not the closed benchmark described
below. Its remaining budgets come from the task file. Use `--method main` and
fresh output/checkpoint paths for the main-only comparison. Resume an interrupted
session with the exact same configuration and `--resume`; completed episodes do
not reopen. No model override is supplied or needed.

Source availability is explicit: the example has no additional source corpus
unless the host configures one. Optional `--science-config` supplies the existing
host-controlled source/replay configuration. A bare citation in a route does
not make a source accessible. See [scientific tool contracts](SCIENTIFIC_TOOL_CONTRACTS.md)
and [runtime recovery](RUNTIME_RECOVERY.md) for the existing host interfaces.

## Frozen development comparison

The frozen matrix is **eight source-derived cases × two repeats × three arms =
48 episodes**: a fixed direct-tool policy, main-only and main-plus-Route-Critic.
Each episode began with the same three stored candidates and authorized public
source retrievals, established through a common recorded prefix. Candidate IDs
and ordering were fixed before model calls; controlled-edit labels stayed
host-private until every decision was committed.

The agent allowance is 24 model requests, 350,000 tokens, 80 actions and
600 seconds per episode, with at most two case/repeat blocks running concurrently.
Both agent arms use the same main profile and shared-limit rules. The direct
policy uses the same host facts and source-identity comparisons; it must not be
weakened to create an apparent specialist advantage. Actual resource use can
differ within matched allowances.

Four controls derive from the already reviewed PaRoutes development references
and support dataset connectivity. Four derive from previously reviewed Doyle
reaction records and support the recorded reaction identities. Their inventories
are compact derivations for the diagnostic task, not comprehensive process
inventories. Missing operations, solvent, temperature, workup, quantities or
other source details must retain their uncertainty. These reused sources do not
supply eight independent experimental demonstrations or untouched held-out data.

Selection requires source-consistent records **as written**, including correct
declared citations. An incorrect citation is an unsupported record, even when
a matching source is accessible elsewhere. It does not establish that the transformation is chemically impossible. Both agent prompts and the fixed policy use this rule.

The benchmark is a closed candidate-selection diagnostic; generic environment
route revisions remain supported and are tested separately. The comparison
focuses on distinguishing controlled record errors from source-consistent
controls with legitimate caveats. It does not ask the critic to invent a new
route or supply its own ground-truth labels.

Primary scoring must use **raw submitted route IDs**, rather than only the
host's `accepted_route_ids`, to avoid hiding invalid attempted submissions.
Report invalid/unsupported submissions together with source-control retention
and false rejection. An empty shortlist or rejecting everything cannot count as
successful error prevention. A soft review finding alone is not a rejection,
and source inconsistency is distinct from chemical impossibility. Secondary
analysis can report finding detection, proposed/repeated checks, acted-on advice,
conversation completion, failures and resource usage. Rechecks count validation
attempts after review; completed rechecks and recommendations marked as used
require a successful action response.

Artifacts live under `artifacts/steps/srg-09/pilot-v1/`, including the frozen
plan, execution/source hashes, per-run decisions, commitment receipts and
post-commitment evaluation. The frozen launcher commands are:

```bash
.venv/bin/python artifacts/steps/srg-09/run-development.py \
  --plan artifacts/steps/srg-09/pilot-v1/plan.json \
  --freeze artifacts/steps/srg-09/pilot-v1/freeze.json \
  --output-dir artifacts/steps/srg-09/pilot-v1/runs

.venv/bin/python artifacts/steps/srg-09/evaluate-development.py \
  --pilot artifacts/steps/srg-09/pilot-v1
```

The launcher refuses an existing output directory. To reproduce, prepare a new
pilot directory and freeze its exact code/input identities before execution.
Do not overwrite or silently rerun a completed comparison under changed settings.
Evaluation verifies all 48 commitments before parsing the selected private
controlled-edit labels. Final evaluation data remain closed.

## Results, ownership and acceptance

All **48 episodes submitted**, and all **32 main-agent conversations finished
normally**. No episodes were manually interrupted. Independent source review
verified 24 candidate records, all 48 selections and available diagnostic scores.
Independent accounting review reconciled all 32 agent ledgers, event chains,
advice deliveries and aggregates. This is an AI source-consistency audit, not
external chemist review or experimental validation.

| Measure | Direct tools | Main | Main + critic |
|---|---:|---:|---:|
| Exact expected selections | 16/16 | 16/16 | 16/16 |
| Invalid / unsupported submissions | 0 / 0 | 0 / 0 | 0 / 0 |
| Supported controls retained | 24/24 | 24/24 | 24/24 |
| False rejections | 0 | 0 | 0 |
| Model requests | 0 | 52 | 71 |
| Confirmed tokens | 0 | 441,229 | 588,650 |
| Unsettled requests | 0 | 1 | 6 |
| Retained token reservations | 0 | 20,321 | 214,000 |
| Charged token units | 0 | 461,550 | 802,650 |
| Environment actions, including bootstrap | 96 | 99 | 103 |
| Sum of episode seconds | 6.82 | 322.83 | 512.39 |

Assisted versus main produced **zero wins, sixteen ties and zero losses**. The
direct policy reached the same ceiling without model calls. Exact token totals
are unknown in both agent arms: confirmed values are lower bounds where usage
is unsettled. Reservations are accounting units, not monetary cost. Episode
seconds are summed durations, not the parallel experiment's wall-clock time.

Critic delivery was **3 accepted, 8 rejected and 5 failed**. Every rejection
involved a fact citation mismatched to its route or step. The five failures were
provider stream idle timeouts. Both arms also had one main-request stream idle
timeout; those conversations recovered automatically and finished normally.
Failures and rejected advice remained consumed and were delivered once to main.

The three accepted reports detected their three annotated blocking categories
without false blocking findings. This conditional diagnostic excludes thirteen
unsuccessful consultations and does not establish overall critic accuracy.
Review annotations are incomplete; unannotated review findings are not automatic
false positives. Main-only does not emit a structured critic report, so it is
not assigned a finding-level score. Independent review inspected all ten findings
in accepted reports and found no unsupported chemical-impossibility or
experimental-validation claims.

Three main-initiated validation rechecks completed in the assisted arm. No
accepted critic report recommended a recheck, so these actions do not demonstrate
benefit from accepted advice. This pilot permitted no route revisions; immutable
revision support is tested separately in the environment.

**Verification:** 1,767 configured tests passed, with 94.44% branch-inclusive
package coverage. Independent production review passed 351 tests. Benchmark
review passed 73 synthetic tests and 36 post-fix core tests. Runner/evaluator
verification passed 19 integration/end-to-end tests with 97.55% coverage. These
counts overlap and must not be added together. A separate native synthetic
main-profile smoke completed one typed critic call.

**Scientific gate: open.** This reused-development shortlist diagnostic shows no
selection benefit, greater resource use and poor critic delivery reliability.
Keep the critic experimental. Report binding and provider reliability need
improvement under a new frozen development comparison before broader independent
evaluation. Preserve this negative result; do not overwrite or tune this pilot.

Evidence: [summary](../artifacts/steps/srg-09/pilot-v1/summary.json),
[source audit](../artifacts/steps/srg-09/review-source.md),
[ledger audit](../artifacts/steps/srg-09/review-final.json),
[acceptance](../artifacts/steps/srg-09/acceptance.json).

| Contract or responsibility | Version / owner |
|---|---|
| Public host review packet | `srg-route-review-v1`; environment/validation maintainer |
| Main-profile advice context | `srg-route-critic-context-v1`; specialist contract maintainer |
| Structured report | `srg-route-critic-report-v1`; specialist contract maintainer |
| Consultation state | `srg-route-critic-runtime-v1`; specialist/controller maintainer |
| Agent runtime checkpoint | `srg-agent-runtime-critic-v1`; runtime/accounting maintainer |
| Development data, scoring and failures | Benchmark maintainer; frozen plan and source/input hashes |
| Individual source and ledger checks | Separate review responsibility; evidence-qualified acceptance |

Implementation hashes, source identities, test evidence and the receipt
pin the delivered local version. This does not fully pin installed transitive
dependencies or the remote provider backend. The user's final-evaluation requirement remains
open: SRG-12/SRG-13 must test both matched-budget and genuinely unbudgeted research
execution. This development comparison uses finite budgets and does not satisfy
that later requirement. See the [optimization plan](OPTIMIZATION_PLAN.md).
