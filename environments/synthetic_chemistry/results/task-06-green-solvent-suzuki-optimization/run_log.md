# Task 06 — run log

| Order | Stage | Tool / job | Status | Evidence |
|---:|---|---|---|---|
| 1 | Structure validation | local RDKit | completed | 17/17 structures parsed and canonicalized |
| 2 | Retrosynthesis | `retrosynthesis` `6b05593ab5ae2f156e63e787` | completed after invalid-JSON status re-poll | 55 route entries; correct top route |
| 3 | Forward prediction | `forward_reaction` `6b058889c45f4015f0eb48b3` | completed | exact target-string top-1; score ~1.0 |
| 4 | Condition recommendation | `condition_recommendation` `6b0588c27fb17f3eac9cb206` | failed | three HTTP 429 errors + 300 s backup timeout |
| 5 | Condition retry | `condition_recommendation` `6b07cb3fb5e9e7e2abe1fade` | completed | 10 dioxane/water candidates |
| 6 | Impurity prediction | `impurity_prediction` `6b058ae6c45f4015f0eb48e1` | completed | 12 condition-blind candidates |
| 7 | Local design campaign | `reaction-optimize` BayBE v1 | completed | 480 candidates; 12-run diverse batch |
| 8 | Frozen yield estimates | `reaction-optimize --yield-model` | completed | 13 predictions; solvent-blind confirmed |
| 9 | Curated recipe search | `--dataset ord-v2.sqlite` | unsupported | zero matching recipes for exact pair |

No accepted-but-pending job was duplicated. The failed job was retried only as a distinct new submission. No wet-lab experiment, model training or new service job occurred during packaging.
