# Base release 0.1.0

Owner: environment/integration maintainer. This is the software release contract
for a local GitHub-update candidate. The user has deferred full scientific
benchmarking until after the base version is reviewed and updated. Preparation
is local only: a commit or push requires the user's explicit instruction, and no
deployment is included.

## What the base release provides

Agent Scientist remains the decision maker. Its existing retrosynthesis tool,
platform skills and other permitted tools remain available in normal usage.
The environment is an optional synthesis workspace and local search capability.
It records target/inventory tasks, candidate routes, validation findings,
evidence labels, revisions, resource use and final submissions.

Normal workflow:

1. Create an environment task from target, inventory and constraints.
2. Let Agent Scientist select existing platform tools or a local search policy.
3. Parse results through an explicitly supported route-import format, or store
   a canonical route proposal. Retain source job identity and unknown values.
4. Inspect inventory, graph, quantity and evidence findings; revise the workflow
   or candidate routes where useful.
5. Rank and submit route IDs with their unresolved requirements.

A route's presence, a job's completion and deterministic validation do not prove
experimental feasibility. Imported predictions cannot acquire literature or
experimental authority from a legacy flag or an agent explanation.

The normal `srg_action` plugin and the controlled `agent` benchmark command are
separate entry points. The plugin adds an optional toolset to ordinary Agent
Scientist. The benchmark runner deliberately isolates the permitted actions for
a matched comparison; installing the plugin does not apply that restriction to
ordinary conversations.

## Portable source installation

Use a fresh virtual environment for this renamed distribution. For an existing
installation, uninstall the old `synthesis-route-gym` distribution before
installing `retrosynthesis`: both own the `synthesis_route_gym` Python namespace
and legacy command. Keep existing task files and externally configured assets.

From `environments/retrosynthesis` in the repository, with Python 3.10 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test,api,search]'
.venv/bin/python -m synthesis_route_gym --help
.venv/bin/python -m pytest --cov=synthesis_route_gym \
  --cov-report=term-missing --cov-fail-under=80
```

Linux is the verified platform for the live subprocess integration. Other
platforms do not have an equivalent tested parent-death cleanup guarantee; the
portable source/demo checks and the live scientific-runtime requirements are
separate.

The `search` extra pins the native Syntheseus engine. LocalRetro, AiZynthFinder,
ReactionT5-yield and impurity checkpoints have separately configured scientific
runtimes and assets; installation does not download them. Missing predictors
must report unavailable status, not manufacture chemistry or use another LLM.

The normal plugin must be configured through trusted host settings so Agent
Scientist can call the chemistry runtime even when its own interpreter lacks
RDKit. See [the integration guide](../integrations/agent_scientist/README.md) for
the exact settings and supported actions. Model-supplied action arguments cannot
choose an arbitrary interpreter, source directory or executable.
The optional trusted `SRG_BACKEND_TIMEOUT_SECONDS` setting defaults to 120,
accepts finite positive values up to 3595 seconds, and gives the outer expansion
registry five additional seconds for worker cleanup. It is a per-call backend
timeout, not a research cap. The host forwards the actual `HOME` for library
caches, but not provider secret environment variables. The subprocess is trusted
scientific code, not a filesystem sandbox.

All research LLM sessions use the Agent Scientist main/default profile. The
normal plugin does not select a model or change an already running conversation;
launch ordinary Agent Scientist with the main profile. The dedicated benchmark
runner resolves the main profile itself and disallows alternate-model fallback.
Its native runtime compatibility requirements are documented separately.

## Examples without external models or LLM access

Run the offline synthetic base demonstration first:

```sh
.venv/bin/python examples/base_demo.py
```

Its values and predictions are synthetic software fixtures; it performs no LLM
call, model download or laboratory experiment. Run an inventory replay:

```sh
.venv/bin/python -m synthesis_route_gym replay \
  --task examples/applications/inventory/task.json \
  --science-config examples/applications/inventory/science-config.json \
  --actions examples/applications/inventory/actions.json \
  --output artifacts/reproduction/inventory.json
```

Use the same command with the `process` or `biocatalysis` directory and a new
output filename. These replays exercise supplied routes and records, not new
route discovery. Process values are illustrative; biocatalytic source identity
is separate from measured activity or a validated process.

Condition optimisation has a finite-study/replay interface and optional
scientific predictors. Impurity analysis has route-bound reports and an optional
existing local checkpoint. Measured condition tables, model weights and prior
run outputs may be local-only assets. Never relabel synthetic release fixtures
as measured experiments. See [application contracts](APPLICATION_WORKFLOWS.md)
for the five implemented application interfaces and their evidence limits.

## Route generation and imported results

`plan` defaults to breadth-first search with LocalRetro proposals. Best-first,
SynthChem A*, SynthChem MCTS and SynthChem portfolio are selectable. A new session
does not automatically run a fixed search. In normal use the agent chooses when
to call a search and whether to combine it with existing tools.

The import API accepts only declared schemas. It must preserve precursor
obligations and target identity, reject malformed or unsupported inputs, and
record provenance without upgrading predictions. The platform's submit/status
adapter is not by itself an end-to-end route import. A remote platform job is
not claimed tested unless a specific completed artifact and execution receipt
support that claim. See the integration guide for available import formats.

## Release contents and exclusions

Prepare a positive file allowlist. The parent REBOLT working tree contains
unrelated changes, so blanket staging or copying is inappropriate. Include the
package source, tests, documented integration/skill files, permitted examples,
required third-party notices and small audited test-driver scripts.

Exclude virtual environments, caches, build leftovers, credentials, `.env`
files, private/final evaluator answers, model checkpoints, source snapshots,
provider logs, local runtime records and large research artifacts. Raw measured
tables with unresolved redistribution terms are excluded. Do not assign an
open-source license to project code without owner authorization; preserve the
required notices for adapted dependency code.

Historical guides may link into `artifacts/`. Those are local research evidence
references, not required installation assets or guaranteed bundled release
results. The exported package's own file manifest and verification report
determine what was included and tested.

## Base-release verification gate

Before describing the package as ready for the user's GitHub update:

- Build a wheel and verify installation/imports from the prepared source copy.
- Run unit, integration and end-to-end software checks with at least 80% coverage.
- Exercise normal-session tool registration, profile/session isolation,
  chemistry-runtime bridging, supported route import and explicit local search.
- Verify malformed inputs, unknown/expired sessions, missing scientific assets,
  finite budgets and explicit unbudgeted execution without a hidden session TTL.
- Verify existing Agent Scientist tools remain registered and the main-profile
  configuration remains untouched.
- Inspect the exact file allowlist for secrets, private data, oversized assets
  and required attribution; preserve prior research receipts unchanged.
- Record test commands/results, version identities, external requirements and
  unresolved limitations in the release verification report.

Injected predictions test the software contract and must be labelled as such.
They do not count as actual model inference or scientific benchmark wins. The
normal plugin cannot measure the total LLM use of arbitrary external workflows;
only its own recorded environment actions are within that accounting boundary.
Controlled benchmark ledgers have their separately defined shared accounting.

Linux direct scientific workers arm `PDEATHSIG=SIGKILL` and recheck the parent
to close the startup race. Explicit timeout cleanup also kills the worker group.
This is not a recursive cleanup guarantee for arbitrary future descendants or
an immediate-termination guarantee during uninterruptible kernel I/O. The normal
runtime diagnostic retained its first timeout failure; a later explicitly timed
BFS/LocalRetro draft/import/validate/rank/submit check completed. Portfolio and
full-release results remain separate verification items, not inferred successes.

## Deferred scientific work

The optimization tracker remains at 8/14 accepted steps. Step 12 has implemented
both resource regimes, a completed 24-run fixed development screen and three
naturally completed unbudgeted fixed runtime checks. Its remaining agent and
specialist comparisons, model on/off studies and final configuration freeze are
deferred. Step 13's held-out benchmark and blinded source review are deferred.
Step 14's essential software release checks happen now; the wider performance,
reproducibility and scientific-report gate remains open. Runtime source has
changed for this base release, so historical Step 12 freezes remain records of
their original version and must be replaced by a new prospective freeze before
resuming comparisons. Do not edit old freezes or call new-runtime runs identical
to the earlier frozen experiments.

The later benchmark still requires strongest fixed, main Agent Scientist and
selected specialist configurations, in both matched-budget and unbudgeted
regimes. Final outcomes remain sealed until the required decisions are committed.
Failures, resource use, negative findings and uncertainty must be reported.

Main-only remains the default treatment. Specialist software is experimental;
scientific benefit from delegation and cross-pod handoffs is unproven. The existing
pretrained yield predictor is a scientific tool. A new custom scientific model is
deferred by the user, and its original improvement requirement is not silently
satisfied by packaging or by an existing model.
