# task_003_histidine_free_antibody_ph_dependent_contact_frequency

## Description

Calculate the pH dependence of one defined local intramolecular interaction in a fixed histidine-free antibody. The endpoints are the interaction frequency between adjacent light-chain glutamate and serine residues and the occupancy of the intramolecular hydrogen bond between two heavy-chain glutamates in the antigen-free variable fragment.

Choose suitable computational methods independently. Record the actual implementations in the output bundle.

## Target

**Antibody:** C08 / TPL0197_01_C08.\
**Molecular format:** Verified paired heavy/light variable domains, antigen-free.\
**Primary residue pair:** Light-chain Glu55 and Ser56, mapped to the actual sequence and simulation indices.\
**Primary pH contrast:** 7.4 versus 5.5.\
**Additional condition:** pH 5.0 as a separately labeled sensitivity branch if the acidic simulation assignment cannot be resolved from the input records.\
**Objectives:** Calculate light-chain Glu55–Ser56 interaction frequency and heavy-chain Glu95–Glu96 hydrogen-bond occupancy independently at each declared pH. The acidic heavy-chain occupancy is assessed as a bounded numerical quantity, not an exact point target.

## Scope and Constraints

- Preserve the fixed heavy/light sequences, fragment boundaries and all verified disulfides, including the additional heavy-chain recognition-loop disulfide. Confirm that the variable domains contain no histidine.
- Obtain a recoverable starting structure with verified identity. If a new structure must be built from sequence, retain starting-model uncertainty and label the run as an adaptation. Do not select models based on their agreement with expected interaction frequencies.
- Keep production antigen-free. Do not replace the task with antibody–antigen docking, affinity scoring or toxin modification.
- Keep pH 5.0 and 5.5 distinct. If the original acidic assignment remains unresolved, run both acidic branches independently rather than silently assigning one label to the other.
- Freeze the Glu55/Ser56 atom selections and interaction definition before production analysis. Use the intended contact type, distance/angle criteria, frame selection and population-weighting rule if provided in the input-only analysis specification. If unavailable, predeclare an alternative and mark its direct numerical comparability unresolved.
- Use consistent explicit solvent, the ff14SB all-atom protein force field with compatible titration parameters and the TIP3P water model, 300 K, atmospheric pressure, a 2-fs constrained timestep and at least 12 Å of initial solvent clearance.
- Only the two specified interaction frequencies are assessment objectives. Protonation, loop motion and fold checks support interpretation and quality control; they do not add binding-affinity or kinetic objectives.

- Use the shared project environment where compatible. Choose valid open-source or eligible academic/noncommercial implementations independently and verify required capabilities before production.
- Preserve input sequences and coordinates. Save preparation changes and identify substitutions in structure preparation or physical modeling as adaptations.
- Keep expected outcomes outside the calculation process. Do not use earlier numerical outcomes to select a starting model, threshold, trajectory subset or favorable result.
- Freeze the run configuration before production: physical parameters, titration formulation, temperature/pressure, solvent/charge treatment, restraints, seeds, sampling lengths, equilibration removal and analysis definitions. Record any missing prerequisite rather than inventing it.

## Computational Capabilities and End-to-End Instructions

| Stage | Required Calculation or Action |
| --- | --- |
| 1. Freeze sequence and structure inputs | Verify both C08 variable-domain sequences, their pairing, the residue map and the extra disulfide. Obtain an initial coordinate model or construct an independently justified model ensemble. Preserve all input identifiers and hashes. |
| 2. Prepare matched systems | Build each pH branch from the same eligible structures using one repair, terminal, solvation and charge-treatment policy. Inspect the Glu55–Ser56 neighborhood before and after preparation. |
| 3. Calculate protonation behavior | Run 100 ns of explicit-solvent constant-pH dynamics per declared pH. Track ionization states of the relevant acidic residues and establish the charge-state models used in subsequent sampling. Save state histories and sampling diagnostics. |
| 4. Explore structural states | Run well-tempered bias-exchange metadynamics for 500 ns using the six recognition-loop ψ-angle sine/cosine features. Use Gaussian height 10 kJ/mol, width 0.3 rad, deposition every 1,000 integration steps and bias factor 10. Freeze replica, exchange and frame-recording settings before execution. |
| 5. Obtain unbiased structural samples | Align the variable fragment and perform hierarchical average-linkage clustering with a 1.2-Å RMSD criterion using declared loop selections. Equilibrate the representatives and run 100 ns of unbiased dynamics from each. Preserve the mapping from every representative to its originating condition. |
| 6. Calculate the contact indicator | For every eligible analyzed frame, evaluate the frozen Glu55–Ser56 interaction rule and the heavy-chain Glu95–Glu96 hydrogen-bond rule. For the latter, define eligible donor/acceptor atoms, protonation states, distance and angle cutoffs; count each residue-pair interaction at most once per frame while retaining atom-level records. Save a binary interaction indicator and the geometric quantities needed to reproduce the decision. |
| 7. Aggregate without population bias | Calculate contact frequency with the declared ensemble estimator. If trajectories start from selected cluster representatives, use validated state populations or a validated equilibrium estimator; do not treat unequal or deliberately selected starts as automatically population weighted. Do not combine biased frames without valid reweighting. |
| 8. Finalize the pH contrast | Report per-trajectory and pH-level contact frequencies, the eligible-frame denominator, uncertainty and the acidic-minus-neutral frequency change. Keep both acidic branches separate if the input assignment remains unresolved. |

## Evaluation Metrics

| Objective | Output and Conditions | Calculation Scope and Reporting |
| --- | --- | --- |
| Glu55–Ser56 interaction frequency | Percent; one value per declared pH | Compute 100 × sum(w_i I_i) / sum(w_i), where I_i is the declared interaction indicator and w_i is the justified equilibrium/reweighting weight. Use unit weights only when equal weighting is justified. |
| Heavy-chain Glu95–Glu96 hydrogen-bond occupancy | Percent; each declared pH, with the acidic branch primary | Calculate the population-weighted fraction of eligible frames containing the declared intramolecular hydrogen bond. Retain donor/acceptor identities and raw geometry. A bounded assessment must not be reported as agreement with an exact percentage. |
| pH-dependent contact-frequency change | Percentage points | Calculate frequency(acidic) − frequency(7.4) separately for each acidic branch. A percentage-point change is not a fold change or a binding-energy difference. |

Record all per-run observations and aggregate results with metric definitions, conditions, units, uncertainty and native-artifact paths. Keep non-comparable quantities explicitly separated.

## Expected Output

**Format:** `ph_dependent_antibody_analysis_bundle`\
**Directory:** `results/task_003_histidine_free_antibody_ph_dependent_contact_frequency/<run_id>/` (relative to the environment root)

- `contact_timeseries.csv`: condition, trajectory/frame, residue selections, geometric measurements, indicator and frame weight.
- `contact_frequencies.csv`: per-trajectory and pH-level frequencies for both residue pairs, denominators, uncertainty and estimator definition.
- `condition_differences.csv`: acidic-minus-neutral frequency differences with the acidic branch explicitly identified.
- `ph_assignment_status.json`: resolved versus unresolved acidic-condition assignment and the executed branches.

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
