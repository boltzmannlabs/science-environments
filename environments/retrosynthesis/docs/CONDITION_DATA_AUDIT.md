# SRG-02 measured condition source audit

Audit date: 2026-10-27. This is an eligibility and provenance audit, with no training, inference, condition ranking, or experimental outcome inspection. Only outcome missingness and validity as a finite percentage were aggregated. The earlier Dreher–Doyle dataset has already informed development and must not serve as a fresh final test.

## Source and integrity

The new adapter reads the GAUCHE copy of the Suzuki–Miyaura screen associated with Perera et al., *A platform for automated nanomole-scale reaction screening and micromole-scale synthesis in flow*, *Science* (2018), [DOI 10.1126/science.aap9112](https://doi.org/10.1126/science.aap9112). The [original publication abstract](https://pubmed.ncbi.nlm.nih.gov/29371464/) describes 5,760 reaction datapoints generated using the screening platform. The CSV is a processed source copy, not independently remeasured experiments.

Pinned GAUCHE source revision: `2bf761afb3b2cc7ba2bfc55dc98fec76a4d102bb` (source-file commit, 2023-11-08). [Pinned source CSV](https://raw.githubusercontent.com/leojklarner/gauche/2bf761afb3b2cc7ba2bfc55dc98fec76a4d102bb/gauche/datasets/reactions/SuzukiMiyaura.csv).

| Item | SHA-256 |
|---|---|
| Pinned upstream CSV | `0595c7956128cb3b4998c543204a3650c57d0432d6871c3f7195cf532d8b3172` |
| Locally installed CSV | `1908fc8ea3e5d8103c1d4cf40377a7554fe6bb1df568aa7352c2e1d13fd7153a` |
| Pinned repository LICENSE | `6e106283e207174d5b0898732c4c94ec6f49284316b52a3d52038cb9f03c2fe7` |

The local file has 2,246,060 bytes. Its parsed records and ordering match upstream. The byte difference is completely resolved by CRLF/LF normalization. Local path: `/home/boltzmann6/server3_data/boltzmann3/anaconda3/lib/python3.13/site-packages/gauche/datasets/reactions/SuzukiMiyaura.csv`.

The [GAUCHE repository license at the pinned revision](https://raw.githubusercontent.com/leojklarner/gauche/2bf761afb3b2cc7ba2bfc55dc98fec76a4d102bb/LICENSE) is MIT. That establishes the repository's stated license, not an independently verified grant of redistribution rights for all original publication data. Original dataset-specific redistribution terms have not been independently established. This deliverable contains code and aggregate audit facts; it does not redistribute the CSV.

## Structural eligibility and grouping

| Audit quantity | Result |
|---|---:|
| Loaded measured records | 5,760 |
| Distinct canonical products | 1 |
| Distinct product Murcko scaffolds | 1 |
| Publication/source families | 1 |
| Duplicate canonical chemical-input records | 0 |
| Invalid/missing/out-of-range outcomes | 0 |
| Empty ligand source cells | 480 |
| Empty reagent source cells | 720 |
| Source-input/reaction-input inconsistencies | 0 |

No individual outcome, outcome extrema, or best-performing condition was emitted. Raw source-input cardinalities are seven `reactant_1_smiles`, four `reactant_2_smiles`, one catalyst, twelve ligand cells, eight reagent cells, and four solvent cells; these counts include empty optional cells. They do not establish independent target diversity.

The adapter validates the exact eight-column source schema; finite percentage outcomes; nonempty, parseable required molecular structures; one product per reaction; and matching canonical input-fragment multisets between source role fields and reaction SMILES. Source reactant fields contain mixtures, including a reported internal-standard component. Every component is preserved; source role names are explicitly not treated as proof that every molecule contributes atoms to the product. This structural audit does not establish chemical feasibility, scale-up readiness, or a complete experimental protocol.

Empty optional ligand/reagent cells are omitted from `conditions` and retained in `unspecified_condition_roles`. Empty source cells do not distinguish an intentional omission from unreported information. Required catalyst and solvent cells cannot be empty. Salt and solvent mixtures remain role-associated canonical SMILES.

All 5,760 records belong to `doi:10.1126/science.aap9112`; the conservative split unit is the entire publication. Reserve the whole publication for a fresh **condition-final** partition and keep previously inspected Dreher–Doyle records in development. Do not split this publication into nominally independent train/test sources. This dataset supports prospective frozen-protocol comparison of choices within one product screen. It cannot alone establish multi-target, scaffold-generalization, source-level inferential, or multi-step route-search gains. Many condition rows do not create many independent publication groups.

## Applicability and overlap

This is a Suzuki C–C coupling screen. Every adapted record carries `doyle_predictor_applicability=outside_model_domain`; it must not be scored using the existing Doyle C–N condition predictor. No new model was fitted or selected in this task.

Exact canonical product comparison against the frozen `artifacts/model/protocol.json` training membership found:

| Known/unknown overlap assessment | Records |
|---|---:|
| Existing Doyle model training rows checked | 2,374 |
| Suzuki rows sharing a product with those training rows | 0 / 5,760 |
| Suzuki rows sharing a product with any previously seen Doyle row | 0 / 5,760 |
| Suzuki records with unknown main-profile LLM pretraining membership | 5,760 / 5,760 |
| Suzuki records with unknown LocalRetro checkpoint training membership | 5,760 / 5,760 |

Zero product overlap also excludes exact same-target reaction-record overlap with the known Doyle training set. It does not exclude shared reagents, reaction-class information, or other representation overlap. Public availability means a fresh local evaluation dataset is not necessarily unseen by a pretrained model. Without a complete checkpoint training manifest, stronger contamination claims would be unsupported.

## Loader contract and evaluator boundary

`load_condition_records(path, "gauche_suzuki_miyaura")` returns private records with `record_id`, `target`, `reactants`, `conditions`, `outcome_yield_percent`, `source_family`, and `source_locator`, plus domain/missingness metadata. Record identifiers depend on source, row position, and chemical inputs, never outcomes. A caller-supplied source ID selects an adapter; it does not attest file provenance. Compare file hashes against `condition_source_metadata()` before accepting a source as the pinned benchmark.

`public_condition_records(records)` returns deep-copied, allowlisted inputs and omits both outcomes and exact label-bearing source-row locators. `summarize_condition_records(records)` returns grouping/missingness/validity counts without outcome values or condition rankings. Neither function implements access control. The evaluation harness must keep private records and raw CSV outside agent-visible files, deny source retrieval during final decisions, and retain private record-ID-to-outcome joins in the evaluator. A public dataset still has unknown pretraining exposure.

Synthetic tests cover hidden-label independence, stable identifiers, canonical role handling, explicit optional missingness, malformed schemas/reactions, input discrepancies, finite percentage validation, and aggregation. The real CSV was loaded once and all 5,760 records passed. Test command:

```bash
COVERAGE_FILE=/tmp/srg_condition_data_coverage .venv/bin/python -m pytest tests/test_condition_data.py -q --cov=synthesis_route_gym.condition_data --cov-report=term-missing --cov-fail-under=80
```

Result: 21 tests passed; 100% statement/branch coverage for `condition_data.py`. No hidden yield values were printed and no model or LLM calls were made.
