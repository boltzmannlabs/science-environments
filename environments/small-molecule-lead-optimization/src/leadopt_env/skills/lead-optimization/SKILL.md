---
name: lead-optimization
description: Investigate supplied small-molecule leads with advisory checks, recorded evidence and compatible comparisons.
---

# Lead-optimization campaigns

Use `leadopt_campaign` for local campaign records and advice. Use Agent-Scientist's existing scientific tools for uploads, job submission, polling and downloads. This environment neither submits scientific jobs nor calls a model. It does not replace existing tool contracts or host validation.

First call `operation="describe"` to read the exact environment record schemas. This read needs neither campaign ID nor database setting. Use its field names, requiredness and enums when constructing records. These schemas describe campaign records, not scientific tool inputs.

The policy is **warn and record; let the agent decide**. Read the advice before choosing your next action. If you continue after a warning, retain the failed or unresolved assessment and record your reason when available. An executed action is not proof that a warning was acknowledged, a constraint passed or a scientific objective improved.

## Begin and associate work

1. Obtain a reviewed task describing starting leads, objectives, scientific context, candidate scope, constraints, allowed jobs, budgets, provenance and evaluation. Do not invent scientific defaults or a target-specific model ID. Synthesis planning, FEP and simulations are outside this environment.
2. Create the campaign with `operation="create"`, an explicit `campaign_id`, and `payload={"task": task}`. Registration and installation do not create campaigns.
3. Explicitly attach the current session with `operation="attach"` and that campaign ID. If omitted, `payload.session_id` uses the actual host-provided session identity. If the host supplies none, give the intended real session ID explicitly; never fabricate one. One session may be attached to one campaign at a time. Use `detach` before changing its association. Attach delegated sessions explicitly and record their intended association; no global most-recent campaign is inferred.
4. Read `status` to review the recorded task, candidates, observations, checks, actions and usage before continuing after an interruption.

All operations except `describe` require an explicit campaign ID. Session attachment records association; it is not universal interception of the host's tool calls.

When the host supplies a known attached session, mutation records must name that campaign. Reading another campaign's status/report is allowed. To change the active association, explicitly detach and attach; an association mismatch is a record-validation error, not a restriction on scientific execution. A storage error is reported without automatic retries; inspect the configured database rather than assuming the requested record was saved.

## Before a costly action

Call `operation="check"` with an explicit check `id`, exact catalogue `job`, `candidate_ids`, and any known `resource_requests` mapping units to quantities. Include the investigation `question` when available. Review whether the job's documented controls support the objective internally, assess it afterward, or leave it unsupported. A separate predictor job name is not an optimizer model identifier.

Then decide and execute through the existing scientific tools. The advisory check never executes the proposed request. A missing tool input or host rejection must be handled through the existing tool interface; continuing past an environment warning cannot override it. Do not rewrite scientific inputs silently.

Record what actually happened with `operation="action"`: event `id`, stable `attempt_id`, exact `job`, `candidate_ids`, `status`, `source`, optional `check_id`, returned `job_id`, and `rationale` when supplied. Retain the same attempt identity through state updates; use distinct event IDs. Accepted, pending, failed, completed and unknown are different outcomes. For an ambiguous submission, inspect the original job and retain the uncertainty before deciding whether another attempt is justified. Never let local recovery itself submit a duplicate.

**Recording is explicit.** Scientific calls made without these operations are not automatically captured. Missing call records, unavailable host usage, direct execution and unreported remote-internal work are coverage gaps, not zero usage. Do not claim full tracking or hard budget enforcement.

## Candidates and evidence

Register candidates with `operation="candidate"` using an explicit `id`, `representation`, `form_id`, `source`, and `parent_id` where known. Preserve original molecules and distinguish salts, protonation, tautomers, stereochemistry, prepared forms and conformers. Do not silently collapse uncertain identities.

The current environment treats molecular representations and form IDs as supplied records. It does not perform graph chemistry, infer equivalence or verify a declared scaffold. Its constraint comparisons support compatible numerical endpoint bounds and baseline differences. Obtain chemical checks through suitable existing tools and record their evidence; do not claim those checks ran merely because the record was accepted.

Record observations with `operation="observation"`: `id`, `candidate_id`, `form_id`, `endpoint`, `value`, `unit`, `method`, `method_version`, `context`, `kind`, `qualifier`, `status`, and `source`, plus `artifact` or `action_id` when available. Use actual returned quantities and their semantics. Missing results remain missing. Predictions are not experimental measurements.

For every improvement claim, use a compatible starting-lead baseline. Preserve any immediate-parent comparison separately. Keep IC50, Ki, Kd, docking energy, confidence and predicted property scales distinct. Report incompatible evidence and absent baselines instead of subtracting unlike values. Preserve uncertainty and qualifiers; do not invent intervals or average incompatible predictors. Show preservation failures and objective tradeoffs even if a candidate is retained.

## Resources, decisions and completion

Record usage with `operation="usage"`: `id`, `unit`, `amount` (null if unknown), `category` (`requested`, `observed`, `estimated`, `unknown`), `scope`, `source`, and `attempt_id` when relevant. A batch submission, candidate count and remote optimizer's internal scoring calls are different units. Unknown is never zero. Pending or uncertain work remains unresolved; no unused allowance is implied by a timeout. Allowance warnings are advisory; if continuing, preserve overages and the decision.

Use `decision` to record how observations change the investigation: `id`, `question`, `outcome` (`supported`, `contradicted`, or `inconclusive`), actual `evidence_ids`, `next_action`, and `rationale`. These are the recorded investigation outcome, not a molecule's measured activity. Read `report` for evidence-linked baseline comparisons, missing assessments, warnings and observed accounting. Stopping alone is not scientific success.

For final evaluation, call `freeze` with an event `id`, final `candidate_ids`, `rationale` and `stopping_reason`. Keep the resulting snapshot identity with the evaluator submission. Do not revise candidates or tune policies using final-evaluator answers while still claiming an untouched test. Independent assay answers must remain outside the tested agent's actual access; instructions in this skill do not provide isolation. Reusing the search scorer evaluates its objective; another predictor evaluates computational transfer/agreement; compatible hidden assays evaluate the measured compounds. New molecules have no experimental answers until measured.
