# SRG protocol v1: frozen decisions and pending final seal

Protocol ID: `srg-protocol-v1`. Stage: **SRG-01 protocol framework**.
Machine-readable companion: [srg-protocol-v1.json](../artifacts/protocols/srg-protocol-v1.json).
Scope: local execution. **Final benchmark runs are not authorized by this protocol yet.**

This protocol freezes the questions, estimands, evidence rules, comparison rules,
and promotion thresholds below. It does not claim that data, final resource
limits, selected configurations, or sample sizes are already sealed. Those fields
remain explicitly pending. See the [optimization plan](OPTIMIZATION_PLAN.md).
Baseline: `srg-01-mvp-v0.1.0`, with its manifest hash recorded in the JSON
companion and [preservation guide](BASELINE_PRESERVATION.md). Codex `/root` owns
local implementation and protocol maintenance under the user's request. This
automated ownership is not an independent human scientific review.

## Four distinct questions

| ID | Question and primary comparison | Primary decision metric |
|---|---|---|
| Q1 | Does the new scientific model improve condition choice over the strongest eligible fixed condition policy selected on development data? | Group-macro reduction in simple regret, in measured-yield percentage points, at the same observation budget. |
| Q2 | Does a ranking method improve selection from an identical, frozen candidate pool over the strongest development-selected fixed ranker? | Group-macro source-supported success at 5, with complete support adjudication as defined below. |
| Q3 | Does main Agent Scientist improve inventory-constrained search over the strongest development-selected fixed workflow? | Group-macro source-supported success at 5 under common resource caps. |
| Q4 | Does the frozen specialist-enabled configuration improve on main-only Agent Scientist? | The same Q3 success metric, on paired tasks with common aggregate caps. |

Q2 holds candidates fixed; Q3 permits search; Q4 changes orchestration. Do not
attribute improvements across these settings to the same mechanism. A separate
reference-recovery track measures recovery of known routes, not chemical
feasibility. A predictor-on/off comparison on identical pools isolates the
scientific model before any search claim. Every confirmatory contrast, including
any additional model-on/off contrast, must appear in the final claim registry.

For Q1, an offline choice task reveals no test outcomes before decisions. An
adaptive replay task reveals only queried measured records, charges each
observation, and uses identical initial observations and observation budgets.
These are separate task strata. The final seal selects the primary stratum and
observation budget. Regret is the highest recorded outcome in the frozen eligible
candidate set minus the outcome of the submitted measured candidate. Unmeasured
conditions have no invented outcome. Missing/invalid submissions receive 100
percentage points of penalized regret only for datasets validated to contain
percentage yields in [0,100]; this penalty is an algorithm score, not a measured
yield. Other outcome scales require a new preregistered endpoint before use.

## Evidence labels, denominators, and missingness

Each submitted route is assessed separately for structure, inventory identity,
quantities, declared constraints, reference matching, and step-level evidence.
Source-supported success requires at least one submitted route with all declared
hard gates satisfied and every step supported by a matching, located source at
the registered evidence scope. Evidence for a transformation does not establish
unreported quantities, operating conditions, yield, or laboratory readiness.
Unknown mandatory quantities cannot pass a quantity-required task. Identity-only
inventory tasks must carry that designation.

Top 5 means the first five **unique** submitted chemical routes under the frozen
canonical route-equivalence policy; duplicate entries and unfilled positions do
not earn credit. Existing top-3 tasks and artifacts remain unchanged. New top-5
tasks require their own versioned manifests.

| Reported quantity | Numerator and denominator / interpretation |
|---|---|
| Source-supported success at 5 | Target-repeat episodes with at least one qualifying route / all assigned eligible target-repeat episodes, including timeout, empty submission and budget exhaustion. |
| Inventory-closed success at 5 | Episodes with a structurally closed route whose leaf identities are in stock / all assigned episodes. Report quantity compliance separately. |
| Reference recovery at 1 and 5 | Episodes recovering at least one eligible pinned reference under the frozen matcher / all assigned reference-track episodes. A mismatch is not a negative chemistry label. |
| Review coverage | Unique submitted top-5 routes with an attempted complete review / all unique submitted top-5 routes. Also report resolved support status / submitted routes. |
| Hard-constraint violations | Violating submitted unique routes / submitted unique routes, plus episodes containing violations / all assigned episodes. No submissions makes the route denominator undefined, not 0% violations. |
| Condition regret | Average penalized regret across all assigned condition episodes; report submission coverage, actual measured regret among valid submissions, and failure count alongside it. |
| Ranking quality | Primary success-at-5 includes every eligible task; conditional ranks among adjudicated pools are secondary with judged coverage disclosed. |
| Search effort | Restricted expansions to first qualifying submission, using the common expansion cap for every unsuccessful episode. Report total actual expansions separately. |

For primary inference, first average repeats within each target, then targets
within each predeclared independent source/chemical group, then weight groups
equally. Report raw episode counts and micro-averages as descriptive quantities;
they are not additional independent samples.

Source labels are supported, contradicted, or unresolved. An unresolved route
contributes no verified-success credit, but is **not** recorded as chemically
infeasible. Report a verified-success lower bound and an upper bound permitting
unresolved eligible alternatives to succeed. Conclusions must say
"source-supported retrieval," not true synthesis success. Missing literature,
failed search, or removing a reference starting material does not prove that no
feasible route exists. No silent complete-case removal of unresolved episodes.

## Data isolation and eligibility

SRG-02 owns dataset/source selection, licensing/provenance review, candidate
allocation, eligible counts, and partition manifests. No new dataset is allocated
by SRG-01. The already inspected Doyle test is development/regression evidence
for future work; its reuse cannot support a new untouched-test claim.

Create train, development, calibration where applicable, and final partitions
at the level of connected leakage groups: related targets/products, repeated
inventory versions, substrate variants, source/patent families, and duplicate
reactions. Record the grouping and exclusions before final selection. Audit known
scientific-model training overlap; unavailable training sets remain an explicit
unknown. LLM pretraining exclusion cannot be inferred from a local overlap audit.

Final labels, reference answers, and outcome-bearing caches/indexes are unavailable
to optimization. In a closed-information track, hide reference records. In an
evidence-retrieval track, give every arm the same frozen corpus and retrieval
allowance and label the result retrieval-assisted. Do not pool these tracks into
one primary endpoint. The evaluator reads outcomes only after ordered decisions
and run manifests are saved. No oracle-sorted warm starts or full-data tuning.

## Fair arms, resources, and cache policy

Required route arms are the strongest eligible fixed workflow, main Agent
Scientist, and the development-selected specialist configuration. The specialist
configuration remains experimental until it passes this protocol. Development
ablations include each specialist alone, the combined/adaptive policy, and a
single-agent control with equivalent role instructions. A critic participating
in optimization is not an independent evaluator.

All arms receive identical targets, inventories, allowed tools, scientific
checkpoints, condition models, source access, and environment constraints. Use
the same expansion backend for the orchestration claim. AiZynthFinder using a
different backend is a separately identified external baseline.

All research LLM roles, including automated source review, resolve only the
Agent Scientist main-profile model/provider. Record the resolved identifier and
configuration hash at the final seal; do not introduce another LLM or fallback.
Scientific predictors remain separately versioned tools. Secrets never enter
task manifests or reports.

Pilot defaults are 600 wall seconds, 80 actions, 12 expansions, 200,000 aggregate
LLM tokens, and 24 aggregate LLM calls per episode. A top-5 shortlist is proposed
for new benchmark tasks; old top-3 examples retain their contract. These defaults
are **not final sealed limits**. Observation counts, GPU/CPU allocation, output
caps, threads, retries, concurrency, and aggregate experiment ceilings are pending
measured pilot planning. The deterministic baseline need not consume unused LLM
allowance. All specialist calls, messages, retries, and finalization share the
same arm budget; no hidden host-generated submission or free specialist work.

For primary end-to-end resource reporting, use isolated cold per-episode caches;
charge initialization and computation within the declared episode clock. A
precomputed-cache track is secondary, with identical immutable entries available
to every arm and precomputation cost reported separately. No arm inherits cache
entries generated by another arm's test run. Cache keys include tool/checkpoint,
input, configuration, and dependent stock/evidence versions. Final manifests
specify the treatment of operating-system/model-residency effects. Randomize arm
order within task blocks and enforce matched hardware/thread allocations.

Record actual and reserved tokens, CPU/GPU allocation and usage, wall time,
scientific calls, expansions, observations, retries, cache behavior, and separately
charged review overhead. Equal caps are not equal consumption. Predeclare any
infrastructure exclusion and whole-block rerun policy; retain original attempts
and costs. Provider failures and budget exhaustion otherwise remain outcomes.

## Frozen promotion and statistical rules

For Q2–Q4, choose exactly one primary promotion branch per contrast in the final
claim registry **before opening final outcomes**:

- **Quality:** estimated improvement in group-macro source-supported success at
  5 is at least 5 percentage points, and its multiplicity-adjusted lower
  confidence bound exceeds zero.
- **Efficiency:** estimated reduction in group-macro restricted expansions is
  at least 20%; the adjusted upper confidence bound on the candidate/baseline
  effort ratio is at most 0.80; and the adjusted lower confidence bound on the
  quality difference exceeds -5 percentage points. A zero baseline mean effort
  makes this branch ineligible. No switch to the quality branch after results.

Q1 promotion requires a positive multiplicity-adjusted lower confidence bound
for regret reduction and achievement of a scientifically justified minimum
regret reduction frozen at the final seal. Its value depends on the eligible
measured outcome population, which SRG-02 has not allocated. No Q1 promotion is
possible while that field is pending. No promoted configuration may introduce
an observed hard-constraint violation; report valid-route false rejections too.

Let M be the number of confirmatory claims registered at sealing, across all
questions, models, and contrasts. Use familywise alpha 0.05 and Bonferroni
one-sided bounds at alpha/M. Efficiency is an intersection-union decision:
both efficiency and quality-noninferiority components must pass at alpha/M;
there is no extra uncorrected opportunity to claim success. Other comparisons,
top-k values and portfolio endpoints are exploratory unless registered and
included in M. Do not select whichever metric happens to be significant.

Use paired resampling of independent leakage groups, retaining all targets,
repeats, and arms inside each resampled group; calculate 10,000 bootstrap
replicates using a frozen analysis seed. For ratio claims resample paired group
means jointly. Report both absolute effects and intervals. Bootstrap validity
with sparse or few groups is not assumed: before final sealing, use development
data to evaluate interval coverage and decision operating characteristics under
plausible group heterogeneity and effect sizes. If this method is inadequate,
amend the protocol before final access or restrict the result to descriptive
reporting; do not improvise an analysis after seeing final labels.

The final independent-group count, repeats, design effect, expected review
resolution, minimum meaningful Q1 effect, and power/precision analysis are
pending. Proposed counts such as 50 targets are not power guarantees. Repeats
estimate stochastic variability, not new chemistry. Select a justified design
alternative before power calculations; do not promise high probability of
clearing a point-estimate threshold at that exact boundary. Record feasible
precision and detectable effects if resources cannot support the intended claim.
No optional stopping, repeated final-set tuning, or unregistered sample extension.
An inconclusive result leaves the incumbent enabled; a new cohort requires a
separate preregistration before its labels are accessed.

## Review and remaining seal gates

Reviewers are blinded to arm, generator scores, and comparative results. Review
all top-5 steps, deduplicate chemical content, randomize review order, retain
source locators, and adjudicate disagreements under a frozen rubric. Preselect
an audit of both acceptances and rejections. Same-main-model review in a separate
context is an automated source audit, not independent human validation. Any
human review records its distinct reviewer provenance and scope.

`final_run_authorized` remains `false` until all of these are recorded:

1. Baseline snapshot identity and protocol/doc hashes; accountable named owners.
2. SRG-02 source/task/candidate manifests, group splits, overlap audit, eligibility
   rules and sealed evaluator access controls; fresh final condition evidence.
3. Final independent-group/sample/repeat counts with development-only design
   analysis, confidence-method adequacy, review capacity and fixed analysis seed.
4. Final claim registry, M, chosen promotion branches, Q1 minimum effect and
   primary observation stratum/budget; no unresolved primary endpoint choices.
5. Development-selected fixed/main/specialist configurations, prompts, tool and
   scientific-model hashes, main-profile resolution, and route matching rubric.
6. Final per-episode and aggregate resource limits, hardware/concurrency/cache
   policy, retry/exclusion/restart rules, finalization allowance and budget tests.
7. Blinded review rubric, corpus scope, adjudication and audit plan; a signed
   final-seal record referencing the complete immutable configuration bundle.

Owners: benchmark maintainer (protocol and statistical seal), data curator
(sources, groups and hidden outcomes), environment/integration maintainer
(resources and access boundary), scientific-model maintainer (training and
applicability), and chemistry reviewer (evidence adjudication). Named ownership
is assigned to Codex `/root` for this local work; automated chemical source review
uses Agent Scientist's main profile. Reconfirm responsibility at the final seal.
Amendments must be versioned with rationale, date, affected claims,
and whether any final outcome was accessed; never replace an earlier receipt.

The final seal is a technical readiness receipt referencing frozen files and
passing checks. It is not a new request for user permission to continue the
already authorized local implementation.

## Research basis

[PaRoutes](https://pubs.rsc.org/en/content/articlehtml/2022/dd/d2dd00015f) provides
patent-derived routes, stocks and route evaluation measures. This protocol keeps
stock closure and reference recovery separate from source-supported chemistry.
[SciPy's bootstrap documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html)
describes paired resampling and warns about degenerate distributions. It does
not establish coverage for this project's grouped, sparse outcomes; the
development-only statistical adequacy gate remains required.
