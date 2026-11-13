# task_005_antibody_complex_ph_dependent_hydration_and_clustering

## Description

Calculate pH-dependent local hydration energetics and conformational diversity of a fixed antibody–antigen complex. Evaluate the hydration of a defined light-chain recognition-loop histidine and the number of conformational clusters under matched neutral and acidic conditions.

Choose suitable computational methods independently. Record the actual implementations in the output bundle.

## Target

**Antibody:** A05 / TPL0552_01_A05, using its verified paired variable-domain sequences and intended simulated construct.\
**Antigen:** Myotoxin II, preserving the verified antigen sequence and structure in the complex input.\
**Primary complex conditions:** pH 7.5 and 5.5.\
**Protonation-preparation conditions:** pH 7.5 and 5.0 are represented in the initial setup; determine whether these state assignments adequately represent the pH 5.5 analysis condition.\
**Region of interest:** Light-chain His91 in the third recognition loop, with an explicit numbering and atom-selection map.\
**Primary objective:** Calculate the selected residue–water interaction energy at each primary pH.\
**Secondary diagnostic:** Calculate complex conformational cluster counts under a frozen definition. Direct numerical cluster-count comparison is conditional on independently verified matching definitions; otherwise report a method-dependent diagnostic rather than an exact reproduction target.

## Scope and Constraints

- Use the fixed A05 antibody and the verified cognate antigen. Do not generate new antibody sequences, antigen substitutions, toxicity variants or additional design candidates.
- Obtain the correct paired antibody sequences, antigen construct and starting complex from the designated input package. Prefer recoverable verified coordinates. If a new complex must be predicted, declare the starting-pose uncertainty and treat the run as an adaptation.
- Keep the antibody fragment boundaries, chain pairing, disulfides, antigen assembly and terminal treatment consistent across conditions. Preserve interfacial waters where justified and document all solvent changes.
- Use the ff14SB all-atom protein force field with compatible titration parameters and the TIP3P explicit-water model. Use at least 12 Å of initial protein-to-box clearance, 300 K, atmospheric pressure and a 2-fs constrained timestep.
- Prepare protonation through three independent 100-ns constant-pH trajectories per declared preparation condition. A preparation pH of 5.0 is not a simulation at pH 5.5; establish the mapping or add a separately labeled pH 5.5 titration branch before claiming condition equivalence.
- For each primary pH condition, execute three independent 1-μs classical production trajectories. Keep pH 5.0 as a separate optional sensitivity condition, not a pooled acidic replicate.
- Freeze the histidine atom/water selection and energy terms. Freeze the clustering alignment, feature atoms, distance metric, algorithm, threshold, frame stride, replica combination and occupancy rule. These clustering details are not established by the numerical cluster counts alone.

- Use the shared project environment where compatible. Choose valid open-source or eligible academic/noncommercial implementations independently and verify required capabilities before production.
- Preserve input sequences and coordinates. Save preparation changes and identify substitutions in structure preparation or physical modeling as adaptations.
- Keep expected outcomes outside the calculation process. Do not use earlier numerical outcomes to select a starting model, threshold, trajectory subset or favorable result.
- Freeze the run configuration before production: physical parameters, titration formulation, temperature/pressure, solvent/charge treatment, restraints, seeds, sampling lengths, equilibration removal and analysis definitions. Record any missing prerequisite rather than inventing it.

## Computational Capabilities and End-to-End Instructions

| Stage | Required Calculation or Action |
| --- | --- |
| 1. Establish exact input identities | Verify the paired A05 sequences, cognate antigen, fragment boundaries, chain mapping and light-chain His91 position. Recover or construct the declared complex, record its provenance and freeze the starting-pose inclusion rule. |
| 2. Prepare matched complexes | Repair required defects, apply verified bonds, build equivalent explicit-solvent systems, and save topology/parameter and residue/atom mappings. Inspect the recognition-loop hydration region without selecting a preferred configuration by its expected energy. |
| 3. Determine protonation models | Perform the three 100-ns titration replicates at each preparation condition, with and without antigen where specified by the frozen protocol. Establish condition-specific fixed-charge models for the subsequent classical runs and validate or extend the pH 5.5 assignment as required. |
| 4. Equilibrate and run classical production | Minimize/equilibrate every prepared complex and run three independent 1-μs trajectories at pH-state models corresponding to 7.5 and 5.5. Record seeds, stability, actual simulated durations and any restarts. Save energy-analysis frames and structures at a frozen cadence. |
| 5. Calculate local residue–water energy | Calculate the selected histidine–water electrostatic and van der Waals interactions on every eligible frame. Preserve component terms, their total, atom selections and the handling of solvent entry/exit from the selected region. |
| 6. Calculate conformational clusters | Make the complex whole, align using the declared protein selection, and apply the frozen clustering protocol to the declared complex features. Preserve every frame assignment and representative. If exact clustering definitions are not supplied, run an explicitly labeled alternative and retain the unresolved comparability status. |
| 7. Assess sampling and uncertainty | Report local-energy estimates by replicate and time block. Evaluate cluster-count stability under matched frame counts and sampling durations; keep this diagnostic distinct from changing the declared primary clustering rule. |
| 8. Finalize the condition comparison | Report both pH-specific primary energy estimates and secondary diagnostic cluster counts, together with the acidic-minus-neutral differences. Mark exact cluster-count comparison unavailable when the matching clustering specification is absent; this limitation is distinct from whether the diagnostic itself was executed. Freeze all numerical outputs for later independent assessment; do not choose a clustering threshold or interaction definition to force a desired answer. |

## Evaluation Metrics

| Objective | Output and Conditions | Calculation Scope and Reporting |
| --- | --- | --- |
| Selected light-chain histidine–water interaction energy | kcal/mol; mean and uncertainty at pH 7.5 and 5.5 | Report electrostatic, van der Waals and total terms with the exact histidine atom set, solvent selection and molecular context. This is a local interaction energy, not antibody–antigen binding ΔG. |
| Secondary, method-dependent complex conformational cluster count | Integer count at each primary pH | Report the diagnostic count using one frozen definition, plus the analyzed-frame denominator, replica policy, feature selection, threshold and representative coordinates. |
| pH-dependent changes | kcal/mol difference and count difference | Calculate acidic-minus-neutral changes only under matched definitions and sampling scope. Treat alternative-clustering results as separate outputs. |

Record all per-run observations and aggregate results with metric definitions, conditions, units, uncertainty and native-artifact paths. Keep non-comparable quantities explicitly separated.

## Expected Output

**Format:** `ph_dependent_antibody_analysis_bundle`\
**Directory:** `results/task_005_antibody_complex_ph_dependent_hydration_and_clustering/<run_id>/` (relative to the environment root)

- `local_energy_timeseries.csv`: per-frame local energy components and selections.
- `local_energy_summary.csv`: per-replicate and pH-level energies, spread and uncertainty.
- `cluster_counts.csv`: condition, replicate/combined scope, analyzed frames, primary cluster count and protocol identifier.
- `cluster_assignments.csv`: frame-level assignments with a coordinate file for each representative.
- `condition_differences.csv`: matched pH-dependent energy/count changes.
- `protonation_assignment_status.json`: preparation conditions, state assignments and the justification or limitation for representing the pH 5.5 branch.

- `input_manifest.json`: verified input identities, sequences, structure paths, chain/residue/atom maps, hashes and unresolved facts.
- `protocol.json`: frozen conditions, physical-model identities, sampling budgets, primary metric definitions and uncertainty estimators.
- `run_manifest.json`: actual implementations and versions, commands/configuration paths, seeds, devices, durations, execution status and artifact hashes.
- `metrics.json`: newly calculated objective values with condition labels, units, definitions, uncertainty and comparability status.
- `report.md`: executed workflow, numerical findings, quality-control evidence, adaptations, incomplete endpoints and limitations.
- Native starting/prepared coordinates, parameter/topology files, trajectories, state/bias histories where applicable, analysis scripts, configuration files and logs.


## Independent Execution and Input Access

- Work from this task, explicitly supplied input files, authoritative structure/sequence records, and implementation documentation. Choose suitable computational implementations independently.
- Do not search for or open research papers, supplements, answer tables, earlier comparison reports, historical calculation results, or prior conversation logs. Do not follow publication links attached to structure/sequence records.
- Restrict file discovery to the task directory, designated input folders, required software-installation locations and this run's output directory. Do not search parent/home directories or unrelated caches for results or instructions.
- If essential sequence or setup information is absent, request an input-only package or declare the missing input. Do not retrieve a paper to fill the gap, and do not invent the missing information.
- Before production, freeze input hashes, molecular context, conditions, metric definitions and sampling policy. Freeze final results before a separate evaluator gains access to numerical comparison material.

## Important Instructions

- Execute new calculations and retain their native outputs. A proposed workflow, prepared structure or short pilot does not complete production.
- Treat the listed metrics as the only assessment objectives. Structural checks and sampling diagnostics support validity rather than adding new property-design objectives.
- Use a separate run directory and unique run ID. Keep generated artifacts outside this task-definition directory and preserve a restartable directory layout.
- Run long calculations in a persistent terminal session with logging, checkpoints and recorded instructions for reattachment. Record the compute/sampling budget and the reason for stopping.
- Before long runs, perform a small setup/runtime check of the chosen physical model, titration behavior and analysis path. Do not substitute pilot values for final production results.
- Estimate uncertainty using independent runs and/or correlation-aware time blocks. Label standard deviation, standard error and confidence intervals explicitly; trajectory frames are not automatically independent samples.
- Use valid equilibrium weighting or bias reweighting where required. Preserve native energy units and record conversions.
- If exact sequences, starting coordinates, protonation assignments or a required analysis definition are unavailable from the task and input-only records, finish independent feasible stages and report `NEEDS_INPUT` or `COMPARABILITY_UNRESOLVED` for the affected endpoint. Preserve newly computed alternative results with their changed definition clearly identified.
- Report `COMPLETED` only when every mandatory computation has been executed and documented. Use `COMPLETED_WITH_LIMITATIONS` for executed outputs with bounded comparison limitations, and `INCOMPLETE` when mandatory calculations remain unexecuted. Agreement with an expected result is not a completion requirement.
- Freeze computed outputs before an independent evaluator performs any numerical comparison. Do not fabricate outcomes, adjust definitions to improve agreement or label an unexecuted result as calculated.
