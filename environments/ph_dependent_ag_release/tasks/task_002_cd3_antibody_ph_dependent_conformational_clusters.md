# task_002_cd3_antibody_ph_dependent_conformational_clusters

## Description

Calculate how two declared protonation environments change the number of sampled recognition-loop conformations in a fixed anti-CD3 antibody and four fixed variants. Calculate conformational cluster counts and the six geometric measurements of relative heavy/light variable-domain orientation for each variant and condition.

Choose suitable computational methods independently. Record the actual implementations in the output bundle.

## Target

**Target context:** CD3ε recognition.\
**Starting structure:** Structural accession 9T46; retain the parental Fab and remove the bound epitope for the production calculations.\
**Antibody panel:** Parent 40G5c; light-chain T89D, Q90E, I93H, and Q90E/I93H variants.\
**Numbering:** Use mapped antibody residue labels with insertion codes and chain identities preserved.\
**Conditions:** Physiological model at pH 7.4 and acidic model at pH 5.0.\
**Objectives:** Calculate ten conformational cluster counts and, for the same five antibodies at both conditions, the means and distributions of five domain-orientation angles and one interdomain distance.

## Scope and Constraints

- Evaluate only the five fixed antibody sequences. Verify the parental residue identity at every substitution site before applying it. Do not introduce additional substitutions or design a new antibody.
- Use the same Fab construct, chain pairing and disulfide map across the panel. Cap the C termini of both antibody chains with amide groups and preserve that treatment in all systems.
- Use the ff14SB all-atom protein force field, its appropriate titration modifications, and the TIP3P explicit-water model. Preserve these physical-model identities in the run metadata.
- Prepare explicit-solvent systems with at least 15 Å of initial protein-to-box clearance. Maintain 300 K, atmospheric pressure and a 2-fs constrained timestep.
- Estimate parental protonation behavior separately at pH 5.0 and 7.4. The variant comparison also requires an explicit imposed-state map for the introduced titratable residues. The parental condition-changing sites are light-chain E55, E161 and H189 and heavy-chain E10, E152 and H168; map their sequence indices explicitly. For these sites, model acidic carboxyl groups as neutral and acidic histidines as positively charged, with the corresponding negative/neutral states in the physiological model. Apply the declared analogous contrast to introduced titratable residues and freeze all other assignments. Preserve imposed charge contrasts as mechanistic perturbations; do not claim that they establish physical titration at those pHs.
- Use the same six recognition-loop definitions, feature atom set, frame stride, alignment, replica-combination policy and clustering procedure for every system. Cluster count depends on these choices and on sampling duration.
- The primary grouping procedure is hierarchical average linkage with a 1.2-Å RMSD threshold after variable-domain alignment. Establish the loop atom set from the supplied input-only analysis specification before claiming exact comparability; keep any alternative definition separately labeled.

- Use the shared project environment where compatible. Choose valid open-source or eligible academic/noncommercial implementations independently and verify required capabilities before production.
- Preserve input sequences and coordinates. Save preparation changes and identify substitutions in structure preparation or physical modeling as adaptations.
- Keep expected outcomes outside the calculation process. Do not use earlier numerical outcomes to select a starting model, threshold, trajectory subset or favorable result.
- Freeze the run configuration before production: physical parameters, titration formulation, temperature/pressure, solvent/charge treatment, restraints, seeds, sampling lengths, equilibration removal and analysis definitions. Record any missing prerequisite rather than inventing it.

## Computational Capabilities and End-to-End Instructions

| Stage | Required Calculation or Action |
| --- | --- |
| 1. Verify and build the panel | Retrieve and inspect 9T46, map Fab heavy/light chains, remove the epitope, and create the parent plus the four fixed variants. Save sequence/structure checks and a mutation trace for each. |
| 2. Prepare physical systems | Repair only required defects, apply the terminal treatment, solvate consistently, and minimize/equilibrate. Check connectivity, intended side-chain charge states and box geometry before sampling. |
| 3. Sample parental protonation | Run 100 ns of constant-pH dynamics for the parental Fab at each pH. Record residue states, transition statistics and the treatment of solvent relaxation after accepted changes. Keep the pH and charge history with the trajectory. |
| 4. Freeze variant protonation models | Create a residue-by-condition charge-state registry from the parental sampling and the defined variant perturbations. If the intended imposed states cannot be established, mark exact comparability unavailable; do not silently replace them with arbitrary defaults. |
| 5. Explore recognition-loop ensembles | Run well-tempered bias-exchange metadynamics with six exchanging replicas, one biased loop per replica, for 1,000 ns per replica and system/condition. Use sine/cosine ψ-angle loop features, Gaussian height 10 kJ/mol, width 0.35 rad, deposition every 1,000 integration steps, and bias factor 10. Freeze the remaining bias/exchange settings before production. |
| 6. Cluster sampled conformations | Correct periodic imaging, remove solvent for structural analysis, align to the fixed variable-domain selection, and apply the declared CDR RMSD clustering. Keep all frame-to-cluster assignments, representatives and condition labels. |
| 7. Check representative stability | Prepare each selected cluster representative consistently and run 200 ns of unbiased classical dynamics from it. Use these runs for stability/sampling checks; do not substitute their separately computed cluster counts for the primary enhanced-ensemble count. |
| 8. Report the pH comparison | Report one primary cluster count per antibody/condition, the exact number of analyzed frames, total sampling duration and a cluster-count-versus-sampling curve. On the combined unbiased trajectories, calculate the torsion vHL, tilt angles vHC1/vLC1/vHC2/vLC2, and interdomain distance dc using one explicitly defined set of domain frames and geometric conventions. Save time series, means, spread and uncertainty; do not confuse the enhanced-sampling cluster ensemble with the unbiased orientation ensemble. Calculate acidic-minus-physiological count differences without tuning the threshold to obtain a preferred ordering. |

## Evaluation Metrics

| Objective | Output and Conditions | Calculation Scope and Reporting |
| --- | --- | --- |
| Recognition-loop conformational cluster count | Integer count; five antibodies × two conditions | Count nonempty clusters using the frozen hierarchical average-linkage procedure and 1.2-Å RMSD criterion. Report complete cluster assignments, atom selections, alignment, frame stride and replica handling. |
| Heavy/light variable-domain orientation | Five angles in degrees and dc in Å; each antibody/condition | Calculate vHL, vHC1, vLC1, vHC2, vLC2 and dc from the unbiased representative-trajectory ensemble. Record domain alignment/templates, atom selections, frame handedness, angle signs, periodic wrapping and population weighting. Report trajectory spread and uncertainty of the mean separately. |
| Within-antibody pH difference | Count difference | Calculate N(acidic model) − N(physiological model) from the matched primary counts. This is a conformational-diversity summary, not a binding affinity. |

Record all per-run observations and aggregate results with metric definitions, conditions, units, uncertainty and native-artifact paths. Keep non-comparable quantities explicitly separated.

## Expected Output

**Format:** `ph_dependent_antibody_analysis_bundle`\
**Directory:** `results/task_002_cd3_antibody_ph_dependent_conformational_clusters/<run_id>/` (relative to the environment root)

- `cluster_counts.csv`: antibody, pH/model label, analyzed frames, number of clusters and sampling duration.
- `cluster_assignments.csv`: system, trajectory/frame and assigned cluster.
- `cluster_sampling_curves.csv`: cluster count as a function of analyzed frames or sampling time.
- `condition_differences.csv`: matched acidic-minus-physiological count and orientation differences.
- `orientation_timeseries.csv`: trajectory-level values for the five angles and interdomain distance.
- `orientation_summary.csv`: means, distribution spread, uncertainty and geometric convention for every antibody/condition.
- A coordinate file for each cluster representative and the explicit residue-by-condition protonation map.

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
