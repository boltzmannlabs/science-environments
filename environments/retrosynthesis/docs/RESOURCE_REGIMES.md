# Budgeted and unbudgeted local execution

Owner: environment and benchmark maintainers. Implemented during SRG-12.
Agent Scientist uses its configured main profile for every research LLM role.

| Setting | Budgeted | Unbudgeted |
|---|---|---|
| Task actions, expansions, tokens and episode time | Finite recorded ceilings | Explicit `null` ceilings |
| Main and advisor model/tool requests | One shared finite ledger | No aggregate admission ceiling; usage still recorded |
| Budget-triggered finalization | Reserves resources for submission | Disabled |
| Scientific query allowances | Configured finite allowances | Positive authorized allowances become unlimited; disabled tools remain disabled |
| Evidence permissions and inventory | Declared task and host permissions | Same permissions and inventory |
| Output top-k, branch width, synthesis depth and condition candidates | Declared task/policy | Same task/policy definitions |
| Tool timeouts, provider capacity, startup/IPC and artifact capacity | Recorded operational restrictions | Recorded operational restrictions |

Unbudgeted execution has no finite episode-time or token forecast. It may submit,
exhaust its generated search/candidate domain, fail, or be interrupted. A capacity
failure or external interruption is retained as a failed or censored attempt.
It is not counted as natural completion. A completed search phase can still be
followed by an interrupted submission; the overall outcome records both facts.

## Command-line use

After the setup in the [README](../README.md), add the explicit regime to a new
local command:

```sh
.venv/bin/synthesis-route-gym plan \
  --task examples/aspirin_task.json --budget-regime unbudgeted \
  --search-policy synthchem_portfolio \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --output artifacts/reproduction/unbudgeted_fixed.json

.venv/bin/synthesis-route-gym agent \
  --task examples/aspirin_task.json --budget-regime unbudgeted --method main \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --scientist-source "$SRG_SCIENTIST_SOURCE" \
  --scientist-python "$SRG_SCIENTIST_PYTHON" \
  --profile-home /home/boltzmann6/.sci \
  --output artifacts/reproduction/unbudgeted_main.json
```

The explicit conversion retains chemistry, inventory and top-k while replacing
aggregate task ceilings. Supplying finite `--model-calls` or
`--max-frontier-states` with this conversion is rejected. Standalone condition
commands also support `--budget-regime unbudgeted`; finite action, wall, request
and token flags cannot be combined with it. Their authorized candidate pool
remains finite, and query results reveal only the requested measurements.

Python callers can construct `Budget.unbudgeted(top_k=5)` and
`AgentBudget.unbudgeted()`. A serialized unbudgeted budget must identify its
regime and include null aggregate limits. Missing or mixed limits do not imply
unlimited execution. Legacy finite task serialization remains unchanged.
The local HTTP API requires host configuration `allow_unbudgeted=True` and does
not expire an unbudgeted episode by age. Authentication and request-boundary
controls remain separate from research admission.

## Comparison and accounting

Use the frozen benchmark plans for scientific comparisons. Interactive defaults
are not a substitute for matched experimental settings. Fixed methods can finish
without consuming LLM allowance. Unbudgeted comparisons measure quality and
actual resource use; they are not equal-compute comparisons.

Request attempts and tool calls consume accounting even when they fail. Confirmed
tokens, retained reservations and unsettled requests are reported separately.
With no selected output cap, an unconfirmed provider response can have an unknown
output bound; its known input reservation is not a complete usage upper bound.
Do not interpret unconfirmed usage as zero or convert it into an invented price.
Resuming a compatible checkpoint retains consumed resources and downtime.

The [SRG-12 development design](../artifacts/steps/srg-12/development-design.md)
defines staged comparisons. Ordered decisions and receipts precede scoring.
Final reference answers stay closed until all required final decisions in both
regimes have committed. Source review, reference recovery and inventory closure
remain distinct from experimental chemical feasibility.
