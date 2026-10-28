# Local orchestration and Small Molecule handoff

Step 11 composes the existing advisor contracts around one main Agent Scientist
conversation and adds versioned candidate handoff feedback. **Main-only remains
the default.** The new modes are comparison controls and explicitly experimental
policies; Steps 7–9 have not established scientific benefit from advisor use.

**Status: accepted for local orchestration and handoff integration.**
Implementation, regression, separate code review, the frozen local development
pilot and the separate execution audit passed. All ten pilot episodes submitted
routes and all eight native conversations completed. This establishes local
integration behavior, not scientific improvement or specialist promotion.
**8/14 steps are accepted; Step 12 is next.** The final benchmark remains pending.

## Modes and admission policy

| Mode | Main conversation | Additional advisor requests |
|---|---|---|
| `main` | Existing default | None |
| `main_role_prompt` | Main considers strategist, condition and critic perspectives in its own prompt | None; role instructions do not create extra conversations |
| `main_all_advisors` | Main continues after eligible advice | At most one request per eligible role, three in total; an irrelevant role is not forced to run |
| `main_adaptive` | Main with deterministic policy-controlled admission | None by default; explicit experimental policy permits at most one advisor |

Existing `main_strategist`, `main_route_critic` and standalone
`main_condition_scientist` behavior is retained. The older `specialists` mode is
a historical sequence of tool-enabled specialist sessions followed by main. It
is different from `main_all_advisors`, whose advisor requests have zero tools.

Every request uses the resolved main profile's model and provider. There is no
per-role model override or provider fallback. Main executes tools and chooses
whether to follow advice. Advice cannot alter routes, reset budgets, read private
outcomes, submit a result or promote its own role.

The host-only `srg-orchestration-policy-v1` contract contains `policy_id`,
`experimental`, `enabled_roles`, `max_consultations` and a complete `priority`
ordering of `strategist`, `condition_scientist`, `route_critic`. Enabled roles
require `experimental=true`. Priority resolves simultaneous eligibility; it is
not a learned ranking. The normalized policy and its digest are saved with the
runtime/session binding. A model cannot supply or change the policy through a
tool argument.

This explicit adaptive development policy enables at most one critic request:

```json
{
  "schema_version": "srg-orchestration-policy-v1",
  "policy_id": "experimental-critic-only-v1",
  "experimental": true,
  "enabled_roles": ["route_critic"],
  "max_consultations": 1,
  "priority": ["strategist", "condition_scientist", "route_critic"]
}
```

It is an opt-in experiment, not evidence that the critic improves decisions.
Omitting `--orchestration-policy` with `main_adaptive` enables no advisors.
`main_role_prompt` rejects a policy that enables advisor calls;
`main_all_advisors` requires all three roles and a three-consultation allowance.
The strict policy has no automatic promotion mechanism.

The role-prompt control includes the substantive specialist instructions in
main's prompt. It is not an exact causal control for delegation: context,
instruction timing, tokens and conversation isolation still differ. Step 12 must
retain these differences when interpreting any comparison.

## Triggers, metering and recovery

The host updates public observer state after a tool response, computes eligible
contexts and applies policy/resource guards. It admits at most one advisor for
that response. Main callbacks and advice share serialized accounting; advisor
requests are not launched concurrently against the same main stage.

The Strategist reuses the existing search-feedback trigger and bounded action
menu. The Route Critic requires a successful explicit `review_routes` response.
The route-condition scientist requires a complete public candidate catalog,
at least two observed candidates, actual remaining observation allowance and an
unattempted candidate. Mere role availability does not make it eligible.

All roles share main's request, token, tool and wall-time ledger. Individual
advisors retain their one-request, tool-free contracts and finalization guards.
An allowance of three consultations is a maximum, not a promise of three calls
or an additional budget. Calls stop after submission or terminal closure; no
new advice is admitted during the reserved finalization phase.

`srg-orchestration-runtime-v1` records the normalized policy, policy digest,
three advisor states, consultation order and a bounded decision history. The
history retains the latest 256 decisions with the total count and an explicit
truncation flag. Each decision binds the tool input/response hash, eligible
roles, chosen role, reasons and selected context identity. Child consultation
records carry admission outcome and report/failure details.

The outer runtime uses `srg-agent-runtime-orchestrated-v1`. Pending, rejected,
failed and interrupted consultations remain consumed after recovery. Saved
advice may be delivered again to a restarted main conversation without a new
provider request. Stage settlement remains role/attempt-specific. Resuming with
a changed policy, task, profile, limits, implementation or scientific-tool binding
is rejected rather than silently resetting resources.

The returned `srg-orchestration-result-v1` summary includes mode/policy identity,
consultations used, order, advisor dispositions, decision count and closure.
The containing agent result separately records conversation completion,
submission status and the authoritative shared ledger. Confirmed tokens and
unsettled reservations are distinct: reservations are retained accounting units,
not measured provider tokens or monetary cost. No fallback route is manufactured
if the agent fails to submit. See [runtime recovery](RUNTIME_RECOVERY.md).

## Route-bound condition advice

Step 10's public condition catalog now includes a host resource projection,
`srg-route-observation-resources-v1`: `calls_used`, `call_limit`,
`remaining_calls` and `attempted_candidate_ids`. Remaining allowance comes from
actual charged observation attempts, not the number of successful measurements.
Failed or pending requests therefore cannot create free observations. The
route-bound and older observation actions share the same allowance.

The pure observer merges paginated candidate records, validates their recipes
and study binding, and requires the full catalog before advice. It rejects
changed route/step identity, recipe, study or application configuration, changed
observations and reset query counters. A query without a fresh attached catalog
requires refreshed public accounting before another context can be built.
Revisions do not inherit advice or measurements by reusing a step name.

`srg-route-condition-context-v1` includes the exact stored route/step reference,
public candidate recipes, revealed observations, source/binding identities,
query charges and shared runtime resources. The isolated contract imports no
RDKit or private study/evaluator. Its public context bound is 300,000 bytes;
observer state is bounded to 650,000 bytes.

`srg-route-condition-plan-v1` binds the context SHA256 and either recommends
one known unattempted candidate or abstains. It includes at most 20 observed
source citations and a rationale of at most 1,200 characters. An observation
recommendation must cite revealed feedback. The host hydrates the validated
candidate into an exact `observe_route_condition` action for main to consider.
Unknown citations, duplicate fields, stale contexts and already attempted
candidates are rejected. The plan stays `agent_proposal`.

No hidden study optimum is exposed. A candidate's measured replay yield is not
grafted onto the proposed route, and no recommendation grants an extra
observation. See [application workflows](APPLICATION_WORKFLOWS.md) for source and
recipe scope and [condition scientist](CONDITION_SCIENTIST.md) for the separate
standalone study environment.

## Candidate handoff and feedback

`srg-small-molecule-handoff-v1` accepts candidate ID, target SMILES, source job and
tool, optional source-tool version and upstream payload SHA256, optional target
scale, inventory, constraints, budget and seed. Molecular identity is canonical
while retaining encoded stereochemistry and isotopes. Inventory identities must
be unique. The target task uses the candidate ID as its task ID.

`srg-small-molecule-manifest-v1` preserves the normalized handoff, task and their
digests. Supplied source metadata remains `caller_supplied_unverified`: an
upstream job ID or digest is not authentication of another pod or verification
of its scientific claims.

Feedback uses `srg-small-molecule-feedback-v1`. It is deterministic
postprocessing, with no new prediction, retrieval or LLM request. Before building
feedback, the host checks the task/seed, committed event chain, proposal records,
submission identities and deterministic assessment consistency. Feedback returns:

- Candidate/upstream identity, handoff/task/episode hashes and event-chain head.
- Distinct execution, conversation and submission status, including empty or
  missing submission; submitted routes and deterministic gates remain visible.
- Recorded source-support gaps and assessments, explicitly short of independent
  chemical review or experimental feasibility.
- Matching recorded process estimates, with scale, currency, basis, quote lines
  and source-event identity; absent or ineligible costs remain unavailable.
- Failed actions, recorded provider failures, environment/scientific usage and
  confirmed versus reserved/unsettled token counts. Monetary cost remains null.

An episode may have submitted routes while its conversation is incomplete;
those are separate facts. A successful report does not erase a prior tool or
provider failure. Fully settled actual tokens are available only when no
reservations or unsettled requests remain. Deterministic eligibility does not
establish fully specified quantities or feasible chemistry; inspect the complete
assessment and its unknown fields.

The local runner writes `handoff.json`, `environment/`, `agent/` and
`handoff-state/` beneath its output directory. Each attempted run has separate
`attempts/0001/run.json`, `feedback.json` and `receipt.json` files, with subsequent
attempts numbered separately. Receipts bind file hashes and durable environment/
agent heads; files are created without overwriting prior artifacts. Attempt
admission is persisted before invoking the agent. The current runner permits at
most 100 attempts and preserves the shared episode budget across them.

Resume verifies the handoff, host configuration, implementation and checkpoint
bindings. A closed attempt returns its verified previous result without another
agent call. Failures record an explicit incomplete result with unknown resource
accounting where confirmation is unavailable. These are local durability and
identity guarantees, not authenticated upstream provenance.

The existing API remains in-memory: its feedback commitment says
`in_memory_snapshot`, not `durable_local_store`. Failure/recovery tests and the
separate code review cover the durable runner's resume and partial-failure
contracts; the real pilot additionally records recovered provider failures.

## Local commands

From the repository root, use the existing runtimes:

```bash
export REBOLT_ROOT=/home/boltzmann6/server3_data/boltzmann3/joel/REBOLT-FEATURES
export REBOLT_PYTHON=/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python
export SRG_SCIENTIST_SOURCE=/home/boltzmann6/Agent-Scientist
export SRG_SCIENTIST_PYTHON=/home/boltzmann6/.sci/tools/python-3.14.7+20260901-linux-x64/bin/python3

.venv/bin/python -m synthesis_route_gym agent \
  --task examples/aspirin_task.json --method main_role_prompt \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci --model-calls 24 \
  --episode-dir artifacts/reproduction/role-prompt-episode \
  --output artifacts/reproduction/role-prompt.json
```

Use fresh output/checkpoint directories for each comparison. Substitute
`main_all_advisors` for the all-eligible control. For experimental adaptive use,
save the policy above to a local JSON file and pass
`--method main_adaptive --orchestration-policy /path/to/policy.json`.
Changing the mode alone does not create condition data: route-condition advice
requires a configured study, binding and successful observed feedback through
the existing `--science-config` interface.

Prepare a handoff input from the existing benign example without changing its
inventory, constraints or budgets:

```bash
.venv/bin/python - <<'PY'
import json
from pathlib import Path
task = json.loads(Path('examples/aspirin_task.json').read_text())
handoff = {
    'schema_version': 'srg-small-molecule-handoff-v1',
    'candidate_id': 'local-aspirin-candidate',
    'smiles': task['target'],
    'source_job_id': 'local-demonstration-job',
    'source_tool': 'local_example_unverified',
    'inventory': task['inventory'],
    'constraints': task.get('constraints', {}),
    'budget': task.get('budget', {}),
    'target_amount_mmol': task.get('target_amount_mmol'),
    'seed': 0,
}
path = Path('artifacts/reproduction/local-handoff-input.json')
path.parent.mkdir(parents=True, exist_ok=True)
with path.open('x') as stream:
    json.dump(handoff, stream, indent=2, allow_nan=False)
PY

.venv/bin/python -m synthesis_route_gym handoff \
  --input artifacts/reproduction/local-handoff-input.json \
  --output-dir artifacts/reproduction/local-handoff-episode \
  --output artifacts/reproduction/local-handoff-result.json \
  --method main --model-calls 24 \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci
```

`handoff` also accepts `--science-config`, the existing scientific model options
and `--resume`. Resume must use the same input and configuration. These commands
invoke the existing local agent and produce fresh artifacts. The recorded pilot
below used the same local interface with frozen development inputs.

## Local API contract

`POST /v1/handoffs/small-molecule` accepts the same typed handoff and creates an
episode; it does not automatically run an agent. Continue through the existing
episode action endpoint. `GET /v1/episodes/{episode_id}/feedback` builds the
current feedback snapshot. A non-handoff episode receives HTTP 409. The endpoint
uses existing bearer authentication, owner isolation, request limits and
`Cache-Control: no-store` behavior. It does not accept a model-supplied host
policy or source corpus.

API feedback without an attached agent result reports conversation/token usage
as unknown. In-memory episode state does not survive a server restart. Use the
persistent local runner for checkpointed work; no service deployment is part of
this delivery. See [local API](../src/synthesis_route_gym/api.py).

## Completed local development pilot

The frozen pilot used two already-public Step 9 development cases, one repeat,
and five arms: direct tools, main, main with role instructions, main with all
eligible advisors, and default adaptive main. Each episode received the same
three-route shortlist and shared prefix of three proposals and one source
retrieval. Limits were 80 actions, six expansions, 600 seconds, 350,000 token
accounting units and 24 model calls; source retrieval was limited to one and
condition observations to zero. Native arm order was reversed on the second
case. These are bounded integration runs, not a held-out final benchmark.

All **10/10 episodes submitted one deterministically eligible route**, with the
same selected route across all five arms for each case. All **8/8 native main
conversations completed**. There were 62 environment actions and ten source
retrievals. The all-advisors arm admitted one critic on each case: one report was
accepted and one rejected for failing the bounded report contract. Neither the
Strategist nor condition advisor was eligible in this closed-shortlist setup.
Default adaptive main admitted zero advisors, as its policy specifies.

| Arm, two episodes each | Model requests | Confirmed tokens | Unsettled reservation units | Unsettled requests |
|---|---:|---:|---:|---:|
| Direct tools | 0 | 0 | 0 | 0 |
| Main | 8 | 45,356 | 60,420 | 2 |
| Main with role instructions | 9 | 81,706 | 0 | 0 |
| Main with all eligible advisors | 8 | 77,255 | 0 | 0 |
| Default adaptive main | 6 | 45,406 | 0 | 0 |
| Total | 31 | 249,723 | 60,420 | 2 |

Main recovered from one provider stream idle timeout and one provider request
error. The two unsettled requests retain reservations; **310,143 charged units
are not a measured token total**. Exact total tokens and monetary cost remain
unknown. Rejected advice remained charged and consumed; the pilot did not
replace failed requests with new episodes.

The same two-candidate pool and evaluated feedback supported a deterministic
with/without-feedback selection comparison. Without feedback, the fixed upstream
priority selected the first candidate. With feedback, the rule preferred a
candidate with an eligible submitted route, then used the same priority. The
choice was unchanged in **all five arms**. Candidate identities and synthetic
upstream provenance were preserved, but there are no independent molecular
quality measurements and no cross-pod gain. Direct tools reached the same route
decisions without LLM calls. This pilot provides no evidence to promote an
advisor or the adaptive policy.

Evidence: [pilot summary](../artifacts/steps/srg-11/pilot-v1/summary.json),
[decision commitments](../artifacts/steps/srg-11/pilot-v1/commitments.json),
[1,623-file integrity check](../artifacts/steps/srg-11/pilot-v1/integrity.json)
and [execution freeze](../artifacts/steps/srg-11/execution-v1/freeze.json).
The freeze covers declared project/native runtime sources, public inputs and
interpreter identities; it does not independently attest every transitive
installed dependency. No private or reserved final labels were opened.

## Versions, ownership and verification

| Surface | Version / ownership responsibility |
|---|---|
| `orchestration.py` | `srg-orchestration-policy-v1`; host policy owner |
| `orchestration_runtime.py` | `srg-orchestration-runtime-v1`, `srg-orchestration-result-v1`; composition/accounting owner |
| `agent_runner.py`, `agent_session.py` | `srg-agent-runtime-orchestrated-v1`; native main-profile/session integration owner |
| `route_condition_advice.py` | `srg-route-condition-observer-v1`, context/plan v1; condition contract owner |
| `route_condition_runtime.py` | `srg-route-condition-runtime-v1`; one-request condition-advice/recovery owner |
| Route observation projection | `srg-route-observation-resources-v1`; environment admission/accounting owner |
| `handoff.py` | Small Molecule handoff/manifest/feedback v1; handoff identity/feedback owner |
| `handoff_cli.py`, `handoff_runner.py`, API | `srg-handoff-binding-v1`, execution/attempt/run v1; CLI persistence and authenticated endpoint integration owner |

The [implementation plan](../artifacts/steps/srg-11/planning-review.md) records
dependencies and required recovery, evidence and isolation tests. Full regression
passed **2,315 tests with 24 warnings and 95.04% branch-inclusive coverage**;
the package build passed. The [separate code review](../artifacts/steps/srg-11/review-code-final.md)
and [pinned receipt](../artifacts/steps/srg-11/review-code.json) leave no unresolved
HIGH/MEDIUM findings. Its 339 focused tests overlap the full suite. A separate
[native ABI smoke](../artifacts/steps/srg-11/native-interface-smoke.json) verified
interface loading with zero model calls; the eight actual native conversations
are recorded separately in the pilot. The
[execution accounting/source audit](../artifacts/steps/srg-11/review-execution.json)
verified all ten event chains, resource receipts, candidate/source bindings and
feedback comparisons. This is automated source-consistency review, not external
chemist sign-off or experimental validation. The
[acceptance receipt](../artifacts/steps/srg-11/acceptance.json) records the local
integration gate, ownership, evidence hashes and remaining scientific limits.

Final evaluation with and without research-budget
limits remains a Steps 12–13 requirement; large finite ceilings are not genuinely
unbudgeted execution. Step 11 cannot close that gate or the scientific promotion
gates by adding orchestration alone.
