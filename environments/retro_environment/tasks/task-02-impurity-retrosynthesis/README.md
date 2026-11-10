# Task 02 — Impurity retrosynthesis and literature benchmarking

## Recovery update — supersedes earlier missing-artifact statements

The prior retro_case execution artifacts have now been recovered: parent racemic ibuprofen has **7 routes and 25 reaction-node comparisons**, distinct from the A/M subset. Comparator patents are US3385886A Example 4, EP0337803A1 and US5166418A; no measured superiority was found. See the recovered parent comparison and JSON linked from the Task-02 results index. Earlier owner-confirmed/unlinked wording below is a historical state, not current availability.


Task ID/folder: `task-02-impurity-retrosynthesis`. Use this identical name under tasks/, benchmark/ and results/. This is the current impurity project, distinct from Task 01's fluorinated quinoline.

## Overall objective

Evaluate candidate synthesis routes against literature for 100 g isolated material per target at ≥95% purity, with defensible INR costs where sufficient inputs exist. Identify a credible lead/backup or state why evidence requires a hold. Do not equate model yield/rank with experimental yield or literature superiority.

## Problem statement and scope

| Case | Question | Current evidence boundary |
|---|---|---|
| Ibuprofen EP impurity A, CAS 66622-47-7 | Do meta-isobutyl acid routes match the intended structure and direct patent precedents? | 12 paths/38 reaction nodes; PubChem-provisional identity; stereo/form specification open |
| Ibuprofen EP impurity M, CAS 60057-62-7 | Can the alpha-hydroxy para-isobutyl acid be made without losing OH or creating a related compound? | 7 paths/21 reaction nodes; provisional structure; conditions and exact-substrate precedent incomplete |
| Racemic ibuprofen parent | Compare completed parent-compound run with its actual literature baseline | Owner confirms completed run/comparison; numerical export and reference mapping not linked here |
| Original osimertinib label/CAS proposal | Resolve whether supplied Impurity A name means CAS 1421373-98-9 / AZ5104 | Historical identity hold; separate from racemic task; no generated export in snapshot |

Inputs: authorized route export, independently reviewed target SMILES, scope/form/purity method, primary paper/patent examples, supplier pack/date/INR evidence, and measured yields/recoveries if available. Raw service/account records are not published. This task excludes formulation optimization, biological efficacy comparison and unsupervised physical synthesis.

## Execution approach

1. Confirm exact connectivity, substitution position, stereochemistry and form. Preserve original route IDs and raw evidence separately from corrections.
2. Generate/retrieve authorized model paths (historical completed A/M jobs), traverse reaction nodes without duplicate molecule-node counting and run RDKit root/SMILES checks. Record absent element sources among listed precursors without declaring the incomplete graph atom-balanced or impossible.
3. Audit *every* path for bond changes, functional-group compatibility, conditions, byproducts, isolation and safety; classify exact-substrate, analogous and model-only evidence.
4. Inspect named references in the [benchmark](../../benchmark/task-02-impurity-retrosynthesis/README.md), compare actual substrates/products rather than reaction labels. Do not transfer patent yields to unlike model steps.
5. Build backward material balances including final recovery and price actual packs only when yields, stoichiometry and quotes are defensible. Missing costs and measurements remain unavailable.
6. Record outputs, achieved metrics, failed/held routes and a gap/recovery plan under [results](../../results/task-02-impurity-retrosynthesis/README.md). Physical validation requires qualified safety review and authorization.

## Expected outcomes and acceptance criteria

- All returned paths and original IDs represented; exact target root, intermediate and form checks documented with limitations.
- Reference table lists actual papers/patents, relevant examples and reported experimental outcomes with precise evidence class.
- A defensible lead/backup OR explicit no-winner decision; no aggregate score masks a critical structural/safety gap.
- 100 g/≥95% target basis stated; itemized INR low/base/high scenarios with dated sources OR not-estimable rationale.
- Identity/purity, isolated yield, impurity purge, reproducibility and safety validation plan separated from completed computational work.
- Data/readme links and numerical summaries agree; null is used for unavailable metrics, not a fabricated zero.

## Actual outcomes

A/M: 19 model paths and 59 reaction nodes screened, 19/19 provisional root matches, no nonempty exported node citation/procedure fields. Direct A product literature found, but no exact complete generated route experimentally confirmed. No observed yield/purity or INR superiority. Racemic completion is owner-confirmed, not independently reconstructed from linked numerical output. See [achieved metrics](../../benchmark/task-02-impurity-retrosynthesis/achieved_metrics.json), [comparison](../../results/task-02-impurity-retrosynthesis/achievements_and_comparison.md) and [gap analysis](../../results/task-02-impurity-retrosynthesis/gaps_and_improvement_plan.md).
