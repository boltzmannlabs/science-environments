# LEH stability — workflow

![Final workflow tools](figures/sha256-fad13faa3267db19d2f2ce8b10f6a66006adcb3837c9d05291d3056982898f0a-c36e6a7b_unreported_unreported_0fd35d_unreported_unreported.jpg)

The diagram shows the final method path, with later benchmark calculations in a separate panel. Relevant screens and assessments were repeated after sequence revisions.

| Stage | Tools | Work performed | Results |
|---|---|---|---|
| Parent checks | Python | Fix the 149-residue 1NWW/Q9ZAG3 sequence and biological dimer. | [Records](steps/01_parent_preparation/README.md) |
| Generation and revision | SolubleMPNN; ThermalMPNN | Generate variants and use mutation landscapes for subsequent revisions. | [Records](sequences/sha256-3f5ff3a2035d8517e6dfe782d6b8420db3ee101a3e729e0ac1f9e10765f9b864-22c94851_unreported_unreported_0fd35d_unreported_unreported.csv) |
| Property screening | Enzymes / TemBERTureTm; NetSolP | Screen parent and revised variants for predicted temperature and solubility. | [Records](steps/03_property_screening/sha256-c82813dbe63c2010646d2d1d49bf8fbf16195482b03eadb60e236dd16a75d62c-7c944909_unreported_unreported_0fd35d_unreported_unreported.csv) |
| Structures and substrate poses | Boltz2; Vina | Investigate dimer/joint-complex states and substrate poses. | [Records](steps/04_structure_and_chemical_assessment/sha256-4e9d49045293ab1e41fdfb0cf53ae09526ab80b458d7cdddbecb2c148431aa2f-7c0b819f_unreported_unreported_0fd35d_unreported_unreported.csv) |
| Quality assessment | MolProbity; PDBFixer/OpenMM and ACPYPE preparation | Prepare chemical states and inspect geometry, hydrogen and polar-contact evidence. | [Records](steps/04_structure_and_chemical_assessment/README.md) |

## Benchmark calculations

Later benchmark calculations used Enzymes (TemBERTureTm and raw pHPred), NetSolP and verified existing DDGun_SEQ outputs. LEH_R004 and LEH_R003 are the retained raw comparison sequences.

[Property comparison](reference_comparison/README.md)

[Results and outcome](README.md) · [Sequences](sequences/identities.json) · [Usage and time](README.md#usage-and-time)
