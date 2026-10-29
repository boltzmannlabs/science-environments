# Agent Scientist integration

The normal plugin adds `srg_action` alongside Agent Scientist's existing
retrosynthesis tools and skills. It does not replace the conversation, disable
other toolsets or instantiate another LLM. Agent Scientist chooses its own
workflow and uses the environment when appropriate.

The dedicated benchmark runner is separate: it intentionally restricts tools
and shares a research ledger for a controlled comparison. Installing this plugin
does not impose that restriction on ordinary conversations.

## Normal plugin setup

The recommended setup on a machine with the existing LocalRetro assets and
runtime is one command from the environment root:

```sh
python3 scripts/setup_retrosynthesis.py install
```

This installs the plugin and skill in the main Agent Scientist profile, copies
the four verified model inputs into that profile and enables the plugin. It
stores the trusted runtime paths in the profile plugin's private `runtime.json`.
Restart Agent Scientist after installation. The model is not embedded in the
public source release. On another machine with an approved REBOLT copy, use
`--existing-rebolt-root` and `--existing-rebolt-python` to select it. The
installer rejects missing or digest-mismatched assets.

The settings below remain available for operators who manage their own
scientific runtime or need an explicit override.

Install the gym and chemistry dependencies in a Python 3.10+ environment using
[the base release guide](../../docs/BASE_RELEASE.md). The plugin itself imports
only Python's standard library. It starts a persistent local chemistry process
on the first normal tool call, so Agent Scientist's interpreter need not have
RDKit or the chemistry package.

Set trusted operator environment variables before starting Agent Scientist:

```sh
export SRG_PACKAGE_ROOT=/absolute/path/to/science-environments/environments/retrosynthesis
export SRG_CHEMISTRY_PYTHON="$SRG_PACKAGE_ROOT/.venv/bin/python"

# Optional: existing LocalRetro source, checkpoint/templates and model runtime.
export REBOLT_ROOT=/absolute/path/to/REBOLT-FEATURES
export REBOLT_PYTHON=/absolute/path/to/model-environment/bin/python

# Optional operator override; defaults to 120 seconds per backend request.
export SRG_BACKEND_TIMEOUT_SECONDS=120
```

`SRG_PACKAGE_ROOT` locates this checkout's `src/` when the plugin is copied
elsewhere. It can be omitted if the package is installed in the selected
chemistry interpreter. `SRG_CHEMISTRY_PYTHON` must be an absolute executable path;
without it the plugin tries the current Agent Scientist interpreter, which may
lack chemistry dependencies. This is the gym runtime, not necessarily the heavy
checkpoint interpreter. `REBOLT_ROOT` configures LocalRetro. Without that backend,
manual proposals/imports remain useful and expansion reports unavailable.
These are host settings, never model-generated tool arguments.
`SRG_BACKEND_TIMEOUT_SECONDS` must be finite, greater than zero and no more than
3595 seconds. The adapter uses that timeout, and the outer expansion registry
allows five additional seconds so the adapter can kill and drain its worker
first. This is a per-call operational timeout, not an aggregate research budget.

Use Agent Scientist's local plugin workflow to install this directory as
`retrosynthesis`, or place a reviewed copy under the main profile's
`plugins/retrosynthesis` directory and enable it with the installed plugin
controls. When migrating, disable the old `synthesis-route-gym` environment plugin before
enabling `retrosynthesis`; both register the same `srg_action` tool. Preserve
unrelated chemistry tools. Restart the conversation after activation. Enable the
[synthesis skill](../../skills/retrosynthesis/SKILL.md) alongside the existing
platform chemistry skill. Credentials stay in the ordinary Agent Scientist
profile; do not copy authentication files into tasks or plugin artifacts.

Launch ordinary Agent Scientist with its main/default profile. This plugin does
not change an active conversation's model/provider. Every research and specialist
LLM role must use that main-profile configuration. The chemistry host makes no
LLM calls. The actual `HOME` is forwarded for scientific-library caches; provider
secret environment variables are not forwarded. This trusted-code subprocess
is not a filesystem sandbox against a malicious scientific backend.

## Normal session actions

Create a session with:

```text
srg_action(action="reset", arguments={"task": <Task JSON>, "seed": 0})
```

Retain the returned `session_id` for subsequent calls. Sessions belong to the
calling profile. Finite sessions expire at the declared task wall limit;
explicitly unbudgeted sessions have no age-based TTL. Call `close` to release one.
Sessions are in memory and are lost when the plugin/chemistry process restarts.
The persistent benchmark checkpoints do not provide normal-plugin recovery.

| Action | Arguments and behavior |
|---|---|
| `inspect` | Inspect the same task, routes, findings and resources. |
| `generate_routes` | SynthChem portfolio by default; optional `search_policy`, `proposal_mode`, `expansion_top_k`, and budgeted `max_frontier_states`. Returns drafts and unresolved intermediate products without submitting. |
| `propose_expansion` | Register bounded, exact-product, one-step main-agent precursor hypotheses. The action is metered; source and evidence authority are assigned by the host. |
| `graft_route` | Replace one exact intermediate preparation in a stored parent route using a stored donor route; keep both originals and inspect the new revision. |
| `import_routes` | Required `format` and `payload`; optional `provenance`; convert supported completed artifacts into predicted candidates. |
| `propose_route` | Store a canonical `route` proposal or explicit revision. |
| `validate` | Check an existing `route_id` against graph, inventory and constraints. |
| `rank_routes` | Compare stored `route_ids`, preserving unknown values. |
| `submit` | Submit ordered `route_ids` selected by the main agent. |
| `close` | No arguments; release the session. |

Existing environment actions remain exposed. A registered action does not imply
every optional predictor, evidence catalog or condition study is configured.
The normal host currently configures LocalRetro through the trusted settings
above. Advanced scientific configurations have explicit CLI/Python interfaces;
do not invent normal-tool arguments for them. Follow current capability/error
responses and the tool schema.

Search policies are `synthchem_portfolio` (default), `synthchem_astar`,
`synthchem_mcts`, `breadth_first` and `best_first`; SynthChem requires the `search` extra.
For SynthChem search, `proposal_mode` can be `hybrid` (default), `agent_fallback`,
`agent_only` or `model_only`. Agent hypotheses are entered through
`propose_expansion` by the main Agent Scientist conversation. The chemistry
host does not start a separate LLM. A missing model can be handled with an
explicit agent hypothesis, and `unresolved_products` identifies intermediates
that need more work before another search. Repeated searches share the session's
resource ledger. Only successful, same-session proposal events feed the pool.
`expansion_top_k` is 1–100. An unbudgeted search rejects an explicit
`max_frontier_states`. Creating a session does not start search.

`generate_routes` returns `submitted=false`. It may produce incomplete drafts,
no candidates, a budget stop or an explicit `backend_failure`. A failed backend
is not silently reported as successful empty chemistry. The main agent can inspect
and revise in the same session, then submit explicitly. Another search does not
reset consumed resources.

## Existing platform retrosynthesis results

Keep using the existing Boltzmann skill for discovery, submission, polling and
download. This plugin does not silently submit remote jobs, fetch URLs or change
those tools' authentication/execution policies. Import a parsed completed
artifact with one of the explicit formats:

- `srg-route-candidates-v1`: a list of canonical `RouteCandidate` objects.
- `rebolt-scored-paths-v1`: supported REBOLT `topN` entries with `path` and `idx`,
  where `path` contains the nested `rd3t` route tree. Other historical output
  shapes are not implicitly supported.

Optional provenance carries bounded identifiers such as `job_name`, `doc_id`,
`artifact_id` and `source_version`. Do not pass credentials, signed URLs or
private payloads as provenance. The import report retains input identity and
warnings. Imported `reference` flags, asserted evidence IDs, predicted yields
and aggregate legacy costs do not become evidence authority or measurements.
Required branches and target identity must survive conversion; unsupported or
malformed inputs are rejected rather than guessed.

A completed job is not itself a route, and an imported candidate is still a
prediction. Inventory, quantities, constraints and source support remain separate
checks. Partial storage from exhausted action resources is reported with
`complete=false`; inspect returned observations and route IDs. Import never
submits a final decision. Support for a real output format is not a claim that
a new remote platform submission/download cycle was executed for this release.

## Accounting and operational limits

Environment actions follow the supplied task regime. The normal plugin does
not measure every LLM/external-tool call in an arbitrary Agent Scientist workflow;
its ledger is not complete end-to-end workflow cost. Use the dedicated runner
for a controlled shared-ledger experiment.

The transport bounds requests to 4 MB and replies to 16 MB. Host session capacity
and per-backend infrastructure limits remain explicit in unbudgeted research.
A crash loses sessions and reports failure rather than natural completion.
Profiles cannot use another profile's session IDs. Model arguments cannot
choose interpreters, source directories or arbitrary executables.

The subprocess integration is verified on Linux. Direct scientific workers arm
Linux `PDEATHSIG` with `SIGKILL`, then check the expected parent again to close
the startup race. The existing explicit timeout still kills the worker process
group. On other platforms the guarded bootstrap skips this Linux mechanism;
no equivalent parent-death cleanup or Windows integration is claimed. This does
not guarantee cleanup of arbitrary future descendant processes or immediate
termination during kernel uninterruptible I/O.

## Dedicated benchmark runner and native compatibility

`run_agent_scientist` and `run_agent_scientist_bridge` start controlled native
conversations. They resolve `model.default` and `model.provider` from the
main/default profile's `config.yaml`, ignore a different active profile, and
provide no alternate-model fallback. They expose only supplied experimental
tool schemas and remove only their own temporary registrations afterward.
Do not attach hidden evaluation data or arbitrary filesystem/terminal tools.

The benchmark adapter passes `unbudgeted_run` to native `AIAgent`. A version
without that argument is incompatible even for finite benchmark runs. The
bundled compatibility patch is:

`compatibility/agent-scientist-unbudgeted.patch`

It targets Agent Scientist commit
`062351dd048c142840f78ea198f22417d983ccda`, with SHA-256
`0b40dce9ceef4fd2b6592ff6c9bd48b517e1e107b01ab3f42c543480a7afc868`.
Review it and check applicability before applying in a compatible checkout:

```sh
git -C "$SRG_SCIENTIST_SOURCE" apply --check \
  "$SRG_PACKAGE_ROOT/integrations/agent_scientist/compatibility/agent-scientist-unbudgeted.patch"
git -C "$SRG_SCIENTIST_SOURCE" apply \
  "$SRG_PACKAGE_ROOT/integrations/agent_scientist/compatibility/agent-scientist-unbudgeted.patch"
```

Do not apply it twice or force it onto another version. It adds native
absent-ceiling/finalization support; it does not select a model or authenticate
an account. **Normal plugin use does not require this patch**, because the
plugin does not instantiate `AIAgent`.

The benchmark bridge separates the chemistry and native Python runtimes.
Specialist attempts and retries share its ledger. Confirmed tokens, retained
reservations and unknown usage stay distinct. Specialists cannot reset or submit
the shared episode. Unbudgeted execution removes aggregate research ceilings and
budget-triggered finalization while preserving operational/evidence restrictions.

Main-only remains default. Optional specialist modes have separate contracts;
successful consultation or submission does not establish benefit from delegation.
The native profile itself is unchanged by the benchmark adapter.

## Verification

The discovery script uses temporary profiles and no model calls:

```sh
"$SRG_SCIENTIST_PYTHON" integrations/agent_scientist/verify_discovery.py \
  --scientist-source "$SRG_SCIENTIST_SOURCE"
```

This verifies registration and bound dispatch, not an entire chemistry workflow.
The prepared release's verification report records normal-session host checks
and actual scientific executions separately. Synthetic predictions and injected
dispatchers are contract tests, not real model inference or benchmark wins.
Historical `*-smoke.json` files may remain local research artifacts and are not
required runtime inputs or guaranteed files in a code-only export.

## Backend diagnostic history

The initial normal-runtime diagnostic retained a failure caused by the outer
60-second scientific timeout expiring before the adapter's 120-second timeout
under slow dependency loading. That attempt and its cleanup findings remain
recorded rather than being replaced by a later successful attempt.

The follow-up diagnostic explicitly declared a 300-second backend timeout,
305-second outer timeout, 600-second task limit and two permitted expansions on
CPU. This diagnostic setting is not a recommendation to use 300 seconds for
every task and does not alter the default 120-second backend setting. The normal
Agent Scientist runtime → chemistry host → actual LocalRetro → breadth-first
draft generation → import → validation → ranking → explicit submission path
completed on this server. Final portfolio outcomes and release verification are
recorded separately; this diagnostic does not establish full-release readiness,
autonomous-workflow superiority or a completed scientific benchmark.
