# Denovo Enzyme Design

**Status: In Progress.** This package includes a resumable execution controller and scientific contracts. Scientific adapters, reaction-specific chemistry qualification and end-to-end enzyme validation remain separate requirements.

**Default operation: agent-led execution and recovery.** Give the existing harness the scientific request and available inputs. The [controller](runtime/controller.py) owns stage progression, invokes execution and independent review, records evidence and resumes bounded repairs without a new user prompt. Routine settings and technical recovery are agent decisions. Each stage requires its own valid inputs; a missing final chemistry profile no longer blocks all exploratory generation.

Accept a requested chemical conversion and design requirements; generate enzyme candidates; evaluate folding, protein properties and catalytic chemistry; return a traceable shortlist. Fixed execution is implemented; reinforcement learning remains a specified extension using the same mandatory acceptance rules.

**One environment, different enzyme requests.** The workflow and recovery logic are shared. The agent prepares a separate reaction/assembly/motif/evaluation profile for each request; the user does not write enzyme-specific chemistry rules. Enzyme identifiers, residue numbers, chain lengths, research conditions and numerical chemistry gates belong to that run's evidence, never universal defaults. L-DEX YL is a development case study only.

Generation profiles are bound to the current resolved request by hash. Reusing another enzyme's profile requires a new applicability review and request binding. The controller rejects stale bindings before generation; the reviewer must still verify the actual biology. A matching hash alone cannot establish scientific correctness.

Recovery distinguishes startup/integration problems, failed method controls, and candidate-specific defects. Agents test startup components together, resolve routine failures within the run policy, and validate prediction methods on applicable controls before structural promotion. Exploratory predictions can run while those controls are being established. A failed control does not by itself reject a design. Genuine execution-tool approval blocks are preserved and cannot be bypassed by automatic repair. These rules are target-independent; see the [runtime contracts](runtime/CONTRACTS.md).

Configured smart-mode approval counts for the approved operation; a second manual prompt is unnecessary unless explicitly requested. Remote polling preserves the original provider/job IDs, and invalidated structure/chemistry exports move to marked history. The default agent-selected mode chooses suitable tools and records their actual contracts and versions; it does not require a fixed tool list.

**Must use real tools.** Scientific predictions and calculations require actual execution receipts and hashed raw outputs. Catalog searches, downloaded weights, mock results, descriptors and agent opinions cannot stand in for a prediction. New `agent_selected` runs use Boltzmann or ToolUniverse executors, with small Python scripts for preparation/checks/analysis and a documented external-chemistry exception. `tools_specified` runs preserve their prescribed implementations, including explicitly specified local tools. The [execution policy](ENVIRONMENT_SPEC.md#tool-execution-and-run-isolation) defines the limits; exact tools and versions belong in each run's capability registry.

**Keep paired runs isolated.** New controller runs freeze their condition, execution policy, runtime and instructions in `environment_snapshot/`. Resume through that snapshot's `runtime/controller.py`; workers receive its Markdown paths. Editing the shared repository does not migrate an existing run. Earlier runs without a snapshot must use their recorded runtime/instructions or an explicit versioned continuation, preserving evidence, unresolved jobs and cumulative usage. Changing a comparison's tool policy creates a new condition and must be reported as such.

Every generation route requires independent, sequence-bound assessment models with applicable method controls and reviewed integrity evidence before `fold` can be accepted. Preparation or minimization alone cannot meet that requirement. Restart, downstream stages and final qualification recheck the same evidence; qualified exports cannot fall back to generated coordinates. This is assessment contract 2.1, with unchanged evidence-field formats. Preserve earlier runs and use an explicit versioned continuation when adopting the updated runtime; old acceptance flags are not validation.

## Read in this order

For a **fresh run**, start a new harness session and controller directory using `agent_selected`. Review any reused reference inputs; leave historical candidates, PASS flags and inference patches in their original runs. Discover ready platform executors before spending on generation, then plan a diverse batch within the current budget. The default small pilot tests integration; it is not a production campaign. See [fresh-start instructions](runtime/CONTRACTS.md#fresh-start).

1. [Agent task](tasks/denovo_enzyme_001.md): the task-facing description, 14 required execution steps, constraints and expected deliverable, organized like the supplied BioDesignBench example.
2. [Environment specification](ENVIRONMENT_SPEC.md): inputs through final evaluation, including chemistry, RL, interfaces, failure handling and benchmarking.
3. [Environment configuration](config/environment.yaml), [request contract](config/request.schema.json), [generation contract](config/generation.schema.json) and [full protocol contract](config/protocol.schema.json): stage-specific entry and final qualification requirements.
4. [Acceptance plan](tests/ACCEPTANCE.md), [package checks](tests/specification-validation.json) and [runtime validation](tests/runtime-validation.json): what has been tested and what still requires scientific validation.
5. [Runtime contracts and usage](runtime/CONTRACTS.md): harness configuration, worker/reviewer responses, immutable evidence and resumable execution.
6. [Research notes](../../research/Denovo-Enzyme-Design/research-notes.md) and [references](../../research/Denovo-Enzyme-Design/references.md): rationale, scientific foundations, provenance and open work.

The task preserves the reference's Description, Target, Design Constraints, Expected Output, Constraints and Important Instructions sections. Its software-list section is replaced with Required Execution Steps. The specification describes operations, acceptance decisions and outputs without prescribing named scientific software.

## Package structure

```text
Denovo-Enzyme-Design/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/
│   ├── environment.yaml
│   ├── request.schema.json
│   ├── generation.schema.json
│   └── protocol.schema.json
├── runtime/
│   ├── controller.py
│   ├── agents.py
│   ├── contracts.py
│   ├── assessment.py
│   ├── structure_preparation.py
│   ├── reporting.py
│   └── CONTRACTS.md
├── tasks/
│   ├── denovo_enzyme_001.md
│   ├── request.example.json
│   └── homodimer.request.example.json
└── tests/
    ├── ACCEPTANCE.md
    ├── test_agents.py
    ├── test_assessment.py
    ├── test_contracts.py
    ├── test_controller.py
    ├── test_structure_preparation.py
    ├── runtime-validation.json
    ├── scientific-review.md
    ├── validate_spec.py
    └── specification-validation.json
```

The [monomer request](tasks/request.example.json) and [homodimer request](tasks/homodimer.request.example.json) illustrate input syntax only. Conditions, design counts and budgets are illustrative, not approved run limits. Neither request supplies a qualified reaction profile or a completed design run. No motifs, model weights, experimental results or invented benchmark scores are included.

## Scope

The scientific scope is soluble, cofactor-free **monomers and homodimers**. A monomer has one protein chain; a homodimer has two copies of one sequence. Each enabled combination needs working capabilities and reviewed generation inputs; final qualification additionally needs a qualified full reaction profile. Heterodimers, larger assemblies, metals, organic cofactors and membrane systems require extensions. Controller availability alone does not establish scientific support for a requested enzyme.

When assembly is unspecified, resolve it from biological evidence before generation; do not default to a monomer or infer it from the coordinate-file chain count. The homodimer path includes coupled sequence design, independent assembly assessment, interface checks and explicit active-site/state coverage. See [assembly requirements](ENVIRONMENT_SPEC.md#assembly-resolution-and-homodimer-contract).

Contract version 2.0 adds assembly, chain and site fields to reaction profiles. Earlier profiles require explicit migration and renewed qualification for their declared scope; changing the version string is insufficient.

The user supplies the conversion and any explicit requirements. The agent resolves omitted settings, prepares mapped chemistry and assembly inputs, and builds the scientific profile progressively. Generation readiness covers supported motifs, representations, constraints and generator behavior. Full catalytic states, control-tested methods and calibrated gates are required at their evaluation stages and before qualification.

Unspecified research settings are resolved from reference evidence and method applicability, with assumptions recorded. The request schema describes the resolved execution request, not a form the user must fill completely. A missing qualified profile starts preparation and eligible exploratory work; it does not authorize a qualification claim. The reviewer chooses accept, retry, repair, reject, blocked or needs-input based on current evidence. See [autonomous preparation](ENVIRONMENT_SPEC.md#autonomous-resolution-and-preparation).

The controller supports reviewed `accept_sequence_only` generation with a hashed defect report. Sequence screening and independent assembly prediction may use that unchanged FASTA while the generated coordinates remain unresolved. Prediction outputs are separate, sequence-bound assessment models; every chain must match the request, and independent geometry review with matched controls is required before downstream structural use. Results and final exports use the exact reviewed model version and retain the original generated scaffold. See [runtime contracts](runtime/CONTRACTS.md) for the agent-generated evidence fields. The optional structure-preparation adapter preserves original models and records its own limitations; successful minimization does not establish folding or catalysis. Previous runs remain pinned to their old implementation; use a new versioned run after runtime changes.

Resource policy is set once for a run. The fallback remains a small pilot: two generated assemblies, one chemistry finalist, no optional refinement, seed 42, and total ceilings of two active wall-hours, 16 CPU-core-hours and one GPU-hour. Setup and candidate work are accounted separately within those same totals unless explicitly allocated otherwise. Explicit deadlines and external limits still apply; an expired historical session is not renewed by this policy. This controller is not a security sandbox: scientific CPU/GPU and provider limits require harness reservation, metering and enforcement. No new paid-service spending is implied.

Candidate revisions and evidence remain bound to the accepted generation outputs. Repairs invalidate dependent results; independent predictions are recorded as assessment evidence. Durable receipts support restart reconciliation, and the final report lists outstanding remote jobs because a local timeout does not prove remote cancellation.

Reuse applicable shared preparation for paired tests and retain previous reports as historical evidence. Apply each run's frozen autonomy and execution policy when continuing; an older report's request for routine approval does not create a new approval requirement. Policy upgrades require an explicit versioned continuation.

## Validate this specification package

The [scientific/code review](tests/scientific-review.md) records the latest consistency corrections and remaining validation boundaries. Passing package tests does not establish that a designed sequence folds, forms its intended assembly or catalyses the reaction.

From this directory, with Python, PyYAML, jsonschema and NumPy available:

```bash
python3 tests/validate_spec.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

This checks document links, schemas, example requests, stage dependencies and policy invariants. Runtime behavior tests are separate; neither set establishes enzyme activity or qualifies a chemistry method.

Recorded validation includes software behavior tests and a prior live harness transport call that wrote the requested JSON response. The current counts, source hashes and scope are in the runtime validation report. No scientific model job was submitted by that transport check. Controller dependencies are `jsonschema` and `PyYAML`; the structure adapter and its tests additionally require NumPy. Executing that optional adapter requires its separately installed preparation dependencies; the OpenMM-specific test is skipped when OpenMM is unavailable. Tested versions and any separate runtime checks are recorded in the runtime validation report.

## Contribution and licensing

**Owner, tracking issue and reviewers:** pending assignment.

Repository location: `environments/Denovo-Enzyme-Design/`. Supporting research and sources are maintained in `research/Denovo-Enzyme-Design/`, following [CONTRIBUTING.md](../../CONTRIBUTING.md). The repository structure, contribution guidelines, PR template and license notice were read on 26 October 2026.

This is an implementation-and-specification contribution. Issue linkage and scientific/software review remain pending. Package and controller tests do not establish a scientifically validated enzyme-design environment.

The repository's [LICENSE](../../LICENSE) states that license selection is pending; it is not a license grant. This package does not add a separate license or redistribute third-party code, weights or restricted datasets.
