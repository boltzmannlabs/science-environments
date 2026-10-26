# Task: denovo_enzyme_001

**Task family:** de novo enzyme design. **Status:** specification; the operations below require implementation. This file follows the supplied BioDesignBench demo's task structure. Its tool-list section is replaced by **Required Execution Steps**, as requested; the enzyme-specific task text is original.

## Description

Design new enzyme sequences and structures for the conversion in the resolved request. Preserve the requested chemistry and the selected profile's catalytic groups. Return up to the requested number of diverse candidates that pass every mandatory chemistry, assembly/interface, folding, solubility, aggregation and operating-condition rule.

Use the [environment specification](../ENVIRONMENT_SPEC.md) for the execution contract. A qualified reaction profile must exist before design starts. Do not manufacture motifs, thresholds, chemistry evidence or successful results to complete the task.

## Target

- **Reaction:** resolved reactants, products, stereochemistry and intended bond changes from `00_inputs/reaction.json`.
- **Assembly:** resolved monomer or homodimer from `00_inputs/assembly.json`, with chain/sequence-copy mapping and active-site definitions.
- **Catalytic reference:** fixed groups and mapped atoms from `motif.pdb` and `motif_map.json`.
- **States and steps:** the profile's complete required reaction-state and chemical-step set.
- **Conditions:** resolved pH, temperature, host, solvent and salt composition; protein concentration and its basis when relevant to the requested claim.
- **Profile identity:** immutable ID/version/hash and qualification evidence.

The harness binds these fields from the request and registry; this is not a task with a hidden fixed enzyme family. [request.example.json](request.example.json) and [homodimer.request.example.json](homodimer.request.example.json) illustrate monomer and homodimer request syntax only. Their conditions, design counts and budgets are example limits, not recommended scientific settings or runtime estimates. Neither is runnable until a matching qualified profile and working execution components exist.

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

Execution is defined by required operations and evidence, independent of software choice. Perform these steps under the frozen scientific profile:

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Resolve the request | Clarify the conversion, conditions, design constraints, required/preferred properties, desired final count and budgets. | Complete request or `NEEDS_INPUT`. |
| 2. Normalize the reaction | Validate identities, stereochemistry and stoichiometry; reconcile charge/protons; assign atom maps and intended bond changes. | Chemically consistent mapped reaction. |
| 3. Select the profile | Resolve biological assembly from evidence and match reaction, assembly, chain/site coverage and operating domain to a qualified profile. | Compatible profile or `PROTOCOL_REQUIRED`; do not infer biological assembly from coordinate-file chain count. |
| 4. Prepare and freeze | Materialize molecules, assembly/chain/site maps, motifs, state policy, sequence ties, gates, rewards and versions. Reserve full-assembly chemistry resources. | Immutable task inputs or a specific missing scientific/infrastructure requirement. |
| 5. Generate designs | Generate a monomer or full homodimer scaffold. Design one shared sequence for both homodimer copies in their interface context; check mapping, completeness and clashes. | Valid candidate assemblies with the correct number of sequence copies. |
| 6. Filter sequences and early properties | Validate unique sequences and ties, deduplicate candidate identities, assess solubility and applicable thermal/pH endpoints with domain checks. | Eligible candidates; do not count identical chain copies as separate designs. |
| 7. Verify independent folding and assembly | Independently predict the full assembly. Check each chain, sites and homodimer interface/relative placement; disclose imposed restraints. | Fold and assembly/site gates passed; a copied dimer is not independent evidence. |
| 8. Check aggregation and protein properties | Assess assembled-surface hotspots and dissociated exposure when required. Combine with separate solubility and condition rules. | Applicable protein-quality gates passed before chemistry work. |
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

A preflight failure instead returns the structured failure status and missing requirements. Empty FASTA is valid for a completed run with no qualifying designs. Do not present an unevaluated candidate as qualified.

## Constraints

- **Compute/time:** the frozen request and profile specify limits; reserve finalist chemistry resources before generation.
- **Knowledge/data:** use the recorded reference and dataset snapshots. A benchmark-specific temporal cutoff, if required, must be declared when that benchmark is instantiated.
- **Scope:** computational results only; no wet-lab procedure or experimental performance claim.
- **Reproducibility:** preserve native artifacts, hashes, seeds, implementation versions and all failed/unresolved candidates in the audit record.

## Important Instructions

- Use the environment's supported reaction profile; stop with `PROTOCOL_REQUIRED` when essential scientific preparation is absent.
- Treat local fold confidence, protein–protein interface confidence, substrate pose, solubility, aggregation and chemistry as distinct evidence.
- Never delete a required partner, force all catalytic states to be symmetric, or waive site coverage to make a candidate pass.
- Use state-appropriate rules for reacting and resting sites. Fixed catalytic identities do not freeze their coordinates, protonation or state-specific bonds throughout catalysis.
- Disclose shared prediction inputs, templates and restraints. Agreement between predictions does not establish experimental folding, assembly or activity.
- Resolve concentration-dependent claims explicitly. Compare activity only with matched conditions and a declared subunit, complex or active-site normalization basis.
- Before promotion, record the evidence review and next permitted action. An agent opinion or a high average score cannot override a required failure.
- A missing or unconverged required result is `UNRESOLVED`, never PASS or a fabricated zero measurement.
- Do not modify the evaluator, thresholds, rewards, fixed chemistry or held-out task data.
- Re-evaluate affected evidence after sequence/structure changes; record candidate lineage.
- Respect budgets and stop explicitly rather than weakening acceptance criteria.
