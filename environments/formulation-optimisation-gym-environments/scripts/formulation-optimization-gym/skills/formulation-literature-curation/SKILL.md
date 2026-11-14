---
name: formulation-literature-curation
description: Audit ranolazine formulation tables and dissolution figures into a traceable exploratory literature dataset. Use for publication extraction without treating research data as recalled-lot QC measurements.
---

# Formulation literature curation

Read `data/processed/public_literature_catalog.json`, `docs/source_and_tool_matrix.md` and [implementation plan](../../docs/implementation_plan.md) T04. Verify actual saved source files and reuse terms before extraction. Neither catalogued paper is a recalled Glenmark/Ajanta lot record.

## Source-specific checks

- DOI `10.5281/zenodo.1311884`: visually audit shifted/blank dissolution cells and the apparent nonmonotonic value. Match accepted cells to page/table/row/column; do not fill gaps from adjacent columns or force monotonicity.
- DOI `10.5281/zenodo.1170150`: seek numerical tables/supporting data first. If graph digitization is appropriate/permitted, record axes, scale, curve identity, method and extraction uncertainty, with independent visual review.

Discovery is not dataset readiness. Additional sources require the same review.

## Curate

1. Record publication/version, URL, access date, reuse terms, PDF checksum and exact locator.
2. Extract formulation identity, ingredient quantities/grades and dose basis only where stated. Missing features stay unknown; do not borrow another formulation's composition.
3. Link every value to formulation, method, timepoint, unit and reported replicates/variability. Missing variability is not zero variability.
4. Published numbers remain `literature_reported`. Graph-derived/transformed values are `derived` with literature parentage and extraction uncertainty. Neither becomes authenticated case `measured` data.
5. Have an independent reviewer accept, exclude or escalate transcription/ambiguity decisions. Preserve reviewer and rationale; unresolved cells stay quarantined. Do not silently repair inconsistent data.
6. Group replicates, related formulation families, shared controls and duplicate data across papers before splitting. Assess independent support and method coverage for the intended use.

## Hand off

Produce source/cell audit and quarantine ledgers, accepted rows, method/feature dictionary and grouping manifest in permitted storage. Keep exploratory data separate from recall episodes.

The current predictor/benchmark require `measured` rows. Do not relabel literature to bypass that guard. If implementing T04, introduce an explicitly exploratory eligibility path preserving labels, and test that the measured-only path remains strict.

Use [benchmark](../formulation-benchmark/SKILL.md) after curation eligibility. If independent training/calibration/test support is inadequate, deliver the audited dataset with `not_evaluated`. Research tables cannot establish recalled-product criteria, root cause or a corrective formula.
