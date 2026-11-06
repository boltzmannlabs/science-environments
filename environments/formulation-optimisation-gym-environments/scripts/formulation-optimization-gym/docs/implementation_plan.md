# Implementation plan: evidence-backed formulation optimization

Prepared 2026-10-27 from [STATUS_AND_GAPS_REPORT.md](../STATUS_AND_GAPS_REPORT.md), the source code and [task configuration](../configs/task.yaml). This is a proposed backlog, not evidence that optimization has been achieved. Live sources and connector availability were not rechecked for this documentation task.

## Target

Build a reproducible environment that evaluates authorized ranolazine ER candidates against verified dissolution objectives, stability evidence, manufacturing constraints and experiment budgets. Improvement claims require independent evaluation and expert review. This plan supplies no numerical product target, ingredient range, manufacturing setting or promised model accuracy.

| Track | Deliverable | Required evidence | Claim boundary |
| --- | --- | --- | --- |
| Exploratory literature | Audited research dataset and, if adequate, exploratory benchmark | Original publications, reuse rights, reviewed extraction, method metadata and frozen groups/splits | Cannot establish recalled-lot compliance, root cause or corrective formula |
| Selected recall case | Case-specific analysis and prospective candidate evaluation | Controlled method/specification, actual measurements, batch/process records and authorized access | Product decisions require responsible experts and controlled approval |

Keep Glenmark D-0092-2024 and Ajanta D-0010-2027 separate until the user selects a case. Software hardening and literature curation can proceed before that selection. Skills supply workflows, not missing evidence or permission to use external systems.

## Success gates

| Gate | Required result |
| --- | --- |
| G0: software baseline | Reproducible behavior, explicit missing-data/tool failures and verified tests. This planning run confirmed 23 passing tests; coverage was not measured. |
| G1: data eligibility | Approved, traceable case records OR an explicitly separate reviewed literature dataset. Literature eligibility never satisfies recall eligibility. |
| G2: analysis readiness | Enforced method identity, units, provenance, required constraints, budgets and approved tool contracts. Unknown required constraints block candidate eligibility. |
| G3: predictive evidence | Frozen independent evaluation with prespecified error, uncertainty and applicability requirements. Inadequate independent support yields `not_evaluated` or `not_established`. |
| G4: optimization evidence | Matched-budget comparisons support the incremental benefit, if any, of tools, specialists and improved model/policy. All failures and negative results are reported. |
| G5: prospective confirmation | An authorized laboratory executes an approved protocol; independent measurements and expert review support the specific candidate claim. Retrospective scores alone are insufficient. |

Investigation closure is distinct from these scientific gates. Manufacturing release and regulatory decisions remain outside the environment's authority.

## Confirmed code gaps

The repository has separate public episodes, FDA/DailyMed importers, six bounded specialist functions, composition checks, an empty approved-tool registry, a scalar nearest-mixture baseline and a preliminary grouped benchmark. It has no verified lot measurements, product criteria, calibrated intervals or live scientific-tool contract.

| Current behavior | Consequence | Backlog |
| --- | --- | --- |
| `tools/mixture_validator.py:Check.valid` means no failed checks, including when constraints are `not_evaluated` | Arithmetic validity can be mistaken for scientific eligibility | T03 |
| `run.investigate` accepts adapters/budget but does not orchestrate tool actions; predictor requests have empty features | Supplying a connector would not complete the analysis loop | T06 |
| `Episode.load` trusts nested dictionaries; schema files do not establish runtime validation | Malformed and cross-linked records need stronger boundary checks | T01–T02 |
| `record_measurement` checks but does not persist `confirmed_by`; approval IDs are unchecked strings | Approval scope and execution identity cannot be reconstructed independently | T07 |
| Adapter timeout does not terminate its worker; retries can repeat unknown-outcome calls; budget counts actions | Late results, duplicates and actual cost need explicit handling | T05 |
| Composition-only scalar model; uncertainty function reports point errors | Profiles, context and calibrated intervals need additional implementation | T08–T09 |
| Group-hash split has no persisted dataset/split manifest or calibration partition | Reproducibility/leakage protection rely on caller convention | T04, T09 |
| Provenance-complete public episodes can be finalized | Closure must not imply validated optimization | T01, T11 |

These are proposed fixes. This documentation change does not modify runtime behavior.

## Skills

Canonical workflows live under `skills/`; `.agents/skills/` links expose those files for project discovery without copying instructions. They are reusable instructions, not newly deployed tools or autonomous scientific agents.

| Skill | Responsibility | Tasks |
| --- | --- | --- |
| [formulation-roadmap](../skills/formulation-roadmap/SKILL.md) | Select track, assess gates, coordinate next authorized work | All |
| [formulation-data-intake](../skills/formulation-data-intake/SKILL.md) | Case identity, controlled provenance and dataset eligibility | T01–T02 |
| [formulation-literature-curation](../skills/formulation-literature-curation/SKILL.md) | Audit publication tables/figures into a separate dataset | T04 |
| [formulation-tool-integration](../skills/formulation-tool-integration/SKILL.md) | Documented contracts, retries, failures and budgets | T05–T06 |
| [formulation-candidate-review](../skills/formulation-candidate-review/SKILL.md) | Composition, process, compatibility and stability eligibility | T03, T06, T10 |
| [formulation-experiment-design](../skills/formulation-experiment-design/SKILL.md) | Discriminating proposals and approval/result reconciliation | T07, T10 |
| [formulation-benchmark](../skills/formulation-benchmark/SKILL.md) | Frozen evaluation, applicability, uncertainty and A/B/C/D | T08–T11 |

Each skill specifies inputs, procedure, outputs and abstention rules. Existing `agents/` modules remain bounded local functions. Planning/code-review delegation under project instructions does not enable SCI delegation or establish scientific specialist benefit.

## Implementation backlog

Paths marked **new** are proposed, not existing capabilities. Controlled records/results belong in approved private storage, not repository datasets. Role names assign responsibilities; actual staff and scientific reviewers must be identified for dependent work.

### T01 — Case manifest and readiness (P0)

Owner: environment maintainer with data owner/QC reviewer. Dependencies: none for software; case selection for scientific intake.

- Add **new** `schemas/case.schema.json`, `schemas/source.schema.json` and a versioned readiness contract: product/strength/lot, source scope, document/method version and effective dates, allowed processing destinations and verification attestation.
- Update `environment/state.py`, `environment/observations.py`, `evaluation/verifier.py` and `run.py` with runtime validation and explicit investigation, analysis, model and optimization readiness. Migrate legacy episodes without changing raw sources or upgrading scientific status.
- Require evidence IDs and reviewer attestations for readiness claims. Checksums establish byte integrity, not manufacturer authenticity.
- Test first: wrong case/strength, missing record, method outside effective scope, unsupported schema version and legacy migration. Acceptance: both existing public episodes load but cannot become validated optimization solely from public records.

### T02 — Controlled-data intake (P0)

Owner: data engineer with QC/data owner. Dependencies: T01; authorized channel and records for scientific completion.

- Add **new** `schemas/dissolution_profile.schema.json`, `schemas/batch_record.schema.json` and `tools/controlled_data_import.py` with runtime validation and quarantine.
- Capture supplied method/specification identity, effective dates, apparatus, media, agitation, timepoints, assay/units and stage-specific criteria exactly as recorded. Link dose/potency basis, material quantities/grades/lots and recorded process/storage history.
- Preserve individual-unit/replicate results and run, instrument/calibration, analyst, timestamp, reference-lot and OOS/deviation links where supplied. Missing critical fields prevent eligibility; do not average away raw observations.
- Keep approved historical records distinct from new experiments. Historical intake needs access/source verification; never fabricate a prospective proposal or approval to satisfy the current measurement action.
- Preserve original bytes, source hashes, transformations and controlled-record verification in authorized private storage. Do not upload externally without permission covering the destination.
- Test first: wrong lot/method, nonfinite values, duplicate run/unit, missing authorization and broken provenance. Acceptance: each eligible value resolves to its original source and permitted purpose; incomplete records remain quarantined.

### T03 — Scientific eligibility beyond arithmetic (P0)

Owner: constraint maintainer with formulation reviewer. Dependencies: T01; verified bounds for scientific use.

- Update `tools/mixture_validator.py`, `agents/constraint_critic.py`, `environment/actions.py`, `schemas/candidate.schema.json` and `evaluation/verifier.py`.
- Separate arithmetic checks from scientific eligibility. Required constraints need source/version, units and applicability; reviewed non-applicability is explicit. Unknown checks remain `not_evaluated`.
- Block ranking/acquisition/readiness promotion when required dose/potency, material identity, composition/process or compatibility/stability constraints are unresolved. Do not invent excipient/process limits.
- Test first: balanced composition with missing bounds, absent potency, wrong units, unknown process and changed constraint version. Acceptance: arithmetic-only candidates remain inspectable but cannot be ranked as scientifically feasible.

### T04 — Audited literature dataset (P1; independent track)

Owner: curator and independent reviewer. Dependencies: T01 evidence contracts; no selected recall needed.

- Start with `data/processed/public_literature_catalog.json` and original PDFs. Check publication identity, source bytes and reuse terms. Add **new** `schemas/literature_row.schema.json` and `tools/literature_import.py` after defining the extraction contract.
- Audit shifted/blank cells and the apparent nonmonotonic value in DOI `10.5281/zenodo.1311884` against page/table/cell coordinates. For `10.5281/zenodo.1170150`, seek numerical source data first; any graph digitization needs axes, extraction method, uncertainty and independent review.
- Keep published numbers `literature_reported`; graph-derived values are `derived` with literature parentage and extraction uncertainty. Missing cells remain missing; never silently repair an inconsistent profile.
- Link formulations, features, method and units. Group related formulations, replicates, shared controls and duplicate publication data before splitting. Preserve accepted/excluded/unresolved reviewer decisions.
- Add a separate exploratory dataset/eligibility path without relaxing the existing measured-only pathway. Never relabel literature as case `measured` data.
- Test first: ambiguous cell quarantine, graph lineage, duplicate source profile and attempted promotion to recall QC. Acceptance: accepted cells are traceable and reviewed; inadequate independent groups/coverage yields `not_evaluated`. Two articles do not establish sufficient sample size.

### T05 — Documented tool integration (P1)

Owner: integration engineer with platform/data owner. Dependencies: T01; authorized documented contracts for live capabilities.

- Extend `tools/boltzmann_adapters.py`, `configs/tools.example.yaml` and `tests/test_api_adapters.py`; registry stays empty by default.
- Discover actual session capabilities. The report's locked connector is a snapshot. If requested, use its supported masked-key authorization flow, then inspect real names/schemas/versions, permissions and retention. Do not infer dissolution capability or guess endpoints; keep credentials outside chat/repository.
- Separate typed contracts for prediction, analysis/statistics and source retrieval. The existing registry accepts predicted observations only; do not misclassify imported measurements or arbitrary analysis outputs.
- Validate task/case/candidate/method, units, output shape, evidence type, source/model/request identity and applicability. Record available training-data provenance and known/unknown benchmark overlap for pretrained tools. Check destination rights before external transfer.
- Specify deadline/cancellation, late-result quarantine, retry/idempotency semantics and sanitized errors. Charge every actual invocation attempt/cost before dispatch. Unknown-outcome operations cannot be retried without documented safe semantics.
- Test first: unavailable connector, auth failure, malformed/cross-case response, timeout plus late completion, duplicate retry and attempt-budget exhaustion. Acceptance: explicit failures, accurate costs and no unapproved repeated operation.

### T06 — Budgeted analysis orchestration (P1)

Owner: environment maintainer. Dependencies: T02/T03 for recall or T04 for literature; T05 for external calls.

- Update `run.py`, `environment/actions.py`, `environment/budget.py` and relevant specialist request contracts to construct feature-bearing requests, call allowed tools through actions and persist provenance.
- Enforce source eligibility → materials → candidate review → permitted assessments/predictions → proposal → independent audit. Use action-specific prerequisites: authorized assessments may investigate unresolved compatibility/stability when their input, applicability and permission requirements are met; required unresolved evidence still blocks feasibility claims, ranking and advancement. Missing inputs/tools produce resumable outcomes.
- Keep compatibility and stability scope separate; record actual conditions, packaging, duration and method. A structure descriptor or compatibility prediction cannot establish shelf life.
- Use new state objects/copies for transitions and append audit events; failed validation preserves prior scientific state. Tie rankings to evidence/model versions and actual budgets.
- Test first: complete synthetic CLI workflow with documented mocks, unavailable-tool abstention, failed transition without partial updates and resume without duplicate calls. Acceptance: actual calls occur only with prerequisites/budget; fixtures remain visibly synthetic.

### T07 — Approval and execution reconciliation (P1)

Owner: maintainer with laboratory approver. Dependencies: T01–T03; implementation uses mocks, not physical execution.

- Extend `schemas/experiment.schema.json`, state/actions and verifier with a versioned approval object linking case, candidate/protocol hashes, method version, scope, approver/time/expiry, budget and execution organization.
- Persist `confirmed_by`, approval and execution/confirmation identifiers. Changed protocol, wrong candidate/case, withdrawn/expired scope or exhausted budget cannot authorize intake.
- Keep proposal, approval, externally executed run and verified result separate. Model output cannot complete an experiment. Laboratory execution stays outside the environment.
- Test first: wrong-case/changed-protocol approval, replayed confirmation, missing execution record, revoked scope and predicted-as-measured submission. Acceptance: a reviewer can reconstruct who approved what, what ran and where results originated.

### T08 — Method-aware predictive baseline (P2)

Owner: modeling engineer with formulation/statistical reviewer. Dependencies: eligible T02 or T04 data; T03 constraints.

- Extend `models/mixture_predictor.py` and add **new** `schemas/model_manifest.schema.json`. Keep the existing scalar nearest-mixture predictor as an explicit comparator for a defined endpoint.
- Specify a method/timepoint endpoint, profile vector or other reviewed response. Include material grade, dose/potency, process and method context when justified by available data. Missing required features are unknown, not zero.
- Split groups before fitting preprocessing/model selection. Tune on development data only. Match model complexity to independent support; advanced optimization packages need a testable benefit.
- Version training hashes, feature roster, units, transforms, model and declared applicability. Preserve predicted labels and lineage.
- Test first: method/timepoint mismatch, unseen material, missing feature and deterministic reconstruction. Acceptance: reproducible baseline on eligible data; performance claims await T09.

### T09 — Frozen evaluation and uncertainty (P2)

Owner: independent evaluator/statistician. Dependencies: T08 and sufficient independent data. Freeze evaluation design before model selection.

- Extend `evaluation/holdout_benchmark.py`, `models/uncertainty.py`, split documentation and `docs/evaluation_protocol.md`. Add dataset/split manifests with source hashes, inclusion decisions, group IDs, method strata, seed and assignments.
- Audit leakage across lots, replicates, related formulation families, shared controls and reused publications. Select grouping and temporal/site/study holdouts for the intended claim; do not pool incompatible methods blindly. Check available external-tool training provenance against holdout sources: public literature may have been seen during pretraining. Record known/unknown overlap and exclude affected results from uncontaminated external-generalization claims unless independence is established.
- Separate development, calibration and final-test groups for calibrated intervals, or justify a reviewed alternative. Log independent test access; tuning after inspection requires a new untouched evaluation set.
- Before final-test access, responsible owners set endpoints/units, independent sample support, meaningful error/improvement, uncertainty coverage/width and applicability limits. The code's small-sample guards are not scientific acceptance criteria.
- Report errors by method/timepoint, interval coverage/width only if established, out-of-domain abstention and failures. Target attainment requires verified applicable product criteria; avoid generic dissolution or profile-similarity thresholds.
- Test first: overlapping groups, changed frozen dataset, holdout-fitted transforms, incompatible units and insufficient calibration support. Acceptance: reproducible manifests/scores or explicit abstention when evidence is inadequate.

### T10 — Candidate policy and prospective protocol (P2)

Owner: formulation scientist with DoE/statistical and laboratory reviewers. Dependencies: T03/T06–T09 for model-informed acquisition; an evidence-backed non-model proposal may proceed with T07.

- Extend acquisition policy and formulation, compatibility/stability and experimental-design specialists.
- Record objective direction, units, scaling, approved tradeoffs, hard constraints, applicability and costs. Compare policies under identical evidence/budgets; current weighted scores remain illustrative until evaluated.
- Prepare supported hypotheses/alternatives, approved factor ranges, response definitions, controls, replicate/randomization rationale, analysis/stop rules, resources and approval packet. This plan provides no numerical formula or laboratory settings.
- Test first: missing objective, unresolved stability/process evidence, out-of-domain prediction, exhausted budget and unapproved protocol. Acceptance: auditable ranking of eligible candidates and reviewable proposal; no physical execution by the environment.

### T11 — A/B/C/D comparison and scientific reporting (P2)

Owner: independent evaluator/domain reviewers. Dependencies: T06–T10 and necessary authorized tools/data.

- Extend baseline/benchmark modules, `run.py` and evaluation protocol with replayable runners and common result manifests.
- A = existing zero-tool evidence-gap baseline; B = direct approved tools; C = same tools plus six bounded specialists; D = C plus evaluated model/policy. Freeze identical task, permitted evidence, criteria, versions, rubric and online attempt/cost/experiment budgets. Disclose D's offline training data/compute separately; no arm sees final-test labels.
- A has no predictive output. Compare evidence-gap/provenance/unsupported-claim handling where applicable and mark numeric prediction metrics not applicable. Use T08's predictive comparator for accuracy comparisons; never invent A predictions.
- Include constraints, justified abstentions, unsupported claims, source accuracy, failures, time, attempts, cost and independent outcomes when available. Prespecify meaningful improvement and uncertainty analysis. Missing arms stay unevaluated.
- Test first: unequal budgets/access, unavailable arm, contaminated holdout and excluded failed run. Acceptance: all outcomes are represented and relative benefit is claimed only when supported. Investigation closure cannot imply G5.

### T12 — Verification and handoff (continuous)

Owner: maintainer with independent code/security/domain reviewers. Dependencies: the implemented increment; scientific completion requires G1–G5.

- For runtime work, write failing behavior tests first, implement and review in small increments. Unit tests cover validation, integration tests cover imports/state/tools, and local CLI end-to-end tests cover critical flows. No external laboratory test is implied.
- When implementation begins, choose/document a coverage tool as a development dependency. Meet at least 80% coverage for maintained application code and report actual scope/exclusions. The 23 passing tests do not establish this coverage.
- Review authorization, confidential logging/storage, artifact permissions and dependencies. Run applicable dependency audits before commits and inspect diffs before publishing. Do not commit secrets or controlled data.
- Update existing architecture, provenance, evaluation and status docs with exact implemented behavior. Separate software, dataset, scientific and approval status.
- Acceptance: required checks pass, review findings are resolved, reproducibility artifacts exist and scientific assertions retain their scope. If external gates remain blocked, deliver only the verified software/exploratory result with that limitation.

## Execution order

1. Implement T01/T03, then T02 contracts/quarantine with labelled fixtures. Apply T12 throughout. These close consequential readiness errors without needing private records.
2. In parallel, start manual T04 review and obtain case/access/method/batch-data decisions. Implement T05 failure semantics using mocks while real contracts remain unavailable.
3. After eligible data/contracts exist, complete T06–T07. Freeze T09's protocol before T08 model selection; use development data, then perform independent T09 evaluation.
4. Evaluate T10/T11 after relevant validation. G5 requires separate laboratory approval/execution. Calendar commitments depend on records and laboratory availability.

First reviewable software increment: legacy public episodes load; unknown bounds prevent candidate eligibility; an authorized synthetic profile passes intake checks; invalid/cross-case records are quarantined; CLI reports exact unmet gates. No new measurement is claimed.

## External inputs

| Input | Responsible party | Unlocks |
| --- | --- | --- |
| Selected recall/product/strength and intended decision | Project owner | Case-specific T01–T03 |
| Data owner, secure channel, permitted processing and reviewer | Data/platform owner | Controlled T02 and permitted external transfers |
| Effective controlled method, criteria and history | QC owner | Method-aware analysis/compliance evaluation |
| Individual-unit lot/reference results and run metadata | Laboratory/data owner | Recall T08–T09 dataset |
| Actual formula, material grades/lots, process and stability/storage records | Manufacturing/formulation owner | Candidate constraints and causal investigation |
| Documented exposed tool contracts and authorized scope | Platform owner | Live T05–T06 |
| Reviewed objectives/bounds/budget and protocol approvals | Scientific/laboratory owners | T07/T10 and prospective confirmation |

Missing inputs do not prevent software hardening or literature audit. They do prevent substantiated recalled-lot root cause, corrective formulation, validated predictor or a claim that the scientific target has been met.
