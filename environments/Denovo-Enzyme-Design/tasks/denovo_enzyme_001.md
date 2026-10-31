# Task: denovo_enzyme_001

**Task family:** de novo enzyme design. **Status:** In Progress; resumable controller included, scientific qualification remains reaction-specific. This file follows the supplied BioDesignBench demo's task structure. Its tool-list section is replaced by **Required Execution Steps**, as requested; the enzyme-specific task text is original.

## Description

Design new enzyme sequences and structures for the conversion in the resolved request. Preserve the requested chemistry and the selected profile's catalytic groups. Return up to the requested number of diverse candidates that pass every mandatory chemistry, assembly/interface, folding, solubility, aggregation and operating-condition rule.

Use the [environment specification](../ENVIRONMENT_SPEC.md) and [controller](../runtime/controller.py) for execution. Own preparation, discovery, review and bounded recovery through the existing harness. A reviewed [generation contract](../config/generation.schema.json) permits exploratory generation; the complete qualified profile is required for final qualification. Build missing later requirements progressively. Do not manufacture motifs, thresholds, chemistry evidence or successful results.

For a whole-run user request, initialize and run the controller using the existing harness configuration and available inputs; follow [runtime usage](../runtime/CONTRACTS.md#start-and-resume). Reading these files alone does not start the controller. If invoked by the controller with an assigned stage/role, execute only that assignment and return its response; do not start a nested controller. Use internal resolution for routine settings and missing chemistry preparation. A user question requires the structured, reviewed reason defined in the runtime contract.

Resolve unspecified settings from run policy and reference evidence, recording assumptions. Use the configured fallback pilot limits when no task-specific policy exists. Choose routine parameters and evaluate stage outcomes yourself; do not ask the user to approve seeds, mappings, method choices or every transition. Preserve explicit requirements and prescribed-tool test conditions. Ask only when an essential goal ambiguity or access/resource requirement cannot be resolved within existing authorization. Continue independent preparation work before reporting the precise remaining blocker.

Follow the run's frozen [tool execution policy](../ENVIRONMENT_SPEC.md#tool-execution-and-run-isolation). **Must use real tools**, saving execution receipts, hashed inputs and raw outputs; discovery, mocks and agent opinions are not calculations. `agent_selected` discovers scientific executors through Boltzmann or ToolUniverse. `tools_specified` retains its prescribed implementations, including explicitly named local tools. Small Python scripts may prepare, map, check and analyse data; they may not install/train replacement predictors as a fallback. External chemistry requires the recorded capability gap, validated method and existing authorization. Use the instruction paths supplied in the controller task, never a moving shared Markdown file. A policy change requires an explicit versioned continuation.

## Target

For a fresh campaign, use a new session and run directory with the current frozen environment. Reuse verified reference inputs only after applicability review; generate new candidates and new evidence. Do not import old PASS flags, model patches or expired allocations. Discover ready executors first and size a diverse batch within the current quota; avoid spending the whole budget repeatedly repairing one unsupported route. A missing later capability remains explicit while eligible work continues.

Resolve these fields independently for the requested enzyme. Example identifiers, residue positions, lengths and conditions are not defaults. Keep the reusable environment unchanged when switching targets; create or qualify the corresponding run profile and capability bindings.

- **Reaction:** resolved reactants, products, stereochemistry and intended bond changes from `00_inputs/reaction.json`.
- **Assembly:** resolved monomer or homodimer from `00_inputs/assembly.json`, with chain/sequence-copy mapping and active-site definitions.
- **Catalytic reference:** fixed groups and mapped atoms from `motif.pdb` and `motif_map.json`.
- **States and steps:** the profile's complete required reaction-state and chemical-step set.
- **Conditions:** resolved pH, temperature, host, solvent and salt composition; protein concentration and its basis when relevant to the requested claim.
- **Profile identity:** generation-contract ID/version/hash at generation; full-profile ID/version/hash and qualification evidence at final qualification.

The agent and harness resolve these fields from the request, policy and evidence. [request.example.json](request.example.json) and [homodimer.request.example.json](homodimer.request.example.json) illustrate syntax only. Their conditions and budgets are not policy defaults or runtime estimates. Each operation requires its own verified scientific inputs and working capabilities; neither example supplies those artifacts or proves enzyme qualification.

## Design Constraints

- Length is per unique sequence; final count is per complete candidate assembly. Resolve omitted assembly preferences from evidence, never by assuming monomer.
- Homodimers have two identical sequence copies. Preserve their mapping, required interface and declared state/site coverage. Cofactor-dependent enzymes, heterodimers and larger assemblies remain outside this version.
- Preserve the intended reaction, mapped catalytic identities and allowed sequence-edit mask.
- Record retained reference regions and scaffold-generation provenance. Distinguish scaffold redesign from de novo generation; a new fold is not mandatory.
- Respect the profile's supported chemistry and property-prediction domains.
- Solubility and aggregation are mandatory separate gates, even when the user's additional property-target list is empty.
- Apply the profile's fold, motif, assembly/interface, state and chemistry gates; confidence or affinity cannot compensate for a failed chemical step.
- Return a smaller qualified set when necessary and explain the shortfall.

## Required Execution Steps

Execution is defined by required operations and evidence, independent of software choice. Prepare each stage's prerequisites, preserve frozen scientific intent and review before promotion:

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Resolve the request | Extract explicit requirements; resolve routine settings from policy and evidence, recording their source. Clarify only remaining essential ambiguities. | Complete resolved request or specific `NEEDS_INPUT`. |
| 2. Normalize the reaction | Validate identities, stereochemistry and stoichiometry; reconcile charge/protons; assign atom maps and intended bond changes. | Chemically consistent mapped reaction. |
| 3. Prepare generation readiness | Resolve assembly, reaction, motif, chain/site mapping and compatible generation inputs. Test missing capability and independently review evidence. | Ready generation contract; missing later chemistry qualification does not block valid exploratory generation. |
| 4. Prepare and freeze | Hash generation inputs, sequence ties, fixed/designable regions and versions. Predeclare objectives, required rule groups and control-based calibration. Prepare later state/method artifacts before use. | Immutable generation inputs and evaluation plan; reserve each scientific job's resources before dispatch. |
| 5. Generate designs | Generate a monomer or full homodimer scaffold and design one shared sequence for both homodimer copies. Check mapping, completeness and clashes; record geometry defects explicitly. | Valid full assemblies, or explicitly `accepted_sequence_only` exploratory output with a hashed defect report, never promoted as a physically valid scaffold. |
| 6. Filter sequences and early properties | Validate unique sequences and ties, deduplicate candidate identities, assess sequence-only solubility and applicable thermal/pH endpoints with domain checks even when geometry is unresolved. | Eligible sequences with explicit structural uncertainty; do not count identical chain copies as separate designs. |
| 7. Verify independent folding and assembly | Predict the full declared assembly from the unchanged designed sequence; defective generated coordinates do not require repair first. Record inputs and supported method settings. Test applicable reference controls and independently review predicted physical integrity, assembly and catalytic mappings. Optional matched structural preparation remains separate evidence. | Sequence-bound assessment models with reviewed method-control and integrity reports before structural promotion. Failed method controls do not alone reject the candidate. Retain original scaffolds and unpromoted predictions. A copied or geometry-fitted assembly is not independent folding evidence. |
| 8. Check aggregation and protein properties | Assess assembled-surface hotspots and dissociated exposure when required. Combine with separate solubility and condition rules. | Separate outcomes and applicability; missing final evidence stays unresolved while eligible independent work continues. |
| 9. Check substrate placement | Assess every required site in the full assembly with declared occupancy, partner state, access, contacts and steric constraints. | Supported site-specific reactive complexes. |
| 10. Check reaction-state compatibility | Check all required states, sites, bonds, waters and catalytic identities. Preserve justified asymmetric states and partner-chain contributions. | Complete state/step/site coverage; uncertainty remains unresolved. |
| 11. Evaluate finalist chemistry | Evaluate required reaction steps/sites with partner effects retained. Apply the declared energy-path or free-energy route and its controls, convergence checks and uncertainty analysis. | Per-site evidence with energy type/reference states; representative-site reuse requires validated equivalence. |
| 12. Review evidence and optionally refine | Check artifacts and conflicting evidence before promotion. Choose a bounded technical retry, approved further evaluation, refinement, rejection or continuation. Preserve assembly, chemistry and gates. | Recorded evidence/reason/action; new candidates invalidate affected evidence and update both sequence copies. |
| 13. Qualify and rank | Independently enforce all required rules across chains, sites and interface. Cluster and rank complete qualifying assemblies. | Up to K assemblies; no averaging away a failed required site or interface. |
| 14. Return the final bundle | Export unique sequences, full assemblies, chain/site mappings, chemistry/property evidence, exclusions, decisions and resource use. | Complete output with achieved count and exact stop reason. |

Step 12 is a conditional decision after evaluated evidence, including early failures; it does not require completing expensive calculations for a rejected candidate. No refinement or RL action may change the intended chemistry, required checks or acceptance thresholds. The [environment specification](../ENVIRONMENT_SPEC.md) defines the detailed chemistry substeps, per-rule rewards and failure handling.

## Expected Output

**Format:** `enzyme_design_bundle`.

Required final files in `08_results/`:

- `designed_sequences.fasta`: one unique sequence per qualified candidate.
- `assemblies.json`: sequence-to-chain/copy/site mapping; a homodimer uses its sequence twice.
- `shortlist.csv`: ranked IDs and qualifying metrics.
- `evaluation.json`: every required rule, evidence, status and exclusion.
- `report.md`: interpretation, limitations and requested-versus-returned count.
- `manifest.json`: input/profile/implementation/model/policy revisions, seeds and resource use.
- `trajectory.jsonl`: action/job/lineage history.
- Full qualified assembly structures and per-site chemistry evidence references when candidates exist.

A stage that cannot complete after bounded recovery returns its actual tests/jobs, structured status, retained exploratory outputs and precise missing prerequisites. Identify preparation, candidate execution and final qualification separately. Development fixtures never become candidates by relabeling. Exploratory candidates remain outside the qualified FASTA until all required evidence passes. `PARTIAL` can contain zero qualified designs when evaluation is unfinished; final evaluated failure and incomplete evaluation are distinct outcomes.

## Constraints

- **Compute/time:** policy fixes the total allowance; setup and campaign counters share that total unless separately allocated. Respect explicit deadlines and reserve scientific jobs through the harness. Resuming does not renew expired limits.
- **Knowledge/data:** use the recorded reference and dataset snapshots. A benchmark-specific temporal cutoff, if required, must be declared when that benchmark is instantiated.
- **Scope:** computational results only; no wet-lab procedure or experimental performance claim.
- **Reproducibility:** preserve native artifacts, hashes, seeds, implementation versions and all failed/unresolved candidates in the audit record.

## Important Instructions

- The outer agent starts or resumes one controller run for the user request, using the [runtime instructions](../runtime/CONTRACTS.md). Stage workers perform only their assigned operation and return the required JSON; they must not start nested controllers. Routine stage reports are consumed internally, not handed back to the user for a new continuation prompt.
- Reuse shared preparation and validated infrastructure. Generate exploratory candidates once generation prerequisites pass; missing full qualification only blocks dependent calculations and qualification claims.
- Follow the run's startup and method-validation policies. Test routine compatibility fixes internally; distinguish technical errors, method-control failures and candidate defects. Keep biological mappings and gates per target. A genuine tool approval block requires the supported execution gate and cannot be retried through another route.
- Treat local fold confidence, protein–protein interface confidence, substrate pose, solubility, aggregation and chemistry as distinct evidence.
- Never delete a required partner, force all catalytic states to be symmetric, or waive site coverage to make a candidate pass.
- Use state-appropriate rules for reacting and resting sites. Fixed catalytic identities do not freeze their coordinates, protonation or state-specific bonds throughout catalysis.
- Disclose shared prediction inputs, templates and restraints. Agreement between predictions does not establish experimental folding, assembly or activity.
- Resolve concentration-dependent claims explicitly. Compare activity only with matched conditions and a declared subunit, complex or active-site normalization basis.
- Before promotion, review current evidence and select accept, retry, repair, reject, blocked or needs-input. The controller executes bounded recovery without a new user prompt. Accepting a stage does not mark unresolved final criteria PASS; reviewer opinion cannot override a required failure.
- A missing or unconverged required result is `UNRESOLVED`, never PASS or a fabricated zero measurement.
- Do not modify the evaluator, thresholds, rewards, fixed chemistry or held-out task data.
- Re-evaluate affected evidence after sequence/structure changes; record candidate lineage.
- Respect budgets and stop explicitly rather than weakening acceptance criteria.
