# Models, tools and execution boundaries

This is a dependency inventory for a **specification**, not an installation report.
Task execution must resolve actual versions, hashes, credentials and capabilities.

| Component | Role | Qualification needed |
| --- | --- | --- |
| Agent Scientist | Main reasoning, tool access, workflow choices and artifact collection | Available authorized profile and permitted scientific tools |
| Existing Boltzmann connector | Native upload/submission/status/download operations | Live access, accepted input/output contract and job/result identity |
| Allowed molecular generators/optimizers | Candidate proposals, screening and adaptive search | Actual methods/weights, libraries, supported parameters and observable costs; no one method mandated |
| Smina 2020.12.10 | Common final de novo docking assessment | Executable/build hash, fixed target preparation, box, seed and search settings |
| RDKit | Molecular identity, QED, calculated LogP and similarity | Pinned release and matching fingerprints/canonicalization |
| SA and NP descriptor implementations | Synthetic-accessibility and natural-product-likeness diagnostics | Code and model-data identities, native scales and failure handling |
| Supplied DRD2 predictor | Mandatory optimization activity assessment | Actual artifact/hash, dependencies, features and positive-class mapping; loading not yet qualified |
| Supported ADMET models | Optional optimization reward guidance or a separately defined constrained variant | Authorized model identities, version/scale, target ranges and missing-data behavior |
| Separately controlled evaluator | Final assessment after output freeze | Frozen metric implementation, verified inputs/output hashes and access boundary |

Smina's seed does not control ligand embedding randomness. Freeze preparation,
conformer enumeration, attempts, seeds, caching and repeat aggregation separately.
A different docking engine or similarly named hosted property is not numerically
interchangeable with a specified scorer.

Hosted tool exports can filter duplicates/invalids or round predictions. Recompute
mandatory optimization metrics from molecular identities at full precision.
Record unobservable internal work; do not infer raw attempts from returned rows.

DRD2/QED availability is not established by a generic global-property selection
interface. A custom-model ID does not prove compatibility with the supplied local
predictor. No checkpoint, restricted dataset, credentials or account configuration
is included here.
