# Five application workflows in the shared environment

Step 10 adds route-bound application reports to the existing local environment.
All five applications use stored routes, the same action history and the same
resource accounting. Reports expose the available evidence and its limits;
they do not edit routes, perform independent chemical review or certify a
synthesis. Agent Scientist can use these actions through its existing main
profile. No new LLM, trained model or deployment is required.

**Delivery status:** Step 10 is accepted for local integration. All five frozen
examples completed, produced their reports and submitted without failed actions
or truncation. The existing impurity checkpoint ran successfully. The full
configured regression passed 2,092 tests with 94.95% branch-inclusive coverage,
and separate implementation and source audits passed. This establishes software
integration, not measured scientific improvement. The accepted count is 7/14;
Step 11, adaptive orchestration and the Small Molecule handoff, is next.

## Common action and report contract

First register a route with `propose_route`. Use `application_report` with one of
the exact application names below. Route IDs must exist in the current episode.

| Application | Scope | Domain result version | Meaning |
|---|---|---|---|
| `inventory_planning` | 1–3 routes | `srg-inventory-report-v1` | Graph, constraints and declared inventory demand |
| `condition_optimization` | One route and one step | `srg-condition-application-report-v1` | Registered alternatives and admitted measured replay observations |
| `impurity_analysis` | One route and one step | `srg-impurity-report-v1` | Recorded impurity hypotheses and matching assay annotations, if supplied |
| `process_route_selection` | 1–3 routes | `srg-process-report-v1` | Declared material costs and step counts on a common basis |
| `biocatalytic_synthesis` | One route and one step | `srg-biocatalysis-report-v1` | Retrieved enzyme-reaction source matches and unresolved requirements |

For example, after storing a route and its step:

```json
{
  "action": "application_report",
  "arguments": {
    "application": "impurity_analysis",
    "route_ids": ["candidate-route"],
    "step_id": "step-1"
  }
}
```

Every successful report is returned inside the ordinary environment response.
Its `result` has version `srg-application-report-v1`, the application name, task
and application-configuration SHA256 identities, route references, an optional
route-step reference, input-event references and the domain-specific `result`.
`claims_experimental_validation` is false, and `validation_status` is
`software_contract_checked_scientific_validation_not_established`.

Route references include `route_id`, `route_sha256` and `parent_route_id`.
Step references additionally include `step_id` and `step_sha256`. Successful
observations, predictions and source retrievals join a report only through this
exact stored reference. Reusing a step name in a revised route does not transfer
the earlier route's observations or retrieved records. Propose a revision with
a new route ID and its parent ID; inspect and report it as a distinct record.
Hashes establish identity, not experimental truth.

The public boundary rejects unknown fields and duplicate route IDs. Application
routes have at most 12 steps; step actions require exactly one unambiguous step.
Configuration/report JSON is bounded to one megabyte. The condition helper has
a tighter 256,000-byte public bound. Host catalogs contain at most 100 condition
candidates, 100 impurity annotations or 100 biocatalytic records. Source and
condition requests paginate with `offset` and `limit` (1–20); responses provide
`next_offset`. Impurity `top_k` is 1–10. Only condition reports accept an optional
`candidate_id`, which must identify an already observed candidate.

## Additional actions

| Action | Required arguments | Result and access rule |
|---|---|---|
| `condition_options` | `route_id`, `step_id` | Registered factor/recipe alternatives and already admitted observations; unobserved yields stay private |
| `observe_route_condition` | `route_id`, `step_id`, `candidate_id` | One registered retrospective observation, subject to the shared observation allowance |
| `predict_route_impurities` | `route_id`, `step_id`; optional `top_k` | Existing configured predictor applied to canonical stored reactants and product |
| `retrieve_application_sources` | `application`, `route_id`, `step_id` | A page of host-registered records for `impurity_analysis` or `biocatalytic_synthesis`, subject to retrieval access and allowance |

Retrieval returns `srg-application-source-retrieval-v1` with the exact step
reference and catalog identity. It reads the host's bounded configured catalog;
it is not unrestricted internet search. A source in configuration is not yet
accessible evidence for a step report. The step must have a successful matching
retrieval event. A model-authored citation cannot register new evidence.

## Condition optimisation

The host supplies a finite measured study and a
`srg-route-condition-binding-v1` binding. The binding fixes the dataset identity,
source locator, complete base reactant multiset, product and each candidate's
factor values and recipe. Exact comparisons preserve encoded stereochemistry,
isotopes and multiplicity. Candidate recipe IDs match candidate IDs; candidate
factors must agree with explicit recipe inputs or `name=value` condition tags.
A chemical factor must also appear among declared recipe materials.

The sequence is `condition_options` → `observe_route_condition` for admitted
candidates → `application_report`. The report validates observations against
their source-bound candidate. Its best candidate is computed only from observed
outcomes; hidden optima and unqueried measurements are absent. Selecting an
unobserved candidate is rejected. An already attempted candidate cannot be
purchased again through either the route-bound or older observation action.

The recipe digest includes reactants, reagents, declared amounts, product,
conditions, inputs, equipment, operations and procedure-completeness flag.
Proposal scores, asserted evidence IDs and route/step labels do not change this
recipe identity. Even an exact recipe match leaves `route_step_yield_percent`
null: a retrospective candidate measurement is not automatically a measured
yield for the proposed route, scale or procedure.

The example reuses previously public Step 8 Doyle development observations.
This demonstrates integrated measured-data replay, not a fresh held-out
condition-optimisation benchmark or a newly performed experiment. See the
[condition binding notes](../artifacts/steps/srg-10/conditions/README.md).

## Impurity analysis

`predict_route_impurities` derives its inputs from the stored step. With the
explicit `--impurity-model` CLI flag, the adapter uses the existing local REBOLT
direct impurity T5 checkpoint. It performs offline inference, pins model/source
identities and retains failures or unavailable status. The predictor receives
reactants and major product; it does not receive the complete conditions,
reagents or scale. Its training labels are multi-product proxies, so predictions
remain `predicted_impurity_hypotheses`. No concentration is predicted.

An optional host `ImpurityAnnotation` binds a reaction identity and full declared
recipe digest to a source URL/locator/content hash, assay method, assay scope,
coverage declaration and measured identities. Mismatched reactions or recipes
are excluded explicitly. Separate assays are reported separately. A source hash
or supplied annotation does not establish independent verification.

Partial annotations support known-positive recall only. An unlisted prediction
is unlabeled; it is not automatically a false positive. Precision, recall, F1
and false-positive/false-negative counts require a declared complete finite
assay scope, reporting limit and complete declared recipe. Even then, they are
conditional identity metrics above that supplied limit, not evidence that all
other impurities are absent. The legacy standalone impurity helper was corrected
to retain this partial-label distinction; it still reports
`recipe_binding_status=not_bound_legacy_helper`.

Measured concentration fields require explicit units and sample basis plus a
compatible quantitation limit. Detection, quantitation and reporting limits are
distinct. Chromatogram area percentages are not silently treated as
concentrations. This follows the analytical distinction explained in
[ICH Q2(R2), sections 3.2.3 and glossary](https://database.ich.org/sites/default/files/ICH_Q2%28R2%29_Guideline_2023_1130.pdf).
The conservative scoring policy is this project's benchmark design, not an ICH
requirement or claim of regulatory compliance.

No measured impurity annotations were acquired for this delivery. Test assays
are synthetic fixtures. The real-model example can demonstrate inference and
provenance only; it cannot establish impurity accuracy or scientific improvement.
See the [impurity research notes](../artifacts/steps/srg-10/impurities/research.md).

## Inventory planning and process selection

The inventory report recomputes deterministic route checks against the task and
shows external requirements, internal demand, missing materials, shared
intermediates and convergent steps. Repeated demand is summed across consumers.
Known subtotals remain separate from unknown total requirements; missing amounts
do not become zero. Eligibility means the declared graph, inventory, constraints
and required quantities pass these checks, not that reactions are experimentally
feasible. `top_k_route_ids` preserves input preference among eligible records;
this report does not introduce a learned route ranker.

Process selection compares declared material cost and preparative step count.
Comparable routes need the same target/scale and currency, complete declared
flows and prices, source/date metadata, a purity basis and explicit exclusions.
The report retains quote dates, supplied price evidence kind and missing-data
reasons. A complete subtotal is still a supplied estimate. Ineligible records
stay in `unranked_route_ids`; eligible records form a cost/step Pareto set.

Neither report infers stoichiometry, fills missing prices, converts currencies,
rescales routes or multiplies step yields. `route_yield` remains null. Reagents
remain external purchases, even if a matching intermediate is made in-route.
Unreported workup, waste, labour and equipment costs are not inferred. The
examples use artificial inventory graphs and illustrative process amounts and
prices: their purpose is to exercise accounting and uncertainty handling, not
to demonstrate manufacturing savings.

## Biocatalytic synthesis

The host retrieves registered public enzyme-reaction records, then reports
matches to the stored step. The ordering distinguishes:

1. `exact_reaction`: reactant and complete product multisets match. Explicit
   source cofactors must also be declared for complete-query support.
2. `exact_substrates_product_projection`: substrates match, but the query omits
   source products. Omitted coproducts remain visible.
3. `product_only`: a product matches without complete participant agreement.
4. `product_similarity_analogue`: fingerprint similarity only.

Exact identity retains stereochemistry, isotope and participant multiplicity.
Fingerprint similarity is not an activity estimate. Inventory completeness here
means identity membership, not quantity, purity or suitability. Missing cofactor
records mean requirements are unreported. Known enzyme availability requires a
sourced host declaration and remains unverified stock. Conditions are compared
as declared strings; no activity, yield or executable procedure is inferred.

The public example uses [Rhea 58148](https://www.rhea-db.org/rhea/58148) and
[IUBMB EC 3.1.1.113](https://iubmb.qmul.ac.uk/enzyme/EC3/1/1/113.html).
Its ethanol route-step projection omits the source acetate and proton products,
so its appropriate match is a product projection, not a complete exact reaction.
These database records do not provide a measured activity or process yield for
the example. Saved source representations and their provenance are described in
the [biocatalysis notes](../artifacts/steps/srg-10/biocatalysis/README.md).

## Configuration, budgets and persistence

`--science-config` accepts the existing host-only `srg-science-config-v1` with a
new optional `application_config` object, version `srg-application-config-v1`.
Its fields are `condition_binding`, `impurity_annotations`,
`biocatalytic_records` and `process_basis`. The top-level `condition_replay`
contains the private smoke/development outcomes; `condition_binding` contains
the corresponding public factors and recipes. Keep the host configuration out
of model context. The application process basis takes precedence over the
older top-level process basis.

Every admitted action consumes the episode action/wall budget, including
read-only reports and failed requests. Route observations charge the same
`observe_condition` counter as the earlier tool; impurity predictions charge
`predict_impurities`. Application source retrieval shares the retrieval
allowance with `retrieve_sources` and `retrieve_biocatalysis` and requires
`source_access_mode=evidence_retrieval`. Configuration and source identity do
not grant free observations or retrievals.

Reservations persist before external work. The environment's `action_id`
idempotency returns an existing receipt for the same ID and payload; conflicting
payload reuse rejects. This is an environment/API facility: the simple CLI
`replay` loop dispatches actions without user-supplied idempotency IDs. Resuming
an agent episode requires the same application fingerprint and compatible
scientific configuration; changed configuration is rejected. Pending work is
recorded as interrupted/unknown rather than automatically replayed. See
[runtime recovery](RUNTIME_RECOVERY.md) and
[scientific tool contracts](SCIENTIFIC_TOOL_CONTRACTS.md).

## Local reproduction

The example pack is recorded at `examples/applications/`, with
`task.json`, `science-config.json`, `actions.json` and `evidence.json` per lane,
plus a hashed `manifest.json`. The preparation script validates schemas and
refuses to overwrite changed existing inputs. From the repository root:

```bash
.venv/bin/python artifacts/steps/srg-10/prepare-examples.py \
  --output-dir examples/applications

.venv/bin/python -m synthesis_route_gym replay \
  --task examples/applications/conditions/task.json \
  --science-config examples/applications/conditions/science-config.json \
  --actions examples/applications/conditions/actions.json \
  --output artifacts/reproduction/applications/conditions.json
```

The same replay command works with the `inventory`, `process` and `biocatalysis`
lane directories. Replays contain fixed action lists and make no LLM calls.
Use a fresh output location to preserve earlier evidence. For actual impurity
inference, supply the existing REBOLT checkout and compatible chemistry Python:

```bash
export REBOLT_ROOT=/home/boltzmann6/server3_data/boltzmann3/joel/REBOLT-FEATURES
export REBOLT_PYTHON=/home/boltzmann6/server3_data/boltzmann3/anaconda3/envs/mol_gpu/bin/python

.venv/bin/python -m synthesis_route_gym replay \
  --task examples/applications/impurities/task.json \
  --science-config examples/applications/impurities/science-config.json \
  --actions examples/applications/impurities/actions.json \
  --impurity-model --impurity-device cpu \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --timeout 120 \
  --output artifacts/reproduction/applications/impurities.json
```

`REBOLT_ROOT` must contain the existing
`retrosynthesis/impurity_optimizer/runs/t5_impurity_direct/best_model` checkpoint.
No download is triggered. Without `--impurity-model`, a requested prediction can
remain unavailable and its report must retain that status. `--impurity-device`
accepts `cpu` or `cuda`; selecting CUDA does not guarantee device availability.

These CLI flags were checked against `replay --help`. The frozen all-five runner
at `artifacts/steps/srg-10/run-examples.py` additionally requires an execution
freeze that pins inputs, code, runtime and checkpoint bytes. Its run receipts
are recorded in the [execution summary](../artifacts/steps/srg-10/execution-v1/runs/summary.json)
and [completion manifest](../artifacts/steps/srg-10/execution-v1/runs/execution-complete.json).
All 377 frozen inputs passed both preflight and postflight identity checks.

## Ownership and acceptance

| Contract or implementation | Version/owner responsibility |
|---|---|
| `application_contracts.py`, `application_actions.py` | `srg-application-config-v1` and `srg-application-report-v1`; environment integration owner |
| `portfolio_inventory.py` | `srg-inventory-report-v1`; inventory/accounting owner |
| `portfolio_conditions.py`, `portfolio_condition_binding.py` | Finite replay and `srg-route-condition-binding-v1`; condition workflow owner |
| `portfolio_impurities.py`, `adapters/impurity_local.py` | `srg-impurity-report-v1`; impurity contract/adapter owner |
| `portfolio_process.py` | `srg-process-report-v1`; process comparison owner |
| `portfolio_biocatalysis.py` | `srg-biocatalysis-report-v1`; biocatalytic source/matching owner |

The integration receipt records 36 passing tests and 99.09% coverage for its
tested integration modules, including all five reports, source/observation
access, pagination, revision isolation, idempotency and changed-configuration
rejection. This is scoped test evidence, not the final repository coverage.
See the [integration receipt](../artifacts/steps/srg-10/process/application-integration-verification.json).

The actual examples used 24 actions in total: five inventory, six conditions,
four impurities, five process and four biocatalysis actions. Conditions revealed
two registered measurements; impurities made one successful checkpoint request;
biocatalysis retrieved one registered source page. All five runs submitted,
with no failed/unavailable actions and no truncation. The impurity episode took
20.28 seconds; this is episode wall time, not isolated model inference time.
There were no LLM calls and no reserved final labels were opened.

The full configured regression passed **2,092 tests, with 24 warnings and 94.95%
branch-inclusive coverage**. Separate implementation, example-runner and final
accounting reviews left no unresolved HIGH/MEDIUM findings; their overlapping
selected-test counts must not be summed as unique tests. See the
[final code review](../artifacts/steps/srg-10/review-code-final.json) and
[runner review](../artifacts/steps/srg-10/review-code-examples.json).

The separate [source-case audit](../artifacts/steps/srg-10/review-source.md)
verified all five event chains, bindings, source identities and declared
quantity/cost calculations. The illustrative process costs were 51 and 80 USD;
the incomplete route remained unranked with unknown total cost. Biocatalysis
retained acetate and proton as omitted coproducts. Actual impurity predictions
included an unsupported C6 polyol and two unchanged inputs, ethyl acetate and
water. There was no matching assay: successful inference is not evidence of
useful impurity prediction. This is AI source-consistency review, not independent
laboratory validation or external chemist sign-off.

**Step 10's integration gate is accepted.** Scientific measurement gates remain
unvalidated. Steps 7–9 retain their open promotion gates, and main-only remains
default. Step 11 is next; final budgeted and genuinely unbudgeted comparisons
remain required in Steps 12–13. These examples do not establish autonomous gains
or close the held-out scientific improvement gate in the
[optimisation plan](OPTIMIZATION_PLAN.md).
