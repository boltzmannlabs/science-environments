# Retrosynthesis 0.1.0

A local synthesis workspace for Agent Scientist: generate, import, validate,
revise and compare routes against a target, inventory and declared constraints.
Agent Scientist keeps its existing retrosynthesis tools and skills and chooses
its own workflow. The environment adds a common route record, feedback,
evidence labels and resource accounting; it does not replace the orchestrator.

The **base release** and the completed scientific evaluation are separate
milestones. Full benchmarking is deferred while the base integration is prepared.
No general route-feasibility, specialist-benefit or experimental-success claim is
made. See the [base release contract](docs/BASE_RELEASE.md) and
[execution tracker](docs/PROGRESS.md).

**Status:** Implemented; renamed installation and integration checks passed locally (see [migration verification](results/MIGRATION_VERIFICATION.md)).
Scientific comparative validation and maintainer review remain pending.

**Tracking:** [issue #14](https://github.com/boltzmannlabs/science-environments/issues/14).
Owner: Synthetic Chemistry pod (Gopi Krishna). Maintainer and chemistry-SME reviewers remain unassigned. This broader base implementation is related to issue #14; it does not claim that the issue is complete.

The environment folder and installed distribution are named `retrosynthesis`.
The Python namespace `synthesis_route_gym`, legacy `synthesis-route-gym` command,
`srg_action` tool and versioned `srg-*` schemas remain compatible.
The `retrosynthesis` command is the new CLI entry point.

- [Environment specification](ENVIRONMENT_SPEC.md)
- [Configuration](config/README.md) and [task contracts](tasks/README.md)
- [Research notes](../../research/retrosynthesis/research-notes.md) and [references](../../research/retrosynthesis/references.md)
- [Validation status](results/README.md) and [historical snapshot](STATUS.md)
- [Managed LocalRetro setup and evidence](results/LOCALRETRO_SETUP.md)

## Install and run a local example

For a server that already has the REBOLT LocalRetro model and its compatible
Python runtime, install the model assets, skill and Agent Scientist plugin in
one command from this directory:

```sh
python3 scripts/setup_retrosynthesis.py install
```

The installer finds the existing local REBOLT copy on this server, verifies the
checkpoint and all three template hashes, copies the needed assets into the
Agent Scientist profile, installs the chemistry package if needed and enables
the plugin. Start a new `sci` conversation afterward. A different machine can
pass `--existing-rebolt-root` and `--existing-rebolt-python` when it already has
the same approved assets and compatible runtime. See the
[integration guide](integrations/agent_scientist/README.md) for details.

The checkpoint and templates are not distributed in this GitHub repository.
Their provenance and redistribution terms need review before a public model
download can be offered. The installer reports missing or mismatched assets
instead of selecting a different checkpoint. It treats the separately supplied
REBOLT source code as trusted local code and refuses to enable a second copy of
the older `synthesis-route-gym` plugin alongside `retrosynthesis`.

From the repository root, with Python 3.10 or newer:

```sh
cd environments/retrosynthesis
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test,api,search]'

.venv/bin/python -m synthesis_route_gym replay \
  --task examples/applications/inventory/task.json \
  --science-config examples/applications/inventory/science-config.json \
  --actions examples/applications/inventory/actions.json \
  --output artifacts/reproduction/inventory.json
```

The inventory replay uses supplied candidate routes. It demonstrates the action
and validation contract without an LLM or a downloaded reaction model; it is not
an autonomous route-discovery result. The `process` and `biocatalysis` example
directories have the same three-file replay interface. Process prices are
illustrative; a retrieved enzyme-reaction identity does not demonstrate activity.

Run the software tests separately:

```sh
.venv/bin/python -m pytest --cov=synthesis_route_gym \
  --cov-report=term-missing --cov-fail-under=80
```

The prepared release's verification receipt records the actual tested file set,
optional dependencies and integration checks. Historical tests and receipts from
this research host are not substitutes for verification of the exported package.

## Two Agent Scientist entry points

| Entry point | Agent behavior |
|---|---|
| Normal plugin and synthesis skill | Existing tools remain available. Agent Scientist can call platform retrosynthesis, run a local search, import candidates, inspect findings and choose the next action. |
| Controlled benchmark runner | A dedicated conversation receives only the frozen environment tools for that run. It chooses actions inside the declared experimental contract. |

The normal plugin registers `srg_action`; it does not disable other toolsets or
launch a replacement LLM. Follow the [integration guide](integrations/agent_scientist/README.md)
for runtime configuration and the [synthesis skill](skills/retrosynthesis/SKILL.md)
for the intended workflow. Normal usage must select the main/default Agent
Scientist profile; this plugin does not change the running conversation's profile.
All research and specialist LLM roles use that same main-profile configuration.

Platform job submission, polling and download continue through the existing
Boltzmann tools and their skill. Import accepts only explicitly supported result
formats. A job receipt alone is not a route, a parsed route is not evidence of
experimental success, and a legacy `reference` flag cannot grant evidence authority.

The dedicated `agent` benchmark command starts a native Agent Scientist
conversation through a chemistry/runtime bridge. That runner resolves the main
profile itself and shares one ledger across the main session and any enabled
advisors. Its required native compatibility changes are distinct from ordinary
plugin use; see the integration guide before using an unpatched installation.

## Local route generation

The `plan` command runs a complete configured search. The default is the
**SynthChem A*/MCTS portfolio with LocalRetro proposals**. Other policies are
`breadth_first`, `best_first`, `synthchem_astar` and `synthchem_mcts`.
Creating a task session does not automatically start search.

In normal Agent Scientist sessions, the main-profile agent may also register
one-step precursor hypotheses with `propose_expansion`. SynthChem search can
combine these with model proposals, use them only when the model has no result,
or run agent-only. It reports unresolved intermediates for another reasoning
and search turn. `graft_route` replaces a selected intermediate preparation
using stored routes. All of these remain predicted chemistry until independently
supported. See the [integration guide](integrations/agent_scientist/README.md).

LocalRetro needs an existing compatible REBOLT checkout, checkpoint/templates
and chemistry interpreter. Supply their paths explicitly:

```sh
export REBOLT_ROOT=/path/to/REBOLT-FEATURES
export REBOLT_PYTHON=/path/to/chemistry-environment/bin/python

.venv/bin/python -m synthesis_route_gym plan \
  --task examples/aspirin_task.json \
  --search-policy synthchem_portfolio \
  --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" \
  --output artifacts/reproduction/local-search.json
```

This command uses the optional `search` dependency. The [SynthChem guide](docs/SYNTHCHEM_SEARCH.md)
describes the adapted native controller and its limits. AiZynthFinder is an
alternative proposal backend requiring its own model configuration. These
external checkpoints and assets are not bundled or automatically downloaded.
Model proposal scores are not calibrated reaction-feasibility probabilities.

## Scientific tools and applications

| Application | Available software path | Evidence limit |
|---|---|---|
| Inventory-constrained retrosynthesis | Search, route import, structural checks and inventory/quantity findings | Stock closure is separate from chemical feasibility |
| Reaction condition optimisation | Finite candidate studies, metered observations and optional predictors | Dataset/domain-specific; no new laboratory experiment |
| Impurity analysis | Existing optional local REBOLT checkpoint and route-bound reports | Hypotheses; measured impurity truth is absent |
| Process route selection | Comparable declared material costs and step counts | Illustrative examples; unknown costs remain unknown |
| Biocatalytic synthesis | Source matching and unresolved-requirement reports | No inferred enzyme activity, yield or process validation |

The [application guide](docs/APPLICATION_WORKFLOWS.md) describes the interfaces.
Historical measured-data examples and generated outputs may remain local only
when redistribution terms are unresolved; they are not required installation
inputs. The code-only export excludes raw measured tables, private evaluators,
model weights, credential files and research-run payloads.

The [existing ReactionT5v2-yield integration](docs/PUBLIC_YIELD_MODEL.md) provides
a replaceable scientific predictor when its separately supplied model manifest
and assets are configured. It predicts supplied reaction recipes; it is not a
trained route-success model and does not automatically rescore incomplete routes.
Development of a new custom model remains deferred at the user's request.
Earlier custom-model experiments and negative results remain historical records.

**Main-only remains the default agent treatment.** The Retrosynthesis Strategist,
Condition Optimisation Scientist and Route Critic are implemented experimental
roles; the completed small development studies do not establish a general benefit
from delegation. Their contracts are documented in the [Strategist](docs/STRATEGIST.md),
[Condition Scientist](docs/CONDITION_SCIENTIST.md) and [Route Critic](docs/ROUTE_CRITIC.md)
guides. [Orchestration and candidate handoffs](docs/ORCHESTRATION_HANDOFF.md) are
also available, with cross-pod scientific gains unproven.

## Evaluation status

Eight of fourteen optimization steps are accepted within their documented scope.
Step 12 has a completed 24-run fixed-policy screen and three unbudgeted fixed
runtime checks. Remaining development comparisons and final configuration
selection are deferred. Step 13's locked benchmark and blinded source review are
deferred. Step 14's essential release verification is being handled for the base
release; the wider optimization and evaluation program remains unfinished.

The later evaluation must compare the strongest fixed workflow, main Agent
Scientist and a selected specialist treatment in both matched-budget and
unbudgeted regimes. It must retain failures, negative results, actual resource
use and source-review uncertainty. [Resource regimes](docs/RESOURCE_REGIMES.md)
and the [14-step plan](docs/OPTIMIZATION_PLAN.md) define these requirements.

Older guides contain links to this host's `artifacts/` research archive. Those
links identify historical evidence and may be absent from a code-only checkout;
they must not be read as bundled test outcomes or completed release gates.
Predicted reactions, literature analogues, exact sources and measurements retain
separate labels. Automated source consistency review is not external chemist
review or experimental validation.
