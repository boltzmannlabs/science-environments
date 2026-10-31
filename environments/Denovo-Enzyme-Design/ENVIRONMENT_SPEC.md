# Denovo Enzyme Design — Environment Specification

**Environment ID:** `denovo-enzyme-design`

**Status:** In Progress — execution controller included; scientific qualification remains profile-specific.

**Intended runtime claim:** computational qualification under a named reaction profile. This specification delivers no qualified enzyme or experimentally established catalysis.

## 1. Objective and supported task

Given an intended substrate-to-product conversion, operating conditions and design constraints, produce up to K diverse, newly designed enzyme candidates. Every returned qualified candidate must pass its applicable chemistry, fold, solubility, aggregation and user-required gates.

This is a reusable enzyme-design environment, not an implementation dedicated to the enzyme in an example. Resolve the reaction, reference evidence, catalytic roles, assembly, cofactors, design size and conditions anew for each target. Keep all target-specific maps and values in the run's inputs and profiles. Shared code provides stage progression, evidence handling, capability selection, review and repair. A prior pilot supplies reusable engineering evidence only within its tested applicability; its biological settings and outputs cannot silently transfer to a new target.

One reusable environment uses a **generation-readiness contract** for exploratory generation and a **full reaction profile** for final qualification. These supply the mechanism, motif, assembly, supported representations and stage-specific evaluation settings as they become necessary. Scope is soluble, cofactor-free monomers and homodimers; a homodimer contains two copies of one protein sequence. Heterodimers, larger assemblies, membrane systems and cofactor-dependent chemistry require extensions. Unsupported prerequisites block the affected stage. Missing later evaluation capabilities do not prohibit earlier scientifically justified work, but they prevent qualification.

## 2. Inputs: user versus environment

| User supplies | Environment prepares |
| --- | --- |
| Reactant/product SMILES, molecular files or unambiguous identifiers; intended stereochemistry | Normalized participants, stoichiometry, atom maps, reaction steps and compatible profile |
| Operating requirements, when specified; relevant concentration and its basis, when known | Evidence-backed research conditions when unspecified, applicability checks and protonation/state alternatives |
| Sequence restrictions and property targets, when specified | Supported sequence bounds, fixed catalytic identities/atoms and reference geometry |
| Assembly preference and reference identifier, if known | Evidence-based biological assembly, chain mapping, interface requirements and active-site/state coverage |
| Requested shortlist size and approved compute budget, or explicit service defaults | Generation/evaluation quotas, implementation version lock and a chemistry reservation |

The agent resolves the request before validating it against [request.schema.json](config/request.schema.json); the schema is not a requirement for the user to manually supply every field. Preserve explicit requirements. An essential ambiguity that remains after evidence retrieval produces `NEEDS_INPUT`; scientific or infrastructure gaps that remain after bounded recovery produce `BLOCKED` or `PARTIAL` with an explicit reason. An unresolved stereoisomer or incompatible user requirement must not be silently replaced.

The monomer example uses ester hydrolysis; the homodimer example uses the L-DEX YL conversion. Both are syntax examples, not qualified profiles or authorization to spend their illustrative budgets. Missing `assembly` means `resolve_from_evidence`. The environment prepares the scientific assembly data; the user need not manually supply symmetry operators or chain maps.

Protein concentration, when supplied, must include its basis: total subunit equivalents or assembled complexes. Omission is unresolved, not zero. Resolve it when a required assembly or kinetic claim depends on it; otherwise explicitly limit the claim. Assembly populations can depend on concentration, solution conditions and ligand occupancy. A reference's dimer assignment does not establish dimer stability under every requested condition.

### Autonomous resolution and preparation

The agent owns routine preparation, method selection and evidence review. Resolve settings in this order: explicit user requirements, an existing run/service policy, then documented reference evidence and compatible modeling assumptions. Select the seed, candidate quotas, sequence bounds, file formats and scheduling within policy without asking for individual approval. For unspecified operating targets, choose documented reference-study conditions compatible with the intended conversion and methods; record them as adopted research conditions, not user requirements or experimentally verified properties of a new design. Scientific uncertainty still requires evidence rather than an arbitrary default.

Use the fallback pilot in `config/environment.yaml` when no task-specific policy exists. Record setup and campaign costs separately within the same authorized total, including controls and retries. Controller active time and explicit job time consume the local allowance; any explicit calendar deadline and stricter external limits remain binding. Historical expired allowances do not restart. Scientific CPU/GPU and external-service costs require execution-harness reservation and metering; local process time cannot establish remote usage. Check estimated requirements before dispatch and report unknown cost or capacity honestly. Limits do not weaken scientific gates or authorize new spending.

A missing full profile starts progressive preparation: reuse artifacts, retrieve evidence, test capabilities and review the inputs needed for the next stage. A reviewed generation contract permits exploratory candidates even while later state calculations and gates remain incomplete. Adapter fixtures remain development evidence and do not enter candidate success counts. Exploratory candidates retain their status until the full chemistry, protein-quality and assembly requirements pass. An unresolved future check is never converted to PASS merely to advance the workflow.

Discover connected executors and inspect their actual schemas, access, execution route and supported outputs. A ToolUniverse entry may wrap a local dependency rather than a hosted service. Verify readiness before dispatch. Repair input/transport integration within the frozen execution policy; do not automatically install models or train substitutes. Preserve an explicitly prescribed tool condition: an unavailable exact implementation remains a blocker for that condition, without blocking independent work. Share applicable prepared inputs across paired tests; keep execution policies, candidate outcomes and evaluation sessions separate.

The persistent controller invokes execution and independent review, then applies an actionable decision: accept, retry, repair, reject, blocked or needs-input. Review checks artifact identity, mappings, applicability, uncertainty, controls and resources. Accept means the stage's contract was met, not that every final enzyme rule passed. A repair identifies its target, preserves intent and invalidates affected downstream evidence; retries and repairs consume bounded allowances automatically. Resume from current artifact hashes and recorded job state. A narrative approval cannot turn FAIL or UNRESOLVED into PASS. Ask only for an essential unresolved goal ambiguity, incompatible explicit requirements or access/resources outside authorization.

The controller enforces this question boundary: `needs_input` requires a reviewed structured reason, the specific unresolved item and recorded resolution attempts. Routine or malformed questions return to internal repair. Missing chemistry profiles are agent preparation work. Whole-run requests must execute through the controller; stage workers return their assigned result and must not start another controller. See the [runtime response contract](runtime/CONTRACTS.md#reviewer-and-repair-responses).

Before expensive inference, validate the actual inputs, mappings, supported assembly/state inputs, executor access, output/receipt contract and resource limits. For hosted tools, use service contracts and bounded output controls; do not require private model internals or install a local copy. For permitted local execution, jointly check parser/features, trusted checkpoint loading, runtime/device, logging and any tracer. Record which checks need inference. Resolve launcher metadata from the existing run policy; a schema mismatch is an internal repair, not a new permission request. A genuine execution-tool denial or approval timeout stops dispatch and preserves the exact error for that gate. No automatic command substitution or deadline renewal is permitted.

Separate method qualification from candidate quality. A failed positive control means the affected method/claim needs investigation; it does not establish that the candidate is defective. Verify reference assembly, sequence numbering and equivalent chain assignments; test supported pinned settings with predeclared bounded sampling. Controls must support the candidate's actual information regime, including alignments, templates and restraints. Select methods from control evidence and retain all prespecified results. Candidate/native interface identity is not a universal requirement. The agent creates the [method-validation evidence](runtime/CONTRACTS.md#independent-assessment-models); it is required before structural promotion, not before exploratory prediction. Biological geometry and numerical thresholds remain per-run profile fields.

Record resolved values, their source, assumptions and claim limitations in `resolution_decisions.json`; carry its hash into the frozen inputs. Optional property characterization can report supported benefits or missing evidence without becoming a new user-approval step. Mandatory chemistry and protein-quality gates remain binding. Reuse historical preparation reports as evidence; apply the current policy rather than perpetuating old requests for routine approvals.

### Tool execution and run isolation

**Must use real tools.** Every claimed prediction or calculation must trace to an actual execution: provider/tool identity, version or disclosed backend-version gap, hashed inputs, parameters, job ID or local command and receipt, completion status, and hashed raw outputs. Keep these records in the run's capability registry and referenced stage evidence. Discovery, package imports, downloaded weights, synthetic fixtures, mock responses and agent-generated scores are not candidate predictions. A successful process exit is not scientific validation. Evaluation agents inspect the original outputs, calculations, controls and applicability; their reasoning cannot replace a measurement or model result.

| Frozen run condition | Permitted scientific execution |
| --- | --- |
| `agent_selected` | Discover and choose suitable executors through Boltzmann or ToolUniverse. Verify the actual backend and supported assembly/chemistry. No automatic local prediction-model installation, weight download, training or inference reimplementation. |
| `tools_specified` | Preserve the exact implementations named in the frozen request/input manifests, including explicitly prescribed local tools. Use either platform when it provides the required implementation. No silent substitution to satisfy the platform preference; unavailable exact tools remain a condition-specific gap. |

Both conditions permit small Python scripts for input preparation, format conversion, atom/residue/chain mapping, numerical geometry checks, output validation and result analysis. These scripts may not bypass provider restrictions through network/subprocess calls, invent predictions or relabel descriptors as solubility, aggregation or catalytic evidence. For a required chemistry calculation unavailable through both providers, the agent may use an external chemistry engine after recording the capability search, named method/version, scientific justification, validated inputs/controls and existing access/resource authorization. Independent review remains required. This exception does not extend to other prediction stages and must preserve prescribed-tool constraints.

Normal execution uses tested tool interfaces. Inference-internal patches require a separately declared, versioned development scope, unchanged code during each job and capability tests before adoption; routine recovery does not authorize uncontrolled model modifications. Exact tool names and versions belong in each run's verified capability registry rather than a universal scientific tool list. A wild-type reference is used when scientifically appropriate and available, not imposed on every de novo request.

New controller runs copy and hash their runtime, configuration and task instructions into `environment_snapshot/`; each executor, reviewer and repair task receives that snapshot's paths and its condition-specific `tool_execution_policy`. Resume with the frozen controller. Do not hot-reload shared Markdown, change a saved policy, reset usage or replace previous results. Legacy runs keep their recorded version; adopting this policy requires an explicit versioned continuation with provenance and existing usage retained. A changed tool-selection policy creates a separately labeled comparison condition. Shared-input reuse never transfers candidate scores or method qualification automatically.

The controller enforces snapshot/policy identity and artifact contracts, including a required `execution_evidence` artifact for completed scientific stages. It checks stage/condition/current-candidate bindings, declared execution routes, actual invocation records, and hashes for receipts, inputs and raw outputs. Support-only scripts cannot replace predictions. See the [execution-evidence contract](runtime/CONTRACTS.md#execution-evidence) for fields and scoped exceptions. Scientific execution authenticity is checked through original receipts and independent review; the configured harness must enforce provider access, network/subprocess restrictions, exceptions and resource reservations. Markdown and an arbitrary command backend alone are not a security sandbox or independent proof that a provider executed a calculation.

Fresh campaigns use a new session, run directory and frozen environment with agent-selected platform executors. Review reusable reference inputs independently; do not inherit old candidates, PASS flags, inference patches or expired allowances. Discover ready capabilities first, plan diverse sampling within the current budget, and use bounded internal review/recovery. Missing later capabilities remain explicit while eligible work continues. Historical unknown remote jobs remain in the nonduplication record; they are not implicitly cancelled or repeated.

## 3. Stage-specific scientific preparation

The agent first prepares [generation.schema.json](config/generation.schema.json): a consistent reaction; evidence-based assembly, chain/site mapping and occupancy; a supported motif; fixed/designable constraints; pinned generator behavior; and readiness evidence. `status: ready` requires current artifact verification and independent scientific review. It authorizes exploratory generation, not activity claims or final qualification. Do not invent catalytic coordinates or shorten a task merely to fit a failing runtime.

Generation contract version 1.1 includes `request_sha256`, calculated from the resolved request with the runtime's canonical object hashing. Earlier generation profiles require an agent-led applicability review before migration; editing a version/hash is insufficient. The complete chemistry profile retains its separate version 2.0. Target-specific unsupported chemistry requires capability development and testing; do not remove a metal, cofactor or partner to force it into an enabled route.

Build the full [protocol.schema.json](config/protocol.schema.json) progressively for state preparation, chemistry and final qualification. Freeze each assessment's methods and acceptance rules before using it to judge candidate outcomes, with reference/control evidence. Complete state/site coverage and qualified chemistry methods are required for their calculations; every required rule and current evidence is required before qualification. Record the review and controls in `qualification_evidence`. Routine review is agent-owned; a human name is neither a scientific substitute nor a default entry requirement.

Materialize and hash generation inputs first; add later scientific artifacts before the stage that uses them:

```text
00_inputs/
  request.json                 resolved user intent and defaults
  resolution_decisions.json    sources, adopted settings, assumptions and review
  reaction.json                participants, stereochemistry, atom mapping and bond changes
  generation.json              reviewed generation-readiness contract
  evaluation_plan.json         predeclared objective, mandatory groups and control-based calibration
  assembly.json                kind, copy count, sequence groups and provenance
  chain_map.json               entity/operator/chain/residue/atom correspondence
  active_sites.json            site membership and state/occupancy requirements
  molecules/                   reactant/product/intermediate SDFs
  motif.pdb                    fixed catalytic reference
  motif_map.json               stable atom/residue identities and roles
  states/                      add before state/chemistry evaluation
  generation_constraints.json  fixed identities, geometry and designable regions
  chemistry_protocol.json     add control-tested settings before chemistry evaluation
  gates.json                   freeze each assessment's rules before candidate scoring
  reward_spec.json             bounded reward transform for each required rule
  rl_config.json               controller mode, action limits and policy identity
  implementation_versions.json immutable code/container/model/data identifiers
```

These are generated artifacts, not a user input checklist. Generation does not depend on a completed catalytic-cycle calculation. Final qualification still requires the complete qualified profile and current candidate evidence; this package includes no fabricated qualified profile.

Before each stage, check its molecular and artifact mappings, supported representations, method access, applicability, component compatibility and resource reservation. Complete state/step coverage is required where that stage consumes states, rather than as a universal generation gate. Preserve reaction and assembly identity throughout. Unsupported prerequisites trigger repair or an explicit stage-specific incomplete result; independent useful work may continue within the same policy.

Fixed catalytic groups mean preserved residue identities and declared state-specific constraints. They do not mean immobile atoms or identical protonation and covalent bonds throughout the catalytic cycle.

Use abbreviated sampling for integration diagnostics only, unless scaffold-quality equivalence has been separately validated. Randomized initial coordinates and implicit-atom placeholders are not final predictions. Trace atom identities and fixed masks through model output, reconstruction and writing; a preserved ligand contact can coexist with invalid covalent geometry. A whole-residue fixed motif is a profile-specific conditioning choice, never a universal correction or evidence that the constrained geometry was independently generated. Validate the combined assembly, motif and occupancy capability under supported sampling before accepting scaffold-quality claims.

Scope control failures to the affected claims and dependencies. A failed local-geometry or interface control prevents promotion of the corresponding evidence; it does not erase independently verified sequence or coordinate observations. Full structural promotion still requires all mandatory checks. Continue applicable sequence-based solubility/aggregation assessments separately; composition descriptors do not replace them. Richer-information reference predictions may diagnose method limitations, but need a separate applicability argument for candidates with different input information. For de novo catalytic correspondence, reconcile generator motif/atom provenance and structural evidence; a pairwise sequence alignment alone neither proves nor disproves the intended catalytic mapping.

Apply the same fold admission contract to ordinary and sequence-only generation: each retained candidate needs an independent sequence-bound assessment model, applicable method-control evidence and reviewed physical integrity. Preparation/minimization evidence alone is insufficient. Recheck the model records and their exact versions on restart, at dependent stages and before final qualification. Missing records remain incomplete evidence; reviewer acceptance cannot waive them.

### Assembly resolution and homodimer contract

Resolve the biological assembly using curated records and primary evidence, including conditions and conflicting assignments. A crystallographic asymmetric unit is not automatically the biological assembly. Record the assembly identifier, source chains, transformation operators and evidence hashes; check modeled residues against the full reference sequence before reconstruction. Preserve observed versus modeled coordinates and missing-residue uncertainty.

| Requirement | Monomer | Homodimer |
| --- | --- | --- |
| Sequence identity | One sequence, one chain | One sequence, two mapped copies; equivalent positions share the same residue identity |
| Generation | One scaffold with the required motif | Design the full interface-bearing assembly with tied sequence positions and motifs mapped to the relevant sites |
| Structure evaluation | Independent fold and site recovery | Independent full-assembly prediction; examine each chain, relative placement, interface and every declared site |
| Chemistry context | Complete defined catalytic system | Retain the partner chain and its defined state; include cross-chain catalytic contributions where present |
| Output/counting | One candidate per design | One candidate per assembly, not two candidates or two distinct sequences |

The profile's `assembly` block fixes kind, copy count, sequence groups, reference/chain-map evidence, design symmetry, active-site definitions and state policy. Homodimers additionally require an interface-evaluation protocol. Chain labels are identifiers, not biochemical roles; compare equivalent chains through recorded mappings without changing atom or site identity. Length limits apply per sequence; estimate computation using the full assembly and required site/state calculations.

Do not assume two independent active sites. The catalytic map must establish whether sites are chain-local or span the interface, their multiplicity, and occupancy/partner states. Identical sequences do not require perfectly symmetric coordinates or simultaneous ligand occupancy throughout catalysis. C2 generation is permitted when justified; asymmetric generation or states require compatible reviewed inputs for the affected stage. Any representative-site calculation requires predeclared, validated equivalence evidence and an explicit mapping; otherwise evaluate each required site separately.

For symmetry-constrained generation, check asymmetric-unit versus complete-assembly inputs and supported symmetry behavior. Inspect the effective operator and enforcement path when a permitted local implementation exposes them; hosted services use documented input contracts and bounded output controls. A parsed option alone does not establish symmetry, packing or a usable interface. Validate simpler assembly controls before dependent motif/ligand campaigns; additional diagnostic cases after a failed simpler control require an explicit independent purpose. Audit all relevant motif covalent bonds and peptide links. Preserving selected atom distances or a ligand contact must not be reported as preserving complete motif geometry. Keep these measurements and their scope distinct.

Apply each site's rules in its declared state. An empty or resting partner site must satisfy its own state requirements; it need not exhibit substrate-attack geometry at the same instant as the reacting site.

Before accepting interface or site evidence for qualification, qualify its criteria on matched references/controls. Record relative placement, interface confidence where available, contacts/burial, packing/clashes and relevant exposure or assembly alternatives; no universal interface-score cutoff is supplied. Structural confidence alone establishes neither solution oligomerization nor catalytic activity. A copied or symmetry-imposed dimer is a generation model, not independent confirmation. Do not require a homodimer subunit to fold stably in isolation unless that is an explicit, supported task objective.

## 4. End-to-end execution

Execution is defined by required operations and evidence. Steps 1–4 establish generation readiness; steps 5–11 progressively generate and assess candidates; step 12 supplies recovery and optional refinement throughout; steps 13–14 finalize the run. A dependency is checked when its stage needs it, while final qualification remains strict.

| Step | Exact operation | Required result or decision |
| --- | --- | --- |
| 1. Resolve the request | Extract the conversion and explicit requirements. Resolve routine settings from policy and evidence; record assumptions and limits. Ask only for essential ambiguities that remain unresolved. | A complete resolved request or specific `NEEDS_INPUT`; no candidate generation before preflight. |
| 2. Normalize the reaction | Validate molecular identities, stereochemistry, stoichiometry and proton/charge bookkeeping. Map corresponding atoms between reactants and products and identify the intended bond changes. | A chemically consistent reaction definition; inconsistent or ambiguous inputs return for clarification. |
| 3. Prepare generation readiness | Resolve assembly, reaction, motif, chain/site mapping and generator compatibility. Reuse preparation and test missing capabilities; independently review readiness evidence. | Reviewed generation contract; only missing generation prerequisites block generation. Full evaluation-profile work continues progressively. |
| 4. Freeze generation inputs and evaluation intent | Hash the resolved request, motif, sequence ties, fixed/designable regions, generator settings and implementation versions. Predeclare objectives, required rule groups and control-based calibration. | Immutable generation inputs and evaluation plan; reserve each job's resources before dispatch. |
| 5. Generate candidates | Generate the monomer or full homodimer scaffold with mapped motifs. For a homodimer, design one shared sequence in the context of both chains and the interface. Verify copy count, sequence ties, chain integrity, mapping and clashes. A verified sequence with unresolved backbone integrity may be accepted in explicitly scoped `accepted_sequence_only` mode, with a hashed defect report. | Immutable exploratory candidate identity and generation provenance in `01_designs/`; sequence-only scope does not assert a physically valid assembly or interface. |
| 6. Apply early sequence/property filters | Independently validate and deduplicate unique sequences, verify homodimer sequence ties and assess sequence-only solubility and applicable thermal/pH endpoints even if the generated backbone needs preparation. Preserve distinct assembly hypotheses under separate candidate identities. | Eligible sequence evidence and exclusions in `02_sequences/`; no fold, interface, aggregation or catalysis PASS follows from a sequence prediction. |
| 7. Independently predict and assess the structure | Predict the declared assembly from the verified sequence; repairing defective generated coordinates is not a prerequisite for a sequence-input predictor. Preserve the generated scaffold and register each prediction as a separate assessment model. Verify every chain's sequence and mapping, then check completeness, peptide geometry, chirality, clashes and catalytic sites against matched controls. Prepare candidate/reference models when the chosen assessment needs it; disclose source coordinates and restraints. | Reviewed, hash-bound assessment models in `03_folds/`. Downstream structural results use these exact versions. Failed model geometry blocks dependent promotion; it does not erase sequence evidence. A copied or restrained dimer is not independent folding or interface evidence. |
| 8. Assess aggregation and consolidated properties | Assess hotspots on the assembled surface and dissociated surfaces when required by the profile. Distinguish a buried functional interface from an exposed aggregation risk. Combine with separate solubility and operating-condition evidence. | Separate property outcomes and applicability in `04_properties/`. Unresolved evidence remains explicit and prevents final qualification. |
| 9. Assess the substrate complex | Place substrate in each required site with the complete assembly and declared partner-site occupancy. Check reactive poses, access, contacts, interchain conflicts and unintended interface obstruction. | Supported site-specific poses in `05_complexes/`; pose confidence alone cannot qualify a design. |
| 10. Check every catalytic state | Build each required reaction/partner state with stable chain/site/atom mappings. Check state-specific bonds, catalytic identities, waters and contacts. Apply declared asymmetric occupancy or justified site-equivalence rules. | Complete state, step and site coverage in `06_states/`; missing coverage stays unresolved. |
| 11. Evaluate finalist chemistry | Evaluate the required chemical steps/sites in the qualified full-assembly context, retaining partner-chain effects. Validate paths, barriers, controls, convergence and uncertainty as specified in section 5. | Per-site/per-step evidence in `07_chemistry/`; no averaging away a required site failure. |
| 12. Review evidence and optionally iterate | Before promotion, distinguish technical/preparation errors, uncertainty and verified design failures. Record evidence and choose a bounded retry, approved additional assessment, refinement, rejection or continuation. Changes create a new candidate and invalidate affected evidence. | Auditable decisions under the fixed controller or frozen RL policy; preserve assembly, sequence ties, chemistry and gates. |
| 13. Independently qualify and rank | Recompute all required rule decisions across chains, sites, interface and chemistry. Cluster qualifying assemblies with chain-permutation-aware mapping and rank under frozen criteria. | Up to K distinct qualified assemblies; a passing partner cannot compensate for a failed required site. |
| 14. Package results and stop | Export unique sequences, full assemblies, chain/site mappings, all gate evidence, decisions, limitations and actual resource use. Report requested/returned assembly counts and stop reason. | Final bundle in `08_results/`, controller records in `09_rl/` and explicit run status. |

For each screening stage, save normalized metrics, native evidence, `promoted_ids.json` and `exclusions.json`. A verified disqualifying failure blocks dependent promotion. Missing prerequisite evidence blocks its dependent stage; unresolved final criteria may remain while independent useful assessments proceed. They never become PASS by proceeding. Technical recovery preserves the scientific task; candidate refinement creates a new lineage and invalidates affected scores. Limits constrain iteration and never weaken acceptance.

Record scaffold-generation provenance, retained reference regions, sequence identity with alignment coverage, and chain/assembly structural similarity. A new sequence on a retained scaffold is scaffold redesign. De novo scaffold generation can recover a known fold; a novel fold is not mandatory, and low sequence identity alone proves neither structural novelty nor activity. Apply any task-specific novelty criterion only if declared before generation.

### Metric interpretation

- Use **pLDDT** for predicted local confidence; lDDT requires a reference structure. State the reference and metric scale.
- Independent prediction means a fresh prediction without using the generated coordinates as the answer. Record templates, restraints and shared model/data provenance: correlated predictions are computational consistency evidence. A constraint that enforces the geometry being scored cannot independently confirm it.
- Protein–protein interface confidence may support homodimer assessment within a calibrated profile; it is not enzyme–substrate affinity or catalytic evidence. Do not transfer heterodimer/binder cutoffs to homodimers without validation. Record per-interface uncertainty and chain mapping, not only a whole-complex average.
- Binding scores and pose confidence do not establish catalysis or reaction rates.
- Solubility predictions are host/domain-dependent and do not constitute measured soluble yield. Predicted melting temperature, optimum pH, activity retention and pH stability are different endpoints and must be labeled separately.
- Solubility and aggregation have separate mandatory rules. Assess aggregation before complex/state/QM-MM work. Predictions on newly designed sequences need explicit applicability and calibration evidence.
- Each explicit required property target must be linked to a required full-profile rule by `request_target_index`, retaining its endpoint, units, operator and threshold. Additional stricter scientific gates may be separate rules. A generic operating-compatibility PASS cannot replace a requested thermal, pH or other endpoint.
- For any kinetic comparison, record conditions, units, provenance and whether enzyme concentration/activity is normalized per subunit, assembled complex or active site. Convert only with justified stoichiometry and active-site counts; otherwise report not comparable. Keep measured and predicted rates distinct.

## 5. Chemistry evaluation of finalists

Treat the reacting region with quantum mechanics and the surrounding protein/solvent environment with molecular mechanics, using the qualified coupled protocol. Conformational prediction and fixed-topology molecular dynamics provide structural evidence; they do not by themselves establish chemical reaction barriers.

For each admitted finalist, retain the declared assembly and all relevant partner-chain interactions. The chemistry protocol specifies site occupancy and reacting versus partner states. Cross-chain catalytic groups must remain in the reacting model where required; other partner effects remain in the qualified environment. Representative-site reuse requires validated equivalence, not sequence identity alone. Record chain/site IDs and restraint history in every chemistry result.

For each admitted finalist:

1. **Prepare the chemical system.** Verify the mapped substrate, catalytic groups, waters and all required state-specific bonds/adducts. Confirm complete parameters, protonation/tautomers, total charge and relevant spin states.
2. **Define the coupled calculation.** Specify the quantum region, boundary/link atoms, embedding, surrounding force field, electronic-structure treatment and numerical settings. Verify atom order, charges, parameters and energy/force conventions across representations.
3. **Sample conformational alternatives.** Sample the declared modeled conditions using profile-defined replicas and convergence checks. Select distinct representative snapshots; retain trajectories and provenance.
4. **Evaluate each required chemical step.** Follow the profile's declared energy or free-energy route. For a potential-energy path, optimize endpoints and locate/refine the transition state. For free energy, sample the declared reaction coordinates and states with the qualified estimator. Include required protonation/electronic alternatives and competing pathways.
5. **Validate the chosen route.** Check intended bond changes and connection to the correct states. Energy-path calculations require appropriate stationary-point/transition-state checks. Free-energy calculations require sampling convergence, applicable bias/reweighting corrections, reference-state conventions and statistical uncertainty. A static transition-state calculation alone is not a free-energy calculation; failed or unconverged evidence remains unresolved.
6. **Assess reliability and mechanism completion.** Compare matched controls; quantify snapshot/protonation variation and quantum-region sensitivity. Check every required step and catalytic-group regeneration. Evaluate access, release or selectivity separately when required by the requested claim.
7. **Apply chemistry rules and save evidence.** Record every chemical criterion as PASS, FAIL or UNRESOLVED against frozen limits. Save `chemistry_report.json` with candidate/profile, state/step/snapshot IDs, method, barrier type/value/units, uncertainty, controls, convergence/connectivity and evidence hashes.

Report energy barriers as ΔE‡ with the electronic/total-potential energy convention and any corrections. Report ΔG‡ only with the profile's validated free-energy treatment and specified reference states. Missing or unconverged paths are `UNRESOLVED`. Do not infer kcat/Km from docking scores or a static path; even a chemical-step free-energy barrier does not automatically determine whole-cycle kinetics. Regeneration, product release and sustained turnover require their own evidence when the requested claim includes them.

## 6. Rules, qualification and ranking

Every rule records an immutable ID, required/preferred flag, metric and units, state/step/atom targets where relevant, acceptance predicate, applicability/uncertainty policy, reward transform and evidence references. Each candidate rule is `PASS`, `FAIL` or `UNRESOLVED`; raw missing measurements remain null.

Required groups cover:

1. Reaction identity, atom mapping and fixed catalytic groups.
2. Reactive geometry and acid/base or proton-relay contacts.
3. Protonation, essential waters and stabilizing interactions.
4. All required states and chemical steps, including path/connectivity/convergence/barriers.
5. Independent fold and physical integrity.
6. Solubility.
7. Aggregation and exposed hotspots.
8. Applicable operating-condition evidence and user hard targets.
9. Assembly identity, copy count and sequence ties; interface integrity for homodimers.

Expand these into individual mechanism-specific rules. Every required state, step and active site must have explicit coverage. Required chain/site/interface rules are evaluated individually; averages cannot hide a failure. Monomer assembly rules verify monomer identity without inventing a protein–protein interface score. Required chemistry or solubility cannot be compensated by a high structural-confidence score. A rule may be not applicable only through a profile-owner rationale established before execution.

Qualification is `all(required_rules == PASS)` with current, valid evidence. Cluster qualifying candidates using frozen sequence/structure criteria; apply a declared Pareto-ranking and deterministic tie-break. Never fill the shortlist with failed or incomplete candidates. Report a shortfall when fewer than K qualify.

## 7. Fixed controller and optional RL extension

The implemented controller uses `fixed` execution with agent review and bounded recovery. `rl_inference` and `rl_training` remain specified extensions; they are not implemented or validated by the fixed controller. The following episode/reward contract applies when those extensions are implemented. RL training is confined to development tasks; production and held-out evaluation use a frozen checkpoint. Scientific acceptance rules remain fixed.

One RL episode is a candidate lineage within a campaign budget. `reset(task, seed)` returns its initial observation; `step(action)` returns observation, scalar reward, per-rule reward components, action mask, terminated/truncated flags and artifact references.

**Observation:** current candidate/parent, profile identity, rule outcomes/uncertainty, completed/pending stages and remaining resources. **Actions:** choose an approved generation preset, refine permitted positions, run an eligible stage, discard or stop. Mask changes to chemistry, fixed catalytic groups, assembly/copy count, sequence ties, site coverage, gate/reward definitions, mandatory stages and reserved chemistry resources.

Assembly evidence is reviewed before each relevant stage promotion. Check artifact/candidate identity, chains/sites, applicability, uncertainty and contradictory evidence. Technical retries and additional assessments must be bounded. An execution failure can justify an allowed compatible alternative; a valid adverse scientific result cannot justify switching evaluators until a passing score appears. Repairs preserve intent and invalidate affected evidence. A change to reaction, assembly identity or explicit user constraints requires a separate run configuration. Record the decision, evidence, next action and resource cost in `trajectory.jsonl`. This review applies in fixed mode without trained RL.

Every required rule receives a frozen positive weight and a bounded score qᵢ ∈ [0,1]. Define Φ(s) = Σwᵢqᵢ(s), with Σwᵢ = 1. Normalize across the resolved rules, including assembly/site rules; adding an identical chain or reusing evidence must not multiply rewards. Unresolved evidence contributes zero to this conservative reward potential while its raw metric remains null.

Initial configurable reward (an engineering proposal; no biological predictive validity or RL improvement is established):

```text
r_t = 0.1 × (Φ(next) − Φ(current)) − 0.1 × normalized_action_cost
terminal addition = +2 if every required gate passes
                    −1 if a verified required failure remains
                     0 if incomplete/unresolved without a verified failure
gamma = 1; cumulative normalized episode cost ≤ 1
```

Repeated unchanged evidence earns no progress reward. Candidate edits invalidate stale scores. Budget-limited episodes are truncated, not successful. The independent AND-of-gates evaluator determines qualification regardless of cumulative reward. The policy-learning algorithm must support the declared action masks and episode contract; training is not claimed as delivered.

At each completed action: ingest current evidence, recompute per-rule scores, calculate reward, record the transition, and expose only eligible next actions. During development training, collect rollouts with action probabilities, value estimates, costs and termination masks; compute learning targets, update the controller and save/version the checkpoint. Freeze it before production or held-out evaluation. Persist the full rule/reward vector and policy identity in `09_rl/`.

## 8. Developer interfaces and runtime behavior

The [local controller](runtime/controller.py) invokes the existing harness through the [agent bridge](runtime/agents.py). Initialize once, then use `run` to execute or resume and `status` to inspect durable progress. `doctor` checks the local invocation configuration without submitting scientific jobs. Initialization does not import success flags or renew expired historical allowances.

```bash
python3 runtime/controller.py init --run-dir /path/to/run --request 'Design a de novo enzyme for the specified conversion' --input /path/to/reference --agent-config /path/to/agent-config.json --policy /path/to/run-policy.json
python3 runtime/controller.py run --run-dir /path/to/run
python3 runtime/controller.py status --run-dir /path/to/run
```

One execution response is followed by an independent review response. Actionable repair/retry decisions are handled inside the controller's bounded loop. Review receives the current output and artifact identities, not permission to edit acceptance criteria. Fresh execution attempts retain previous outputs and failure evidence. External scientific jobs must be tracked through the execution harness; a detached shell or visible session is not job-completion evidence.

| Component | Contract |
| --- | --- |
| Request resolver / registry | Resolve intent, prepare the generation contract and evaluation plan, materialize/hash stage inputs |
| Execution adapter | Input: run/candidate/stage IDs, artifact hashes, profile/implementation lock, seed and resource limits. Output: job status, native/normalized metrics, applicability, uncertainty, artifact hashes, cost and typed errors |
| Candidate store | Candidate/parent IDs, unique-sequence and full-assembly hashes, copy count, chain/site/atom maps, stage state, rule evidence and accumulated resource use |
| Scheduler | Stage dependencies, promotion limits, concurrency, idempotency, retry limits, cancellation and chemistry reservation |
| Evaluator / report builder | Recompute rule outcomes from immutable evidence; qualify, cluster/rank and package outputs |
| Controller / trainer | Select allowed actions; persist rewards/rollouts; never modify frozen scientific constraints |

Cache keys include input content, assembly/copy count, chain/site mappings, occupancy, symmetry/restraint policy, settings, code/model/data revisions and seed. A shared-sequence edit updates both homodimer copies and invalidates all affected assembly, property, complex and chemistry evidence. Geometry or occupancy edits also invalidate dependent results even if the sequence is unchanged. Store requested versus actual resource consumption and charge retries. Resume from validated artifacts, never solely from a success flag. A declared timeout/cancellation preserves completed evidence and marks unfinished work unresolved.

After eligible recovery, an essential intent ambiguity uses `NEEDS_INPUT`; a missing scientific prerequisite uses reason `PROTOCOL_REQUIRED`; missing scientific or execution capability yields `BLOCKED` or `PARTIAL` according to retained progress. Identify the affected stage and retain completed work. `PARTIAL` may have zero qualified designs when useful exploratory work exists but required evaluation is incomplete. A completed full evaluation with zero passing designs uses `NO_QUALIFYING_DESIGNS`; all requested designs passing uses `QUALIFIED`. Always report requested, generated, evaluated and qualified counts separately. Budget exhaustion, cancellation, timeout and errors retain explicit stop reasons. None of these incomplete statuses imply scientific success.

## 9. Final output contract

```text
08_results/
  report.md                    readable results, limits and shortfall reasons
  designed_sequences.fasta     one unique sequence per qualified candidate
  assemblies.json              candidate-to-chain/copy/site and structure mapping
  assessment_models.json       reviewed prediction versions and generated-scaffold provenance
  shortlist.csv                ordered IDs, ranks and qualifying metrics
  structures/                  full qualified biological assemblies, when any exist
  evaluation.json              candidate rules, decisions and exclusions
  chemistry/                   references to finalist chemistry evidence
  manifest.json                input/implementation/data/policy hashes and resource use
  trajectory.jsonl             agent actions, retries and candidate lineage
```

`evaluation.json` requires run/task/profile IDs, version hashes, requested/returned counts, status/stop_reason, every candidate's per-rule raw value/units/outcome/applicability/uncertainty/evidence, qualified IDs and exclusion reasons. `manifest.json` records immutable software/container/model/data IDs, seeds, device/runtime details and source timestamps. Do not insert fabricated numeric metrics when a calculation did not run.

A homodimer FASTA entry represents one sequence used twice; `assemblies.json` supplies copy count, chain IDs, sequence hash and site membership. K counts assemblies, not chains. Every required site/interface outcome and any approved equivalence mapping must be visible in `evaluation.json`; record the computational claim without asserting experimentally verified oligomerization. Include design provenance, prediction dependencies, resolved conditions and concentration/kinetic normalization basis wherever those claims are reported.

Preflight failures still return a structured status and missing requirements. Empty runtime directories are not committed just to match the tree. Large trajectories/models/results belong in artifact storage with access-controlled references and checksums.

## 10. Evaluation, benchmarking and release

First validate adapter/schema behavior, state/atom-map preservation, cache invalidation, replay, cancellation, resource accounting and failure reporting. Then qualify the scientific gates on profile-specific controls, including a broken catalytic site, unsupported predictor input and missing/unconverged chemistry.

Qualify monomer and homodimer routes separately. Include negative checks for a missing partner, broken sequence ties, incorrect chain/site mapping, an invalid interface and a failed required site masked by a good average. For homodimers, compare wild type, previous designs and new assemblies under the same preparation, site coverage and evaluation conditions; score generation models separately from independent predictions and restrained versus unrestrained evidence. Matching a structural reference is not itself proof of catalysis.

Benchmark fixed execution, rule-based refinement and frozen RL under identical requests, profiles, evaluator and total compute. Hold out reactions/motifs/families as appropriate and control sequence/structure duplicates and model-training overlap. Freeze test tasks and thresholds before evaluation; do not train RL on held-out reward feedback.

Report qualifying designs per task/budget, diversity, failed/unresolved fraction, wall time, CPU/GPU usage and full-chemistry counts. Report RL training cost separately. Where reliable published measurements exist, assess agreement with activity evidence; computational qualification and measured catalytic performance remain separate endpoints.

The package remains In Progress until the required scientific adapters and complete execution path are available. Validated applies only to a named supported scope with recorded scientific evidence. The [acceptance plan](tests/ACCEPTANCE.md) separates package/controller checks from reaction qualification and enzyme benchmarks.

## 11. References and provenance

Supporting rationale, limitations and source provenance are recorded in [research notes](../../research/Denovo-Enzyme-Design/research-notes.md). The scientific source list and task-format attribution are maintained in [references](../../research/Denovo-Enzyme-Design/references.md).

### Version and license policy

Scientific references support the requirements; they do not prescribe an execution stack. For accessible local implementations, record exact commits/container digests, used weight hashes, data snapshots and settings. Hosted executors may instead use `service_provenance`: provider/service identity, the actually reported version (or an explicit undisclosed version), retrieval time, a hashed service-contract capture and reproducibility limitations. Retain actual execution receipts separately. Do not invent private hashes or treat `main`, `latest` or an undisclosed backend as immutable. Review backend uncertainty when judging control comparability and reproducibility; a claim requiring a pinned version remains unresolved without one.

Check code, weights, database access and service terms separately. The repository's eventual license does not grant rights to third-party software or model assets. Access restrictions, unavailable required model files and incompatible runtime terms must be resolved before enabling an adapter. No third-party code, model weights or restricted dataset is redistributed in this package.
