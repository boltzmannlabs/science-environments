# Models and tools

| Component | Actual role | Provenance / limit |
|---|---|---|
| Boltzmann platform `retrosynthesis` | Generated 16 pathway candidates, reaction classes and model yield/ranking fields | Original private account export intentionally omitted; exact model/version, weights, seed and training corpus unknown. Some nodes report forward source `ReactionT5`; no inference version supplied. |
| `forward_reaction` | Ranked candidate products for each of top0's three depicted steps | Scores are model rankings, not probability, conversion or yield. Only top0 has this check. |
| `atom_mapping` | Returned mapped reactant/product connectivity and confidence for top0 steps | Mapping confidence is not experimental feasibility. |
| `impurity_prediction` | Generated candidate side products on top0 steps | Not measured concentrations; candidate atoms may lack an input source. |
| `condition_recommendation` | Generated candidate reagents, solvents and temperatures for top0 | Some suggestions fail basic mechanistic review. Predicted yields are unmeasured; no optimized conditions established. |
| RDKit | SMILES structural comparison and local figure rendering | Reproducible report-builder dependency, optional for JSON-only tests; verify current installed version locally. |
| python-docx | Public report composition | Optional report-builder dependency; not required for the JSON tests. |
| Python standard library | Sanitization, step-tree traversal, checks | `scripts/derive_routes.py` and `tests/test_results.py` do not require external packages. |

The live platform output was processed for this case; these repository scripts never call an external chemistry service. The target and numeric values are **case-specific** and must not be generalized as a validated yield predictor.
