# Task 008 — Reproduce historical Kemp-eliminase QM/MM free energies

## Objective

Repeat the published reaction-surface calculations for KE07, KE10(V131N), and KE15, and compare calculated activation free energies with the published computational values. Retain KE16 as a diagnostic case with an unavailable reported barrier.

## Publication and sources

[Alexandrova et al., Catalytic Mechanism and Performance of Computationally Designed Enzymes for Kemp Elimination, JACS 130, 15907–15915 (2008)](https://doi.org/10.1021/ja804040s). Computational references are Table 1, the system-specific reaction surfaces, Methods, and supporting information.

Obtain designed models using the chemistry paper's provenance and the [original enzyme-design publication](https://www.nature.com/articles/nature06879). A natural scaffold PDB file alone does not encode the designed construct.

## Inputs

| Input | Required information |
| --- | --- |
| Designed enzyme complexes | Exact KE sequence/mutation identity, ligand pose, and atom numbering |
| Reactive substrate | 5-nitrobenzisoxazole, connectivity, proton/charge conventions |
| QM/MM representation | Protein truncation, quantum region, boundaries, Hamiltonian, force field, and solvent |
| Sampling | Monte Carlo moves, FEP windows, reaction-coordinate definitions, constraints, equilibration and production |
| Source outputs | Published reaction surfaces, stationary geometries, and computed barriers |

Recover original machine-readable parameters wherever available. Identify missing input details before dispatch. The historical truncated-system representation is part of this method; a full-protein or full-assembly extension changes the reproduction condition.

## Published computational pipeline

The paper uses semiempirical QM/MM with Monte Carlo sampling and free-energy perturbation. [Primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC2680199/)

1. Begin with the published designed enzyme–substrate coordinates.
2. Construct the source protein/environment representation and assign molecular parameters.
3. Define the quantum region and the source PDDG/PM3 treatment with the surrounding molecular-mechanics model.
4. Equilibrate the reactant complex under the declared constraints.
5. Construct the reaction-coordinate sampling windows for proton transfer and ring opening.
6. Perform Monte Carlo/FEP calculations over the required coordinate space.
7. Assemble the free-energy surface and locate the relevant reactant/transition-state pathway.
8. Inspect intended bond changes and catalytic interactions.
9. Extract and report the activation free energy using the source reactant reference.
10. Analyze KE16's binding-site problem separately instead of supplying an invented barrier.

Recover the exact reaction coordinates, numerical settings, and reference solution calculation from the original Methods/supporting information. A later paper using a different Hamiltonian is a different computational protocol.

## Computational reference results

| System | Published computed ΔG‡ | Units | Source |
| --- | --- | --- | --- |
| KE07 | 8.1 | kcal/mol | Table 1 |
| KE10(V131N) | 13.5 | kcal/mol | Table 1 |
| KE15 | 12.3 | kcal/mol | Table 1 |
| KE16 | Not determined | kcal/mol | Table 1; diagnostic discussion |

These are simulated free-energy barriers, not acceptance thresholds. [Table 1 and individual-system results](https://pmc.ncbi.nlm.nih.gov/articles/PMC2680199/)

## Reproduction and comparison

Apply the [shared procedure](README.md#how-to-execute-a-task).

1. Bind each calculation to the exact designed sequence, reactive atoms, parameters, and starting structure.
2. Recover source numerical definitions and freeze the calculation before execution.
3. Verify charge, atom conservation, quantum/MM boundaries, and endpoint identity.
4. Run the published sampling protocol with traceable real execution.
5. Inspect all windows, convergence, surface connectivity, and the intended reaction mechanism.
6. Extract ΔG‡ from the same reactant reference and convert units explicitly where necessary.
7. Compare each calculated value with 8.1, 13.5, or 12.3 kcal/mol, reporting signed error, absolute error, and sampling uncertainty.
8. Preserve KE16's missing numerical target and evaluate the source-described diagnostic separately.

Use tolerances justified by reproducibility, published precision, and uncertainty. Do not choose a tolerance after seeing which values it would admit. Do not combine ΔE‡, ΔG‡, and a barrier inferred from an experimental rate into one comparison column.

A surface that fails convergence or follows an unintended reaction remains an unresolved calculation. Preserve partial outputs and costs. Do not optimize sampling or restraints until a desired number appears without identifying a changed protocol.

## Execution requirements

Verify an actual reaction-surface/QM/MM executor under the [platform policy](../MODELS_AND_TOOLS.md), including its ability to accept the required Hamiltonian, boundaries, parameters, and sampling. A quantum single-point service, fixed-topology MD, geometry check, or predicted rate cannot perform this reproduction.

If the original method is unavailable, record the exact capability gap. A supported alternative can be assessed as an adapted method with its own controls; its energies are not expected to reproduce the old Hamiltonian by definition. The current restriction does not authorize an external local engine as a fallback.

This calculation-only task can be invoked as a separate assessment experiment. Do not edit controller state to make historical designs appear to have passed fresh generation and folding. A whole-enzyme qualification run has additional requirements beyond this historical benchmark.

## Expected outputs and acceptance

Return source/structure manifests, complete method and parameter identity, raw execution receipts, sampling records, reconstructed reaction surfaces, convergence analysis, barriers/uncertainties, and the comparison table.

Report method reproduction, numerical agreement, and scientific predictive accuracy as separate conclusions. Matching a historical computed number establishes that scoped agreement; it does not establish an accurate enzyme rate.

## Experimental context

For KE15 the paper reports a rate-derived activation barrier near 17.0 kcal/mol, whereas its computed value is 12.3 kcal/mol. [Discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC2680199/) This discrepancy is useful later for evaluating predictive accuracy. The first reproduction target is the published computed value.

See [Task 007](task_007_kemp_eliminases.md) for a distinct modern Kemp simulation protocol; do not mix its EVB parameters with this QM/MM benchmark.
