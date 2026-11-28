# Task 04 — run log (provenance)

This log is derived from the frozen tool trace. It records tool calls, not laboratory experiments. Raw service outputs, signed URLs and account-scoped exports are not included.

| Order | Call ID | Tool / origin | Input summary | Output / validation | Status / fallback |
|---:|---|---|---|---|---|
| 1 | local RDKit 2025.09.6 | local chemistry toolkit | three supplied SMILES | all valid; canonical identity retained | completed |
| 2 | `6b053cb3a74792a53542b531` | `retrosynthesis`, internal | target SMILES | 5 routes parsed from scoring JSON | completed |
| 3 | `6b053cb88e07760a3d1b14c9` | `forward_reaction`, internal | dot-separated reactants, empty intermediates | 30 products; top-1 canonical match to target | completed |
| 4 | `6b0540db274b4c9537b25a85` | `impurity_prediction`, internal | reactants + validated product | 15 impurity candidates; 9 retained | completed |
| 5 | `6b0540e08e07760a3d1b1570` | `condition_recommendation`, internal | reactants + product | none | failed: GLM HTTP 429 |
| 6 | `6b0543a9d2a6d14831427337` | `condition_recommendation`, internal | same | none | failed after bounded retry: HTTP 429 |
| 7 | `6b058bc6c45f4015f0eb48f7` | `condition_recommendation`, internal | same | none | failed: all GLM tokens 429; Discovery RSI timeout |
| 8 | `6b07c97cc45f4015f0eb7561` | `condition_recommendation`, internal | same | 10 conditions; yields 31.285–47.447% | completed |
| 9 | `6b07dac07fb17f3eac9ce04b` | `condition_recommendation`, internal | reversed reactant order | yields 22.066–77.420%; no catalyst/base | completed but chemically invalid; rejected |
| 10 | `parrot-uspto-sc01` | Parrot inference, external open source | reaction SMILES `reactants>>product` | 15 conditions; top-1 toluene, log score −1.3208 | completed; not adopted |
| 11 | `parrot-reaxys-attempt` | Parrot Reaxys config, external | same reaction | none | unavailable: license-gated weights |
| 12 | `local-ro-nhc-plan` | local `reaction-optimize`, BayBE v1 | explicit Pd-NHC `condition_space` | 1,944 candidates; 8 Pd-NHC recommendations | completed |
| 13 | `local-ro-nhc-yield-attempt` | local `reaction-optimize --yield-model` | 8 Pd-NHC candidates | 9 yields unavailable | completed; no resolved catalyst SMILES |
| 14 | `local-ro-loading-v4` | local `reaction-optimize --yield-model` | loading in equivalents + resolved component SMILES | 144 candidates; 9/9 yields available | completed; yield model ignores loading |
| 15 | campaign create / next | `campaign_cli`, local | loading-aware campaign | campaign `a19bfc948594490f9e8f992db4f77af7`; 6 reserved experiments | completed; zero measurements |

Post-hoc documentary review of public Pd-NHC Suzuki references and local tool documentation followed the frozen prediction stage and is recorded in the benchmark folder. No model job or wet-lab experiment was executed while packaging this task.
