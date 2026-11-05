# Decision 0001: Task-document format and verbatim-accuracy policy

**Date:** 2026-11-04

## Context

Each of the 12 tasks is anchored to a published virtual-screening paper, and the agent is graded against the paper's own quantitative pass bar. Task documents therefore carry paper-derived numbers (docking-score cut-offs, grid coordinates, pharmacophore feature counts, MD parameters, ADMET bars). Any drift between document and paper silently corrupts the benchmark's ground truth. At the same time, the task format must be uniform across two environments so agents and graders can navigate any task with the same mental model.

## Options considered

1. Free-form per-task documents, accuracy enforced only by audit.
2. Fixed section skeleton (Description → Target → Design Constraints → Computational Tool Capabilities → Evaluation Metrics → Expected Output → Constraints → Important Instructions → Publication) with paper-verbatim values and every non-paper value labeled.
3. Separate machine-readable task specs (JSON/YAML) generated from papers, markdown as a rendering.

## Decision

Option 2. Every task document follows the fixed nine-section skeleton with bold sideheadings inside Target (**Name**, **Protein**, **Disease**, **Objective**, **Binding Region**, **Reference Inputs**, **Data**, **PDB**, **Structure and Context**), a stage × capability × expected-evidence table inside Computational Tool Capabilities, and **Format:**/**Directory:** lines inside Expected Output. Values that come from the paper are quoted verbatim (including unit conflicts); anything not in the paper — platform substitutions, derived notes, RCSB header metadata — is explicitly labeled "(derived)" or "RCSB metadata".

## Reasoning

A fixed skeleton makes audits mechanical (structure checks are scriptable in `tests/`), while verbatim quoting with explicit labeling is the only policy that keeps the meet-or-beat grading bar trustworthy. Option 1 abandons uniformity; option 3 adds a generation step whose failure modes (silent divergence between JSON and prose) are exactly what this policy exists to prevent.

## Consequences

- Paper-internal conflicts (e.g., 200-vs-100 ns MD in the MMP-9 paper, seven-vs-six pharmacophore features) are annotated in the document, never silently resolved; tables take precedence over prose as ground truth.
- Auditors must verify quotes against the source PDF/XML at claim level; column recounts are required before accepting any table-derived audit finding.
- Platform API spellings that look wrong (e.g., `exhaustivness` in `Vina_basic_docking`) are preserved verbatim because they are the real parameter names.

## References

- `environments/<env>/tests/` — structure validators enforcing the skeleton
- `research/small-molecule-virtual-screening/research-notes.md` §6 (conflicts policy)
