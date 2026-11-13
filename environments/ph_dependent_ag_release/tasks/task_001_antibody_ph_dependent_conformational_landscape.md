# task_001_antibody_ph_dependent_conformational_landscape

## Description

Calculate the pH-dependent conformational landscape of a fixed engineered anti-TNF-α antibody. Evaluate only CDR backbone displacement, the separation of the heavy- and light-chain third recognition loops, and the relative conformational potential of mean force. Execute new simulations and retain numerical outputs for independent assessment.

Choose suitable computational methods independently. Record the actual implementations in the output bundle.

## Target

**Antibody:** W1 engineered anti-TNF-α antibody, with its unmodified parent as a structural control.\
**Antigen context:** TNF-α; the primary production system is the antigen-free antibody fragment.\
**Starting structure:** Structural accession 4NYL, using verified antibody chains and fragment boundaries; structural accession 3WD5 may establish the antigen-bound geometry for alignment only.\
**Input-only bundle:** Supply an external input-only directory containing `parent_HL.pdb`, `parent_sequences.fasta`, `fixed_sequences.fasta`, and `sequence_edits.json`. Record its supplied location and file hashes in `input_manifest.json`; this package does not include the bundle. If it is unavailable, report `NEEDS_INPUT` for affected stages. The fixed edits are light-chain Q89H/Y91H and heavy-chain L108H in one-based full polymer sequence positions; map them to coordinate indices before building the model.\
**pH conditions:** 6.0 and 7.4.\
**Objective:** Calculate CDR backbone RMSD, HCDR3–LCDR3 center-of-mass distance, and their two-dimensional relative conformational free-energy surface.

## Scope and Constraints

- Use the fixed antibody sequence; do not generate or optimize new substitutions. Obtain the exact engineered sequence before production. Parent coordinates alone do not identify the engineered sequence.
- Preserve heavy/light pairing, resolved fragment boundaries, disulfides and the chosen terminal treatment. Keep antigen-free production trajectories separate from any bound structural control.
- Map HCDR2, HCDR3 and LCDR1–LCDR3 explicitly. Freeze the backbone atom selection, alignment selection, residue numbering and coordinate frame before analysis.
- Use matched solvated systems and a validated constant-pH Hamiltonian at both pHs. The temperature is 310 K and the integration timestep is 2 fs with hydrogen-bond constraints.
- Use four independent 300-ns enhanced-sampling production trajectories per pH, following 20 ns of enhanced-sampling equilibration. Perform four independent 200-ns conventional constant-pH comparison trajectories per pH. Log any reduction as incomplete sampling rather than full completion.
- A coupled Gaussian-accelerated/constant-pH method must be implemented consistently with its reweighting procedure. Replacing it with ordinary fixed-charge trajectories changes the calculation.
- Freeze the two-dimensional coordinate grid, bin widths, sparse-bin policy and reweighting settings without consulting expected outcomes. Export the full sampled surface, not only selected minima; include a declared evaluation lattice with 0.5-Å RMSD spacing and 1-Å distance spacing. Keep native histogram estimates distinct from interpolated values. Set a separate free-energy zero for each pH surface.

- Use the shared project environment where compatible. Choose valid open-source or eligible academic/noncommercial implementations independently and verify required capabilities before production.
- Preserve input sequences and coordinates. Save preparation changes and identify substitutions in structure preparation or physical modeling as adaptations.
- Keep expected outcomes outside the calculation process. Do not use earlier numerical outcomes to select a starting model, threshold, trajectory subset or favorable result.
- Freeze the run configuration before production: physical parameters, titration formulation, temperature/pressure, solvent/charge treatment, restraints, seeds, sampling lengths, equilibration removal and analysis definitions. Record any missing prerequisite rather than inventing it.

## Computational Capabilities and End-to-End Instructions

| Stage | Required Calculation or Action |
| --- | --- |
| 1. Verify inputs | Retrieve the starting antibody structure, obtain the fixed engineered sequence, identify the intended fragment, and create an explicit chain/residue/atom map. Record whether coordinates were experimentally determined or rebuilt. If the W1 substitutions cannot be verified, finish input preparation and mark production as needing input. |
| 2. Prepare matched systems | Apply only necessary repairs and the fixed substitutions; preserve bonds and chain boundaries. Build equivalent explicit-solvent systems with the same physical parameters, water treatment and charge policy. Save the parent alignment structure and prepared production structures separately. |
| 3. Minimize and equilibrate | Minimize the systems and run 1 ns of constant-volume equilibration followed by 1 ns of constant-pressure equilibration. Check stability and titratable-residue support before continuing. |
| 4. Run pH-dependent enhanced sampling | At each pH, equilibrate the coupled constant-pH/Gaussian-accelerated dynamics for 20 ns, then run four 300-ns production trajectories with independent seeds. Save coordinates and all bias/protonation records needed to reconstruct unbiased probabilities; preserve the 0.2-ps coordinate-recording cadence or declare a changed cadence. |
| 5. Calculate coordinates | Make molecules whole, align to the frozen antibody frame, and calculate the declared CDR backbone RMSD and HCDR3–LCDR3 center-of-mass separation for every retained frame. Preserve the pairing of these coordinates by frame and trajectory. |
| 6. Construct conformational surfaces | Apply validated bias reweighting and calculate the two-dimensional probability and relative potential-of-mean-force grids. Use F = −R T ln P plus a pH-specific constant, report kcal/mol, and retain the probability grid and support counts. Do not assign finite energies to unsupported bins. |
| 7. Run conventional comparison | Select representatives using a frozen basin-selection rule, then execute the four 200-ns constant-pH comparison trajectories per pH. Assess coordinate and basin stability independently of the biased trajectories. |
| 8. Finalize numerical outputs | Report per-trajectory coordinates, pH-specific conformational surfaces, reproducible basin locations, sampling support and uncertainty. Freeze results before any independent numerical comparison. A difference between the two arbitrary PMF zero points is not a binding-energy change. |

## Evaluation Metrics

| Objective | Output and Conditions | Calculation Scope and Reporting |
| --- | --- | --- |
| CDR backbone RMSD | Å; per frame and per pH | Use HCDR2–HCDR3 and LCDR1–LCDR3 with a fixed backbone atom set and a declared structural alignment. Preserve the alignment and RMSD selections separately. |
| HCDR3–LCDR3 separation | Å; per frame and per pH | Calculate the distance between the declared loop centers of mass with the same atom/mass selections at both pHs. |
| Relative conformational PMF | kcal/mol; two-dimensional grid for each pH | Provide RMSD coordinate, distance coordinate, probability, reweighting support and PMF for every grid cell. Each surface has an independent zero; this is an antibody conformational free energy, not antigen-binding free energy. |

Record all per-run observations and aggregate results with metric definitions, conditions, units, uncertainty and native-artifact paths. Keep non-comparable quantities explicitly separated.

## Expected Output

**Format:** `ph_dependent_antibody_analysis_bundle`\
**Directory:** `results/task_001_antibody_ph_dependent_conformational_landscape/<run_id>/` (relative to the environment root)

- `coordinate_timeseries.csv`: trajectory/frame/pH identifiers, CDR RMSD and interloop distance.
- `conformational_landscape.csv`: pH, grid coordinates, probability, PMF, sampling support and uncertainty.
- `basin_summary.csv`: independently identified basin positions and populations, including the selection definition.
- `conventional_comparison.csv`: coordinate summaries and sampling diagnostics from the conventional trajectories.

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
