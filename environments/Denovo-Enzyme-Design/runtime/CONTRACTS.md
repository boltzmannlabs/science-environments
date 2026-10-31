# Runtime contracts

The controller calls a fresh executor, reviewer or repair session through an existing harness. It implements fixed stage progression and bounded recovery; the harness supplies scientific tools, access, resource reservation and model inference. Software control-flow tests use synthetic evidence and do not establish end-to-end enzyme design.

## Start and resume

From the environment directory, use Python with `jsonschema` installed. The default backend is an installed `sci` executable. An optional agent configuration selects an already configured harness profile:

```json
{"backend": "sci", "executable": "sci", "profile": "your-configured-profile", "max_turns": 40}
```

Omit `profile` to use the existing default. `cwd` may select an existing workspace. The bridge uses the installed finite `chat` interface with a query file; it does not modify credentials, approval settings or the harness installation.

```bash
python3 runtime/controller.py init --run-dir /path/to/new-run --request 'Design a de novo enzyme for the supplied conversion' --input /path/to/reference-manifest.json --agent-config /path/to/agent-config.json --policy /path/to/policy.json
python3 /path/to/new-run/environment_snapshot/runtime/controller.py doctor --run-dir /path/to/new-run
python3 /path/to/new-run/environment_snapshot/runtime/controller.py run --run-dir /path/to/new-run
python3 /path/to/new-run/environment_snapshot/runtime/controller.py status --run-dir /path/to/new-run
```

`--input` accepts files and may be repeated; use a manifest for a collection. `--condition agent_selected` is the default; `tools_specified` preserves explicitly prescribed implementations. `init` requires a new directory. `run` resumes the same state and remaining allowance; `--max-stages N` checkpoints after N accepted stages. A terminal run returns its saved report instead of silently restarting. `doctor` is an offline wiring check, not provider authorization or scientific validation.

`init` copies the runtime, schemas/configuration and execution instructions into `environment_snapshot/`, recording their hashes and a condition-specific `tool_execution_policy` in state. Use the copied controller for future invocations. All role tasks reference its instruction paths; shared repository edits cannot silently update a live run. Changed snapshot files, policy or comparison condition prevent dispatch. Earlier runs without this snapshot retain their old runtime; adopting the new policy requires an explicit versioned continuation, preserving historical evidence, outstanding jobs and cumulative limits. Do not edit a saved state to imitate migration. A changed execution policy is a separately identified comparison condition, not interchangeable benchmark evidence.

Optional policy JSON overrides named defaults: `active_seconds` (7200), `cpu_core_hours` (16), `gpu_hours` (1), `service_spend_usd` (0), `call_timeout_seconds` (900), `max_stage_attempts` (3), `max_repairs_per_stage` (2), `max_review_attempts` (2), `poll_seconds` (5), `max_pending_polls` (120), and `deadline_utc` (null or an ISO timestamp with timezone). Setup and campaign counters share this total; explicit external limits remain binding. A new directory does not authorize renewal of an expired historical allowance. This budget contract is not a security sandbox: provider caps, scientific-job reservations and quotas need harness enforcement. The runtime meters local waited CPU and time; external usage requires actual accounting. Agent-provider inference billing remains the configured harness's responsibility.

For another harness, the command backend accepts an argv list, with no shell expansion:

```json
{"backend": "command", "argv": ["/path/to/adapter", "--task", "{task_file}", "--response", "{response_file}", "--role", "{role}"]}
```

Supported placeholders are `{task_file}`, `{response_file}`, `{prompt_file}` and `{role}`. The adapter must actually execute the role and write its response artifact; stdout is only a log.

## Common task and artifact rules

### Fresh start

Use a new harness session and run directory with `agent_selected` unless the user explicitly requests a prescribed-tool comparison. Initializing the controller freezes the current environment; it does not dispatch science. Start only under the fresh run's resource policy and existing service entitlement. Do not inherit an old session, candidate, accepted gate, inference patch or expired allocation. Reference inputs may be reused after identity/applicability review and new request binding. Preserve historical reports and uncertain remote-job records separately to prevent duplicate submissions; stopping a local chat does not cancel a remote job.

Discover ready executors for the planned stages first. Generate a diverse batch within frozen quotas, use inexpensive screening before costly assessment, and let the reviewer select bounded refinement or a supported alternative. A pilot is an integration test, not a main campaign. Missing later capabilities do not prohibit independent eligible work, but missing chemistry or other mandatory evidence prevents final qualification. Routine choices and repairs are internal agent decisions within the declared policy; a real access denial or exhausted allocation remains binding.

### Real tool execution

`tool_execution_policy` is mandatory for controller tasks and applies to executor, reviewer and repair roles. In `agent_selected`, use actual scientific executors exposed through Boltzmann or ToolUniverse. Verify schema, backend readiness, version/applicability and supported chain/state inputs; a catalogue entry may be a local wrapper. Do not automatically install/download prediction models, train replacements or reimplement inference. In `tools_specified`, the frozen request and hashed input manifests define the exact tools, including explicitly specified local implementations. The platform policy must not silently replace them.

Small Python scripts may perform preparation, conversion, mapping, numerical geometry checks, output validation and analysis. They cannot escape provider policy using network/subprocess calls or replace required predictions with descriptors. External chemistry is permitted only for a recorded provider capability gap, with a justified method/version, valid inputs and controls, existing access/resource authorization and independent review, while retaining prescribed-tool constraints. Inference-internal modifications belong to an explicit, separately versioned development scope; record pre/postprocessing and test before adoption.

Tool locks accept a real local code commit/container digest or a `service_provenance` record for hosted execution. The hosted record contains provider, service ID, actually reported version (or `undisclosed`), retrieval timestamp, a hashed contract capture and reproducibility limitations. This does not pin private weights or establish control comparability; reviewers must evaluate those gaps. Both routes still require real execution records.

**Must use real tools.** For each claimed calculation, retain tool/provider identity, version (or disclosed backend-version gap), hashed inputs, parameters, actual invocation, completion receipt and hashed raw outputs. Scientific stages return the `execution_evidence` artifact below. Retain error receipts for failed attempts. Independent reviewers trace claims to these records. Discovery, imported packages, downloaded assets, test fixtures, mocks and agent opinions cannot establish a prediction. An unsupported calculation remains unresolved. Software-test fixtures are explicitly synthetic and provide no scientific qualification.

The controller pins these policies and checks artifact identity; it does not attest provider execution or intercept every tool call. Provider allowlists, chemistry exceptions, shell/Python network and subprocess restrictions, and resource reservations must be implemented by the configured harness. Arbitrary command adapters are not a sandbox. Honest execution evidence plus scientific review remains necessary even when all structural JSON checks pass.

### Task and evidence identity

Read the complete `task.json`. It supplies the run/stage IDs, mode, scientific request, input hashes, condition, accepted artifacts, expected output kinds, remaining limits, idempotency key, history and any role-specific response contract. The response is one finite JSON object written atomically to the supplied response-file path. Duplicate JSON keys, non-finite numbers, stale response files and symbolic-link response files are rejected.

The bridge adds `_execution_window` with the actual call deadline, response deadline, reserved response time and configured SCI `max_turns` (null for a generic command adapter). This overrides any caller-supplied value for that field. Reserve a final tool turn to persist a partial or complete response. A campaign budget does not extend a finite agent call. Check whether another tool operation can finish and persist its receipt before starting it; return `pending` with recorded remote handles when necessary. A killed submission remains uncertain until reconciled and must not be repeated blindly.

Top-level scientific artifacts use `{"kind": "candidate_manifest", "path": "attempts/.../candidates.json", "sha256": "<64 lowercase hex characters>"}`. The placeholder illustrates the shape; calculate the actual file hash. Kinds must be unique within a response. Paths are absolute or relative to the **run root**, not the invocation directory. Write new immutable attempt files and preserve originals. Hashes are SHA-256 of file bytes; nested references in generation/full profiles use their schemas' `{path_or_uri, sha256, description}` shape. URI evidence must be materialized locally before validation. Accepted artifacts and their nested evidence must retain their recorded identity.

Object-binding hashes use `contracts.object_hash(value)`: SHA-256 of `json.dumps(value, sort_keys=True, allow_nan=False).encode()`. This differs from hashing a pretty-printed JSON file. Use `contracts.candidate_hash(record)` for candidate result bindings; do not choose a different serialization.

## Executor response

```json
{
  "status": "completed",
  "artifacts": [],
  "job_handles": [],
  "usage": {"external_cpu_core_hours": 0, "gpu_hours": 0, "service_spend_usd": 0}
}
```

Allowed status values are `completed`, `failed`, `pending`, `blocked` and `needs_input`. Incomplete responses include `failure: {"category": "execution", "message": "actual failure and remaining requirement"}` and retain available artifacts. Zero usage is valid only when no usage occurred. Each execution, poll, repair or reconciliation response reports **increments since the last accounted response**: CPU outside the bridge's local waited-process measurement, scientific GPU device-hours, and scientific-service spend. Do not double-count local CPU, repeat cumulative remote costs or replace unknown usage with zero.

Every role receives `startup_policy` and `method_validation_policy`. For a hosted executor, check actual schema/access, input parsing and mapping, supported assembly/state inputs, output/receipt contracts, job status and resource limits. Private inference traces, local checkpoints and backend runtime internals are not prerequisites merely to call a service; disclose unavailable provenance and assess its implications for the claim. For a permitted local executor, exercise parser/features, unique mappings, trusted checkpoint loading, device/runtime, logging and instrumentation together wherever feasible. Record checks that require inference. Resolve routine launcher metadata from the existing policy; do not invent approval flags as authorization. Record and test corrections before a bounded retry.

Abbreviated schedules are integration diagnostics unless quality equivalence is validated. Record initial noise/placeholders, actual model predictions and subsequent coordinate transformations separately. Check fixed-atom identities, final covalent compatibility and ligand contacts together. Whole-residue fixing is a run-specific method choice. Demonstrate combined assembly/motif/occupancy behavior under supported sampling; a symmetry flag, two chain records or identical placeholder sequences alone cannot establish assembly suitability.

A genuine execution-tool denial or approval timeout requires `failure.category: execution_approval`, the exact `message`, `blocked_command`, and the actual approval request ID or receipt when available. The controller retains this as `execution_approval_block` and stops without repair or an alternative launch route. This applies to executor, reviewer and repair responses. Approval must occur through the supported gate; an expired allocation also needs an explicitly granted continuation. This is distinct from an ordinary missing dependency or metadata mismatch, which is internally repairable. The harness remains responsible for enforcing access on individual tool calls.

An actual manual or configured smart-mode approval satisfies the gate for that exact operation. Record the decision and continue within the existing resource limits; do not require another manual prompt unless the user explicitly requested manual approval. Do not change approval settings, manufacture receipts or reuse one operation's approval for other commands. A successful dependency check does not authorize a scientific job outside the run policy.

| Stage | Required completed artifact kinds | Scientific purpose |
| --- | --- | --- |
| `prepare` | `resolved_request`, `generation_profile`, `evaluation_plan` | Resolve intent and review generation inputs, not the entire final chemistry profile. |
| `generate` | `candidate_manifest` | Actual new scaffolds and designed sequences with current provenance. |
| `sequence_screen`, `fold`, `aggregation`, `complex`, `catalytic_states`, `chemistry` | `candidate_manifest`, `stage_evidence` | Current candidates plus actual stage checks, applicability and uncertainty. |
| `evaluate` | `evaluation` | Partial results or full rule-based qualification. |

In addition to the table, every completed stage except `prepare` and `evaluate` requires `execution_evidence`. The other permitted top-level artifact kinds are `stage_report` and `capability_registry`. `qualified_profile` is allowed only at `chemistry` or `evaluate`; a later response cannot replace an already accepted profile with different contents. Frozen preparation kinds (`resolved_request`, `generation_profile`, `evaluation_plan`) cannot be returned by later stages. Place supporting scientific files in the appropriate manifest/evidence references, not arbitrary top-level kinds. Every returned file must exist with its stated hash. A successful process exit alone is not completion.

### Execution evidence

The `execution_evidence` JSON binds `stage`, `condition`, `policy_sha256` (the object hash of the task's `tool_execution_policy`), and `candidate_manifest_sha256` (the exact returned manifest's file hash). Its nonempty `records` list contains one entry per contributing operation:

- `route`: one of this condition's permitted execution routes.
- `tool_id`, `tool_version`, `purpose`, `parameters`, and `status: completed`. Disclose an unavailable provider version rather than inventing one.
- A real `job_id`, an executed argv-list `command`, or a hashed `invocation` artifact containing the actual synchronous call. Tools without job IDs need not invent them.
- A nonempty hashed `receipt` artifact and nonempty lists of hashed `inputs` and `raw_outputs`, including at least one nonempty raw output. Each uses the `{path, sha256}` artifact shape. Captured invocations and chemistry-exception evidence must also be nonempty. Empty auxiliary files such as a legitimately empty alignment remain possible; they cannot replace primary execution evidence. Capture original responses locally, excluding credentials; retain source/provider provenance.

Use `purpose: model_prediction` or `chemistry_calculation` for scientific predictions/calculations. In `generate`, `sequence_screen`, `fold`, `aggregation` and `chemistry`, at least one permitted scientific executor is required; support-only scripts cannot complete these prediction stages. Input/state construction and geometry checks in `complex` or `catalytic_states` may use permitted support scripts when the declared operation needs no prediction; this never supplies missing predictive or chemical evidence. Existing stage prerequisites and review still apply.

For `local_python_support`, `purpose` must be one of the policy's enumerated preparation/check/analysis purposes. For `external_chemistry`, `purpose` must be `chemistry_calculation`, the stage must be `complex`, `catalytic_states` or `chemistry`, and the record must include `justification` plus hashed `capability_gap_evidence` and `method_and_controls` artifacts. Access and resource authority must already exist. For `prescribed_tool`, and external chemistry in `tools_specified`, include `prescribed_intent_sha256` from the task; the reviewer must also verify exact-tool compatibility with that frozen intent.

The runtime checks declared routes, bindings, required records and artifact hashes. It cannot authenticate a provider from self-reported metadata or intercept every worker call. The harness enforces tool/network/subprocess permissions and reservations; the reviewer verifies receipts, input identity, actual outputs, scientific applicability and controls. Contract validity alone never establishes execution authenticity or enzyme qualification.

`resolved_request` follows [request.schema.json](../config/request.schema.json). `generation_profile` follows [generation.schema.json](../config/generation.schema.json), has `status: ready`, and requires actual readiness review.

The generation schema version is `1.1`. Its required `request_sha256` is `contracts.object_hash(resolved_request)`. The controller rejects preparation with a different binding. For an existing profile, the agent reviews reaction, assembly, motif, conditions and method applicability before creating a new bound preparation record; copying a hash is not scientific review. Biological settings from examples and case studies must never become target-independent defaults.

`evaluation_plan` contains:

```json
{
  "objective": "The intended conversion and scientific requirements",
  "request_sha256": "<object_hash of the resolved request>",
  "calibration_basis": "reference_controls_only",
  "required_groups": ["reaction_identity", "reactive_geometry", "protonation_and_stabilization", "states_and_chemical_steps", "fold_and_physical_integrity", "solubility", "aggregation", "operating_compatibility", "assembly_and_interface"]
}
```

These objectives and required groups are frozen before generation. Later methods and criteria must be justified using references/controls, not tuned until a candidate passes. Preparation cannot manufacture thresholds or claim a qualified reaction merely because JSON validation passes.

## Candidate and stage evidence

`candidate_manifest` is an object with a `candidates` array. Each record contains:

- `candidate_id`: unique nonempty identifier using letters, numbers, `_`, `.` or `-`, beginning with a letter or number.
- `revision`: positive integer. The canonical revision, sequence and structure are fixed by the accepted `generate` output. A change requires `repair_from: "generate"`, a new revision and invalidation of dependent evidence.
- `generation_kind: "de_novo"` and `sequence_designed: true`, supported by actual provenance. A reference-backbone redesign or placeholder scaffold must not be relabeled to satisfy these fields.
- `status`: `exploratory`, `screened`, `chemistry_evaluated`, `rejected` or `unresolved`.
- `sequence` and `structure`: artifact references with `path` or `path_or_uri` and `sha256`. The FASTA contains one unique, nonempty canonical uppercase amino-acid sequence; equivalent homodimer copies must use the same sequence. Requested length limits apply per unique sequence. The structure file contains the complete declared candidate assembly.

Retain chain/site/atom mapping and generation evidence as additional referenced data. File/hash validation does not inspect physical geometry: scientific adapters and review must check chain count, tied sequences, motif geometry, provenance and model applicability. Keep the designed structure as the canonical candidate structure; independently predicted structures and calculated state models belong in `stage_evidence` references. Later manifests can update assessment status but cannot silently substitute a new revision, sequence or structure. Candidate IDs and revisions—not just filenames—bind subsequent results. Generation, refinement and chemistry limits are cumulative across attempts and repairs; invalidation does not renew them.

`stage_evidence` requires `stage` equal to the current stage ID, `candidate_manifest_sha256` equal to the **candidate-manifest file artifact hash in this response**, and a `checks` array describing actual checks and outcomes. Include candidate/revision identity, raw values and units where meaningful, source artifacts, applicability and uncertainty. The reviewer judges scientific relevance; an empty or declarative checklist cannot establish scientific success. Accepted stage completion is distinct from qualification of its candidates.

## Independent assessment models

The current implemented route requires sequence-based prediction with no coordinate templates or coordinate restraints (`coordinate_input_sha256: []`). Sequence alignments are permitted and their information basis must be disclosed. Do not invent an empty coordinate-input list when a provider's template behavior is unknown. Template-assisted prediction can be scientifically useful, but admission of that route needs an explicit contract extension and appropriately matched controls.

Agents prepare these records; the user does not fill them in. A sequence-input predictor can run even when the generated scaffold is defective. Assessment contract 2.1 requires a nonempty `stage_evidence.assessment_models` list at `fold`, with one model for every candidate in that stage's manifest, for both ordinary and sequence-only generation. Omitted, empty or malformed models block fold acceptance even if the reviewer accepts the stage. Record:

- `candidate_id`, `revision`, `sequence_sha256`, `generated_structure_sha256`: bind the unchanged candidate and preserve its generated scaffold.
- `basis: independent_sequence_prediction` and `structure`: a hashed, normalized PDB containing every declared chain with the exact candidate sequence. Preserve original returned coordinates separately. Explicitly normalize CIF, model choice, chain IDs and alternate locations when needed; record those transformations.
- `prediction_record`: hashed JSON with `sequence_sha256`, `structure_sha256`, `input_basis: sequence`, `coordinate_input_sha256: []`, `method`, `version`, nonempty `settings` and hashed `raw_output`. Record templates/settings honestly; this route must not consume the defective generated coordinates. A coordinate-conditioned method needs a separately supported preparation route.
- `method_validation`: hashed JSON following the assessment contract below. It binds control evidence and applicability to the actual method/settings and evaluation plan. It is required for promotion, not for running exploratory predictions or controls.
- `integrity_report`: hashed JSON with candidate ID/revision, sequence and assessment-structure hashes, `evaluation_plan_sha256`, `status: PASS`, nonempty hashed `reference_controls`, and `checks`. Checks identify `check_id`, status and nonempty hashed `evidence`; required IDs are `atom_completeness`, `peptide_geometry`, `ca_stereochemistry`, `clashes`, `catalytic_mapping` and `assembly_geometry`.

The `method_validation` file has `schema_version: "1.0"`, the prediction record's `method` and `version`, `settings_sha256: object_hash(prediction_record.settings)`, `evaluation_plan_sha256`, and `status`. Its `applicability` object contains `status`, the resolved `assembly_kind`, text fields `candidate_information_basis`, `control_information_basis`, `rationale`, and nonempty hashed `evidence`. Its nonempty `controls` array contains unique `control_id`, `kind: positive|negative`, `expected_outcome`, `status`, and nonempty hashed `evidence` for each required control. Include at least one applicable known-positive reference or benchmark; add negative controls required by the scientific plan. A negative control passes when its predeclared negative behavior is recovered. Promotion requires PASS in all these records and independent inspection of the supporting calculations; parsing JSON never validates science.

Failed reference prediction yields `METHOD_CONTROL_FAILED`; incomplete control or applicability evidence yields `METHOD_CONTROL_UNRESOLVED` or `METHOD_APPLICABILITY_UNRESOLVED`. These do not reject the candidate. Wrong method/settings/plan binding yields `METHOD_VALIDATION_BINDING_MISMATCH`. Candidate geometry has separate `STRUCTURAL_INTEGRITY_FAILED` and `STRUCTURAL_INTEGRITY_UNRESOLVED` errors; stale model bindings yield `ASSESSMENT_IDENTITY_MISMATCH`. Preserve unpromoted predictions in attempt artifacts. Earlier records need evidence-backed migration in a new versioned continuation; do not rewrite historical outcomes or mark missing controls PASS.

Before diagnosing a method-control failure, verify the reference assembly, residue correspondence and equivalent chain permutations. Record actual alignments, templates and restraints. A reference predicted with richer information does not alone validate the candidate's poorer-information regime. Predeclare bounded sampling and use supported pinned settings; select methods from control evidence, not the highest candidate score. Account for stochastic uncertainty and all prespecified samples. Candidate/native interface identity is required only if frozen in the task; a de novo scaffold can have a different valid interface. Keep enzyme-specific residue positions, cis links, occupancy and thresholds in the run profile.

These integrity checks use the declared criteria and matched controls, including supported cis links and all required chains/sites. For a monomer, assembly geometry checks monomer identity; it does not invent an interface requirement. File/sequence validation cannot verify the truth of a geometry report: the fresh reviewer must inspect calculations, numerical results, conditions, applicability and uncertainty. A reported failure or missing check prevents promotion. Independent prediction does not prove scaffold novelty, oligomerization or catalysis.

Identify which claims each failed control actually tests. Partial observations remain in attempt evidence; this does not make the complete assessment model eligible for structural promotion. Sequence-based property assessments can proceed with their own applicable methods and controls; descriptors alone do not satisfy prediction requirements. Additional reference information can diagnose a failure but does not automatically validate the candidate regime. Reconcile catalytic correspondence using the generator's atom/motif provenance and structural evidence; pairwise sequence-alignment shifts alone must not overwrite a de novo design's mapping.

Each later structural stage supplies `assessment_models_sha256 = contracts.object_hash(models)` in its stage evidence. A final qualification request repeats that binding. The models are supplied in subsequent controller tasks. Every generation route requires these independently predicted, reviewed models before final qualification. The controller revalidates the fold artifacts on restart and before accepting dependent evidence; saved status alone is insufficient. Downstream candidates must be covered by the accepted fold models. The final `assembly_map.structure_sha256` and exported structure refer to the assessment model; generated coordinates remain immutable provenance and cannot be an export fallback. Changes to a model require invalidating `fold` and dependent evidence; changes to the sequence or canonical generated scaffold require a new candidate revision from `generate`. `08_results/assessment_models.json` retains accepted models even when chemistry is incomplete.

This separation was informed by the read-only review of [enzyme variant optimization](https://github.com/boltzmannlabs/science-environments/tree/538cb74/environments/enzyme-variant-optimization), particularly its structure bindings, submission store, connector, workflow and recovery tests. The transferable patterns are exact candidate/model identity, durable job receipts, pre-submission contract checks and bounded recovery. The de novo controller now also verifies original job identity on every polling response and archives superseded exports. Its single-chain automatic mapping and variant objectives were not imported; this implementation checks the current request's full monomer/homodimer sequence mapping. Tool choice remains capability-based, with actual contracts and versions recorded per run. This controller does not implement the optimizer's native host-level submission reservation and action restrictions; those remain responsibilities of the configured harness. No optimizer scientific results or qualification claims transfer to this environment.

## Reviewer and repair responses

The reviewer inspects the supplied output and immutable evidence in a fresh conversation. It performs read-only review; request repair or further execution for additional scientific calculations.

```json
{
  "decision": "repair",
  "reason": "Evidence-grounded diagnosis and required correction",
  "reviewed_sha256": "<task.output_sha256>",
  "repair_from": "generate"
}
```

Decisions are `accept`, `accept_sequence_only`, `retry`, `repair`, `reject`, `blocked` or `needs_input`. `accept_sequence_only` is permitted only at `generate`, with a real candidate manifest and hashed `stage_report` recording `geometry_status: failed|unresolved` and `sequence_only_eligible: true`. It permits screening and independent folding from the unchanged sequence; it does not accept the generated geometry. Before structural promotion, `fold` must supply the assessment-model evidence above and independently reviewed `structural_integrity_ready: true`. Optional `stage_evidence.structure_preparation` records remain supporting evidence; the former preparation-only fold acceptance route is removed. A preparation or minimization report cannot establish independent folding, regardless of the generation acceptance mode. Failed geometry is retained as failure; a source-code correction or reviewer opinion cannot establish a molecular PASS.

This revision changes admission behavior without changing the method-validation JSON field format. Existing runs remain pinned to their implementation hashes. Preserve historical results; an explicit versioned continuation must revalidate imported evidence under this contract without silently resetting resource limits or relabeling previous failures as passes.

`reviewed_sha256` must equal the supplied output fingerprint. `repair_from`, when used, is the current or an earlier stage. The controller cannot accept an output with contract errors. Use `reject` for a verified disqualifying scientific failure, not an installation problem. Ask the user only for essential unresolved intent or access outside policy; routine technical choices belong to the agents.

The target-independent `runtime/structure_preparation.py` can bound PDBFixer's otherwise unbounded hidden heavy-atom minimizations and collision dynamics per run-specific mapping; an exhausted cap is a recorded failure with the template-only checkpoint preserved. A separately declared `template_only_then_bounded_outer_minimization` mode bypasses that hidden packing step (zero internal iterations and dynamics), runs the same capped outer local preparation on candidate and reference, and retains hashed template/heavy-atom/hydrogenated checkpoints. This mode is not equivalent to fully packed sidechains or independent folding: always audit sidechain and backbone chirality, the mapped cis links, both chains and residual geometry against matched controls. A zero exit means preparation executed, not that the structural-integrity rule is PASS; fold still requires independent structural review, and all original candidate artifacts remain immutable.

`needs_input` requires an `input_request` object in the executor response and reviewer decision. Its `reason_code` and `item` must match `task.user_input_contract.allowed_reason_items`; include a concise `question`, `why_unresolved`, and a nonempty `resolution_attempts` list of inspected `source`/`finding` objects. Allowed reasons are essential unresolved goal/reaction ambiguity, required access/resources outside existing authorization, or incompatible explicit user requirements. The reviewer verifies the evidence and whether an authorized alternative exists. Missing scientific profiles, omitted pH/temperature/host, seeds, normal tool selection, installation and stage approval are internal preparation decisions. Unspecified settings must be resolved from the supplied policy and evidence with uncertainty recorded.

The controller redirects unsupported or malformed questions to bounded internal repair and records `user_question_redirected`. Exhausted repairs return an explicit partial/blocker report; they cannot invent missing science or authorize more resources. Accepted questions appear as `input_request` in the final report. Every role receives the autonomy policy, fallback settings and remaining limits. This behavior requires execution through the controller; an unrelated chat reading a Markdown file does not automatically acquire persistent execution.

The local structure-preparation adapter uses named N/CA/C anchors when reconstructing missing CB atoms and restricts template alignment to proper rotations. The versioned, process-local dependency wrapper restores the original library function on exit; it does not edit the installed package. Revalidate this private-API integration on dependency changes. It explicitly selects CPU execution, records intermediate heavy-atom and hydrogenated structures, and retains the final chirality and cis checks. Correct template placement alone does not establish that minimization preserves stereochemistry or that the prepared model is physically acceptable. Reconstruction controls should include a reference with the same classes of atoms removed, not only a complete native structure that bypasses reconstruction.

This development preparation adapter requires one normalized PDB model, explicit chain labels, resolved alternate locations and a reversible removal of insertion codes before use. It rejects undefined angles/dihedrals rather than classifying them as cis. Its cis restraints currently support reference-supported cis-before-Pro links only; rare genuine non-Pro cis peptides require another validated preparation route. The 35-degree cis-like label is descriptive, not a universal scientific acceptance threshold. Runtime versions are measured from the installation. Local restrained vacuum energies are preparation diagnostics, not solvent free energies, thermal stability or catalytic barriers.

Repair returns `status: "repaired"` or `"blocked"`, a factual `summary`, hashed `artifacts` showing the diagnosis/change, and incremental `usage`. Repair preserves reaction, assembly, explicit constraints and evaluation intent. Changes to a canonical candidate require repair from `generate`, followed by the new revision and dependent re-evaluation. The controller invalidates affected stages and performs bounded re-execution; repair does not award scientific PASS or reset attempt, candidate or resource counters.

For a remote job, `pending` includes nonempty `job_handles: [{"provider": "provider-name", "id": "actual-job-id"}]`. Persist handles and submission/idempotency information immediately. A polling task only inspects those jobs; it must not resubmit. Receipts remain durable until their results and usage are applied to state; a restart reconciles uncertain execution before another submission. A reconciliation task uses `status: "reconciled"`, `safe_to_retry`, `job_handles`, nonempty hashed reconciliation `artifacts`, recovered incremental `usage`, and optional `completed_response`. A retry is safe only when earlier execution is accounted for and no unresolved active jobs remain. A local timeout does not cancel a remote job. Unknown or still-active jobs remain explicit in the final report, not silently treated as completed or cancelled.

Every poll response includes `polled_job_handles` containing exactly the task's original provider/ID pairs, including after completion. The reviewer must trace downloaded artifacts to those jobs' actual provider receipts; echoing identifiers alone is not evidence of provenance. While any job in a batch remains unresolved, return `pending` with all original `job_handles` and the known per-job states. Return `completed` or `failed` with empty `job_handles` only after all jobs are terminal. Missing, replaced or duplicate identities prevent promotion and retain original handles for reconciliation. The same checks apply when recovering a saved polling receipt after interruption. Incremental usage remains accounted even when a result is rejected.

## Final evaluation

Before qualification, every active site must have a declared directed path from a reactant state to a product state. This graph check does not validate atom maps, stoichiometry, transition states or catalytic regeneration; those still require actual chemistry evidence. Preserve each generation site's catalytic-map hash in the full profile. Each required request property target must map to a required rule via zero-based `request_target_index`, retaining the endpoint (`metric`), units, operator and value; additional stricter gates may be separate rules. Finalization repeats the qualification contract checks.

For incomplete scientific evidence, return an `evaluation` artifact with `qualification_requested: false`, nonempty `unresolved` explanations and `evaluation_plan_sha256` equal to the **evaluation-plan file artifact hash**. Preserve completed exploratory results. This produces a partial outcome, possibly with zero qualified candidates.

Full qualification requires `qualification_requested: true`, the same `evaluation_plan_sha256`, `protocol_sha256` matching a current `qualified_profile` artifact, and candidate evaluations:

```json
{
  "qualification_requested": true,
  "evaluation_plan_sha256": "<frozen plan file hash>",
  "protocol_sha256": "<qualified profile file hash>",
  "candidates": [{
    "candidate_id": "candidate_001",
    "candidate_sha256": "<candidate_hash of the current record>",
    "rules": [{
      "rule_id": "an_existing_profile_rule",
      "status": "UNRESOLVED",
      "value": null,
      "units": "the frozen rule units",
      "evidence": []
    }]
  }]
}
```

This format illustration does not qualify a candidate. The full profile must pass [protocol.schema.json](../config/protocol.schema.json), state/step/site/chain coverage checks and actual scientific review. Evidence must be current, nonempty where required and bound to the current candidate revision. Rule IDs must already exist in the frozen profile; provided `chain_ids`, `site_ids`, `state_ids` and `step_ids` must match its coverage. Units must match. Every mandatory rule needs PASS, supported evidence and a non-null value satisfying its frozen predicate; boolean and numerical values are distinct. Missing, failed or unresolved required evidence prevents qualification. High confidence or reviewer approval cannot compensate for failed chemistry.

The controller retains `state.json`, `trajectory.jsonl`, per-call tasks/responses/logs/receipts and `report.json`, including `outstanding_jobs` and any `unreconciled_call`. It materializes the [scientific result bundle](../ENVIRONMENT_SPEC.md#9-final-output-contract) in `08_results/`. Only qualified candidates enter `designed_sequences.fasta`; incomplete runs have an empty qualified FASTA and explicit missing evidence. Final qualified candidates must also include a hashed `assembly_map` artifact with `candidate_id`, current `sequence_sha256` and `structure_sha256`, and the declared `chain_ids` and `site_ids`. When assessment models are used, `structure_sha256` identifies the reviewed model exported in the result bundle. These records do not substitute for the underlying calculations.

If qualified candidates or accepted artifact versions change, archive any existing structure/chemistry export under `result_history/<unique-id>/` with a `SUPERSEDED.json` marker before rebuilding `08_results/`. Remove superseded structure and chemistry copies from the current bundle; preserve their original attempt artifacts and archived exports. Rewriting an unchanged bundle creates no redundant archive. Historical qualification is not a current result. These exports are derived files, not canonical inputs for subsequent stages.

When a run terminates, a local stage formerly marked `running` becomes `incomplete`. A stage with outstanding remote handles or an uncertain call becomes `awaiting_reconciliation`; the handles remain in the report. This is a controller state, not a claim that remote execution was cancelled.
