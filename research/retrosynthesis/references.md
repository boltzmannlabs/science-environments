# Retrosynthesis — references

This is the central source index for the environment. Links identify upstream methods; they do not attest that a particular model, dataset or source reaction was used in every run. Pin actual revisions, checkpoint/data hashes, access terms and task splits in each execution record. Third-party notices are preserved in the environment.

| Source | Role and limitations |
| --- | --- |
| [AiZynthFinder, Molecular AI](https://github.com/MolecularAI/aizynthfinder) | Baseline retrosynthesis framework and optional proposal adapter. The historical snapshot records a local 4.4.1 setup; assets are not bundled. |
| [PaRoutes, Molecular AI](https://github.com/MolecularAI/PaRoutes) | Public route/stock benchmark source. Historical notes report PaRoutes 2.0; dataset revision, licensing and split identity must be verified for a new benchmark. Stock closure is not experimental feasibility. |
| [LocalRetro](https://github.com/kaist-amsg/LocalRetro) | Local-template reaction proposals through the separately configured REBOLT runtime. Actual checkpoint digest belongs to the run receipt. |
| [Syntheseus, Microsoft](https://github.com/microsoft/syntheseus) | Native route-search dependency pinned to 0.8.0. SynthChem-style controllers are adapted local code; see the implementation guide and required MIT notices. |
| [RDKit](https://www.rdkit.org/) | Molecular parsing, identity and structural checks; these checks do not prove reaction outcome or laboratory safety. |
| [ReactionT5v2 official implementation](https://github.com/sagawatatsuya/ReactionT5v2), [paper](https://doi.org/10.1186/s13321-025-01075-4), [yield checkpoint](https://huggingface.co/sagawa/ReactionT5v2-yield) | Optional pretrained recipe-level yield tool. Requires separately supplied assets/configuration; not a validated route-success model or proof of best-in-class performance. |
| [ASKCOS](https://askcos.mit.edu/) | Starting reference for synthesis-planning capabilities; inclusion here does not claim a tested adapter or executed ASKCOS benchmark. |

Application-specific source identifiers supplied in task records are interpreted with their declared evidence scope. Frozen measured data, source snapshots and held-out answers are excluded from this code release when access or redistribution is unresolved. The exact sources for a claimed chemical reaction must be checked individually.
