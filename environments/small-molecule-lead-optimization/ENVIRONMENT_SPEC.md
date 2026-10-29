# Small-Molecule Lead Optimization — Environment Specification

**Lifecycle: In Progress.** Version 0.1 implements the local record/advice interface, transactional storage, native plugin and offline evaluator. Broader scientific requirements below remain subject to the stated implementation boundaries and live qualification.

## 1. Purpose and boundary

Help Agent-Scientist investigate improvements to supplied small-molecule leads while preserving task constraints and an auditable connection between molecules, tool requests, artifacts, and scientific conclusions.

The environment is general across tasks. The target, starting compounds, assay context, objectives, permitted tools, budgets, and evaluation belong to each task. A task may be target-independent when its objective concerns molecular properties alone.

Synthesis planning, FEP, and molecular-dynamics simulation are excluded. Computational completion does not establish synthesis feasibility or experimental improvement.

The [research notes](../../research/small-molecule-lead-optimization/research-notes.md) describe the references. SMDD-Bench informs objective/constraint separation; PMO informs resource-aware comparisons. Neither supplies universal chemical cutoffs or experimental truth for this environment.

## 2. Responsibility split

| Component | Responsibility |
| --- | --- |
| Task | Scientific case, candidate scope, objectives, constraints, budgets, permitted evidence, and expected deliverables. |
| Agent-Scientist | Planning, model calls, tool discovery, input preparation, and configured tool execution. |
| Boltzmann connector/catalogue | Authoritative tool requests and file-input validation; upload, submit, poll, and download. |
| This environment | Baseline comparisons, investigation history, candidate lineage, task constraints, evidence associations, resource accounting, and evidence-qualified reporting. |
| Independent evaluator, when used | Protect reference answers outside the tested agent's access and score frozen submissions under a preregistered task protocol. |

Delivery is a standalone Agent-Scientist plugin plus its registered skill. `leadopt_campaign` exposes explicit operations and schema discovery; SQLite stores immutable task snapshots and records. No specialist model or additional agent loop is introduced, and Boltzmann request schemas are not duplicated. See [installation](scripts/README.md) and [contracts](config/README.md).

**Agreed policy: warn and record; let the agent decide.** Task-rule violations produce advice and durable findings, not environment-imposed execution blocks. Existing host/tool validation still applies. Continuing after a warning does not change candidate eligibility or turn missing evidence into a pass. Hard constraints remain assessment criteria even though this plugin does not enforce them at execution time.

## 3. Task information

The version-1 JSON task contract is [task.schema.json](config/task.schema.json). The following table describes the scientific information; the current schema supports opaque molecular identities, numerical endpoints and bounds. Unsupported chemical-graph or assay interpretations must be resolved in a task-specific assessment, not inferred by this implementation.

| Information | Meaning |
| --- | --- |
| Identity/provenance | Task ID/version, scientific question, and sources. |
| Starting leads | Molecule records, source representations, known identities, and baseline evidence with assay context. |
| Scientific context | Target identity/sequence/structure where required, preparation state, and source provenance. |
| Candidate scope | New analogues permitted or selection restricted to a declared library. |
| Improvement objectives | Endpoint, direction/range, comparator, units/scale, evidence method, and task-defined required improvement where applicable. |
| Preservation requirements | Properties/features to retain, their comparison methods, and tolerances where applicable. |
| Hard constraints | Eligibility rules, evaluation methods, and missing-evidence behavior. |
| Resources | Separate candidate, submission, molecule-evaluation, model, time, and concurrency limits where applicable. |
| Capabilities | Permitted canonical jobs, used only when their input and endpoint requirements are met. |
| Deliverables/evaluation | Artifact formats, selection/report requirements, and independent scoring protocol when applicable. |

No universal potency target, docking cutoff, molecular-weight range, similarity threshold, ranking weight, seed, sample count, or resource budget is selected. Such values need task-specific rationale and review.

### Objective-to-tool compatibility

For each objective, record whether the selected capability supports it through documented internal controls, assesses it after generation, requires an unverified model/mapping, or has no established support. Include endpoint/scale, model identity where known, and contract evidence. A documented control does not guarantee improvement or establish the internal reward formula.

The [capability mapping](config/tool-mapping.md#map-each-objective-to-an-actual-capability) provides source-backed examples. Property controls do not establish arbitrary target-potency optimization. A separate prediction job cannot become an optimizer model identifier without an explicit compatible contract. Unmapped objectives receive warnings and remain unassessed; they cannot acquire success claims because another property improved.

## 4. Campaign workflow

| Stage | Question the agent answers | Recorded outcome |
| --- | --- | --- |
| Define the objective | What must improve, what must be preserved, and which candidates are allowed? | Reviewed objectives, constraints, candidate scope, and unresolved inputs. |
| Establish baselines | What evidence describes each starting lead, and can the intended assessments be compared with it? | Baseline observations, objective gaps, preservation risks, and missing comparison evidence. |
| Plan an investigation | What change or additional assessment could address the current limitation? | Question, expected benefit, possible competing explanation/tradeoff, comparator, and suitable tool capability. |
| Propose or select | Which analogues or library members should be investigated? | Candidate identities, parent/comparator links, and rationale. |
| Assess | What do the chosen existing tools actually report? | Linked observations, artifacts, resource use, and incomplete/failed operations. |
| Compare | Did the candidate improve, satisfy constraints, or introduce a tradeoff? | Endpoint-specific differences and separate constraint assessments. |
| Revise or stop | What did this round establish, and what is the next useful step? | Continue, reassess, retain, reject, or stop with evidence and rationale. |
| Report | Which conclusions can the completed evidence support? | Candidate comparison table, selection rationale, unresolved questions, and resource summary. |

These stages describe responsibilities and evidence checks, not a fixed tool sequence. The user approved explicit checks before costly actions and one active campaign binding per session, with explicit subagent attachment. The installed skill instructs the agent to use these operations alongside its existing scientific tools.

Each investigation connects previous observations to a question and a next action. For example, a candidate may improve a task's predicted activity endpoint but fail its solubility constraint. The next investigation can address that limitation, revisit the evidence, or end that branch. Repeating the same assessment without a reason does not establish progress. This is an illustrative decision pattern, not a fixed optimization policy.

The investigation record should distinguish an expected effect supported by observations, contradicted by observations, or left inconclusive. A failed tool execution establishes none of these scientific outcomes by itself. The next decision should cite what changed in the evidence and why it changes the plan.

The environment can recommend stopping when goals are met, an allowance is reached, evidence is missing, a job is unresolved, or no justified next investigation remains. The agent decides whether to stop or continue; continuing beyond an allowance remains an overrun. Record its rationale when supplied and the final stopping reason. Ending the campaign does not imply scientific success.

## 5. Molecule identity and lineage

Preserve source representations and distinguish derived working forms. Salt handling, protonation, tautomerism, stereochemistry, and normalization changes must be recorded; results for one form must not silently become evidence for another.

Version 0.1 keeps candidate IDs, source representations, form IDs, optional parent links and provenance verbatim. It does not parse structures, canonicalize, infer equivalence or deduplicate molecules. Unspecified stereochemistry remains uncertainty. Chemical identity checking beyond explicit record associations requires a separately reviewed extension.

Docking poses, conformers, and prepared molecules must retain preparation context and candidate associations. File names, row order, or similar molecular strings alone do not establish identity. Ambiguous or unmatched outputs remain unresolved.

## 6. Evidence and comparisons

Observations need candidate/form, endpoint, units or score scale, method/version where available, inputs/settings provenance, job/artifact references, and completion state. Experimental measurements additionally need source assay context and qualifiers.

Keep IC50, Ki, Kd, docking energy, docking confidence, predicted affinity, solubility, and other endpoints distinct. A predicted-score change is not a new experimental measurement. Comparisons require compatible methods/conditions or an explicitly reviewed mapping. Censored measurements retain their qualifiers.

Evaluate hard constraints, improvement objectives, and preservation requirements separately. Missing required evidence cannot count as a pass. Assessment states are `pass`, `fail` and `unresolved`. Candidate-scope eligibility and numerical constraint findings remain separate from objective improvement.

Preserve individual endpoints and tradeoffs. Composite scores or automatic ranking require a task-declared, reviewed policy. Do not hide weights or infer conversions between unlike endpoints.

### Baseline coverage

For each improvement objective, identify the designated starting lead and a baseline observation compatible with the candidate assessment. A historical assay measurement and a new predictor output cannot be subtracted to claim improvement. When a comparable baseline is absent, expose the gap and propose a matched assessment if the task and remaining resources permit. Whether to require automatic baseline re-scoring is still open.

Keep the original lead comparison alongside any immediate-parent comparison. This makes cumulative changes visible without treating an improvement over a weak intermediate as improvement over the starting lead.

### Candidate comparison table

The report presents one row per candidate and objective, with separate constraint rows. Its records preserve:

- Starting-lead and candidate observation references and values.
- Endpoint, units/scale, molecular-form and method/context compatibility.
- Raw difference only when meaningful, plus interpretation under the declared objective direction or target range.
- Hard-constraint and preservation assessments, separate from the improvement assessment.
- Available uncertainty, measurement qualifiers, missing evidence, and disagreements between methods.
- Retention, rejection, or further-assessment rationale.

Unknown uncertainty remains unknown; do not invent confidence intervals or average incompatible predictors. If two candidates trade gains across objectives, show the tradeoff. The final selection method remains a task/policy choice.

## 7. Execution and resource accounting

Agent-Scientist supplies configured scientific tool execution. The environment records campaign actions and results using those existing operations and canonical input contracts.

### Advisory review and observation boundary

A planned-action review should return the affected rule, evidence, warning category, and suggested resolution before the agent chooses whether to submit. Distinguish confirmed violations from missing information and scientific tradeoffs. Record the subsequent action and agent rationale when supplied; never invent acknowledgment or infer it from a submission alone.

Version 0.1 uses explicit pre-action checks and explicit agent-entered action/observation/usage records. It does not automatically observe native tool calls. A recorded action that skipped advice receives a retrospective finding; unrecorded activity is outside coverage. A check response proves the operation returned advice, not that the model considered it. Host validation and evaluator eligibility remain separate responsibilities.

Native loader, registry dispatch and skill lookup are tested in an isolated host context. Explicit session bindings prevent silent reassignment, and the adapter rejects mutations inconsistent with a known binding. Code paths without a host session ID must supply campaign identity explicitly; no global most-recent campaign is inferred. Automatic observation remains a future enhancement; see the [integration review](../../research/small-molecule-lead-optimization/research-notes.md#advisory-integration-review).

Retain original job identities and accepted, running, completed, failed, and unknown outcomes. Acceptance is not completion. Warn against repeating an ambiguous submission and recommend reconciliation. If the agent continues, preserve the new attempt and its possible duplication; a retry is not a harmless read.

Account separately for model calls/tokens, submissions, requested/returned candidates, molecule-level evaluations, and elapsed time. Every quantity needs a unit, scope, source, and label: requested, observed, estimated, or unknown. Unknown is never zero. Returned candidates and requested optimization steps do not establish remote internal evaluation counts. Reused evidence is not an independent measurement.

Compare allowances and observable usage without implying equal hidden work inside remote services. Warn when known usage or a request exceeds an allowance. Pending/ambiguous operations retain unresolved usage commitments until reconciled; they do not reset apparent usage. Estimates and commitments remain distinct from observed consumption. The environment does not impose budget blocks under the agreed policy.

The [tool mapping](config/tool-mapping.md) is a reference, not integration evidence. Task settings come from the current catalogue and reviewed task. Catalogue status does not guarantee account entitlement or worker readiness.

## 8. Outputs and recovery

The report and associated records include the task/configuration snapshot; objective-capability matches; candidate lineage; investigation questions and outcomes; actions/job identities; artifact references; endpoint comparisons; objective/constraint assessments; warnings and timing; agent responses where recorded; selected candidates with rationale; stopping reason; resource accounting and coverage gaps; and completed/failed/unresolved/unattempted work.

SQLite transactions preserve records across restart. Repeating an identical record ID is idempotent; conflicting content is a data-integrity error. Unknown job outcomes stay unresolved; this implementation never submits or retries jobs. `freeze` stores a fixed report/submission snapshot and SHA-256 digest; the offline evaluator requires a separately retained expected digest. Checksums do not establish trustworthy provenance, evaluator isolation or resistance to a writer controlling both snapshot and receipt.

## 9. Evaluation and acceptance

Software acceptance covers task handling, identity/lineage, result associations, failure/unknown states, accounting, recovery, packaging, and actual Agent-Scientist integration. The [validation plan](tests/README.md) distinguishes proposed checks from executed evidence.

Scientific comparisons need the same task, starting evidence, tools, and resource limits across the base agent and environment-assisted agent. Report operational errors and scientific outcomes separately. Protected evaluator answers require real host isolation, not a prompt instruction alone.

Identify all scores available during search and their relationship to final evaluation. Freeze objectives, scoring rules, relevant versions, and the submitted candidates before final scoring. Final-evaluator feedback used to revise candidates or tune policy becomes development evidence; that evaluation is no longer an untouched final comparison.

| Final evidence | Supported interpretation |
| --- | --- |
| Same scorer used during search | Performance against that scoring objective; not independent confirmation. |
| Different computational predictor | Transfer or agreement under another model, qualified by applicability and shared data/methods. A different name does not establish independence. |
| Compatible held-out experimental measurements | Retrospective performance on that measured endpoint/cohort, subject to exposure and assay review. |
| New measurements of submitted candidates | Prospective evidence under the actual assay conditions, if separately arranged. |

An agent may continue after a warning while its submission remains ineligible under the evaluator's task rules. Report both completed work and eligibility. Do not silently discard failed or over-budget runs. Unknown internal service work limits claims about equal resources.

A measured-library task can score only its recorded compounds against compatible hidden measurements. Open analogue design needs a declared prospective assay or computational evaluation for new structures. Published measurements of other compounds cannot be assigned to generated candidates. Public-data/model-training exposure remains a caveat even when labels are hidden in files.

COVID Moonshot Mpro is a future task pending data and endpoint review. No comparison has run; no better-performance or error-free-execution claim is established.

## 10. Remaining qualification and extensions

The runnable synthetic example, record schemas, storage, native interface and installation path are implemented. Version 0.1 supports numerical bounds and baseline-relative constraints, preserves raw identity/provenance, and does not choose a ranking algorithm.

Still required: live scientific-job/result qualification; verification that a model follows the installed skill; case-specific assay/cohort review and protected evaluator deployment; and the matched base-agent comparison. The [status](STATUS.md) and [validation evidence](results/validation.md) track these separately.

Further decisions include chemical normalization/graph constraints, automatic observation of native calls, evidence aggregation across replicates, richer uncertainty treatment, ranking and specialist model roles. These are not silently selected by the first implementation.
