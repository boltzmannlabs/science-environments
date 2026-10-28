# SRG-02 benchmark data and access boundary

This local cohort separates reference-route recovery from measured condition
selection. It supplies inputs and private evaluation records; it is not a
completed agent comparison or proof of experimental synthesis success.

## Curated allocation

| Track | Smoke | Development | Candidate final | Independent-unit limitation |
|---|---:|---:|---:|---|
| PaRoutes route targets | 10 | 20 | 50 | One target per connected group of known chemical/document links; patent-family audit is supplemental. |
| Route tasks including stock variants | 20 | 40 | 100 | Two inventories of one target are correlated observations. |
| Condition decision tasks | 0 | 15 | 15 | Each source is one publication; the fresh source has one product. |
| Measured condition records | 0 | 3,955 | 5,760 | Rows and substrate variants are not independent publications. |

There are **190 executable task records**. The 80 route targets cover two to
seven reference steps, including 20 with specified stereochemistry and two
convergent routes. The official shared stock contains 13,432 canonical identities.
The restricted variant removes a fixed, hash-selected 10% of stock without using
reference leaves. All arms receive the same inventory for each task. Removing
stock can invalidate the reference without proving no alternative route exists.

Inventory availability here means identity membership. Amounts and prices are
unknown; these tasks do not establish quantitative sufficiency or cost savings.
Pilot budgets are 600 seconds, 80 actions, 12 expansions, 200,000 LLM tokens and
a top-5 shortlist. Final budgets and statistical sample design remain unsealed.

## Sources and overlap

PaRoutes version 2 is pinned to [Zenodo record 7341155](https://zenodo.org/records/7341155)
and upstream commit `bc5e69568092246f7c7bb5405216f8a3a334adbc`. Published checksums
and local SHA-256 hashes were checked. Its dataset license is CC-BY-4.0; the
repository software license is Apache-2.0. See [the route audit](ROUTE_DATA_AUDIT.md).

Both n1 and n5 parse to 10,000 multistep routes, but share 2,128 route fingerprints
and 3,598 documents. This cohort uses **n1 only**. n5 is not an independent
future test simply because its filename differs.

An audit of the available 274,494-reaction LocalRetro corpus found 4,024 n1
records sharing a publication-number key and 1,745 sharing an exact canonical
reaction edge. Their union is 4,491 records. These records and their connected
groups were excluded before allocation. The retained 80 targets have no detected
overlap under those checks. The corpus-to-checkpoint link, other training sources
and LLM pretraining remain unverified; absence of detected overlap does not prove
unseen chemistry. See [the training-overlap receipt](../artifacts/steps/srg-02/localretro_training_overlap.json).

All 10,000 n1 references were also checked with the environment's deterministic
submission rules. Eighteen fail: 17 exceed eight steps, and one lacks an encoded
element source. All are outside the selected cohort. All 80 selected references
pass the hard gates with full stock. Incomplete conditions and stoichiometry
remain unknown. See [the constraint audit](../artifacts/steps/srg-02/reference_constraint_audit.json).

The fresh condition source is the [Perera Suzuki screen](https://doi.org/10.1126/science.aap9112),
using a pinned GAUCHE CSV. All 5,760 measurements belong to one product, scaffold
and publication. The whole publication is reserved; previously inspected Doyle
data are development-only. The Suzuki source lies outside the current Doyle
predictor's domain. No model was trained, no yields were ranked and no final
outcomes were shown to an LLM during curation. See [the condition audit](CONDITION_DATA_AUDIT.md)
for missingness, provenance, line-ending reconciliation and redistribution limits.

## Grouping and privacy

Before sampling, connected components link canonical targets, produced
intermediates, exact reaction records, route duplicates, source documents and
nonchiral Murcko scaffolds. Molecule matching coarsens stereochemistry for
grouping while the original stereochemistry remains in tasks and answers.
Acyclic molecules use their coarse molecular identity rather than a shared empty
scaffold. Repeated inventories inherit their target's partition. Unknown source
identity is grouped conservatively, not replaced with a fabricated unique source.

The curation audit reports zero cross-partition links under these declared keys.
This is not exhaustive analogue detection or a guarantee about undisclosed
patent-family relations. The [supplemental family audit](PATENT_FAMILY_AUDIT.md)
resolved all 80 selected documents to 80 distinct Google Patents displayed
families, with zero observed cross-partition family conflicts. It retains
document-matching evidence and raw HTML hashes. This verifies the named metadata
source's grouping; independent DOCDB/INPADOC validation and exhaustive training-
corpus family mapping were not performed. The earlier curation receipt retains
its pre-audit uncertainty; the acceptance receipt references the supplement.

`artifacts/benchmarks/srg02-v1/` is the **agent-visible local input bundle**.
“Public” in the loader API means agent-visible, not published on the Internet.
It contains shared stock, whitelisted task inputs and source-version metadata.
Closed-information route tasks have empty evidence and no inventory source notes.
Condition candidates expose structures and reported condition roles, never yields
or source-row locators. Missing optional roles remain unspecified.

`artifacts/private/srg02-evaluator-v1/` contains reference routes, measured yields
and curator assignments. Private directories use mode 0700 and files 0600.
The creator refuses overwrite. Public and private manifests have separately
retained hash anchors; rewriting a label and its private manifest fails against
the original private anchor. Changing hidden labels cannot change public bytes
or observations, as tested with deliberately different hidden records.

This is an agent-tool capability boundary, not an operating-system sandbox
against the same Unix user. Only the restricted benchmark runner is suitable:
it exposes no file, shell, web, memory or evaluator tool to the research LLM.
Giving a general-purpose agent unrestricted filesystem tools would invalidate
the closed-information condition.

## Local reproduction and evaluation

From the package root, reproduce into **new** directories:

```sh
.venv/bin/python -m synthesis_route_gym.curation_cli \
  --config artifacts/steps/srg-02/curation_config_v1.json \
  --public-output artifacts/benchmarks/srg02-reproduction \
  --private-output artifacts/private/srg02-evaluator-reproduction \
  --report-output artifacts/steps/srg-02/curation-reproduction
```

The configuration pins input hashes, the allocation seed, source provenance and
the SRG-01 baseline/protocol hashes. Keep raw source files and normalized source
records private. Actual outputs are documented by the
[curation receipt](../artifacts/steps/srg-02/curation-v1/curation.json).
The operator-only `bundle_receipt.json` retains both manifest anchors.

`dataset_bundle.load_public_task()` materializes a task without opening labels.
For route execution, pass only fields declared by `schemas.Task` into
`Task.model_validate`; wrapper fields describe the partition/track and are not
environment actions. `commit_decision()` writes an ordered submission once.
Host-only `score_decision()` verifies that commitment and both retained manifest
anchors before accessing development labels. Pass `expected_manifest_sha256`
and `expected_private_manifest_sha256` from the trusted receipt.

Route scoring considers the first five unique canonical route cores, ignoring
proposal annotations. It reports reference connectivity recovery separately
from inventory/constraint-qualified recovery. Neither is an independent chemical
review. Condition scoring compares only a selected recorded candidate with its
private measured outcome. Invalid/missing submissions remain explicit failures;
the later aggregate runner must apply the protocol's failure denominators.

**Final scoring is deliberately unavailable.** The final configuration, sample
adequacy, review rubric and resource limits must be completed before implementing
the separate final-seal gate. One fresh condition publication is insufficient for
source-level inferential promotion. Independent source review, additional measured
source groups where required, and matched three-arm runs remain later steps.
