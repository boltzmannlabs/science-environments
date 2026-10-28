# SRG-08 Condition Optimisation Scientist

Step 8 adds a local condition-selection workflow and an optional advisory
specialist. The workflow chooses among registered, source-measured recipes,
reveals only requested outcomes, updates its choices and submits an observed
candidate. The coordinating agent and advisor both use Agent Scientist's main
profile. The feature does not install another LLM or deploy a service.

**Status: implementation and 96-episode development comparison complete;
scientific promotion remains open.** A functioning advisor is a software
deliverable; reliable improvement in condition decisions is a separate gate.
This comparison does not establish benefit from successfully delivered advice.
Main-only remains the default, and the specialist remains optional.

## Research basis and reused capabilities

[Shields et al., Bayesian reaction optimization as a tool for chemical synthesis](https://doi.org/10.1038/s41586-021-03213-y)
provides a primary research basis for sequential, feedback-driven condition
selection and comparison with fixed optimization policies. The
[official RXN yield-prediction repository](https://github.com/rxn4chemistry/rxn_yields)
provides the published context for the Dreher–Doyle benchmark and reaction-based
yield prediction. These references motivate the comparison; their reported
performance is not a result of this environment.

The fixed Bayesian-optimization comparator uses categorical one-hot inputs and
Gaussian-process expected improvement. It uses the existing
[scikit-learn GaussianProcessRegressor](https://scikit-learn.org/stable/modules/gaussian_process.html)
implementation with frozen kernel and acquisition settings. Its episode-specific
surrogate is updated only from revealed observations. It is an optimization
policy, not a newly trained transferable chemistry model or a replacement for
the existing public predictor.

Implementation reuses `FiniteConditionStudy`, `EpisodeStore`, the shared agent
ledger, the isolated Agent Scientist bridge and the pinned
[ReactionT5v2-yield integration](PUBLIC_YIELD_MODEL.md). `ConditionEpisode` supplies
the condition-specific state and final decision without overloading route IDs
or changing route submission semantics.

## What the agent can do

| Action | Public result and authority |
|---|---|
| `inspect` | Read candidate conditions, the frozen prediction table, initial/queried measurements, unavailable IDs and remaining resources. |
| `observe_condition` | Reveal one registered candidate's measured dataset value. A new query consumes the separate observation allowance. |
| `predict_reaction_yield` | Read requested rows from the pinned, precomputed public-model table. This action performs no new model inference. |
| `submit` | Select an already observed candidate, or `null` to abstain, and end the episode. |

The public `srg-condition-view-v1` view identifies the study, substrate, target,
measurement endpoint, candidate pool, observations, prediction records, resources
and submission. It contains no private data path, unqueried outcome or study
optimum. The host validates the study, outcome commitment and prediction binding
before an episode starts. `candidate_inputs_sha256` binds both outcome and
prediction files to the complete scientific inputs, so retaining an ID while
changing its recipe is rejected.

The finite-study endpoint is source-reported yield in percent. The host supplies
the registered candidate pool; the agent cannot obtain a measured outcome for
an invented combination or change the pool, source measurements or observation
allowance. The current source projection varies ligand, additive and base.
Unreported temperature, time, concentration, solvent details and workup remain
unknown. This is not full process-condition optimization.

Two evidence types remain separate throughout:

- **Measured dataset replay:** an initial or explicitly queried source value,
  with a source-record identity. Replaying it is not a new experiment.
- **Public-model prediction:** a frozen ReactionT5 value or explicit abstention,
  retaining model version, transfer-domain and calibration limitations. A
  registered measured study does not establish that the model transfers well to it.

The JNJ CAD-response records used in earlier development are not relabeled as
yield here. The current pilot uses the existing Dreher–Doyle yield source. The
reserved Perera/Suzuki final source remains outside this development comparison.

## Advisor trigger and typed recommendation

`main_condition_scientist` uses the same main prompt and environment tools as
`main`. The host considers one consultation after at least two actual new
measurements have returned, with an observation still available and at least one
queryable candidate. Initial measurements and interrupted queries without a
returned value do not count as new feedback. Unknown or unrelated study domains,
closed episodes and exhausted allowances suppress the consultation.

The advisor receives the bounded public view and remaining shared resources.
It receives zero tools, one model-request allowance and the resolved main-profile
model/provider. It cannot read files, retrieve hidden source values, perform
observations, submit a decision, edit recipes or grant extra budget. Main chooses
whether to act on the advice through ordinary environment actions.

The `srg-condition-plan-v1` response contains:

- `context_sha256`, binding the plan to the observed state and resources;
- `decision: observe | abstain` and `next_candidate_id`, which must be `null` for abstention;
- `cited_observation_ids` and `cited_prediction_ids`, restricted to available host records;
- a bounded `rationale` and `evidence_status: agent_proposal`.

The parser rejects extra fields, duplicate JSON keys, stale context hashes,
unknown/already observed/unavailable candidate IDs and invented evidence
citations. The host then adds the exact registered conditions, cited measurement
records and model prediction metadata. Numeric outcomes, uncertainty estimates
and recipes are never accepted merely because the advisor generated them.
Advice is delivered as `condition_scientist_advice` in a main-agent tool result;
a valid recommendation is not automatically an executed or useful recommendation.

Admission protects an advisor request, a subsequent main action round and the
configured finalization reserve: at least
`max(3, finalization_model_calls + 2)` model calls must remain. Tool, token and
time reserves also apply. Main and advisor share the same ledger; advisor usage,
failed requests and retries are included in the reported resource totals.

## Persistence, failures and resume

Each action is recorded in an immutable revision store. A new observation is
reserved before its value is revealed. Repeating a known measurement under a
new action ID consumes an action but no additional observation; exact replay of
the same action ID returns the saved response without another charge. Reusing an
action ID for different arguments is rejected.

An interrupted query whose value is unknown remains charged. Its candidate is
listed in `unavailable_candidate_ids` and cannot silently be queried again.
Similarly, an admitted but interrupted specialist consultation is consumed on
resume; it is not automatically retried. Pending admissions are checkpointed
before external requests, and accepted advice is revalidated against its saved
context when restored.

Resume preserves elapsed time, absolute deadlines, observation usage and model
request accounting. Changes to inputs, prediction identities, implementation,
profile, method or budgets refuse incompatible resume. Stale writers fail before
source lookup. Missing submissions, abstentions, interrupted runs and incomplete
model conversations remain distinct outcomes; the evaluator does not substitute
its preferred condition for the agent's final choice.

## Local commands

Run from the repository root with its existing `.venv`. The
[bound-inputs-v2 manifest](../artifacts/steps/srg-08/development-v1/bound-inputs-v2/manifest.json)
lists the eight public study files, prediction files and host-only replay-file
paths, together with their pinned identities. This example uses one listed
study. These variables configure the host CLI; private outcome paths are never
included in the LLM prompt or tool schemas.

```bash
export SRG_CONDITION_INPUTS=artifacts/steps/srg-08/development-v1/bound-inputs-v2
export SRG_CONDITION_STUDY=condition-study-97db486cd59f3050b2bddb9d
export SRG_CONDITION_OUTCOMES=/home/boltzmann6/srg-data/srg08/development-v1/bound-inputs-v2
export SRG_SCIENTIST_SOURCE=/home/boltzmann6/Agent-Scientist
export SRG_SCIENTIST_PYTHON=/home/boltzmann6/.sci/tools/python-3.14.7+20260901-linux-x64/bin/python3

.venv/bin/python -m synthesis_route_gym condition-plan \
  --study "$SRG_CONDITION_INPUTS/studies/$SRG_CONDITION_STUDY.json" \
  --outcomes "$SRG_CONDITION_OUTCOMES/$SRG_CONDITION_STUDY.json" \
  --predictions "$SRG_CONDITION_INPUTS/predictions/$SRG_CONDITION_STUDY.json" \
  --policy gp_expected_improvement --seed 20261027 \
  --max-actions 80 --wall-seconds 600 \
  --episode-dir artifacts/reproduction/condition-gp-episode \
  --output artifacts/reproduction/condition-gp.json

.venv/bin/python -m synthesis_route_gym condition-agent \
  --study "$SRG_CONDITION_INPUTS/studies/$SRG_CONDITION_STUDY.json" \
  --outcomes "$SRG_CONDITION_OUTCOMES/$SRG_CONDITION_STUDY.json" \
  --predictions "$SRG_CONDITION_INPUTS/predictions/$SRG_CONDITION_STUDY.json" \
  --method main_condition_scientist \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci \
  --model-calls 24 --max-tokens 350000 --max-actions 80 --wall-seconds 600 \
  --episode-dir artifacts/reproduction/condition-scientist-episode \
  --output artifacts/reproduction/condition-scientist.json
```

For main-only, select `--method main` and use fresh output/checkpoint paths.
The fixed-policy choices are `fixed_order`, `random`, `public_model_rank` and
`gp_expected_improvement`. For an interrupted agent episode, repeat its exact
command with `--resume`; changing its configuration does not create a fresh
allowance. Completed episodes do not reopen into additional observation rounds.

## Frozen development comparison

The input selection was frozen before public-model inference. Each of eight
substrate studies contains 24 source-measured candidate recipes selected by
chemical-input identities. All methods start with the same two measured
observations and may query four further candidates, for six observations total.
The same 192 ReactionT5 prediction rows are available to every method. Shared
precomputation is recorded separately, including its elapsed time, rather than
being presented as free inference or repeated independently for each arm.

| Arm | Selection behavior |
|---|---|
| `fixed_order` | Candidate-ID ordering fixed before outcomes. |
| `random` | Seeded random selection without replacement. |
| `public_model_rank` | Frozen public-model prediction ranking, with declared abstention/tie handling. |
| `gp_expected_improvement` | Fixed categorical GP/acquisition policy updated from revealed measurements only. |
| `main` | Main-profile Agent Scientist chooses and submits through the environment. |
| `main_condition_scientist` | The same main workflow with one eligible, metered advisory consultation. |

The completed execution is **eight studies × two repeats × six arms = 96 episodes**,
with at most two study/repeat blocks running concurrently. Agent allowances are
24 model requests, 350,000 tokens, 80 actions and 600 seconds per episode;
specialist requests share those allowances. Observation allowance, starting
measurements, candidate pool, prediction table and evaluation rules are matched.
Fixed methods are not required to consume unused LLM resources.

The eight studies share **five products, three product scaffolds and one
publication**. Repeats and substrate variants are correlated; they do not create
96 independent chemistry problems. This is previously used development data,
not an untouched held-out or final benchmark. Membership in pretrained LLM or
ReactionT5 training corpora is not established. No new experiments are performed.

The [execution plan](../artifacts/steps/srg-08/pilot-v1/plan.json) and
[freeze](../artifacts/steps/srg-08/pilot-v1/freeze.json) are saved under
`artifacts/steps/srg-08/pilot-v1/`. The freeze pins 1,485 source/input/runtime
files; a declared pre-execution amendment expanded Agent Scientist source
coverage before any episode started. The original launcher invocation was:

```bash
.venv/bin/python artifacts/steps/srg-08/run-development.py \
  --plan artifacts/steps/srg-08/pilot-v1/plan.json \
  --freeze artifacts/steps/srg-08/pilot-v1/freeze.json \
  --output-dir artifacts/steps/srg-08/pilot-v1/runs
```

The launcher refuses an existing output directory. Keep the recorded runs
unchanged; a new comparison needs a new reviewed plan/freeze and output path.

The host oracle holds replay values so it can answer authorized queries, while
research policies see only initial and queried measurements. Commit all episode
decisions before retrospective scoring. The evaluator is host-only and never
an agent tool; after all commitments and integrity checks are complete, its
interface is:

```bash
.venv/bin/python artifacts/steps/srg-08/evaluate-development.py \
  --pilot artifacts/steps/srg-08/pilot-v1
```

The primary decision metric is submitted-candidate regret against the finite
study's evaluator-only optimum. Also report best-observed regret, the observed
yield trajectory, final-choice quality, actual observation use, successful
submissions, failures, abstentions and full resource consumption. A zero-yield
penalty for missing/abstained submissions is a scoring convention, not a fabricated
measurement. Keep conditional metrics and penalized metrics explicit.

## Results and acceptance

All 96 episodes submitted an observed condition. All 32 main-agent conversations
finished normally. Every method used all four new observations per episode;
each final selection was its best observed candidate. All decisions were
committed before retrospective scoring of the selected development measurements.
The finite optimum refers to each registered 24-candidate pool, not the complete
source screen or an experimentally achievable global optimum.

| Method | Runs | Mean selected source yield (%) | Mean regret (yield percentage points; lower is better) | LLM requests |
|---|---:|---:|---:|---:|
| Fixed order | 16 | 46.7985 | 7.9752 | 0 |
| Seeded random | 16 | 47.5012 | 7.2725 | 0 |
| Public-model ranking | 16 | 50.2037 | 4.5699 | 0 |
| GP expected improvement | 16 | 48.7673 | 6.0064 | 0 |
| Main Agent Scientist | 16 | 50.0238 | 4.7498 | 112 |
| Main + Condition Scientist | 16 | 50.5421 | 4.2315 | 128 |

The assisted arm had two paired wins, thirteen ties and one loss against main,
an average regret reduction of 0.5183 percentage points. **Both wins occurred
in the two runs whose advisor requests failed.** The fourteen successfully
delivered consultations corresponded to thirteen ties and one loss. This is
a post-hoc descriptive breakdown, not a causal experiment: it does not show
that failed advice helps or that valid advice caused the loss. It does mean
the aggregate advantage cannot be presented as evidence that delivered
specialist advice improved decisions.

All fourteen accepted plans passed context, evidence-ID and host-hydration
checks. Eleven recommended candidates were queried later, including nine as
the next observation. Those action overlaps show advice can reach the workflow;
they do not establish that it caused a better decision. The two failure statuses
were also delivered to main, with no automatic advisor retries.

Public-model ranking also slightly outperformed main-only in average regret
while using no LLM requests. It shares the same predictor precomputation cost
as every other arm. The fixed-policy comparison therefore remains relevant;
neither agent method establishes a general quality/cost advantage here.

Main recorded 3,010,400 tokens, all settled. Assisted runs recorded 3,219,754
tokens plus 60,759 retained reservation units across two unconfirmed advisor
requests, for 3,280,513 budget-accounting units. Those two requests reported
`provider_stream_idle_timeout`; each consultation stayed consumed and main
continued to a valid submission. The exact full assisted token use is unknown.
Reservations are neither measured token use nor a monetary cost. Cumulative
episode wall times were 836.72 seconds for main and 992.23 seconds for assisted,
under shared-host concurrency; these are descriptive, not isolated latency
measurements. Shared ReactionT5 precomputation took 71.89 seconds for 192 scores
and is reported separately. One synthetic native advisor check is also separate
from the 96 scored episodes.

Validation: **1,514 package tests passed with 93.97% branch-inclusive coverage**;
the independent runner/evaluator review passed 20 synthetic end-to-end cases.
Separate source verification checked all 192 candidate recipes and predictions,
all 96 selections and 576 final observation instances, with no discrepancies.
This is computational verification against source records, not an external
chemist review or new experimental validation. Unqueried source values were
not emitted into the case review, and reserved final data stayed closed.

Evidence: [frozen summary](../artifacts/steps/srg-08/pilot-v1/summary.json),
[individual source cases](../artifacts/steps/srg-08/review-source.md),
[source receipt](../artifacts/steps/srg-08/review-source.json),
[accounting review](../artifacts/steps/srg-08/review-final.json),
[production review](../artifacts/steps/srg-08/review-code.json),
[runner review](../artifacts/steps/srg-08/review-runner.json),
[regression log](../artifacts/steps/srg-08/pytest-final.log) and
[acceptance status](../artifacts/steps/srg-08/acceptance.json).

The scientific gate is a reproducible improvement in observed outcome or
held-out decision regret at the same observation allowance, with appropriate
abstention outside the registered scope. An inconclusive or negative result is
reported and the specialist remains experimental. A small reused-development
pilot alone cannot establish source-generalization or close the final evaluation.

The user's final-evaluation requirement still applies: SRG-12/SRG-13 must test
both matched-budget and genuinely unbudgeted research execution. This condition
pilot intentionally measures equal observation allowance. Its finite call/time
limits are not an implementation or demonstration of the future unbudgeted mode.

Ownership: the condition-workflow maintainer owns the episode, input bindings and
CLI/session integration; the specialist/controller maintainer owns advisory
contracts and shared-ledger orchestration; the benchmark maintainer owns policy
comparators, frozen comparisons and scoring. Versioned scientific inputs,
contracts, implementation hashes and acceptance artifacts record the delivered
configuration.
