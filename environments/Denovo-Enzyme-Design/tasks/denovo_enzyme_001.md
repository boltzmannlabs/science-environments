# Task: denovo_enzyme_001

**Task family:** de novo enzyme design. **Status:** specification; the operations below require implementation. This file follows the supplied BioDesignBench demo's task structure. Its tool-list section is replaced by **Required Execution Steps**, as requested; the enzyme-specific task text is original.

## Description

Design new enzyme sequences and structures for the conversion in the resolved request. Preserve the requested chemistry and the selected profile's catalytic groups. Return up to the requested number of diverse candidates that pass every mandatory chemistry, folding, solubility, aggregation and operating-condition rule.

Use the [environment specification](../ENVIRONMENT_SPEC.md) for the execution contract. A qualified reaction profile must exist before design starts. Do not manufacture motifs, thresholds, chemistry evidence or successful results to complete the task.

## Target

- **Reaction:** resolved reactants, products, stereochemistry and intended bond changes from `00_inputs/reaction.json`.
- **Catalytic reference:** fixed groups and mapped atoms from `motif.pdb` and `motif_map.json`.
- **States and steps:** the profile's complete required reaction-state and chemical-step set.
- **Conditions:** resolved pH, temperature, host, solvent and salt composition.
- **Profile identity:** immutable ID/version/hash and qualification evidence.

The harness binds these fields from the request and registry; this is not a task with a hidden fixed enzyme family. [request.example.json](request.example.json) illustrates the request syntax only. Its design counts and budgets are example limits, not recommended scientific settings or runtime estimates. It is not runnable until a matching qualified profile and working execution components exist.

## Design Constraints

- Length, generation/refinement limits and requested final count come from the resolved request.
- Preserve the intended reaction, mapped catalytic identities and allowed sequence-edit mask.
- Respect the profile's supported chemistry and property-prediction domains.
- Solubility and aggregation are mandatory separate gates, even when the user's additional property-target list is empty.
- Apply the profile's fold, motif, state and chemistry gates; confidence or affinity cannot compensate for a failed chemical step.
- Return a smaller qualified set when necessary and explain the shortfall.

## Required Execution Steps

Execution is defined by required operations and evidence, independent of software choice. Perform these steps under the frozen scientific profile:

| Step | What must happen | Required result |
| --- | --- | --- |
| 1. Resolve the request | Clarify the conversion, conditions, design constraints, required/preferred properties, desired final count and budgets. | Complete request or `NEEDS_INPUT`. |
| 2. Normalize the reaction | Validate identities, stereochemistry and stoichiometry; reconcile charge/protons; assign atom maps and intended bond changes. | Chemically consistent mapped reaction. |
| 3. Select the profile | Confirm a qualified mechanism, catalytic motif, required reaction states/steps and supported operating domain. | Compatible profile or `PROTOCOL_REQUIRED`. |
| 4. Prepare and freeze | Materialize molecules, motifs, state models, fixed/designable regions, acceptance rules, rewards and implementation versions; reserve chemistry compute. | Immutable task inputs, or a specific scientific/infrastructure failure. |
| 5. Generate designs | Produce scaffold–sequence pairs that satisfy motif and length constraints; assign IDs and verify chain/atom integrity and severe clashes. | Valid initial candidate set. |
| 6. Filter sequences and early properties | Remove invalid/duplicate sequences; assess solubility and applicable thermal/pH endpoints with domain checks. | Candidates eligible for independent folding. |
| 7. Verify independent folding | Predict folding without forcing the design coordinates; check confidence, scaffold agreement and catalytic-site recovery. | Independently supported folds. |
| 8. Check aggregation and protein properties | Assess structural aggregation and hotspots; combine evidence with separate solubility and operating-condition rules. | Protein-quality gates passed before complex/chemistry work. |
| 9. Check substrate placement | Assess pose alternatives, reactive orientation, access, catalytic contacts and steric conflicts. | Plausible reactive complexes; confidence alone is insufficient. |
| 10. Check reaction-state compatibility | Evaluate each required state, its bonds, catalytic groups, protonation alternatives, waters and geometry. | Complete and compatible state coverage. |
| 11. Evaluate finalist chemistry | Prepare the coupled quantum/mechanical model, sample alternatives, locate and validate each required reaction path/transition state, assess barriers and controls, and record uncertainty. | Per-step chemical evidence and PASS/FAIL/UNRESOLVED decisions. |
| 12. Decide and optionally refine | After an evaluation, record the reward for every required criterion. Within budget, continue, refine, discard or stop through the fixed controller or frozen RL policy. Recheck changed candidates from the earliest invalidated stage. | Auditable iteration with current evidence and preserved chemistry. |
| 13. Qualify and rank | Independently enforce all mandatory gates; cluster qualifying designs and rank under frozen criteria. | Up to K diverse qualified candidates. |
| 14. Return the final bundle | Export the shortlist, sequences, structures, chemistry/property evidence, exclusions, uncertainty, provenance, resource use and stop reason. | Complete final output with an honest shortfall where applicable. |

Step 12 is a conditional decision after evaluated evidence, including early failures; it does not require completing expensive calculations for a rejected candidate. No refinement or RL action may change the intended chemistry, required checks or acceptance thresholds. The [environment specification](../ENVIRONMENT_SPEC.md) defines the detailed chemistry substeps, per-rule rewards and failure handling.

## Expected Output

**Format:** `enzyme_design_bundle`.

Required final files in `08_results/`:

- `designed_sequences.fasta`: qualified candidates only.
- `shortlist.csv`: ranked IDs and qualifying metrics.
- `evaluation.json`: every required rule, evidence, status and exclusion.
- `report.md`: interpretation, limitations and requested-versus-returned count.
- `manifest.json`: input/profile/implementation/model/policy revisions, seeds and resource use.
- `trajectory.jsonl`: action/job/lineage history.
- Qualified structures and chemistry evidence references when candidates exist.

A preflight failure instead returns the structured failure status and missing requirements. Empty FASTA is valid for a completed run with no qualifying designs. Do not present an unevaluated candidate as qualified.

## Constraints

- **Compute/time:** the frozen request and profile specify limits; reserve finalist chemistry resources before generation.
- **Knowledge/data:** use the recorded reference and dataset snapshots. A benchmark-specific temporal cutoff, if required, must be declared when that benchmark is instantiated.
- **Scope:** computational results only; no wet-lab procedure or experimental performance claim.
- **Reproducibility:** preserve native artifacts, hashes, seeds, implementation versions and all failed/unresolved candidates in the audit record.

## Important Instructions

- Use the environment's supported reaction profile; stop with `PROTOCOL_REQUIRED` when essential scientific preparation is absent.
- Treat pLDDT, pose confidence, solubility, aggregation and reaction chemistry as distinct evidence.
- A missing or unconverged required result is `UNRESOLVED`, never PASS or a fabricated zero measurement.
- Do not modify the evaluator, thresholds, rewards, fixed chemistry or held-out task data.
- Re-evaluate affected evidence after sequence/structure changes; record candidate lineage.
- Respect budgets and stop explicitly rather than weakening acceptance criteria.
