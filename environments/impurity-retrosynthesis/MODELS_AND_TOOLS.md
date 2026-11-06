# Models and tools

| Component | Executed role and provenance | Limits |
|---|---|---|
| Agent-Sci (active profile in historical run) | Scoped task, Boltzmann tool-contract use, job tracking/recovery, documentary review | Not bundled; profile credentials and original service exports remain private. |
| Boltzmann `retrosynthesis` | Original user-authorized target-molecule SMILES submissions; exported nested route graphs | Architecture, training corpus, score calibration, model version, `path_cost` units unknown; no retraining or direct connector in this package. |
| RDKit 2026.9.1 | Historical SMILES parse, formula, root canonical comparison and heavy-element presence; package CLI repeats structural checks on authorized exports | No atom mapping, stereo-spec verification, reaction prediction, toxicity or process feasibility certification. |
| Python >=3.10 standard library | JSON parsing, pure input checks, CLI, tests | This package requires RDKit at runtime to avoid false structural assurance. Historical runtime used Python 3.14. |
| PubChem PUG REST | CAS/name/synonym structural context | Database not a pharmacopeial impurity standard. |
| Google Patents; Crossref | Literature-source checking (three task-specific subagent lookups and manual retrieval) | Source text/OCR/translation errors; bibliographic titles alone do not prove a transformation. |
| Local `unittest` | Synthetic input contracts and failure gates | Passing tests is not experimental chemistry validation. |

Not executed or implemented: wet-lab experiments, forward-reaction confirmation, structure generator training, formulation optimization, atom-mapping engine, cost estimator with current INR quotes, Bayesian optimization and supplier APIs. `reaction_yield` is a platform field, never measured in this package. See [reference status](../../research/impurity-retrosynthesis/references.md).
