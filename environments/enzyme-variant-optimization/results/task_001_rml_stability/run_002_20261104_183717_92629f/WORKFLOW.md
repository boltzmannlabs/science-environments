# RML stability — workflow

![Final workflow tools](figures/sha256-a17e445cdcaed454be25fbdf3d39f37dd8519d553cf4ba7c615ff00e2b18ec70-c36e6a7b_unreported_unreported_92629f_unreported_unreported.jpg)

The diagram shows the final method path, with later benchmark calculations in a separate panel. Relevant screens and assessments were repeated after sequence revisions.

| Stage | Tools | Work performed | Results |
|---|---|---|---|
| Parent checks | Python | Freeze the 269-residue 3TGL parent and protected positions. | [Records](steps/01_parent_preparation/README.md) |
| Generation and revision | SolubleMPNN | Generate variants, then generate revised sequences after reviewing scores. | [Records](sequences/sha256-d803a54148c855912e14524b6682e0d1ddd5b95b92107ef2b8ddc9739ba7c877-22c94851_unreported_unreported_92629f_unreported_unreported.csv) |
| Property screening | Enzymes / TemBERTureTm; NetSolP | Compare temperature and solubility predictions for parent and variants. | [Records](steps/03_property_screening/sha256-99cc3971aba1a65a2a82a273aabe69cdcc804b827c003def05eefe6817502fbb-7c944909_unreported_unreported_92629f_unreported_unreported.csv) |
| Structures and substrate poses | Protein Structure Prediction; Vina | Build protein/complex models, propose poses and score retained substrate states. | [Records](steps/04_structure_and_chemical_assessment/sha256-8aba45a443964fbdf48492b4816ebe8c7fc22194c1e8d5bb38fcbb98870adb84-7c0b819f_unreported_unreported_92629f_unreported_unreported.csv) |
| Quality assessment | MolProbity; local CCTBX/OpenMM preparation | Measure structure quality and inspect prepared chemical states. | [Records](steps/04_structure_and_chemical_assessment/README.md) |

## Benchmark calculations

Later benchmark calculations used Enzymes (TemBERTureTm and raw pHPred), NetSolP and verified existing DDGun_SEQ outputs. RML_R2_02 and RML_R2_01 are the retained comparison sequences.

[Property comparison](reference_comparison/README.md)

[Results and outcome](README.md) · [Sequences](sequences/identities.json) · [Usage and time](README.md#usage-and-time)
