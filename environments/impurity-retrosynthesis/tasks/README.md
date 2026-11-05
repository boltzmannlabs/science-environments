# Task: evidence-gated impurity route screening

Inputs: an authorized platform route export and confirmed target identity. The default `config/targets.json` is provisional; never infer exact identity from CAS alone. Three targets are separate tasks. Do not combine rank/cost across targets.

Execution: run `scripts/audit_exports.py` separately for each target with the required explicit inputs and a *new* output filename. Inspect route IDs, model steps, target root matches, parse failures, omitted-element flags and absence of citations/conditions; the CLI holds all routes pending independent chemistry review. No model submission is performed by this package.

Required human review for a lead: product regiochemistry/stereochemistry/form, atom-mapped steps including all reagents, exact versus analogous precedent, reagent/solvent/byproduct compatibility, availability, work-up/isolation, impurity purge, >=95% analytically demonstrated purity, 100 g safety and scale suitability, and dated INR pack-price scenarios. Unsupported scores and unknown costs remain unknown.

Expected outputs: per-route table for *all* returned route IDs, optional documented lead/backup only after hard gates, stepwise 100 g material-balance and cost scenarios if priced/yield data exist; otherwise `Hold pending evidence` and a recovery note naming blocker and exact next human decision. Historic published results under `results/` are summaries, not a source of measured synthesis data.
