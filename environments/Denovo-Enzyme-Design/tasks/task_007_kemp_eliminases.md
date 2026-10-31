# Task 007 — Reproduce Kemp-eliminase design and simulation results

## Objective

Reproduce selected computational results for Des27 and Des27.7: substrate retention, reactive conformations, catalytic geometry, and EVB free-energy profiles. Use the released models to establish numerical comparison before rerunning the broader design workflow.

## Publication and sources

[Listov et al., Complete computational design of high-efficiency Kemp elimination enzymes, Nature 643, 1421–1427 (2025)](https://doi.org/10.1038/s41586-025-09136-2). Relevant sources include Fig. 3, MD/EVB Methods, Supplementary Data 2, and the source computational records.

Recover the [design code and datasets](https://github.com/Fleishman-Lab/denovoKemp) and [simulation files](https://doi.org/10.5281/zenodo.14563437). The supplement contains calculated activation energies, geometries, protonation, and simulation settings. These are the initial numerical references.

## Inputs

| Input | Required identity |
| --- | --- |
| Des27 and Des27.7 | Exact sequences, mutation lineage, FuncLib models, and residue numbering |
| Ligand | 5-nitrobenzisoxazole topology, charges, parameters, and initial poses |
| MD systems | Bound/unbound representations, protonation, solvent/ions, restraints, and equilibration |
| EVB systems | In/out conformers, parameterization, calibration, windows, trajectories, and reference states |
| Computational references | Supplementary Data 2, Fig. 3 source values, and released analysis outputs |

Preserve native Rosetta energy units separately from kcal/mol. Distinguish designed structures from crystal structures and generated simulation snapshots. Confirm the full modeled system, including solvent ions, rather than treating every nonprotein atom as a removable cofactor.

## Published computational pipeline

The [author design repository](https://github.com/Fleishman-Lab/denovoKemp) provides the fragment-assembly/design stage. The [simulation deposit](https://zenodo.org/records/14563437) provides the molecular-simulation stage.

1. Assemble diverse TIM-barrel backbones from the source fragments.
2. Apply PROSS stability design and Rosetta catalytic-site matching/design.
3. Filter/stabilize selected models and apply FuncLib to the specified active-site positions.
4. Use the exact published Des27/Des27.7 models as starting points for simulation.
5. Parameterize ligand/system and prepare the bound/unbound MD conditions.
6. Run equilibration and independent production replicas.
7. Analyze substrate retention and productive orientations.
8. Extract the in/out starting conformers for EVB.
9. Run the source EVB protocol and calculate reaction free-energy profiles.
10. Aggregate trajectories, uncertainty, stationary-point structures, and geometry statistics.

The study used experimental screening between design stages. For computational reproduction, use the same published selected inputs; do not describe the historical selection as wholly computational or invent experimental outcomes for new designs.

## Computational reference results

| Quantity | Published reference | Type |
| --- | --- | --- |
| Relative substrate retention | Des27.7 approximately five times Des27 | Computed dynamics outcome |
| Bound-state definition | Ligand to specified active-site centre-of-mass distance ≤4 Å | Analysis setting |
| MD production | Five 1-µs replicas per system | Sampling setting |
| Trajectory analysis interval | 400 ps | Analysis setting |
| EVB sampling | 30 trajectories per system/conformation | Sampling setting |
| Activation energies and catalytic geometries | Extract Supplementary Data 2 and Fig. 3 | Detailed numerical baseline |

These analyses are described in the [primary simulation results and Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC12310539/). Recover the exact active-site residue set and the definition behind the retention ratio before calculating it. A sampling count or occupancy threshold alone is not a reproduced outcome.

## Reproduction and comparison

Follow the [shared procedure](README.md#how-to-execute-a-task).

1. Recover the original numerical table for each system, conformation, and replicate.
2. Reanalyze released trajectories/snapshots where sufficient to test source metric definitions.
3. Repeat MD with the original system representations and methods where supported.
4. Calculate retention, productive-orientation distributions, and uncertainty over replicas.
5. Repeat the EVB calculations and compare profile shape, activation energies, and geometry by conformation.
6. Report per-system errors and uncertainties before combining any estimates.
7. Rerun backbone/sequence design separately if that broader reproduction is selected.

Compare identical methods: the paper's MD and EVB calculations use distinct parameterizations. Preserve their force fields, solvent treatment, restraints, and calibrated reaction model. Do not carry an MD topology into another method without the specified conversion.

Do not read EVB bar heights as exact values when tabulated data are available. Label any unavoidable digitization and its uncertainty. Keep barriers derived from measured rates separate from simulated activation energies.

## Execution requirements

Verify original-method support through the allowed platforms, including PROSS/Rosetta/FuncLib where generation is selected and an actual EVB executor where chemistry is selected. Record unsupported stages before substituting a method.

Apply the [tool policy](../MODELS_AND_TOOLS.md). A different MD engine/force field or a QM/MM calculation replacing EVB is an adapted reproduction, not a numerical replication of the source method. EVB evidence also does not automatically satisfy a full-environment profile that requires coupled QM/MM.

Use a separately identified calculation-only experiment when evaluating published models. The existing controller has no documented arbitrary-stage replay interface. Do not manufacture generation or fold acceptances.

## Expected outputs and acceptance

Return source/model identities, a recovered computational baseline, system/protonation parameters, native trajectories and reaction profiles, per-replica metrics, uncertainty, numerical differences, receipts, and resource use.

A meaningful comparison preserves the original system and metric definitions. Report reduced sampling and unavailable reference rows explicitly. Reproducing the historical design outcome is a different claim from comparing a selected model's simulation results.

## Experimental context

Des27.7 has measured kcat/KM 12,700 M⁻¹s⁻¹ and kcat approximately 2.8 s⁻¹. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12310539/) Keep these as supporting evidence for that construct. The first computational targets are occupancy, geometries, and simulated free energies.
