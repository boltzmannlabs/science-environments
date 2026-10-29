# Selected-cohort patent-family metadata audit

This audit checks explicit family identifiers on the focal documents' Google
Patents pages. It does not read patent chemistry into an LLM, evaluate reaction
outcomes, or alter the frozen task bundle. Document-to-family mappings, raw HTML,
and source receipts remain private. The public artifact contains aggregate
coverage, file hashes, request counts, and partition-conflict counts only.

## Scope and sources

The input is the tightened cohort in
`artifacts/private/srg02-evaluator-v1/assignments.json`, joined by `record_id` to
`artifacts/private/srg02_sources/normalized_n1.json`. Only assignments whose
`task_id` begins with `route-` are selected. Duplicate inventory variants collapse
to their underlying reference record; all of a record's source documents are
included. This gives **80 route records and 80 source documents**, with no missing
document identifiers. Condition tasks are excluded from this metadata audit.

The acquisition source is the first-party [Google Patents](https://patents.google.com/)
page for each document. Exact per-document HTTPS URLs, retrieval timestamps,
status codes, and raw HTML SHA-256 hashes are in the private receipts. Google also
publishes a [`family_id` field in its patent data schema](https://github.com/google/patents-public-data/blob/master/tables/dataset_Google%20Patents%20Public%20Datasets.md),
but this audit reads the displayed page metadata directly; it does not query
BigQuery or assert equivalence to another provider's family taxonomy.

The identifier namespace is **`google_patents_family:<displayed ID>`**.
“Verified” in the artifact means the requested document identity and the explicit
family field match the retrieved primary page. It does **not** mean independent
DOCDB/INPADOC validation or complete detection of every related application.

## Extraction rules

[The executable audit](../scripts/audit_patent_families.py) requires both:

1. Matching focal publication identity from `citation_patent_publication_number`,
   `citation_patent_number`, or the primary `dd[itemprop=publicationNumber]` field.
   Conflicting identities are rejected. Legacy leading-zero document numbers are
   normalized; a supplied kind code must match an explicitly available kind code.
2. Exactly one distinct numeric `ID=...` header inside the focal
   `section[itemprop=family]`. Citation-family sections and arbitrary numbers or
   family references elsewhere on the page are ignored. Multiple conflicting
   family identifiers produce an unknown result.

Unknown, blocked, malformed, mismatched, ambiguous, and timed-out responses remain
unknown. No family is inferred from patent-number similarity, source-document
uniqueness, reaction chemistry, or a cached LLM answer. The metadata parser never
extracts descriptions, claims, examples, chemical structures, or measured outcomes.

Each fetch makes one HTTPS request without following redirects. The script limits
concurrency to four workers, socket/request timeout to 15 seconds, and response
size to 8 MiB. A persistent request ledger reserves requests before dispatch and
caps the acquisition at 100 total requests, including the two prototypes.
Interrupted reserved attempts still consume budget. There are no automatic
retries. One transient network failure received a single bounded manual retry;
the original failure receipt and the extra request reservation were preserved. Hash-checked cached responses can be re-parsed without network requests.

## Observed result

| Quantity | Result |
|---|---:|
| Selected route records / source documents | 80 / 80 |
| Explicit family metadata verified against focal document | 80 / 80 (100%) |
| Unique displayed Google Patents family IDs | 80 |
| Unknown family metadata after bounded acquisition | 0 |
| Verified family IDs crossing assigned partitions | 0 |
| Total HTTP requests, including two prototypes and one transient retry | 83 |
| Network requests in final cached verification pass | 0 |

The sole transient network failure succeeded on one manual retry. All 80
responses were then re-parsed from hash-verified private caches. No cross-partition
family collision was observed under the displayed Google Patents family IDs.
Independent DOCDB/INPADOC validation remains **not performed**; the improved
coverage is specifically for this source and taxonomy.

Family links are a supplement to the document, reaction, target, scaffold, and
intermediate overlap checks. The script reports any verified family spanning
multiple assigned partitions; it never silently changes those assignments.
Unknown family metadata remains an unresolved acceptance limitation. The result
also does not address an upstream prediction model's training contamination.

## Artifacts and reproduction

- Private mapping and aggregate report:
  `artifacts/private/srg02_sources/family_audit_v1.json`.
- Private per-document raw HTML and receipts:
  `artifacts/private/srg02_sources/patent_family_html/`.
- Public aggregate:
  [artifacts/steps/srg-02/patent_family_audit.json](../artifacts/steps/srg-02/patent_family_audit.json).
- The report pins the input assignment file, normalized record file, and parser
  source by SHA-256. Existing task-bundle files are read only.

```bash
.venv/bin/python scripts/audit_patent_families.py \
  --candidate artifacts/private/srg02-evaluator-v1/assignments.json \
  --records artifacts/private/srg02_sources/normalized_n1.json \
  --cache-dir artifacts/private/srg02_sources/patent_family_html \
  --output artifacts/private/srg02_sources/family_audit_v1.json \
  --public-output artifacts/steps/srg-02/patent_family_audit.json \
  --prior-requests 2
```

A repeat run uses existing receipts and rechecks their raw hashes. A later cohort
can reuse mappings by document ID, while the persistent request ledger continues
to enforce the same acquisition budget. Private paths are Git-ignored and raw
files use owner-only permissions. Same-user processes can still read them;
workflow isolation is not an adversarial filesystem boundary.

## Validation

Synthetic fixtures were written before the implementation and cover exact and
ambiguous family metadata, publication mismatches, citation-family exclusion,
legacy IDs, kind-code matching, redirects, timeouts, oversized responses, cache
hash integrity, persistent request limits, route-only assignment selection,
partition-family conflicts, and an offline CLI end-to-end run. No benchmark
patent text or chemistry is embedded in tests.

```bash
.venv/bin/python -m pytest tests/test_patent_family_audit.py -q \
  --cov=audit_patent_families --cov-report=term-missing --cov-fail-under=80
```

Latest validation: **33 tests passed; 96.97% branch-inclusive coverage** for the audit script.
