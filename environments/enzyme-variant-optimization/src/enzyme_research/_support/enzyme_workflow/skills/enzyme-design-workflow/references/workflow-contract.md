# Workflow contract

Five agent operations come from the independent `enzyme_workflow` add-on. They
reuse the authenticated Boltzmann toolset and supported pre/post tool-call hooks.
No original Agent-Scientist or Boltzmann connector file is modified.

`enzyme_workflow_start(specification)` takes an object with:

- `objective`: nonempty reaction/design objective.
- `approved`: JSON true after explicit user approval of the plan and budget.
- `steps`: 1–100 step objects.
- `initial_candidates`: optional local prepared structures (see below).

A step has `step_id`, `tool`, `experiment_name`, `inputs`, optional `depends_on`,
`expected_count`, `candidate_ids`, `selection` (`all` or `passed`),
`required_gates` (named preceding quality/geometry steps), and `max_retries` (0–3,
default 0). The experiment name is explicitly confirmed, unique across tracked
intents in this profile, and unrelated to the backend wire job name.

Scientific `inputs` omit credentials and server-generated identity fields.
The existing Boltzmann catalogue is the single authority for scientific inputs,
API names and call instructions. `enzyme_workflow_catalog` contains only workflow
stage, capabilities, adapters, activation and `contract_ref`/`contract_document`.
Read the referenced document before preparing inputs. The document hash is saved
with the plan; changed documentation requires plan review. The harness checks
JSON/credential safety and handoffs, not a duplicated scientific input schema.
Scientific validation remains with the agent's original contract procedure and
the remote worker. New optional fields need no duplicate registry update.

Current catalogue references identify a stable `entry` in the original canonical
`tool-contracts.v1.json`. Read that entry's request schema and call information;
`contract_document.entry` identifies it. Only the selected entry is hashed.
Legacy references may instead identify an explicit Markdown `section`. Do not
substitute the archived catalogue when a current entry cannot be resolved.

An input path may be a relative storage path or an artifact reference object:

`{"from_step":"generation","artifact":"structures","upload_as":"zip"}`

Supported conversions: `structures/zip`, `sequences/csv`, `sequences/fasta`,
`mapping/json`, or `artifact/artifact` for an unfiltered upstream artifact.
Sequence CSV has `seq_id,sequences`; candidate IDs become downstream record labels.
Whole archives cannot be forwarded after candidate selection changed their set.

CatPred has a dedicated local handoff adapter. A CatPred step additionally carries
`"handoff": {"smiles": "<user-supplied molecule>"}` for one shared molecule, or
`"handoff": {"smiles_by_candidate": {"<candidate_id>": "<molecule>"}}` for a map
covering exactly the selected candidates. Do not combine these two forms or
invent a molecule. This is workflow configuration, not another CatPred API field.
Its `input_path` artifact reference uses `sequences/csv`; the adapter writes
`seq_id,sequences,smiles`. The remote request still contains only the documented
tool inputs, normally the uploaded `input_path`.

For a pre-uploaded CSV path, the same local handoff and selected candidates record
the expected sequence/molecule pairs; returned pairs must match them exactly.
The adapter requires the updated all-three output and its per-mode uncertainty
columns. It rejects old kcat-only files with a clear schema error. It matches
returned rows to persisted sequence-SMILES pairs, not row order, and can ingest
without manually supplied bindings. Conflicting bindings or IDs fail.
Protein sequences and chemical SMILES are not lowercased. Chemically equivalent
but differently serialized molecules are not guessed to be identical; the current
combined CatPred output preserves its input sequence and SMILES strings.
Identical sequence/molecule pairs across candidate IDs fail before submission;
deduplicate candidates or explicitly approve separate jobs. Multi-chain sequence
rows are unsupported by this adapter. Input hashing, job download receipts,
duplicate-submission protection and approved retry budgets remain in force.

`enzyme_workflow_next(workflow_id, action, step_id, ...)`:

- `inspect`: show ready/waiting/running/ambiguous steps without remote polling.
- `prepare`: validate dependency/capability gates, request uploads or return one
  `boltzmann_submit` call; repeated prepare returns the same reserved intent.
- `record_upload`: `field` and actual connector `result` containing `s3_path`.
- `ingest`: actual downloaded `local_path`, optional authoritative top-level
  `member`, and `bindings` indexed by the exact output label. A binding contains
  either `candidate_id` for the same candidate or `parent_ids` for a new child.
  Optional `mapping` describes actual residue correspondences for structures.
- `retry`: allowed only after confirmed remote failure and within the approved
  per-step retry budget; never after ambiguous submission or poll timeout.
- `recover_submission`: actual original submit `result` (`doc_id`, `job_name`),
  not a new job or a fabricated ID.

Generation creates stable candidate IDs. Sequence changes invalidate old side-chain
coordinates. Structure capability requires actual finite coordinates; all-atom
capability requires all standard protein heavy atoms. EnzyControl outputs remain
backbone-only regardless of placeholder residue identities. Ligand presence does
not establish correct ligand chemistry, protonation or pose. Mapping availability
is not proof of catalytic residue identity; the geometry service resolves atoms.

State is in the current profile's `enzyme-workflows/state.sqlite`; reports and
hashed artifacts are under `enzyme-workflows/<workflow_id>/`. The database and
reports deliberately exclude authentication tokens and signed download URLs.
`enzyme_workflow_status` reads this local state; actual remote status still uses
`boltzmann_status`. `enzyme_workflow_report` exports JSON and candidate CSV.

All listed tools resolve their exact Node API `job_name` from the referenced section
of the original Boltzmann catalogue. They need no separate `settings.bindings`.
Documented diagnostic collections are recorded when available; a missing Mongo
collection does not block submission because the connector routes by job name.
`live_verified` remains false until actual testing; routing availability is not
proof that a backend is healthy or that a scientific result is correct.

RFD3, EnzyControl, DeepAllo, Catalytic Geometry and MolProbity use this same
catalogue resolution. Their wire job names come from their referenced entries,
not from Docker task names. No additional profile binding is required for them.
An explicit operator binding can still pause a tool or configure a separately
documented extension. It is not a second activation step for deployed tools.

`plugins.entries.enzyme_workflow.settings.contracts` admits additional workflow
adapters without changing original source. Each declares `stage`, `adapter`,
`requires` and `contract_ref` into the existing
catalogue. Optional `adapter_source` records provenance. Duplicate input schemas
are not accepted. Additional extensions need a documented catalogue reference
and routing configuration. No code or endpoint is accepted in a binding.

Enable the add-on through the host's normal plugin flow. Tool calls must pass
through native dispatch so its hooks run; directly importing/calling a handler
bypasses tracking. The add-on never replaces or patches connector handlers.
