# Denovo Enzyme Design — Environment Specification

**Environment ID:** `denovo-enzyme-design`

**Status:** Specification

**Intended runtime claim:** computational qualification under a named reaction profile. This specification delivers no qualified enzyme or experimentally established catalysis.

## 1. Objective and supported task

Given an intended substrate-to-product conversion, operating conditions and design constraints, produce up to K diverse, newly designed enzyme candidates. Every returned qualified candidate must pass its applicable chemistry, fold, solubility, aggregation and user-required gates.

One reusable environment serves multiple **qualified reaction profiles**. A profile supplies the scientific mechanism, catalytic motif, state models, supported representations, thresholds and validated calculation settings. The specified scope is soluble, cofactor-free monomers and homodimers. A homodimer contains two copies of one protein sequence. Heterodimers, larger assemblies, membrane systems and cofactor-dependent chemistry require qualified extensions. Unsupported science returns `PROTOCOL_REQUIRED` before generation. These are specification requirements, not delivered scientific runtime capabilities.

## 2. Inputs: user versus environment

| User supplies | Environment prepares |
| --- | --- |
| Reactant/product SMILES, molecular files or unambiguous identifiers; intended stereochemistry | Normalized participants, stoichiometry, atom maps, reaction steps and compatible profile |
| Operating pH, temperature and expression host; relevant solvent/salt conditions and protein concentration, when known | Applicability checks, concentration basis and required protonation/state alternatives |
| Length range per unique sequence, prohibited features and required/preferred property targets | Fixed catalytic identities/atoms and candidate-independent reference geometry |
| Assembly preference and reference identifier, if known | Evidence-based biological assembly, chain mapping, interface requirements and active-site/state coverage |
| Requested shortlist size and approved compute budget, or explicit service defaults | Generation/evaluation quotas, implementation version lock and a chemistry reservation |

Validate against [request.schema.json](config/request.schema.json). Do not silently replace an ambiguous structure, infer an unspecified stereoisomer or claim a required endpoint has been resolved. Missing essential user information produces `NEEDS_INPUT`; unavailable scientific preparation produces `PROTOCOL_REQUIRED`; unavailable infrastructure produces `BLOCKED`.

The monomer example uses ester hydrolysis; the homodimer example uses the L-DEX YL conversion. Both are syntax examples, not qualified profiles or authorization to spend their illustrative budgets. Missing `assembly` means `resolve_from_evidence`. The environment prepares the scientific assembly data; the user need not manually supply symmetry operators or chain maps.

Protein concentration, when supplied, must include its basis: total subunit equivalents or assembled complexes. Omission is unresolved, not zero. Resolve it when a required assembly or kinetic claim depends on it; otherwise explicitly limit the claim. Assembly populations can depend on concentration, solution conditions and ligand occupancy. A reference's dimer assignment does not establish dimer stability under every requested condition.

## 3. Reaction-profile preparation and preflight

A scientific owner qualifies each profile against appropriate references and controls before enabling it. [protocol.schema.json](config/protocol.schema.json) specifies its minimum contract. The developer implements loading and checks; the agent must not invent mechanisms, catalytic coordinates or numerical chemistry thresholds.

Before generating candidates, materialize and hash the following runtime inputs:

```text
00_inputs/
  request.json                 resolved user intent and defaults
  reaction.json                participants, atom maps, states and steps
  assembly.json                kind, copy count, sequence groups and provenance
  chain_map.json               entity/operator/chain/residue/atom correspondence
  active_sites.json            site membership and state/occupancy requirements
  molecules/                   reactant/product/intermediate SDFs
  motif.pdb                    fixed catalytic reference
  motif_map.json               stable atom/residue identities and roles
  states/                      required state structures and bond definitions
  generation_constraints.json  fixed identities, geometry and designable regions
  chemistry_protocol.json     supported parameterization and QM/MM settings
  gates.json                   explicit acceptance rule for each criterion
  reward_spec.json             bounded reward transform for each required rule
  rl_config.json               controller mode, action limits and policy identity
  implementation_versions.json immutable code/container/model/data identifiers
```

These are generated runtime artifacts, not files the user must manually provide. A complete profile is an environment dependency. This package defines its contract but includes no fabricated qualified profile.

Preflight checks atom-map round trips; complete state/step coverage; residue/ligand representation; implementation, model and license access; predictor applicability; compatibility of model components; and sufficient reserved chemistry resources. Freeze the profile, gate/reward definitions and implementation lock for the run. Publish the resolved task to the agent only after these checks.

Fixed catalytic groups mean preserved residue identities and declared state-specific constraints. They do not mean immobile atoms or identical protonation and covalent bonds throughout the catalytic cycle.

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

Do not assume two independent active sites. The catalytic map must establish whether sites are chain-local or span the interface, their multiplicity, and occupancy/partner states. Identical sequences do not require perfectly symmetric coordinates or simultaneous ligand occupancy throughout catalysis. C2 generation is permitted when justified; asymmetric designs or states require a compatible qualified profile. Any representative-site calculation requires predeclared, validated equivalence evidence and an explicit mapping; otherwise evaluate each required site separately.

Apply each site's rules in its declared state. An empty or resting partner site must satisfy its own state requirements; it need not exhibit substrate-attack geometry at the same instant as the reacting site.

Before enabling the profile, qualify interface and site criteria on matched references/controls. Record relative placement, interface confidence where available, contacts/burial, packing/clashes and relevant exposure or assembly alternatives; no universal interface-score cutoff is supplied. Structural confidence alone establishes neither solution oligomerization nor catalytic activity. A copied or symmetry-imposed dimer is a generation model, not independent confirmation. Do not require a homodimer subunit to fold stably in isolation unless that is an explicit, supported task objective.

## 4. End-to-end execution

Execution is defined by required operations and evidence. Implementations must satisfy these contracts regardless of which software is selected. Steps 1–4 form preflight; steps 5–11 screen candidates in increasing computational cost; step 12 governs optional iteration; steps 13–14 finalize the run.

| Step | Exact operation | Required result or decision |
| --- | --- | --- |
| 1. Resolve the request | Extract the desired conversion, conditions, sequence constraints, hard/preferred property targets, final count K and resource limits. Resolve essential ambiguities and record accepted defaults. | A complete request; otherwise `NEEDS_INPUT`. No generation starts. |
| 2. Normalize the reaction | Validate molecular identities, stereochemistry, stoichiometry and proton/charge bookkeeping. Map corresponding atoms between reactants and products and identify the intended bond changes. | A chemically consistent reaction definition; inconsistent or ambiguous inputs return for clarification. |
| 3. Select the scientific profile | Resolve the biological assembly and match reaction, operating conditions and assembly to a qualified profile. Confirm chain/site mappings, interface requirements and complete state/step coverage. | Compatible profile; unresolved assembly or unsupported scientific scope returns `PROTOCOL_REQUIRED`. |
| 4. Prepare and freeze the task | Materialize reaction and assembly inputs, chains, sites, waters and states. Freeze sequence ties, fixed/designable regions, interface/chemistry gates, rewards and implementation versions. Reserve resources for full-assembly and site evaluation. | Immutable `00_inputs/`; scientific omissions produce `PROTOCOL_REQUIRED`, unavailable required capabilities `BLOCKED`. |
| 5. Generate candidates | Generate the monomer or full homodimer scaffold with mapped motifs. For a homodimer, design one shared sequence in the context of both chains and the interface. Verify copy count, sequence ties, chain integrity, mapping and clashes. | Valid candidate assemblies in `01_designs/`; identical sequences alone do not establish a valid interface. |
| 6. Apply early sequence/property filters | Validate and deduplicate unique sequences; verify both homodimer copies match. Assess solubility and applicable thermal/pH endpoints within their calibrated domains. Preserve distinct assembly hypotheses under separate candidate identities. | Eligible candidates and exclusions in `02_sequences/`; no double reward or candidate count for identical copies. |
| 7. Verify independent folding and assembly | Predict the declared full assembly independently of the generated coordinates. Assess each chain, motif/site recovery and, for homodimers, relative placement, interface confidence/packing and required alternative assemblies. Record any restraints and their limitations. | Fold, assembly/interface and site gates pass; evidence in `03_folds/`. A good monomer fold alone cannot qualify a dimer. |
| 8. Assess aggregation and consolidated properties | Assess hotspots on the assembled surface and dissociated surfaces when required by the profile. Distinguish a buried functional interface from an exposed aggregation risk. Combine with separate solubility and operating-condition evidence. | Required property gates pass with applicable context; evidence in `04_properties/`. |
| 9. Assess the substrate complex | Place substrate in each required site with the complete assembly and declared partner-site occupancy. Check reactive poses, access, contacts, interchain conflicts and unintended interface obstruction. | Supported site-specific poses in `05_complexes/`; pose confidence alone cannot qualify a design. |
| 10. Check every catalytic state | Build each required reaction/partner state with stable chain/site/atom mappings. Check state-specific bonds, catalytic identities, waters and contacts. Apply declared asymmetric occupancy or justified site-equivalence rules. | Complete state, step and site coverage in `06_states/`; missing coverage stays unresolved. |
| 11. Evaluate finalist chemistry | Evaluate the required chemical steps/sites in the qualified full-assembly context, retaining partner-chain effects. Validate paths, barriers, controls, convergence and uncertainty as specified in section 5. | Per-site/per-step evidence in `07_chemistry/`; no averaging away a required site failure. |
| 12. Review evidence and optionally iterate | Before promotion, distinguish technical/preparation errors, uncertainty and verified design failures. Record evidence and choose a bounded retry, approved additional assessment, refinement, rejection or continuation. Changes create a new candidate and invalidate affected evidence. | Auditable decisions under the fixed controller or frozen RL policy; preserve assembly, sequence ties, chemistry and gates. |
| 13. Independently qualify and rank | Recompute all required rule decisions across chains, sites, interface and chemistry. Cluster qualifying assemblies with chain-permutation-aware mapping and rank under frozen criteria. | Up to K distinct qualified assemblies; a passing partner cannot compensate for a failed required site. |
| 14. Package results and stop | Export unique sequences, full assemblies, chain/site mappings, all gate evidence, decisions, limitations and actual resource use. Report requested/returned assembly counts and stop reason. | Final bundle in `08_results/`, controller records in `09_rl/` and explicit run status. |

For each screening stage, save normalized metrics, native evidence, `promoted_ids.json` and `exclusions.json`. A verified hard failure blocks promotion; an unresolved requirement cannot become PASS. Use a qualified alternative assessment where available or return the missing-evidence status. Candidate refinement is optional and preserves the fixed chemistry. Resource limits constrain iteration and never weaken acceptance.

Record scaffold-generation provenance, retained reference regions, sequence identity with alignment coverage, and chain/assembly structural similarity. A new sequence on a retained scaffold is scaffold redesign. De novo scaffold generation can recover a known fold; a novel fold is not mandatory, and low sequence identity alone proves neither structural novelty nor activity. Apply any task-specific novelty criterion only if declared before generation.

### Metric interpretation

- Use **pLDDT** for predicted local confidence; lDDT requires a reference structure. State the reference and metric scale.
- Independent prediction means a fresh prediction without using the generated coordinates as the answer. Record templates, restraints and shared model/data provenance: correlated predictions are computational consistency evidence. A constraint that enforces the geometry being scored cannot independently confirm it.
- Protein–protein interface confidence may support homodimer assessment within a calibrated profile; it is not enzyme–substrate affinity or catalytic evidence. Do not transfer heterodimer/binder cutoffs to homodimers without validation. Record per-interface uncertainty and chain mapping, not only a whole-complex average.
- Binding scores and pose confidence do not establish catalysis or reaction rates.
- Solubility predictions are host/domain-dependent and do not constitute measured soluble yield. Predicted melting temperature, optimum pH, activity retention and pH stability are different endpoints and must be labeled separately.
- Solubility and aggregation have separate mandatory rules. Assess aggregation before complex/state/QM-MM work. Predictions on newly designed sequences need explicit applicability and calibration evidence.
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

## 7. RL controller

Support `fixed`, `rl_inference` and `rl_training` controller modes. Fixed execution provides the baseline. RL training is confined to development tasks; production and held-out evaluation use a frozen checkpoint. The scientific procedures and acceptance rules remain fixed.

One RL episode is a candidate lineage within a campaign budget. `reset(task, seed)` returns its initial observation; `step(action)` returns observation, scalar reward, per-rule reward components, action mask, terminated/truncated flags and artifact references.

**Observation:** current candidate/parent, profile identity, rule outcomes/uncertainty, completed/pending stages and remaining resources. **Actions:** choose an approved generation preset, refine permitted positions, run an eligible stage, discard or stop. Mask changes to chemistry, fixed catalytic groups, assembly/copy count, sequence ties, site coverage, gate/reward definitions, mandatory stages and reserved chemistry resources.

Assembly evidence is reviewed at preflight and before every stage promotion. Check artifact/candidate identity, chains/sites, applicability, uncertainty and contradictory evidence. Technical retries and additional assessments must be bounded and listed in the frozen execution policy; map them to the existing stage-evaluation action. Do not switch methods until one passes. Verified failures lead to discard or permitted refinement; unresolved evidence cannot advance through its gate. Repairs must preserve the frozen inputs; a change to assembly identity or the scientific profile requires a new, separately qualified run configuration. Record decision, evidence references, reason, next action and resource cost in `trajectory.jsonl`. This review also applies in fixed mode and does not require trained RL.

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

| Component | Contract |
| --- | --- |
| Request resolver / registry | Validate intent, resolve or reject a supported profile, materialize/hash immutable run inputs |
| Execution adapter | Input: run/candidate/stage IDs, artifact hashes, profile/implementation lock, seed and resource limits. Output: job status, native/normalized metrics, applicability, uncertainty, artifact hashes, cost and typed errors |
| Candidate store | Candidate/parent IDs, unique-sequence and full-assembly hashes, copy count, chain/site/atom maps, stage state, rule evidence and accumulated resource use |
| Scheduler | Stage dependencies, promotion limits, concurrency, idempotency, retry limits, cancellation and chemistry reservation |
| Evaluator / report builder | Recompute rule outcomes from immutable evidence; qualify, cluster/rank and package outputs |
| Controller / trainer | Select allowed actions; persist rewards/rollouts; never modify frozen scientific constraints |

Cache keys include input content, assembly/copy count, chain/site mappings, occupancy, symmetry/restraint policy, settings, code/model/data revisions and seed. A shared-sequence edit updates both homodimer copies and invalidates all affected assembly, property, complex and chemistry evidence. Geometry or occupancy edits also invalidate dependent results even if the sequence is unchanged. Store requested versus actual resource consumption and charge retries. Resume from validated artifacts, never solely from a success flag. A declared timeout/cancellation preserves completed evidence and marks unfinished work unresolved.

Scientific input failures use `NEEDS_INPUT` or `PROTOCOL_REQUIRED`; infrastructure failures use `BLOCKED`. Completed runs report `QUALIFIED` when K qualify, `PARTIAL` when 1..K−1 qualify, or `NO_QUALIFYING_DESIGNS` when zero qualify. `CANCELLED` is a separate run status. `stop_reason` records budget, timeout, user cancellation, completion or error.

## 9. Final output contract

```text
08_results/
  report.md                    readable results, limits and shortfall reasons
  designed_sequences.fasta     one unique sequence per qualified candidate
  assemblies.json              candidate-to-chain/copy/site and structure mapping
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

Release status advances from Specification to Implemented only when the adapters/controller exist, and to Validated only for a named supported scope with recorded evidence. The [acceptance plan](tests/ACCEPTANCE.md) separates package checks performed now from those future requirements.

## 11. References and provenance

Supporting rationale, limitations and source provenance are recorded in [research notes](../../research/Denovo-Enzyme-Design/research-notes.md). The scientific source list and task-format attribution are maintained in [references](../../research/Denovo-Enzyme-Design/references.md).

### Version and license policy

Scientific references support the requirements; they do not prescribe an execution stack. Before any scientific run, resolve and store exact implementation commits or container digests, weight hashes, data snapshots and relevant settings in the profile/run manifest. Do not silently use moving `main` or `latest` references as a reproducible lock.

Check code, weights, database access and service terms separately. The repository's eventual license does not grant rights to third-party software or model assets. Access restrictions, unavailable required model files and incompatible runtime terms must be resolved before enabling an adapter. No third-party code, model weights or restricted dataset is redistributed in this package.
