# AtHOL1 substrate expansion — workflow

![Final workflow tools](figures/workflow.jpg)

The diagram shows the final method path, with later benchmark calculations in a separate panel. Relevant screens and assessments were repeated after sequence revisions.

| Stage | Tools | Work performed | Results |
|---|---|---|---|
| Parent and reaction | Python | Freeze the full 235-residue 3LCC construct with SAH and ethyl iodide. | [Records](steps/01_parent_preparation/README.md) |
| Generation and revision | SolubleMPNN; ThermalMPNN | Generate variants and use mutation landscapes for later revisions. | [Records](sequences/candidate_history.csv) |
| Property screening | CatPred; Enzymes | Compare sequence/reaction predictions and general property screens. | [Records](steps/03_property_screening/outputs.csv) |
| Structure and ligand modeling | Protein Structure Prediction; Boltz2; Placer | Investigate protein structures, complex models and ligand states. | [Records](steps/04_structure_and_chemical_assessment/outputs.csv) |
| Quality assessment | MolProbity | Inspect the structure and chemical-state evidence for retained models. | [Records](steps/04_structure_and_chemical_assessment/README.md) |

## Benchmark calculations

Later benchmark calculations used Enzymes, NetSolP and EvoEF1. A separate matched assessment used OpenMM (30 ns per sequence), protein-field analysis and PySCF/GPU4PySCF for C–I localized-orbital calculations on the parent, V140T and ATH_R2_09.

[Property comparison](reference_comparison/README.md) · [Reaction-site assessment](steps/10_reaction_electrostatics/README.md)

[Results and outcome](README.md) · [Sequences](sequences/identities.json) · [Usage and time](README.md#usage-and-time)
