# Task 04 — Pd-NHC Suzuki–Miyaura blind optimization

Folder identifier: `task-04-pdnhc-suzuki-miyaura-optimization`. Use this same identifier under `tasks/`, `benchmarks/` and `results/`.

## Overall objective

Evaluate an autonomous multi-tool workflow for a blind Suzuki–Miyaura cross-coupling: predict the product from the supplied reactants, recover feasible routes, recommend Pd-NHC catalysts and reaction conditions, rank predicted yields, and attempt reduced-catalyst-loading optimization — without accessing withheld experimental answers. Distinguish tool predictions and design hypotheses from measured experimental results at every stage.

## Problem statement and scope

| Input | Value |
|---|---|
| Reactant 1 | 4-chloroanisole, `COc1ccc(Cl)cc1` |
| Reactant 2 | 4-(trifluoromethyl)phenylboronic acid, `OB(O)c1ccc(C(F)(F)F)cc1` |
| Target product (structural input) | `COc1ccc(-c2ccc(C(F)(F)F)cc2)cc1` |
| Reaction class | Suzuki–Miyaura cross-coupling |
| Catalyst class constraint | Pd-NHC precatalyst |
| Configuration | `top_k_routes: 5`, `top_k_conditions: 10`, `blind_mode: true` |

The target is a structural input for target-driven execution, not an experimental answer or independent product discovery. The benchmark's experimental optimum, measured yields and reference conditions were withheld; no exact-pair, benchmark-ID, original-paper or measured-yield lookup was performed during generation.

Problem stages: input validation; retrosynthesis; forward prediction and structural verification; condition recommendation; Pd-NHC constraint enforcement; yield and catalyst-loading optimization; side-product identification; provenance recording; post-hoc literature similarity review.

## Exact target/input and source provenance

Inputs come from the task supplied in the session workspace (`SC01_agent_workflow.md`, identifier `SC01`). All generated artifacts were frozen before any post-hoc literature review. Source call IDs and tool versions are preserved in the machine-readable trace at [results/task_record.json](../../results/task-04-pdnhc-suzuki-miyaura-optimization/task_record.json); raw service exports are not redistributed here.

## Execution approach

| Stage | Tool or method | Inputs | Origin |
|---|---|---|---|
| SMILES validation | RDKit 2025.09.6 | three supplied structures | local |
| Retrosynthesis | `retrosynthesis` job `6b053cb3a74792a53542b531` | target SMILES | internal platform |
| Forward prediction | `forward_reaction` job `6b053cb88e07760a3d1b14c9` | reactant SMILES, empty intermediates | internal platform |
| Side products | `impurity_prediction` job `6b0540db274b4c9537b25a85` | reactants + validated product | internal platform |
| Conditions | `condition_recommendation` jobs `6b0540e0…`, `6b0543a9…`, `6b058bc6…` (failures) and `6b07c97c…` (success) | reactants + validated product | internal platform |
| Order sensitivity | `condition_recommendation` job `6b07dac0…` | reversed reactant order | internal platform |
| External conditions | Parrot, USPTO-Condition weights, 15 predictions | `reactants>>product` | external open source |
| Literature similarity | Public Pd-NHC Suzuki papers, general reaction-class context | post-hoc, no exact-pair lookup | documentary |
| Pd-NHC-constrained design | `reaction-optimize` local pipeline, BayBE v1 | explicit `condition_space` | external local tool |
| Loading-aware design + frozen yield | `reaction-optimize --yield-model reactiont5v2-task` | loading in `equivalents`; resolved catalyst/base SMILES | external local tool |
| Persistent campaign | `reaction_optimizer.campaign_cli create/next` | loading-aware campaign JSON | external local tool |

Fourteen tool calls were recorded. Three condition-recommendation attempts failed with GLM HTTP 429; a bounded later retry succeeded. All outputs were validated structurally with RDKit where molecular identity was involved. No wet-lab experiment, model training or new service job was performed during packaging of these folders.

## Expected outcomes and acceptance criteria

1. Return one correct top-ranked product for the supplied reactants and verify it by canonical molecular identity against the structural target.
2. Preserve up to five ranked routes with precursor identities and compatibility flags; do not fabricate missing route scores.
3. Return up to ten conditions with original numeric fields; missing catalyst loading, base identity and units remain null.
4. Provide up to three Pd-NHC catalyst candidates/families supported by tool output or explicitly labelled as literature context.
5. Report side-product candidates with native score semantics; never call scores experimental yields.
6. Rank candidates only where numerical evidence exists; reject invalid high-yield predictions.
7. Attempt catalyst-loading optimization; report reduction and retention only if computable from comparable measured numbers.
8. Freeze outputs with provenance before any literature comparison and avoid prohibited benchmark lookups.

## Actual outcomes

The top-ranked forward product matched the supplied target by canonical identity (native model score 1.0). Five Suzuki/Negishi routes were recovered; the exact supplied reactant pair was not among the top five and was kept as a separate direct branch. Ten internally recommended conditions were returned after three HTTP 429 failures; the selected condition was water/1,4-dioxane at 100–110 °C with a native predicted yield of 32.338% and feasibility 0.78. Parrot's 15 predictions lacked Pd in top ranks and were not adopted. The local optimizer produced eight named Pd-NHC design candidates and, in a loading-aware run with resolved component SMILES, nine frozen-model yield predictions (8.105–8.886%). Loading was encoded as 0.5/2/5 mol% in `equivalents`, but the frozen yield model does not encode loading, so identical yields appeared across loadings for the same catalyst/base. A persistent campaign with a six-experiment reservation was created; no measurements were supplied. Therefore no validated low-loading, yield-optimal recipe was established.

See [benchmark definition](../../benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/README.md), [results inventory](../../results/task-04-pdnhc-suzuki-miyaura-optimization/README.md), [comparison report](../../results/task-04-pdnhc-suzuki-miyaura-optimization/comparison_report.md), [achievements](../../results/task-04-pdnhc-suzuki-miyaura-optimization/achievements_and_comparison.md) and [gaps](../../results/task-04-pdnhc-suzuki-miyaura-optimization/gaps_and_improvement_plan.md).
