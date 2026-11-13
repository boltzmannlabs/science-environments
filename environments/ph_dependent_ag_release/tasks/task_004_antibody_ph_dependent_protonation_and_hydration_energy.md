# task_004_antibody_ph_dependent_protonation_and_hydration_energy

## Description

Calculate protonation and local residue–water interaction energetics in a fixed antibody panel. Evaluate the light-chain histidine at the variable-domain interface at neutral and acidic pH, without designing new antibody or antigen variants. Include the specified fixed control and fixed control-derived variant in the local-energy comparison.

Choose suitable computational methods independently. Record the actual implementations in the output bundle.

## Target

**Antibody panel:** A01 / 2555_01_A01; D11 / 2554_01_D11; and the fixed D11 light-chain Y32S/Y49A variant.\
**Antigen context:** A01 with α-cobratoxin and the verified D11 context with its cognate antigen. D11 starting structures contain α-bungarotoxin; retain this distinction. Freeze the molecular context for the fixed D11-derived variant in the input manifest. Do not silently replace one antigen with another.\
**Starting complex:** Structural accession 9HUO or another verified A01–antigen structure with the same construct; record the chosen entry and assembly. Use structural accession 9HUB or another sequence-matched D11 entry for its control, and construct only the two declared light-chain substitutions for the fixed variant.\
**Region of interest:** Light-chain His34 in the first recognition loop, with an explicit sequence-to-structure residue map.\
**Primary computational pHs:** 7.5 and 5.5.\
**Objectives:** Calculate the A01 His34 protonated-state probability and the mean local His34–water nonbonded interaction energy for A01, D11 and fixed D11-Y32S/Y49A at both pHs. Only A01 has a primary protonation-probability assessment; do not impose an unsupported probability target on the controls.

## Scope and Constraints

- Use the verified fixed panel and antigen sequences; check that D11 residues 32 and 49 are tyrosines before creating its specified Y32S/Y49A variant. Preserve the experimental chain pairing, construct boundaries, linker where present, and disulfides. Generate only those two fixed control substitutions. Do not optimize new substitutions, redesign the antigen or introduce another antigen as a replacement.
- Keep antigen-bound and antigen-free records distinct. Antigen-bound production is the primary declared context; use any antigen-free variable-domain sampling as a separately labeled auxiliary branch. Establish each quantity's molecular context from the input-only specification before claiming strict numerical matching.
- A crystallization pH describes the starting structure, not the simulated solution. Simulate the chosen structure at both declared computational pHs; do not silently change pH 7.5 to 7.4.
- Use a compatible constant-pH all-atom protein parameterization, the ff14SB protein force field and the TIP3P explicit-water model, at least 12 Å of solvent clearance, 300 K, atmospheric pressure and a 2-fs constrained timestep.
- Map all neutral and positively charged His34 states, including neutral tautomers, explicitly. A fixed charged histidine does not by itself estimate a protonation probability.
- Freeze the local energy selections, water-region rule, electrostatic and van der Waals conventions, cutoffs and long-range treatment before analyzing production trajectories. In particular, establish whether the energy selection is the imidazole group or the entire residue, and whether waters are local or all solvent.
- The local interaction energy is a hydration/nonbonded quantity, not binding free energy. Do not fit empirical affinity coefficients or convert it into a dissociation constant.

- Use the shared project environment where compatible. Choose valid open-source or eligible academic/noncommercial implementations independently and verify required capabilities before production.
- Preserve input sequences and coordinates. Save preparation changes and identify substitutions in structure preparation or physical modeling as adaptations.
- Keep expected outcomes outside the calculation process. Do not use earlier numerical outcomes to select a starting model, threshold, trajectory subset or favorable result.
- Freeze the run configuration before production: physical parameters, titration formulation, temperature/pressure, solvent/charge treatment, restraints, seeds, sampling lengths, equilibration removal and analysis definitions. Record any missing prerequisite rather than inventing it.

## Computational Capabilities and End-to-End Instructions

| Stage | Required Calculation or Action |
| --- | --- |
| 1. Verify the complex | Retrieve the A01 and D11 input complexes, construct only the fixed D11-Y32S/Y49A control variant, map their heavy/light domains and antigen contexts, and identify His34 independently of coordinate-file residue numbering. Record any missing atoms, alternate conformations and relevant crystallographic waters. |
| 2. Prepare matched pH systems | Apply consistent repairs, bond definitions, solvent and charge treatment. Prepare both pH conditions from common coordinates and retain a complete preparation log. |
| 3. Sample protonation | Run three independent 100-ns constant-pH trajectories per pH and molecular context. Save residue-state histories and evaluate histidine tautomer/charge transitions, independent-run agreement and retained equilibration intervals. |
| 4. Sample structural configurations | Use a declared well-tempered recognition-loop bias-exchange protocol for the variable-region ensemble, with a 500-ns exploration budget, Gaussian height 10 kJ/mol, deposition every 5,000 integration steps and bias factor 10. Use the bias width, exchange schedule and molecular context from the supplied input-only protocol; do not treat unknown settings as fixed defaults. |
| 5. Generate unbiased samples | Align the variable region, cluster with hierarchical average linkage at a 1.2-Å RMSD criterion using frozen atom selections, and run 100-ns unbiased trajectories from eligible representatives. If the exploration and energy systems have different antigen contexts, generate a separate matched bound-system ensemble; do not transfer populations or energies between them. |
| 6. Calculate protonation probability | Calculate the His34 positively charged occupancy from the constant-pH state histories after declared equilibration. Include neutral tautomer states in the denominator, handle intermediate states according to the chosen valid titration formulation, and estimate autocorrelation-aware uncertainty. |
| 7. Calculate local hydration energies | For each of the three fixed systems at both pHs, calculate the declared His34–water electrostatic and van der Waals terms and their intended total on the matched analysis trajectories. Within-system pH contrasts are primary; do not interpret differences across unlike antigen contexts as an affinity ranking. Preserve raw frame-level energies and the exact atom/water selection used on each frame. Do not infer energies from water counts. |
| 8. Finalize the pH comparison | Report per-run and condition-level protonation probabilities and local interaction energies with units, distribution summaries, uncertainty definitions and acidic-minus-neutral changes. If the energy component or water definition is not specified in the input-only records, keep the newly calculated metric but mark exact numerical comparability unresolved. |

## Evaluation Metrics

| Objective | Output and Conditions | Calculation Scope and Reporting |
| --- | --- | --- |
| A01 His34 protonated-state probability | Fraction in [0, 1]; each pH, with pH 5.5 primary | Calculate the positively charged population from actual titration sampling. Report effective sample size, transition counts and uncertainty; fixed protonation assignments are not population estimates. |
| Local His34–water interaction energy | kcal/mol; three fixed systems × pH 7.5 and 5.5 | Retain electrostatic, van der Waals and total terms separately. Identify which term matches the defined endpoint, its atom selections and molecular context. Distinguish trajectory spread from uncertainty of the mean. |
| pH-dependent changes | Fraction difference and kcal/mol difference | Calculate acidic-minus-neutral changes only between matched systems and equivalent energy definitions. |

Record all per-run observations and aggregate results with metric definitions, conditions, units, uncertainty and native-artifact paths. Keep non-comparable quantities explicitly separated.

## Expected Output

**Format:** `ph_dependent_antibody_analysis_bundle`\
**Directory:** `results/task_004_antibody_ph_dependent_protonation_and_hydration_energy/<run_id>/` (relative to the environment root)

- `protonation_timeseries.csv`: condition, replicate, time and His34 charge/tautomer state.
- `protonation_probabilities.csv`: per-replicate and pH-level probabilities, retained samples, effective sample size and uncertainty.
- `local_energy_timeseries.csv`: frame-level energy terms, atom/water-selection identity and condition.
- `local_energy_summary.csv`: system- and pH-specific means, spread, uncertainty of the mean and energy definition.
- `condition_differences.csv`: matched pH changes, without mixing free and bound contexts.

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
