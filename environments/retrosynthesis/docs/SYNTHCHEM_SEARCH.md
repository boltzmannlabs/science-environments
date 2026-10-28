# SynthChem search integration

Status: implemented; native tests and real AiZynthFinder pilot passed.
Owner: search/environment maintainer.
This local integration accompanies the 14-step plan. SRG-06's failed model gate
and the reserved final benchmark remain unchanged.

## Requested behavior and provenance

Adapt native Syntheseus 0.8.0 `RetroStarSearch` with zero heuristic and positive
step costs, `MolSetMCTS` with UCT/stock-progress estimates, and an A* then MCTS
portfolio sharing proposals, following the copied SynthChem implementation.
Source snapshot: `/home/boltzmann6/synthchem-review/20261027/source`.
The [audit](EXTERNAL_SYNTHCHEM_AUDIT.md) records its transfer. Source package
metadata declares Apache-2.0; no root license file was in the copied snapshot.
This is local adaptation; redistribution terms are not newly established.
The [Syntheseus dependency](https://github.com/microsoft/syntheseus) is MIT.

## Implementation and acceptance

1. Pin source, dependency and historical artifact identities.
2. Write failing tests, then implement an environment-backed shared proposal
   pool. Route fresh predictions through existing metering/timeouts. Retain
   failures separately from successful empty predictions.
3. Adapt native A*/MCTS, divide remaining resources between phases, bound graph
   and extraction work, and reserve submission capacity.
4. Convert routes into SRG schemas. Preserve disconnected salts and repeated
   reactants; recheck graph, inventory, quantity and task constraints.
5. Expose explicit CLI policies and existing LocalRetro/AiZynthFinder bindings.
   Preserve the old default and main-profile research LLM settings.
6. Run native synthetic/E2E tests, full regression and bounded real-model checks;
   preserve failures and obtain separate code/accounting review.

No supplied root routes, literature seeds or evaluator answers enter search.
Native graph completion does not establish host acceptance or chemical success.
The original runner combines RetroChimera and template proposals; RetroChimera
weights were excluded from the copy. This integration uses one configured
backend per run, reproducing the native controller rather than the original
dual-backend proposal ensemble.

## Predeclared real-model pilot

Two hand-selected engineering examples: aspirin with methyl salicylate stock,
and benzyl acetate with benzaldehyde stock. Inputs are frozen in
`artifacts/synthchem-integration/pilot-plan.json` before backend calls. These are
not held-out benchmark targets or supplied reference routes.

Compare existing best-first search with the native portfolio using AiZynthFinder
template expansion: at most 12 expansions, 100 actions, 300 seconds, four
preparative steps, three submitted routes, width 20 and a 10,000 state/node
search setting. Task/action/time limits match; internal state semantics differ.
Every episode is cold, with no cross-episode cache. Report actual calls/time;
this small comparison does not promote a default or establish general gains.

A separate LocalRetro/portfolio smoke uses the existing single-step aspirin
task with four expansions and 120 seconds. No LLM or final evaluation is run.
Report graph solutions, submission/acceptance, step counts, unresolved chemistry,
errors, calls, time and hashes. Inventory-complete predictions are not experiments.

## Local interface

Install the optional native engine with `pip install -e '.[test,api,search]'`.
The CLI accepts `--search-policy synthchem_portfolio`, `synthchem_astar` or
`synthchem_mcts`. The default remains `breadth_first`.
`--max-frontier-states` sets the graph-node limit per native phase; the portfolio
has separate A* and MCTS graphs. Cache/accounting is shared inside a portfolio
episode, not across independent runs.

Example using existing AiZynthFinder template assets:

```bash
.venv/bin/python -m synthesis_route_gym plan \
  --task examples/aspirin_task.json \
  --search-policy synthchem_portfolio \
  --expansion-backend aizynthfinder \
  --aizynth-config artifacts/synthchem-integration/aizynth-config.yml \
  --chemistry-python .venv-aizynth/bin/python \
  --expansion-top-k 20 \
  --output artifacts/reproduction/synthchem-aspirin.json
```

For LocalRetro, select `--expansion-backend localretro` and supply its existing
chemistry interpreter and repository paths as in the README. These are host
scientific backends; the Agent Scientist main-profile LLM is unaffected.

Python callers construct `SynthesisRouteEnv(task, expand=adapter.expand)` and
call `synthesis_route_gym.synthchem_search.run_synthchem_workflow(env)`.
This is a host search controller, not a recursively dispatched LLM action.
The Strategist ticket can orchestrate it later under shared agent budgets.

## Observed pilot result (2026-10-27)

Both native phases ran in each portfolio episode, with actual model-generated
proposals and no supplied routes. Each accepted route below has **two reaction
steps** and passes SRG graph, inventory and constraint gates. Conditions,
quantities, yield, selectivity and experimental success remain unverified.

| Target | Controller | Accepted predicted routes | Expansion calls | Episode seconds |
|---|---|---:|---:|---:|
| Aspirin from declared methyl-salicylate inventory | Existing best-first | 3 | 11 | 36.58 |
| Same task | Native SynthChem portfolio | 3 | 12 | 35.67 |
| Benzyl acetate from declared benzaldehyde inventory | Existing best-first | 3 | 5 | 14.25 |
| Same task | Native SynthChem portfolio | 3 | 12 | 39.07 |

These are cold runs with matching caps, not matching actual compute consumption.
The native portfolio found no additional accepted routes over the comparator and
used more expansion calls. Small wall-time differences are descriptive. No
default was promoted and no general search advantage was established.

The separate LocalRetro/portfolio check also passed: three single-step aspirin
predictions were submitted and deterministically accepted, using four expansion
calls in 39.71 episode seconds. Across all five episodes there were 44 reported
backend calls, no expansion errors, no missing usage envelopes and no truncation.
All 62 frozen code/input identities and 28 model/runtime asset identities matched
after execution. No LLM call or model training was performed.

This advances the demonstrated engineering capability: actual multi-step routes
were generated in these examples. It does not retroactively change SRG-05's
zero-route LocalRetro pilot: the targets, inventories, expansion backend and
budgets differ. Nor does it close SRG-06's scientific-model improvement gate.

Verification: **944 tests passed, 93.57% combined statement/branch coverage**.
The three new core modules exceed 97% combined coverage in their focused run.
Tests cover native A*/MCTS, three-step and convergent graphs, salt identities,
duplicate reactants, strict per-phase node caps, missing dependencies, failed
expansions and budget exhaustion. Separate review reproduced and fixed two bugs:
reserving route registration as well as submission, and retaining invalid
extracted route contracts as rejections instead of aborting the run.

The native library warns that its own model cache is disabled. This is deliberate:
SRG owns the shared successful-response cache, keeping failed expansions retryable.
Graph-node limits are per phase. In-flight inference can overrun a phase allowance;
the environment's overall timeout and result-discard rules remain authoritative.

Evidence is stored in [the frozen pilot](../artifacts/synthchem-integration/pilot-v1/),
[input plan](../artifacts/synthchem-integration/pilot-plan.json),
[runtime/model identity](../artifacts/synthchem-integration/runtime-provenance.json),
and [test log](../artifacts/synthchem-integration/pytest.log).
The [separate review](../artifacts/synthchem-integration/review.json) rechecked
every submitted route against the host validator; all remain scientifically
unresolved. The [acceptance receipt](../artifacts/synthchem-integration/acceptance.json)
records the local implementation scope and outstanding scientific claims.
