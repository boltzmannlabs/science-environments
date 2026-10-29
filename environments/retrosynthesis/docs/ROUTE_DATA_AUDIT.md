# SRG-02: PaRoutes reference-data audit

The local parser supports the actual PaRoutes 2.0 alternating molecule/reaction
JSON trees. Reference answers and normalized records are retained only under
`artifacts/private/srg02_sources/`; that directory is Git-ignored and has owner-only
directory permissions. Test fixtures contain small synthetic trees, not benchmark
answers. No final-cohort structures, routes, or measured outcomes are printed by
this audit.

## Pinned sources and rights

| Source | Pin / provenance | Verified scope |
|---|---|---|
| [Official PaRoutes repository](https://github.com/MolecularAI/PaRoutes/tree/bc5e69568092246f7c7bb5405216f8a3a334adbc) | Commit `bc5e69568092246f7c7bb5405216f8a3a334adbc` | Download specification, data documentation, extraction scripts, Apache-2.0 software license |
| [PaRoutes 2.0 dataset](https://zenodo.org/records/7341155) | DOI `10.5281/zenodo.7341155`, published 2022-11-22 | Zenodo metadata declares **CC-BY-4.0** for the dataset; this is distinct from the software license |
| [Genheden and Bjerrum, Digital Discovery (2022)](https://doi.org/10.1039/D2DD00015F) | DOI `10.1039/D2DD00015F` | Original framework and benchmarking interpretation; V2 downloaded counts are measured locally rather than copied from the original publication |

The paper describes patent-extracted reference routes, common stocks, reference
retrieval metrics, and excluding reference reactions from one-step model training.
Reference-route recovery evaluates a particular documented route; alternatives
need not be chemically wrong simply because they differ. Stock closure does not
establish practical feasibility or experimental reproduction.

The private `source_manifest.json` records acquisition URLs, sizes, verified
published MD5 checksums, local SHA-256 hashes, licenses, upstream commit, and hashes
of the saved source documents. The Zenodo metadata and upstream source snapshots
are retained alongside it. Dataset attribution must be preserved in any permitted
redistribution; this task does not copy raw references into public artifacts.

| Downloaded file | Bytes | SHA-256 |
|---|---:|---|
| `ref_routes_n1.json` | 64,187,987 | `b818f2115ce10da51f84bf13f19dc2206863b1b074ef348017de258e9e1bff02` |
| `ref_routes_n5.json` | 82,120,928 | `d878bec737d34a861b859912ac783f065c380f704f6d0087af4ea8ef667fa2bf` |
| `stock_n1.txt` | 368,802 | `b8641e2028846d995953b30f7acd36e7521d0301159518d172497340a0bfb115` |
| `stock_n5.txt` | 360,970 | `199ec2d9fad0638c3ae53f2ea091dcd6bf9207a938b12ae1aa9429c37dd097af` |

## Parser and provenance contract

[route_data.py](../src/synthesis_route_gym/route_data.py) provides:

```python
load_paroutes(path, source_id) -> list[dict]
parse_paroutes_record(tree, source_id, index) -> dict
load_stock(path) -> list[str]
```

`load_paroutes` is strict: malformed records abort loading with their array index,
without echoing molecular structures. Curation can call `parse_paroutes_record`
per row and keep rejection indices/reasons privately. The audit does this instead
of silently dropping data. Source file checksums belong in the manifest;
`source_id` identifies the frozen dataset version, not a synthetic patent family.

| Field | Meaning |
|---|---|
| `record_id` | Deterministic digest of dataset identifier, array position, and route fingerprint |
| `target` | Canonical isomeric target SMILES with atom maps removed |
| `source_id`, `source_locator` | Frozen dataset identifier and zero-based JSON array locator |
| `source_family` | Compatibility grouping field: document key when exactly one known document covers every step; otherwise the common unresolved key. **Not a verified patent family.** |
| `source_keys`, `source_documents` | All step-document identifiers, with `unresolved:paroutes` added when any source is missing; use all keys when grouping |
| `source_identity_status` | `resolved_document`, `multiple_documents`, `partial_documents`, or `unresolved` |
| `patent_family_status` | Always `unknown` until an independent family mapping is supplied |
| `reaction_source_locators` | Preserved metadata `ID` values; document/paragraph/reaction locators |
| `route_fingerprint` | SHA-256 of canonical target plus sorted canonical reaction identities; independent of sibling ordering and record position |
| `reaction_keys` | Every step's sorted canonical reactants joined to canonical product; stereochemistry and reactant multiplicity retained |
| `molecule_keys` | Root and all internal produced molecules; excludes common-stock leaves |
| `intermediate_keys` | Internal produced molecules excluding the root |
| `scaffold` | Non-stereochemical Bemis–Murcko target scaffold; empty for acyclic targets |
| `reference_route` | Validated `RouteCandidate.model_dump(mode="json")`; unknown amounts, yields, conditions, and evidence verification remain unknown |
| `stock` | Canonical **reference leaves**, private evaluator data, never the agent's task inventory |
| `step_count`, `has_stereo`, `convergent` | Step count, any explicitly assigned stereochemistry, and any reaction combining two independently synthesized branches |

The official [extraction code](https://github.com/MolecularAI/PaRoutes/blob/bc5e69568092246f7c7bb5405216f8a3a334adbc/setup/extract_uspto_data.py)
uses the first semicolon-separated component of reaction `ID` as its patent
identifier. The parser follows that source-defined convention, including US
reissue and statutory-invention-registration identifiers. It does not infer a document from arbitrary reaction IDs or
invent unique source groups when metadata is absent. Known documents are weaker
than verified patent-family identities: related applications and grants can still
cross a document-only split. Family coverage remains unknown for every record.

Cycles, malformed alternating nodes, multiple producing reactions, zero-step
references, excessive depth/steps, repeated produced molecules, and a molecule
used both as a leaf and a produced intermediate are rejected. The latter two
are rejected even if a repeated subroute looks identical: the current route
schema cannot distinguish those occurrence-level meanings. Repeated stock leaves
are allowed. Inputs are not mutated. Stereo is retained in identities and the
route fingerprint; separate coarse identities may be used by the partitioner.

## Local curation results

The saved private `audit_n1.json` and `audit_n5.json` contain aggregate counts;
`normalized_n1.json` and `normalized_n5.json` contain evaluator-only normalized
records. No models were trained or run and no chemical reviews were requested.

| Audit quantity | n1 | n5 |
|---|---:|---:|
| Raw reference routes | 10,000 | 10,000 |
| Parser-eligible routes | 10,000 | 10,000 |
| Rejected records | 0 | 0 |
| Unique document IDs | 10,000 | 7,946 |
| Routes with explicit stereochemistry | 1,690 | 1,883 |
| Convergent routes | 564 | 1,091 |
| Multi-step routes | 10,000 | 10,000 |
| Unique canonical common-stock molecules | 13,432 | 13,326 |
| Routes with a reference leaf outside common stock | 0 | 0 |
| Targets already present in common stock | 0 | 0 |
| Complete step-document coverage | 100% | 100% |
| Verified patent-family coverage | Unknown | Unknown |

Across n1/n5, 2,128 route fingerprints and 3,598 document IDs overlap; the combined sets contain 17,872 unique route fingerprints. Each set has 10,000 unique route fingerprints internally. Step counts range from 2 to 10 in both sets.

These are parser-eligible records, not a safety-approved or independently
chemically reviewed target cohort. Cohort selection must apply the separately
specified target/domain screening, budget, leakage components, and held-out
partition rules before any route-search experiment.

## Stock and leakage boundaries

Use the full official `stock_n1.txt` or `stock_n5.txt` as a common inventory for
all tasks drawn from the respective set. All arms must receive that identical
inventory. Do not build target-specific inventories from a record's `stock`
leaves, which reveal part of the reference answer. The stock files themselves are
benchmark-defined stop criteria; membership is not a current vendor quote or an
assurance of quantity, purity, catalyst availability, or equipment compatibility.

The partitioner should connect records sharing a source key, coarse target,
scaffold, reference reaction, route fingerprint, or root/internal molecule.
Common stock leaves must not connect unrelated tasks. Multiple document keys
must all participate. Missing sources share one unresolved component across
files; a per-row fallback would falsely claim independence. Patent-family
independence cannot be claimed from the available document metadata alone.
Overlapping n1/n5 reference records and documents must not be counted as
independent evaluation evidence.

Private files are withheld by workflow and directory permissions. Processes
running as the same OS user can still read them; filesystem naming and a Python
API are not an adversarial isolation boundary. Agents must receive only the
public task projection and permitted tools, with the reference evaluator kept
outside their accessible execution context for a stronger held-out guarantee.

## Upstream training contamination

The official [data documentation](https://github.com/MolecularAI/PaRoutes/blob/bc5e69568092246f7c7bb5405216f8a3a334adbc/data/README.md)
states that the bundled one-step model excludes reactions in the n1/n5 reference
routes. The [training extraction script](https://github.com/MolecularAI/PaRoutes/blob/bc5e69568092246f7c7bb5405216f8a3a334adbc/setup/extract_training_data.py)
explicitly removes matching reaction hashes. This is an upstream claim and
source-code check for those designated artifacts; the downloaded reference trees
alone do not prove arbitrary checkpoints satisfy that exclusion.

The pod's LocalRetro checkpoint was trained on USPTO-derived data, and the
separately downloaded AiZynthFinder ONNX artifact has its own provenance.
Reference-reaction exclusion for **these actual local checkpoints is unverified**.
Their route results cannot be labeled training-disjoint simply because PaRoutes
supplies an excluded model elsewhere. Document/scaffold-disjoint evaluation
within a newly curated cohort also does not remove pretrained-model leakage.
No training dataset was downloaded, no model was replaced, and no claim of
zero contamination is made. An explicit checkpoint/training-data reconciliation
or retraining on a verified exclusion set is a separate acceptance gate.

## Tests and ownership

[Fixture tests](../tests/test_route_data.py) were written first and initially
failed because the module did not exist. They cover full file-to-RouteCandidate
loading, deterministic identities, source metadata and missing-source grouping,
stereo, convergence, malformed/cyclic/ambiguous trees, and separate global-stock
loading. Latest run: **32 passed, 97.73% branch-inclusive module coverage**.

```bash
.venv/bin/python -m pytest tests/test_route_data.py -q \
  --cov=synthesis_route_gym.route_data --cov-report=term-missing
```

SRG-02 owns this parser, its fixture tests, the private acquisition/curation
receipts, and this audit. Partition selection, public task projection, safety
screening, model training, and search comparisons are separate responsibilities.
