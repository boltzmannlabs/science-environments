---
name: formulation-data-intake
description: Review and ingest authorized case-specific dissolution, batch and process records with controlled provenance in formulation-optimization-gym. Use for recall data eligibility, not publication transcription.
---

# Controlled formulation data intake

Read `docs/data_and_provenance.md`, `environment/observations.py` and [implementation plan](../../docs/implementation_plan.md) T01–T02. Check whether proposed importers/schemas actually exist; never claim planned code ran.

## Establish context

Require case/product/strength/lot, responsible data owner, permitted purpose and approved storage/processing destinations. Reuse existing authorization. Keep confidential records in approved private storage outside repository datasets. Missing access blocks the scientific import; schema/fixture work may continue.

## Review and ingest

1. Verify document identity, version, effective dates and case applicability with the controlled-record reviewer. Preserve original bytes and hashes. A hash establishes integrity, not manufacturer authenticity.
2. Link supplied method/specification to apparatus, media, agitation, timepoints, assay/units and stage-specific rules exactly as recorded. Public FDA recommendations and SPL labels cannot replace the controlled lot-specific method.
3. Preserve individual-unit/replicate profiles, run/instrument/calibration/analyst identifiers, timestamps, reference lots and OOS/deviation links where supplied. Missing critical fields prevent eligibility; retain raw observations before summaries.
4. Link batch dose/potency basis, material quantities/grades/lots and recorded manufacturing/storage/stability history. Qualitative label ingredients cannot supply levels or settings.
5. Validate identity, finite numeric values, units, timepoints, duplicate identifiers and method compatibility at the boundary. Quarantine mismatches/ambiguities without changing original sources. Preserve transforms and reviewer decisions.
6. Use `measured` only after source authenticity/access and scientific provenance checks appropriate to the case. Derived summaries retain parents/transforms. Predictions, recall text and literature do not become lot measurements.

Historical authorized records need an intake/access decision and source verification. Do not invent prospective proposals/approvals merely to fit `record_measurement`. Prospective results need matching protocol approval and external execution confirmation from [experiment design](../formulation-experiment-design/SKILL.md).

## Deliver and verify

Produce an intake manifest: source/document IDs/hashes, case/method links, permission scope, accepted/quarantined records, units/transforms, reviewer attestations and gaps. Sensitive contents stay at the approved destination; repository summaries use permitted metadata.

Every eligible value must resolve to an original record. Missing method, criteria, measurements or batch/process records restrict the analysis. Public-source consistency does not establish scientific completeness.

For implementation, first test cross-case records, absent authorization, changed method version, nonfinite values, wrong units and broken lineage. Legacy public episodes must remain loadable without scientific-status promotion.
