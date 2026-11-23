# Environment specification

## Research question

Can an agent generate routes to the supplied fluorinated quinoline ether and distinguish predicted transformations from literature-supported reaction classes and experimentally validated same-substrate outcomes?

## Inputs / outputs

Input: exact target SMILES in `results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json`; authorized Boltzmann retrosynthesis route JSON for optional local rebuilding. Each route has `starting_materials`, a reaction-node tree, model ranking and `reaction_yield`. The original raw account export is **not** included.

Outputs: sanitized JSON for all 16 routes, top0 review JSON, research and source documents, and a rendered DOCX with molecular structures. No user-identifying service IDs, signed URLs, keys, or source-site page dumps are distributed.

## Method and boundaries

Traverse the reaction-bearing child nodes of every `topN.path` in postorder. A reaction node and its duplicate molecule node form one transformation. Do not use the inconsistent raw `num_steps` as the count. Validate that reaction yields are numeric percentages before computing illustrative products of fractions; these arithmetic products are **not** forecast total yields. Distinguish reaction-family precedents from verified same-substrate literature and observed reaction products. Independently verify any tool-recommended condition against chemical plausibility.

Only top0 was separately checked by forward prediction, mapping, impurity prediction and condition recommendation. On its central aryl-ether step, the protected target ranked last with model score zero; pyridine/THF without a coupling catalyst did not establish the proposed substitution. The suggested TBAF during silyl *formation* was mechanistically contradictory; TBAF during *deprotection* is a documented reaction-family analogy for a different substrate. No step of the target was experimentally executed.

## Acceptance criteria

- Sixteen route records and unique route identifiers; each step has precursor and product strings.
- Calculated illustrative products agree with step percentage arithmetic at reported precision; at least one explicit check of `top0` and `top1`.
- No assertion of an experimentally validated exact target route or measured target yield.
- Source links and evidence tiers are present; model outputs and third-party experimental observations cannot be conflated.
- Package tests pass and DOCX opens with embedded structure figures.

## Non-goals

No optimization of lab reaction conditions, commercial procurement, patent clearance, calibrated yield modeling, or inferred laboratory observations. Authenticated platform execution is a separate opt-in workflow.
