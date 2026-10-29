# References and software sources

These sources describe external software or experimental resources; citing them does not establish a reproduced result in this environment.

1. [Agent-Scientist](https://github.com/boltzmannlabs/Agent-Scientist) — coordinator/runtime and Boltzmann connector. Record the actual clean checkout revision for native execution.
2. [DiscoveryRSI, pinned source](https://github.com/Gen-Verse/DiscoveryRSI/tree/7389e0b58ae50486ab35aa3dcbfa2fa15fea1a91) — the environment executes its Candidate, DiscoveryLoop, and ReplayBuffer components. The source-only integration does not require a DiscoveryRSI model checkpoint.
3. [CatPred](https://github.com/maranasgroup/CatPred) — sequence/substrate kinetic prediction. Record the deployed model and wrapper contract; predictions are not experimental labels.
4. [ThermoMPNN](https://github.com/Kuhlman-Lab/ThermoMPNN) — structure-based single-substitution stability estimates. This environment preserves the source model scale and does not aggregate individual predictions into multi-mutant scores.
5. [Boltz](https://github.com/jwohlwend/boltz) — external structure/complex prediction. Record the deployed model generation and settings; model confidence does not establish activity.
6. [MolProbity](https://github.com/rlabduke/MolProbity) and [CCTBX](https://github.com/cctbx/cctbx_project) — structural quality methods. Protein and ligand support depend on the actual deployed worker and available chemistry.
7. [RDKit](https://www.rdkit.org/docs/) — molecular graph, stereochemistry, SDF, and coordinate identity checks in the optional chemistry path.
8. [ProteinMPNN](https://github.com/dauparas/ProteinMPNN) and [LigandMPNN](https://github.com/dauparas/LigandMPNN) — external sequence-design methods when permitted by a computational task.
9. [Fordyce Lab data portal, source snapshot](https://github.com/FordyceLab/data-portal/tree/47d9dd2aca002773022a385fc7691addf4c84600) — candidate resource for the separate PafA measured-activity benchmark. Dataset qualification, permitted reuse, assay conditions, splits, and protected measurements require the independent benchmark protocol; none are bundled as test answers here.

Internal source provenance for the included executor and environment modules is recorded in the environment's `SOURCE_PROVENANCE.json`. The newly deployed platform tools' catalogue remains the authority for their API input/output contracts.
