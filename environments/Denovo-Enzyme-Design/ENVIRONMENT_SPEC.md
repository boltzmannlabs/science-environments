# Denovo Enzyme Design — Environment Specification

**Environment ID:** `denovo-enzyme-design`

**Status:** Specification

**Delivered claim:** computational qualification under a named reaction profile; experimental catalysis is not established.

## 1. Objective and supported task

Given an intended substrate-to-product conversion, operating conditions and design constraints, produce up to K diverse, newly designed enzyme candidates. Every returned qualified candidate must pass its applicable chemistry, fold, solubility, aggregation and user-required gates.

One reusable environment serves multiple **qualified reaction profiles**. A profile supplies the scientific mechanism, catalytic motif, state models, supported representations, thresholds and validated calculation settings. The initial scope is soluble, single-chain, cofactor-free enzymes. Unsupported chemistry returns `PROTOCOL_REQUIRED` before generation.

## 2. Inputs: user versus environment

| User supplies | Environment prepares |
| --- | --- |
| Reactant/product SMILES, molecular files or unambiguous identifiers; intended stereochemistry | Normalized participants, stoichiometry, atom maps, reaction steps and compatible profile |
| Operating pH, temperature and expression host; relevant solvent/salt conditions | Applicability checks and required protonation/state alternatives |
| Length range, prohibited features and required/preferred property targets | Fixed catalytic identities/atoms and candidate-independent reference geometry |
| Requested shortlist size and approved compute budget, or explicit service defaults | Generation/evaluation quotas, implementation version lock and a chemistry reservation |

Validate against [request.schema.json](config/request.schema.json). Do not silently replace an ambiguous structure, infer an unspecified stereoisomer or claim a required endpoint has been resolved. Missing essential user information produces `NEEDS_INPUT`; unavailable scientific preparation produces `PROTOCOL_REQUIRED`; unavailable infrastructure produces `BLOCKED`.

The request example contains an ordinary ester-hydrolysis conversion solely to demonstrate schema validation. No supported profile for that request is claimed by this package.

## 3. Reaction-profile preparation and preflight

A scientific owner qualifies each profile against appropriate references and controls before enabling it. [protocol.schema.json](config/protocol.schema.json) specifies its minimum contract. The developer implements loading and checks; the agent must not invent mechanisms, catalytic coordinates or numerical chemistry thresholds.

Before generating candidates, materialize and hash the following runtime inputs:

```text
00_inputs/
  request.json                 resolved user intent and defaults
  reaction.json                participants, atom maps, states and steps
  molecules/                   reactant/product/intermediate SDFs
  motif.pdb                    fixed catalytic reference
  motif_map.json               stable atom/residue identities and roles
  states/                      required state structures and bond definitions
  generation_constraints.json  fixed identities, geometry and designable regions
  chemistry_protocol.json     supported parameterization and QM/MM settings
  gates.json                  explicit acceptance rule for each criterion
  reward_spec.json             bounded reward transform for each required rule
  rl_config.json               controller mode, action limits and policy identity
  implementation_versions.json immutable code/container/model/data identifiers
```

These are generated runtime artifacts, not files the user must manually provide. A complete profile is an environment dependency. This package defines its contract but includes no fabricated qualified profile.

Preflight checks atom-map round trips; complete state/step coverage; residue/ligand representation; implementation, model and license access; predictor applicability; compatibility of model components; and sufficient reserved chemistry resources. Freeze the profile, gate/reward definitions and implementation lock for the run. Publish the resolved task to the agent only after these checks.

## 4. End-to-end execution

Execution is defined by required operations and evidence. Implementations must satisfy these contracts regardless of which software is selected. Steps 1–4 form preflight; steps 5–11 screen candidates in increasing computational cost; step 12 governs optional iteration; steps 13–14 finalize the run.

| Step | Exact operation | Required result or decision |
| --- | --- | --- |
| 1. Resolve the request | Extract the desired conversion, conditions, sequence constraints, hard/preferred property targets, final count K and resource limits. Resolve essential ambiguities and record accepted defaults. | A complete request; otherwise `NEEDS_INPUT`. No generation starts. |
| 2. Normalize the reaction | Validate molecular identities, stereochemistry, stoichiometry and proton/charge bookkeeping. Map corresponding atoms between reactants and products and identify the intended bond changes. | A chemically consistent reaction definition; inconsistent or ambiguous inputs return for clarification. |
| 3. Select the scientific profile | Match the reaction and operating domain to a scientifically qualified mechanism/profile. Confirm the required catalytic roles, reference motif, reaction steps, state alternatives and evidence coverage. | A compatible qualified profile; otherwise `PROTOCOL_REQUIRED`. |
| 4. Prepare and freeze the task | Prepare mapped molecules, catalytic groups, waters and state models. Define fixed/designable regions, per-rule thresholds and uncertainty policies, rewards, version locks, budgets and a finalist chemistry reservation. Check implementation/model access. | Immutable `00_inputs/`; scientific omissions produce `PROTOCOL_REQUIRED`, infrastructure failures `BLOCKED`. |
| 5. Generate candidates | Produce a scaffold and compatible sequence for each design while preserving fixed catalytic identities and geometry. Assign candidate IDs, atom maps and provenance; check chain integrity, length, completeness and severe clashes. | Valid sequence/structure pairs in `01_designs/`; malformed candidates are rejected. |
| 6. Apply early sequence/property filters | Remove invalid sequences and duplicates. Assess solubility and applicable sequence-level thermal/pH endpoints as soon as a sequence exists. Apply calibrated hard-target and model-domain checks. | Eligible candidates and exclusions in `02_sequences/`. A separate sequence-refinement pass is not required before this screening. |
| 7. Verify independent folding | Predict each surviving sequence's fold independently of the generated coordinates. Assess global/local confidence, agreement with the intended scaffold, active-site recovery and physical integrity. | Fold and catalytic-site gates pass; structures and evidence in `03_folds/`. |
| 8. Assess aggregation and consolidated properties | Examine aggregation tendency and exposed hotspots on the independently predicted structure. Combine these results with solubility and declared condition-related evidence, keeping endpoints separate. | Mandatory solubility and aggregation gates pass; consolidated evidence in `04_properties/`. |
| 9. Assess the substrate complex | Place the intended substrate in the enzyme context. Evaluate pose alternatives, reactive-group orientation, pocket access, required contacts and steric conflicts. | Supported reactive poses in `05_complexes/`; binding confidence alone cannot qualify a design. |
| 10. Check every catalytic state | Construct the required reactant/intermediate/product and regeneration states. Check bonds, catalytic identities, protonation alternatives, waters, contacts and geometry for each state. | Complete, compatible state coverage in `06_states/`; missing required states remain unresolved. |
| 11. Evaluate finalist chemistry | For the admitted finalists, prepare and sample the reacting system, evaluate every required chemical step, validate reaction paths and transition states, and assess barriers, controls and uncertainty as detailed in section 5. | Per-step chemical evidence in `07_chemistry/`; failed or unconverged required chemistry cannot qualify. |
| 12. Decide whether to iterate | After any completed evaluation, record all rule outcomes and reward components. Within budget, accept, refine, discard or generate additional permitted candidates using the fixed controller or frozen RL policy. A changed candidate receives a new ID and returns to the earliest invalidated stage. | Recorded lineage/actions; no stale scores, repeated-evidence rewards, modified chemistry or relaxed gates. This is a conditional loop, not an obligatory extra calculation. |
| 13. Independently qualify and rank | Recompute decisions from current evidence. Require every mandatory rule to pass; deduplicate/cluster qualifying candidates and rank them using the frozen criteria and tie-break rule. | Up to K diverse qualified designs; incomplete and failed designs remain outside the qualified shortlist. |
| 14. Package results and stop | Export qualified sequences/structures, all candidate decisions, chemistry evidence, property metrics, limitations, resource use and complete provenance. Report the achieved count and exact stop reason. | Final bundle in `08_results/`, controller records in `09_rl/` and explicit run status. |

For each screening stage, save normalized metrics, native evidence, `promoted_ids.json` and `exclusions.json`. A verified hard failure blocks promotion; an unresolved requirement cannot become PASS. Use a qualified alternative assessment where available or return the missing-evidence status. Candidate refinement is optional and preserves the fixed chemistry. Resource limits constrain iteration and never weaken acceptance.

### Metric interpretation

- Use **pLDDT** for predicted local confidence; experimentally evaluated lDDT is a different quantity.
- Protein–protein ipTM thresholds from binder tasks are not universal enzyme–substrate gates. Any protein–ligand confidence criterion must match the selected metric's definition and a calibrated profile.
- Binding scores and pose confidence do not establish catalysis or reaction rates.
- Solubility predictions are host/domain-dependent and do not constitute measured soluble yield. Predicted melting temperature, optimum pH, activity retention and pH stability are different endpoints and must be labeled separately.
- Solubility and aggregation have separate mandatory rules. Assess aggregation before complex/state/QM-MM work. Predictions on newly designed sequences need explicit applicability and calibration evidence.

## 5. Chemistry evaluation of finalists

Treat the reacting region with quantum mechanics and the surrounding protein/solvent environment with molecular mechanics, using the qualified coupled protocol. Conformational prediction and fixed-topology molecular dynamics provide structural evidence; they do not by themselves establish chemical reaction barriers.

For each admitted finalist:

1. **Prepare the chemical system.** Verify the mapped substrate, catalytic groups, waters and all required state-specific bonds/adducts. Confirm complete parameters, protonation/tautomers, total charge and relevant spin states.
2. **Define the coupled calculation.** Specify the quantum region, boundary/link atoms, embedding, surrounding force field, electronic-structure treatment and numerical settings. Verify atom order, charges, parameters and energy/force conventions across representations.
3. **Sample conformational alternatives.** Sample the declared modeled conditions using profile-defined replicas and convergence checks. Select distinct representative snapshots; retain trajectories and provenance.
4. **Evaluate each required chemical step.** Optimize the specified endpoints, search the connecting reaction path and refine the transition state. Include the profile's required protonation/electronic alternatives and competing pathways.
5. **Validate the path.** Check numerical convergence, intended bond changes, appropriate transition-state character and connection to the correct endpoints. Failed or disconnected paths remain unresolved evidence.
6. **Assess reliability and mechanism completion.** Compare matched controls; quantify snapshot/protonation variation and quantum-region sensitivity. Check every required step and catalytic-group regeneration. Evaluate access, release or selectivity separately when required by the requested claim.
7. **Apply chemistry rules and save evidence.** Record every chemical criterion as PASS, FAIL or UNRESOLVED against frozen limits. Save `chemistry_report.json` with candidate/profile, state/step/snapshot IDs, method, barrier type/value/units, uncertainty, controls, convergence/connectivity and evidence hashes.

Report electronic barriers as ΔE‡. Report ΔG‡ only with the profile's validated free-energy treatment. Missing or unconverged paths are `UNRESOLVED`. Do not infer kcat/Km from docking scores or a static path. Regeneration, product release and sustained turnover require their own evidence when the requested claim includes them.

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

Expand these into individual mechanism-specific rules. Every required state and step must have explicit coverage. Required chemistry or solubility cannot be compensated by a high structural-confidence score. A rule may be not applicable only through a profile-owner rationale established before execution.

Qualification is `all(required_rules == PASS)` with current, valid evidence. Cluster qualifying candidates using frozen sequence/structure criteria; apply a declared Pareto-ranking and deterministic tie-break. Never fill the shortlist with failed or incomplete candidates. Report a shortfall when fewer than K qualify.

## 7. RL controller

Support `fixed`, `rl_inference` and `rl_training` controller modes. Fixed execution provides the baseline. RL training is confined to development tasks; production and held-out evaluation use a frozen checkpoint. The scientific procedures and acceptance rules remain fixed.

One RL episode is a candidate lineage within a campaign budget. `reset(task, seed)` returns its initial observation; `step(action)` returns observation, scalar reward, per-rule reward components, action mask, terminated/truncated flags and artifact references.

**Observation:** current candidate/parent, profile identity, rule outcomes/uncertainty, completed/pending stages and remaining resources. **Actions:** choose an approved generation preset, refine permitted positions, run an eligible stage, discard or stop. Mask changes to chemistry, fixed catalytic groups, gate/reward definitions, mandatory stages and reserved chemistry resources.

Every required rule receives a frozen positive weight and a bounded score qᵢ ∈ [0,1]. Define Φ(s) = Σwᵢqᵢ(s), with Σwᵢ = 1. Unresolved evidence contributes zero to this conservative reward potential while its raw metric remains null.

Initial configurable reward:

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
| Candidate store | Candidate/parent IDs, sequence/structure hashes, stable atom map, stage state, rule evidence and accumulated resource use |
| Scheduler | Stage dependencies, promotion limits, concurrency, idempotency, retry limits, cancellation and chemistry reservation |
| Evaluator / report builder | Recompute rule outcomes from immutable evidence; qualify, cluster/rank and package outputs |
| Controller / trainer | Select allowed actions; persist rewards/rollouts; never modify frozen scientific constraints |

Cache keys include input content, settings, code/model/data revisions and seed. Store requested versus actual resource consumption and charge retries. Resume from validated artifacts, never solely from a success flag. A declared timeout/cancellation preserves completed evidence and marks unfinished work unresolved.

Scientific input failures use `NEEDS_INPUT` or `PROTOCOL_REQUIRED`; infrastructure failures use `BLOCKED`. Completed runs report `QUALIFIED` when K qualify, `PARTIAL` when 1..K−1 qualify, or `NO_QUALIFYING_DESIGNS` when zero qualify. `CANCELLED` is a separate run status. `stop_reason` records budget, timeout, user cancellation, completion or error.

## 9. Final output contract

```text
08_results/
  report.md                    readable results, limits and shortfall reasons
  designed_sequences.fasta     qualified sequences only; empty when none qualify
  shortlist.csv                ordered IDs, ranks and qualifying metrics
  structures/                  mapped qualified structures, when any exist
  evaluation.json              candidate rules, decisions and exclusions
  chemistry/                   references to finalist chemistry evidence
  manifest.json                input/implementation/data/policy hashes and resource use
  trajectory.jsonl             agent actions, retries and candidate lineage
```

`evaluation.json` requires run/task/profile IDs, version hashes, requested/returned counts, status/stop_reason, every candidate's per-rule raw value/units/outcome/applicability/uncertainty/evidence, qualified IDs and exclusion reasons. `manifest.json` records immutable software/container/model/data IDs, seeds, device/runtime details and source timestamps. Do not insert fabricated numeric metrics when a calculation did not run.

Preflight failures still return a structured status and missing requirements. Empty runtime directories are not committed just to match the tree. Large trajectories/models/results belong in artifact storage with access-controlled references and checksums.

## 10. Evaluation, benchmarking and release

First validate adapter/schema behavior, state/atom-map preservation, cache invalidation, replay, cancellation, resource accounting and failure reporting. Then qualify the scientific gates on profile-specific controls, including a broken catalytic site, unsupported predictor input and missing/unconverged chemistry.

Benchmark fixed execution, rule-based refinement and frozen RL under identical requests, profiles, evaluator and total compute. Hold out reactions/motifs/families as appropriate and control sequence/structure duplicates and model-training overlap. Freeze test tasks and thresholds before evaluation; do not train RL on held-out reward feedback.

Report qualifying designs per task/budget, diversity, failed/unresolved fraction, wall time, CPU/GPU usage and full-chemistry counts. Report RL training cost separately. Where reliable published measurements exist, assess agreement with activity evidence; computational qualification and measured catalytic performance remain separate endpoints.

Release status advances from Specification to Implemented only when the adapters/controller exist, and to Validated only for a named supported scope with recorded evidence. The [acceptance plan](tests/ACCEPTANCE.md) separates package checks performed now from those future requirements.

## 11. References and provenance

Supporting rationale, limitations and source provenance are recorded in [research notes](../../research/Denovo-Enzyme-Design/research-notes.md). The scientific source list and task-format attribution are maintained in [references](../../research/Denovo-Enzyme-Design/references.md).

### Version and license policy

Scientific references support the requirements; they do not prescribe an execution stack. Before any scientific run, resolve and store exact implementation commits or container digests, weight hashes, data snapshots and relevant settings in the profile/run manifest. Do not silently use moving `main` or `latest` references as a reproducible lock.

Check code, weights, database access and service terms separately. The repository's eventual license does not grant rights to third-party software or model assets. Access restrictions, unavailable required model files and incompatible runtime terms must be resolved before enabling an adapter. No third-party code, model weights or restricted dataset is redistributed in this package.
