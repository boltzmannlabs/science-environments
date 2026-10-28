# Scientific tool and integration audit

This is a historical audit of the separate REBOLT working repository. Legacy source links and local artifact paths below identify that audit workspace; they are not bundled or expected to resolve in this science-environments checkout. Use the current [environment README](../README.md) for installation and executable examples.

Audited 2026-10-27 against the full repository at
`/home/boltzmann6/server3_data/boltzmann3/joel/REBOLT-FEATURES`, base commit
`3e1d3549a1a726d5e7a75b4f062667c3f4364b5c`, including its existing working-tree
changes. Agent Scientist contracts were checked in
`/home/boltzmann6/Agent-Scientist`. These are source inspections and the local
execution receipts identified below. Finding a worker or a registered contract
does not establish that its service was executed or that its predictions are
chemically correct. No platform scientific jobs were submitted for this audit.

Legacy source links below record paths relative to the original full repository; they do not resolve from this relocated document.
Agent Scientist links use its absolute local path. **Discovered** means source
was inspected; **executed locally** means a saved receipt is available;
**contract registered** describes the plugin catalog, not a new service test.

## Capability inventory and reuse

| Capability | Existing local repo entrypoint | Registered Agent Scientist contract | Reuse decision | Actual validation artifact | Limits |
|---|---|---|---|---|---|
| Retrosynthetic route search | [rebolt_update_opt/main_exp.py](../../rebolt_update_opt/main_exp.py), copied into the legacy `rebolt_update` path by [Dockerfile_tb_gpu](../../Dockerfile_tb_gpu); EG-MCTS/Retro* search and custom-stock worker code | `retrosynthesis`: required `target_mol`; optional `outname` | Reuse existing chemistry proposals through bounded local adapters; preserve stock checks in the gym. Retain registered dispatcher integration for the documented contract. | Legacy full worker **discovered**, not executed end to end. Local generator receipts below. [Adapter contract tests](../tests/test_adapters.py). | Worker `TASK_NAME` values and public `job_name` values differ. Custom stock is present in worker code but absent from the documented public payload; permissive `additionalProperties` does not verify its semantics. |
| LocalRetro single-step proposals | [rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py](../../rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py); existing `req_data/LocalRetro_boltz_USPTO_MIT.pth` and USPTO_MIT templates | No separate LocalRetro job in audited catalog; underlying retrosynthesis implementation | **Executed locally** using the existing compatible `_opt` source and checkpoint through [LocalRetroAdapter](../src/synthesis_route_gym/adapters/localretro.py). | [CPU aspirin receipt](../artifacts/adapters/localretro_smoke.json): four predictions, checkpoint SHA-256, elapsed time. [Matched-stock baseline](../artifacts/adapters/aizynth_baseline/report.json). | Raw scores are proposal scores, not calibrated feasibility. The other `rebolt_update/localretro` copy failed locally with missing `libdgl_sparse_pytorch_2.4.0.so`; `_opt` has a compatible existing edge-extraction implementation. |
| AiZynthFinder reference baseline | Not found as a usable preinstalled baseline; official AiZynthFinder 4.4.1 installed in package-local `.venv-aizynth` | No separate AiZynthFinder job in audited catalog | **Executed locally** with official USPTO expansion policy/templates; [adapter](../src/synthesis_route_gym/adapters/aizynthfinder.py) normalizes route trees into gym candidates. | [Baseline report](../artifacts/adapters/aizynth_baseline/report.json), [frozen task](../artifacts/adapters/aizynth_baseline/task.json), [reproduction script](../scripts/run_aizynth_baseline.py). | One benign target and one root expansion are a smoke test. This is the official AiZynthFinder policy, not LocalRetro relabeled as AiZynthFinder. Stock closure is independently recomputed after normalization. |
| Forward reaction prediction | [retrosynthesis/dual_forward_inference.py](../../retrosynthesis/dual_forward_inference.py), `inference_boltzmann_dual`; [retrosynthesis/main_.py](../../retrosynthesis/main_.py) worker; ASKCOS/T5/model composition | `forward_reaction`: required `target_mol` containing reactants; optional `intermediates` | Reuse as a possible independent prediction signal, with a model/version record. | **Discovered / contract registered**; no new execution receipt for the full forward stack. | The public input key is `target_mol`, not `reactants`. Forward agreement is model consistency, not experimental support. |
| Reaction condition recommendation | [textreact/consumer_main_quarc.py](../../textreact/consumer_main_quarc.py), `predict_conditions` | `condition_recommendation`: required `reactants`, `products` | Preserve the existing QUARC recommendation interface; keep recommendations separate from measurements. | **Discovered / contract registered**; no direct QUARC execution in this delivery. | A condition suggestion does not supply validated yield, impurity control, or operational suitability. |
| Condition optimisation | [conditions_optimization/main_eln.py](../../conditions_optimization/main_eln.py); [BayesianReactionOptimizer](../../conditions_optimization/unified/bayesian_optimizer.py) | No dedicated optimisation/DoE job found in audited catalog | Reuse finite candidate and ask/tell concepts. New [FiniteConditionStudy](../src/synthesis_route_gym/portfolio_conditions.py) exposes only queried observations under a fixed budget. | [Measured-condition replay](../artifacts/portfolio/conditions.result.json), [portfolio tests](../tests/test_portfolio.py). | Legacy Doyle warm-start consults hidden yields; excluded from fair benchmark use. Replay of measured rows is not a new physical experiment. |
| New yield/condition model and route decision scoring | Existing yield integration is in [yield_integration_new.py](../../rebolt_update/rebolt/rebolt_new/yield_integration_new.py); new [model_training.py](../src/synthesis_route_gym/model_training.py) and [ranking.py](../src/synthesis_route_gym/ranking.py) | No standalone yield/route-ranking job found in audited catalog; new versioned [local callable contract](../artifacts/model/tool-contract.v1.json) | Train an explicit scientific predictor on measured data; keep the route utility formula separately identified as a heuristic. | **Executed locally**: [evaluation](../artifacts/model/evaluation.json), [held-out route decisions](../artifacts/model/route_decisions/summary.json), [domain checks](../artifacts/model/condition_domain_verification.json). | Narrow C–N-coupling domain. Three correlated held-out substrate inventories cover one product family. Top-1 improves; top-5/top-10 lose to the stronger baseline. No multi-step retrieval improvement demonstrated. |
| Impurity prediction and analysis | [retrosynthesis/impurity.py](../../retrosynthesis/impurity.py); actual direct-model path [retrosynthesis/eval_impurity_t5.py](../../retrosynthesis/eval_impurity_t5.py) with `impurity_optimizer/runs/t5_impurity_direct/best_model` | `impurity_prediction`: required `reactants`, `products` | **Executed locally** through [LocalImpurityAdapter](../src/synthesis_route_gym/adapters/impurity_local.py), reusing the trained T5 checkpoint. Keep candidates as impurity hypotheses. | [Live inference receipt](../artifacts/portfolio/impurity_live_ethyl_acetate.json), [execution and failure analysis](../artifacts/portfolio/impurity_live_report.json). | The tested direct checkpoint is not evidence that the complete legacy impurity worker was executed. Training labels are multi-product proxies. Several generated molecules are questionable for the simple input. Measured truth, precision, recall, and concentration are unavailable. |
| Process route selection and costs | [pathway_Analysis/get_Scores_cluster_bob.py](../../pathway_Analysis/get_Scores_cluster_bob.py), legacy pathway formatting, `req_data/cs_cd_mcule_costs.json` | No standalone pathway-scoring job found in audited catalog | Reuse source inventory/cost inputs when their units and dates are known. New [portfolio.py](../src/synthesis_route_gym/portfolio.py) offers explicit cost/step Pareto comparison; missing cost remains unknown. | [Process-selection example](../artifacts/portfolio/process_routes.result.json), [inventory example](../artifacts/portfolio/inventory.result.json). | Examples use supplied illustrative costs. No measured process economics or scale-up validation. Currency, amount basis, quantity coverage, and price freshness matter. Legacy weighted scores are not learned feasibility probabilities. |
| Atom mapping and structure checks | [atommapping/main.py](../../atommapping/main.py), [atommapping/atommap.py](../../atommapping/atommap.py), `amas/` ensemble code | `atom_mapping`: required `reactants`, `products` | Retain as an optional transformation diagnostic; use RDKit for local representation and graph checks. | Legacy mapping **discovered / contract registered**. Gym checks exercised through [environment tests](../tests/test_environment.py). | Parseability, mapped atoms, and elemental plausibility do not establish a possible or selective chemical reaction. |
| Literature/procedure retrieval | [procedures_retrival/get_proc_v2.py](../../procedures_retrival/get_proc_v2.py), [get_proc_v3.py](../../procedures_retrival/get_proc_v3.py), local `req_data/uspto_full.csv` | No dedicated procedure-retrieval job found in audited catalog | Retain source identifiers and locators; distinguish exact reaction support from analogue retrieval. | Legacy retrieval **discovered**. [Held-out source audit](../artifacts/model/route_decisions/summary.json) checks selected records against frozen experimental data. | Similarity matches and a legacy `reference=True` flag do not establish exact support. Automated source correspondence is not human chemical review. |
| Biocatalytic synthesis | No dedicated legacy synthesis-route implementation found in this repo. New [retrieve_biocatalytic_routes](../src/synthesis_route_gym/portfolio.py) | Related `Genzyme_Generation`: required `input_substrate`, `input_product`, `num_structures`; candidate enzyme structure generation, not a route-feasibility tool | Execute source-grounded reaction retrieval locally. Keep the discovered Genzyme contract separate from evidence of enzyme function. | [RHEA:58148 retrieval](../artifacts/portfolio/biocatalysis.result.json), [portfolio tests](../tests/test_portfolio.py). Genzyme **contract registered only**, not run. | Database annotation supports the recorded transformation; it supplies no measured enzyme activity, yield, conditions, or availability. Analogue matches do not validate the query substrate. |

## What the registered interface actually provides

The [plugin registration](/home/boltzmann6/Agent-Scientist/plugins/boltzmann/__init__.py)
It registers five generic functions with a credential availability check:

- `boltzmann_submit(job_name, experiment_data, experiment_name)` validates the
  selected scientific contract and returns a job receipt.
- `boltzmann_status(job_name, doc_id)` polls that existing job.
- `boltzmann_download(download_url, output_folder)` retrieves a completed output.
- `boltzmann_upload(local_path, job_name, input_field, ...)` validates and uploads
  an input file.
- `boltzmann_fetch_tool_log(experiment_id, job_name or verified collection)` reads
  diagnostic records.

Exact signatures and constraints are in
[schemas.py](/home/boltzmann6/Agent-Scientist/plugins/boltzmann/schemas.py).
Scientific job names and payload fields above were checked against
[tool-contracts.v1.json](/home/boltzmann6/Agent-Scientist/plugins/boltzmann/skills/boltzmann-tools/references/tool-contracts.v1.json).
Historical `sample_verified`/`live_verified` diagnostic annotations in that
catalog explicitly refer to historical evidence; they are not current-run
receipts.

The new [RegisteredPlatformAdapter](../src/synthesis_route_gym/adapters/registered_tools.py)
accepts the existing `model_tools.handle_function_call` dispatcher. It does not
read credentials or construct private HTTP calls. Its submit/status tests use
injected dispatchers. It returns receipts with `complete=False` and no fabricated
reaction predictions; a result parser requires a real completed artifact and a
verified schema. The plugin's input validation and execution policies remain in
the dispatch path. This audit did not verify credential availability or exercise
the scientific jobs remotely.

## Scientific gaps that change benchmark interpretation

**Hidden-yield warm-start leakage.**
[get_doyle_warmstart](../../conditions_optimization/unified/evaluation/doyle_benchmark.py)
sorts the complete `oracle_map` by measured yield before sampling a purported
“QUARC-like” warm-start. That gives the optimiser privileged outcome information.
It cannot demonstrate an advantage over an equal-information baseline. The new
finite replay hides unqueried yields from the agent observation, charges queries,
and keeps observed measurements distinct from predictions. Python encapsulation
is not a security boundary against an agent allowed arbitrary filesystem reads;
a stronger external evaluator requires separate process/data permissions.

**Impurity proxy labels.**
[fragment_major_minor](../../retrosynthesis/impurity_optimizer/benchmark/build_dataset.py)
and [build_uspto_impurity_benchmark.py](../../retrosynthesis/build_uspto_impurity_benchmark.py)
treat the largest product fragment as the major product and smaller fragments as
impurity labels, with additional filters in the latter builder. Such annotations
are not chromatography, mass-spectrometry, concentration, or measured selectivity
data. The live checkpoint receipt proves inference executes; it does not establish
useful impurity prediction accuracy.

**Missing yields and misleading path yield.**
In [yield_integration_new.py](../../rebolt_update/rebolt/rebolt_new/yield_integration_new.py),
missing `reaction_yield` values default to `0`/`0.0` before output. A missing
measurement is not a measured zero yield. In
[formatting_paths.py](../../rebolt_update/rebolt/rebolt_new/formatting_paths.py),
`total_yield = mean(ys)` appears in both formatting paths, with an additional
numeric fallback in one path. Mean step yield is not overall route yield.
Overall material yield needs a defined route, stoichiometry, yields, and branch
accounting. The new schemas preserve unknown quantities/yields; the model's
declared route utility is not presented as overall yield.

**Missing costs and heuristic scores.** Legacy formatting/integration uses a
fallback cost of `262`; the pathway scorer combines manually chosen features.
Neither creates a measured purchasing cost or a calibrated success probability.
The gym keeps missing cost unknown and requires comparable currencies and amount
bases before cost selection.

**Route closed is not route feasible.** In
[main_exp.py](../../rebolt_update/main_exp.py), the forward-filter call is
commented out and `output_feasible=output` remains in two paths; another path
assigns `pathway_score=0`. Those names do not certify reactions. Stock membership
alone omits amounts, co-reagents, catalysts, conditions, equipment, selectivity,
purification, and evidence. The gym separately records graph validity, inventory
closure, quantity status, constraint status, and evidence/review. AiZynthFinder's
own `in_stock` flags are not accepted as the gym's inventory verdict.

**Retrieved support and model confidence.** Patent similarity retrieval may
provide useful analogues, but the legacy formatter's `reference=True` is not exact
experimental verification. Keep source locators, reaction identity, and condition
matching explicit. Neither raw LocalRetro/AiZynthFinder scores nor forward-model
agreement can upgrade a prediction to literature-supported or experiment-supported.

## Executed baseline and data provenance

The AiZynthFinder/LocalRetro comparison used the same aspirin target, four-entry
inventory, one-step limit, one root expansion, top-5 proposal cap, and 60-second
per-method wall cap. AiZynthFinder returned one inventory-closed route plus an
unclosed root-only candidate; LocalRetro returned four one-step candidates, three
inventory-closed. The [receipt](../artifacts/adapters/aizynth_baseline/report.json)
records the complete routes, assessments, timing, model/template hashes, task,
and inventory. This is an execution check, not a ranking superiority result.

LocalRetro and impurity inference reused
`/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python`
on CPU. AiZynthFinder uses a separate optional environment with PyArrow 20.0.0
for its NumPy 1.x compatibility. Its official expansion assets are approximately
95 MB total, with published checksums verified by the reproduction script.
Existing Agent Scientist Python environments were not modified.

The full repository contains LocalRetro training tables/checkpoints,
`req_data/uspto_full.csv`, and a large stock/cost JSON. Their presence does not make
them held-out benchmarks: training overlap, duplicate reactions, patent-family
leakage, source attribution, and redistribution rights must be checked before use.

The new model instead uses measured GAUCHE Dreher–Doyle data, with a frozen
product-family split and exact row assignments. The
[provenance reconciliation](../artifacts/model/provenance_reconciliation.json)
checks all 3,955 records against the upstream table; the different file hashes
come from CRLF/LF serialization. The learned model improves mean top-1 selected
yield by 0.961 percentage points over the training condition-mean baseline, while
that baseline wins at top 5 and top 10. The
[route-contract evaluation](../artifacts/model/route_decisions/README.md)
re-expresses the same held-out observations as 790 one-step candidates across
three correlated tasks; it is not another independent test set or retrosynthetic
discovery. Automated record review is recorded separately from human chemical
review and experimental reproduction.

## Ownership and acceptance boundaries

The synthesis-route-gym adapter owner maintains local dependency isolation,
bounded invocation, source/checkpoint fingerprints, sanitized diagnostics, route
normalization, and [adapter acceptance tests](../tests/test_adapters.py). The
Agent Scientist plugin owner maintains registered schemas, authentication,
validation, and dispatch. The condition-model owner maintains
`doyle-condition-ranker-0.1.0`, frozen protocol/data provenance, applicability
checks, and its [versioned contract](../artifacts/model/tool-contract.v1.json).
Portfolio-specific tests and receipts belong to their respective implementation
owners. These are responsibility boundaries; named operational owners are not
invented by this audit.

Acceptance distinguishes successful execution from scientific validity. Passing
adapter/environment tests establishes software behavior; a saved inference
receipt establishes a particular model ran; matching a source row establishes
record correspondence. Independent chemical review and broader held-out route
performance remain separate gates. See [LOCAL_DELIVERY.md](LOCAL_DELIVERY.md)
for the runnable local application and experiment commands.
