# Status

**Lifecycle: In Progress. Scientific tier: DESIGN_ONLY.**

## Implemented and actually executed in the source investigation

- 12 supplied plus 12 generated 800 mg designs, with hard gates and ten deliberate rejection controls.
- PubChem/Europe PMC source retrieval, RDKit descriptors, 100 Optuna information-design trials with exact verification.
- Actual PTCalc.Core 1.1.0 execution: 288 descriptive fit records across sixteen published profile records; independent arithmetic review. Not a target-recipe predictor.
- Improvement study: fifteen deduplicated profiles, eleven configurations, 1,155 profile/model/split evaluations; four additional valid recipes; 28-recipe pool.
- Held-out forward error improved for selected configurations; other LOTO errors worsened. No superiority over a literature tablet is established.

## Repository integration

Portable source, explicit task registry, consistent `Task - 01` folders, source snapshots, versioned curated results, research notes and executable regression tests.

Executed integration validation: **29 tests passed, zero failures/errors/skips** on Python 3.13.7. A fresh portable runner execution reproduced all 33 aggregate metric rows within absolute tolerance 1e-7 and generated the 28-recipe pool. Link/source-hash/publication scans, CLI overwrite/unknown-task rejection and Python compilation passed. Receipts are in `results/Task - 01/repository_validation.json`, `repository_tests.txt` and `repository_run_receipt.json`. Unrelated existing environment suites were not rerun.

## Not accomplished

No candidate manufactured, measured or independently replicated. No controlled QC specification, assay reconciliation, trained formulation surrogate, external batch validation, calibrated candidate intervals, approved clinical equivalence, shelf life or manufacturing window. Draft method/material gates require scientific approval. Early sampling and eleven pilot batches are PLANNED_NOT_RUN.

## Governance

User requested publication to **Rebolt**, not main. No main merge, reviewer approval or completed scientific qualification is claimed. Repository license selection remains pending. Existing environments and prior result versions are preserved.
