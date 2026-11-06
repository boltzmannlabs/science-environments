# Task - 01 — Retrosynthesis and evidence audit

## Overall objective

Find candidate synthetic pathways to the supplied fluorinated quinoline ether, evaluate whether a selected route is chemically supported, and compare generated chemistry and yield fields with publicly available research papers, patent records and experimental references without confusing model predictions with laboratory evidence.

## Exact input

- Target SMILES: `CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`
- Experiment label: `test_agent`.
- Existing authorized platform outputs, archived as sanitized derivatives; no credentials or account-scoped exports are published.
- Separate cinnamic-acid/diaminouracil `synth-test` work is outside Task - 01.

## Complete workflow and expected outcomes

| Phase (subtask) | Work performed | Expected deliverable |
|---|---|---|
| [Route generation](task_001_route_generation.md) | Generate candidates and reconstruct transformations without duplicate molecule/reaction-node counting | Starting materials, intermediates, products, explicit step counts and model rankings for each route |
| [Selected-route validation](task_002_step_validation.md) | Examine top0 with forward prediction, atom mapping, impurities and condition recommendations | Supported steps or explicit contradictions; scores retained as model outputs |
| [Literature comparison](task_003_literature_benchmark.md) | Compare with public chemistry and distinguish exact matches from analogous substrates | Paper/source catalog, comparison tables, measured-versus-predicted status, limitations and recommendations |

These three documents are phases of **Task - 01**, not separate experimental targets or future Tasks 02/03.

## Acceptance criteria

1. Preserve all 16 route proposals, source target SMILES and explicit transformation counts.
2. Record the three selected-route steps and failures without asserting chemistry succeeds merely because it maps.
3. List compared references and disclose substrate/access limitations.
4. Show numerical model fields and their illustrative products, but leave unmeasured target yield/selectivity and unmatched literature error unavailable.
5. Maintain linked, task-scoped outputs that regenerate and pass data consistency tests.

## Actual outcomes

16 model pathways and 56 reaction-node occurrences across routes; one three-step route separately reviewed. Two expected products ranked first, while the key protected ether ranked last with score zero. The central coupling and protection conditions were unsupported. No exact-target experimental route, measured yield/selectivity or superiority over literature was established.

See [Task - 01 benchmarks](../../benchmark/Task%20-%2001/README.md) and [Task - 01 results](../../results/Task%20-%2001/README.md).
