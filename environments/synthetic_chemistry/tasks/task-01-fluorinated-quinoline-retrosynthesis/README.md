# Task 01 — Fluorinated quinoline retrosynthesis and evidence audit

Folder name: `task-01-fluorinated-quinoline-retrosynthesis`. This single document combines the complete objective, workflow phases, expected outcomes, acceptance criteria and observed results.

## Overall objective

Find candidate synthetic pathways to the supplied fluorinated quinoline ether, evaluate whether a selected route is chemically supported, and compare generated chemistry and yield fields with publicly available research papers, patent records and experimental references without confusing model predictions with laboratory evidence.

## Exact input

- Target SMILES: `CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`
- Experiment label: `test_agent`.
- Existing authorized platform outputs, archived as sanitized derivatives; no credentials or account-scoped exports are published.
- Separate cinnamic-acid/diaminouracil `synth-test` work is outside task-01-fluorinated-quinoline-retrosynthesis.

## Complete workflow and expected outcomes

| Phase (subtask) | Work performed | Expected deliverable |
|---|---|---|
| [Route generation](#phase-1--generate-and-reconstruct-routes) | Generate candidates and reconstruct transformations without duplicate molecule/reaction-node counting | Starting materials, intermediates, products, explicit step counts and model rankings for each route |
| [Selected-route validation](#phase-2--review-the-three-step-top0-candidate) | Examine top0 with forward prediction, atom mapping, impurities and condition recommendations | Supported steps or explicit contradictions; scores retained as model outputs |
| [Literature comparison](#phase-3--compare-model-chemistry-with-public-literature) | Compare with public chemistry and distinguish exact matches from analogous substrates | Paper/source catalog, comparison tables, measured-versus-predicted status, limitations and recommendations |

The three phases below are parts of **task-01-fluorinated-quinoline-retrosynthesis**, not separate experimental targets or future Tasks 02/03.

## Acceptance criteria

1. Preserve all 16 route proposals, source target SMILES and explicit transformation counts.
2. Record the three selected-route steps and failures without asserting chemistry succeeds merely because it maps.
3. List compared references and disclose substrate/access limitations.
4. Show numerical model fields and their illustrative products, but leave unmeasured target yield/selectivity and unmatched literature error unavailable.
5. Maintain linked, task-scoped outputs that regenerate and pass data consistency tests.

## Actual outcomes

16 model pathways and 56 reaction-node occurrences across routes; one three-step route separately reviewed. Two expected products ranked first, while the key protected ether ranked last with score zero. The central coupling and protection conditions were unsupported. No exact-target experimental route, measured yield/selectivity or superiority over literature was established.

See [task-01-fluorinated-quinoline-retrosynthesis benchmarks](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/README.md) and [task-01-fluorinated-quinoline-retrosynthesis results](../../results/task-01-fluorinated-quinoline-retrosynthesis/README.md).

---

## Phase 1 — Generate and reconstruct routes

### Problem / input
Generate synthetic candidates for the exact target in [route_summary.json](../../results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json), experiment label `test_agent`.

### Work
Retrieve the authenticated retrosynthesis output, traverse each topN reaction tree, preserve source SMILES, and separate explicit transformation counts from unreliable reported num_steps. Archive a sanitized public derivative without private backend identifiers.

### Expected outcomes / acceptance
Every route must have precursor/product strings, model step-yield fields, route ranking and explicit transformation count. Missing parameters (model version, seed, training corpus) must remain unknown. Do not assume commercial availability.

### Actual outcome
16 candidate paths and 56 reaction-node occurrences across those paths were preserved. Repeated chemistry across routes is not deduplicated. No target synthesis was run. Source-derived model results: [route_summary.json](../../results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json); numerical comparison: [CSV](../../results/task-01-fluorinated-quinoline-retrosynthesis/route_yield_comparison.csv).

## Phase 2 — Review the three-step top0 candidate

### Objective
Check whether proposed TBS protection → aryl ether formation → deprotection is supported by forward product prediction, mapping, impurity candidates and condition recommendations.

### Expected outcome
A stepwise record of product ranking/score, map confidence, predicted reagents/solvent/temperature and scientific plausibility; incompatible suggestions must fail review rather than be called validated.

### Actual outcome
[Selected-route audit](../../results/task-01-fluorinated-quinoline-retrosynthesis/top0_validation.json) records all three reviewed steps. Expected product ranked first for protection and deprotection, but last (score 0) for the protected aryl ether. Protection conditions included TBAF (conflicting with retaining TBS); coupling lacked a suitable catalyst. Mapping confidences were 0.2796387429721354, 0.219711511334239 and 0.6676465097407814; they are not yield or proof of feasibility.

Impurity predictions were run in the original workflow but the public derivative retains summarized findings, not complete raw impurity outputs. No observed impurity concentration, actual conversion or isolated target yield exists. Full model output availability must not be overstated.

### Remaining acceptance gap
Find a chemically supported central coupling strategy and test substrate-specific compatibility. No experimental validation achieved.

## Phase 3 — Compare model chemistry with public literature

### Objective
Determine whether any generated route matches experimental literature and whether conditions, selectivity, yields, step counts and practicality support the proposed target preparation.

### Expected outcome
Paper titles, identifiers and links; explicit same-substrate versus analogous chemistry; condition/yield comparisons only where extracted evidence supports them; missing availability/selectivity marked unknown.

### Actual outcome
[Paper catalog](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/papers.md) contains protection and diaryl-ether papers (bibliographic/class-level evidence), an inspected public TBS-deprotection experiment, and two non-matching patent screening hits. The experimental 32% yield in the deprotection reference concerns another substrate. No exact target-route precedent or matched experimental yield was established. Literature coverage was incomplete and not structure-indexed; no novelty or freedom-to-operate claim follows.

[Comparison tables](../../results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md) distinguish condition-tool predicted yields from retrosynthesis predicted yields. [Metrics](../../benchmark/task-01-fluorinated-quinoline-retrosynthesis/achieved_metrics.json) have null for measured target yield/selectivity and literature yield error. No claim of tool outperformance is supported.
