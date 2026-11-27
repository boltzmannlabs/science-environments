# Sun LEH / Pythia study — workflow

![Final workflow tools](figures/sha256-abf6b6a6b12aa496a8edb13847c59b5c4b1bd7297fe04d889cc7d30338cd4ed9-c36e6a7b_unreported_unreported_f4aa65_unreported_unreported.jpg)

The diagram shows the final method path, with later benchmark calculations in a separate panel. Relevant screens and assessments were repeated after sequence revisions.

| Stage | Tools | Work performed | Results |
|---|---|---|---|
| Prepare inputs | Python freeze_inputs.py | Map the native LEH sequence to 1NWW and freeze inputs. | [Records](steps/01_parent_preparation/README.md) |
| Score mutations | Pythia / run_full_scan.py | Score all 2,755 mapped nonidentity substitutions. | [Records](steps/02_pythia_scoring/sha256-2f54de045ec36a7b7d21d2dedd019e0f4d754638b26ed5c07a2ac71db1bdb8bd-ca2d1aec_unreported_unreported_f4aa65_unreported_unreported.csv) |
| Verify and rank | Python verify_results.py; selection.py | Check coverage and rank by the declared summed-score convention. | [Records](steps/02_pythia_scoring/sha256-7fc771d2134795dcd8c3622b5ac6b603bbe66ef5d0cd059bb8dc259f94939248-af64a189_unreported_unreported_f4aa65_unreported_unreported.csv) |
| Select and seal | Python selection.py; final_audit.py | Apply score < −2, retaining 33 mutations and the scoring evidence. | [Records](steps/03_ranking/sha256-958bc7afff76943f46e55eb67f5482795b9dfb95f73fad3c003f6fd8435450e7-7f997322_unreported_unreported_f4aa65_unreported_unreported.csv) |

## Benchmark calculations

Later comparisons reused the Pythia scan and used Enzymes, NetSolP and DDGun_SEQ for common properties. D101V and T85V are score leaders; P57A is a reference comparison. These are prediction rankings.

[Property comparison](reference_comparison/README.md)

[Results and outcome](README.md) · [Sequences](sequences/identities.json) · [Usage and time](README.md#usage-and-time)
