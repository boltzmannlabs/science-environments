# Decision 0002: Source-paper selection and retirement rules

**Date:** 2026-11-04

## Context

Tasks must be executable end-to-end by an independent agent in ~240 minutes from public data only, without the paper's hit lists. Roughly 1,100 candidate papers were screened across replacement rounds; abstracts routinely hide disqualifying stages (MD protocols, wet-lab sections, library provenance) below the fold.

## Options considered

1. Anchor tasks to methodologically impressive papers regardless of workflow complexity.
2. Restrict to fully computational, simple-chain papers (target → screening → docking → ADMET → secondary MD) on human-disease targets, with hard exclusion rules and file-level supplement verification.
3. Allow partially gated data with best-effort substitutions everywhere.

## Decision

Option 2. Hard exclusions: flora/natural-product libraries; repurposing screens or DrugBank-derived leads; QSAR/DFT/ML stages; wet-lab stages; non-human-disease targets; gated data without a public substitute; wrong-PMC attribution. Every candidate receives a full-text scan (Europe PMC `fullTextXML`) before acceptance, and supplements are downloaded and inspected at the file level — a data-availability statement alone is never sufficient. Where a gated library is otherwise ideal (PI3Kα/ChemDiv, dual-kinase ChemDiv), the task document carries an explicit public-substitute clause instead of dropping the paper.

## Reasoning

Every exclusion rule encodes an observed failure: the H1-antihistamine paper was retired because no SMILES existed anywhere in paper or supplement (2D depictions only) — an execution blocker; the CDK1 paper had a verifiably complete supplement but a workflow (AutoDock 4.2.6 cascade over 100 analogs) judged too complex for the time budget; keyword hits in reference lists (not methods) produced false positives (e.g., "machine learning" in the GSK-3β paper's references) and must be classified by context before rejection.

## Consequences

- Final roster: 6 tasks per environment, each anchored to one 2022–2026 open-access paper (see `research/small-molecule-virtual-screening/references.md`).
- Retired papers are preserved verbatim in `science-environments/retired/<environment>/` with their retirement reason, not deleted.
- The reference policy inside each task forbids looking up the source publication to copy hit lists or scores.

## References

- `research/small-molecule-virtual-screening/research-notes.md` §4 (trap catalog), §5 (supplement findings)
- `retired/structure-based-discovery/task_003_cdk1_docking.md`, `retired/molecular-design-and-generation/task_006_h1_antihistamine_pharmacophore.md`
