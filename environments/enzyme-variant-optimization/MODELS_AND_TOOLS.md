# Models and Tools

Agent-Scientist selects an executable method for each required capability using the current Boltzmann catalogue, ToolUniverse or both. This file explains roles, not API payloads or deployment status.

| Capability | Suitable method families | Selection question |
| --- | --- | --- |
| Sequence generation | Constrained sequence design, inverse folding, mutation search, saturation-library generation. | Can the method generate new complete variants while preserving the declared functional features and mutation budget? |
| Property screening | Mutation-effect, stability, solubility and enzyme/substrate models. | Does the model support this enzyme, reaction and requested endpoint? Are units and uncertainty interpretable? |
| Candidate structures | Structure prediction, local remodeling and protein–ligand complex modeling. | Can candidate sequence identity, construct, components and local uncertainty be checked? |
| Structural quality | Clash, backbone, side-chain and ligand-restraint assessment. | Is the required complete complex evaluated, not just the protein? |
| Catalytic and interaction assessment | Reaction-specific geometry, docking, interaction analysis and supported energetic methods. | Is the chemical state correct and is the measurement relevant to the objective? |
| Focused refinement | Local redesign, repacking, relaxation or a revised sequence search. | Does it address a failure actually observed in this run? |
| Advanced evaluation | Replicated dynamics, binding-energy or reaction-energy analysis where justified. | Are the method, parameters, licenses and compute available for a scientifically comparable calculation? |

ProteinMPNN/LigandMPNN-type methods, mutation-search tools, structure predictors, MolProbity and catalytic-geometry tools are examples of these capabilities, not hard-coded requirements or claims of current availability. Generic sequence plausibility or fold confidence is not a reaction-activity score.

Use SCI's existing tool discovery, contract validation, upload/submit/status/download paths, environment setup and saved-specialist delegation. Do not create another catalogue, client, approval layer, job store or molecular-input parser here. The offline comparison helper uses Python's standard library and never calls scientific tools.

Before freezing each run, record the selected provider, tool/model version, access and license requirements, actual parameters and seed support. ToolUniverse provides access/discovery interfaces; some underlying methods still require additional executables, accounts, models or licensed software. Do not install or enable them without the normal SCI setup and permissions.

The SubTuner study uses advanced electronic-structure and force-field calculations. A docking score is not an interchangeable substitute. An unavailable advanced evaluator leaves that historical comparison unresolved rather than blocking unrelated supported observations.


## Observed reproduction capabilities

Tasks005/006 retain Pythia C/P source-pinned inference and ESM-2 score conventions, with AlphaFold2 structures for Zhang where executed. Actual source/checkpoint/input hashes remain in the exported tables/config receipts and retained run archives. The exact paper ESM checkpoint and historical structural settings remain unresolved. Supplemental Tm is TemBERTureTm.mean3.3c17a7a2.encoder6c5c8a55.v1; NetSolP is a mean score, not measured solubility. CatPred absolute units/checkpoint were not returned. These observations are separate from current SCI tool contracts and do not freeze deployment availability.
