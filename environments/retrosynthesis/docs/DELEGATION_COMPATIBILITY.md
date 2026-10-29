# Advanced Delegation compatibility review

Reviewed 2026-10-27. This is a source review and design recommendation, not an
installation or runtime compatibility test. No Agent Scientist profiles or
configuration were changed.

## Upstream feature

The [official catalog](https://hermes-agent.nousresearch.com/docs/plugins/advanced-delegation)
describes model-route selection (`model_map`) and profile selection
(`profile_routes`) as alternative delegation backends. It lists Hermes 0.22.5+
as the prerequisite. The reviewed plugin commit is
`e404b6816b20237a82f6fbe2749b5a576cf75dba`.

The [profile provider source](https://raw.githubusercontent.com/NousResearch/hermes-official-plugins/e404b6816b20237a82f6fbe2749b5a576cf75dba/advanced-delegation/profile_routes.py)
constructs a profile-name enum from an allowlist and returns a selected profile
to the host. Its documented semantics use that profile's model, skills, persona
and credentials. Therefore selecting a profile is not merely selecting a prompt.

The [registration source](https://raw.githubusercontent.com/NousResearch/hermes-official-plugins/e404b6816b20237a82f6fbe2749b5a576cf75dba/advanced-delegation/__init__.py)
requires `agent.delegation_provider` and
`ctx.register_delegation_provider(...)`. If the required module is missing, its
registration path logs a warning and returns without registering the feature.

The supplied social-post URL could not be retrieved. Findings rely on the
official documentation and pinned code, not an inferred reading of the post.

## Findings in the actual Agent Scientist checkout

Checkout: `/home/boltzmann6/Agent-Scientist`.
Commit: `062351dd048c142840f78ea198f22417d983ccda`.

| Capability | Source evidence | Finding |
|---|---|---|
| Native child delegation | `tools/delegate_tool.py` and `website/docs/user-guide/features/delegation.md` | Existing child contexts, structured task output and lifecycle management |
| Plugin-facing lifecycle | `sci_cli/plugins.py:394`, `agent/subagent_lifecycle.py` | `ctx.subagent_lifecycle` exposes launch/status/wait/cancel/result/reconnect |
| Hermes delegation-provider module | File/identifier inspection | Required `agent.delegation_provider` module not found |
| Hermes provider registration hook | `PluginContext` source and dynamic registrar list | `register_delegation_provider` not found |
| Per-launch profile selection | `SubagentLaunchRequest` fields | No `profile` field; accepting a `model` field is not profile switching |
| Execution roles | `agent/subagent_lifecycle.py:224` | Only `leaf` and `orchestrator`; chemistry role names belong in our registry/metadata/instructions |
| Tool restriction | `agent/subagent_lifecycle.py:398` | Allowed toolsets must be known and may not broaden the parent's permissions |
| Existing profile execution | `website/docs/user-guide/features/kanban-worker-lanes.md` | Kanban profile workers run through `sci -p <assignee>`; this is a distinct worker flow |
| Child runtime resolution | `tools/delegate_tool_config.py:482` | Configured overrides and fallback rules exist; parent-model inheritance alone is not a sufficient main-profile lock |

The direct Hermes plugin is therefore not a verified drop-in extension for this
checkout. Its required registration interface is absent. Common ancestry and
similar configuration names do not establish API compatibility. In particular,
existing `gateway.profile_routes` concerns incoming chat routing, not this
delegation backend.

## Recommended design for this project

Use the profile-style idea of named specialist configurations while preserving
the user's single-main-model policy. Start by evaluating the existing public
Agent Scientist lifecycle API; do not replace working metering until a native
adapter passes the same invariants.

Proposed specialist registry:

| Name | Instructions and relevant tools | Required output |
|---|---|---|
| `retrosynthesis_strategist` | Search alternatives, inventory obligations and expansion tools | Bounded next-action plan and unresolved branches |
| `condition_scientist` | Applicable condition model, source retrieval and measured replay observations | Candidate choices, evidence/domain checks and next observation request |
| `route_critic` | Route validation and accessible evidence | Step-specific findings and requested revisions |

These are proposed role presets. They are not already-created native profiles,
and using them with the current lifecycle API would not implement full Hermes
cross-profile execution. All children should be leaves initially; only the
main controller decides whether another specialist is useful.

The host must resolve the main profile's model/provider for each episode and
validate actual child routing before its first model request. A differing model,
provider or unauthorized fallback must fail closed. Auxiliary model calls also
need the same policy. Credentials remain managed by Agent Scientist rather than
copied into role files.

Expose only approved environment tools to research children. Shared state lives
in the route environment and is accessed through episode/route IDs. Children
receive compact task context and return validated structured results. They do
not receive benchmark labels or unrestricted evaluator-file access.

Every child call, retry and correction consumes the parent's research budget.
Native lifecycle management is useful infrastructure but does not establish
that our aggregate token/action/deadline constraints are enforced. The current
public lifecycle has no per-launch profile argument and rejects some requested
timeout/tool-policy overrides. Its in-process handles do not survive process
restart; durable environment state and restart policy require separate design.

The Route Critic remains an optimization participant. Final source review uses
a separate context and frozen rubric; no critic verdict is promoted to ground truth.

## First integration experiment, before optimization work

1. Map the existing metered runner to the public lifecycle interface without
   changing the baseline science tools or main model.
2. Check main-model/provider enforcement, narrow tool access, shared-state
   identity, output validation, cancellation and aggregate budget accounting.
3. Run a bounded smoke task through both runners and compare behavior, recorded
   resources and failure reporting. This tests integration, not specialist value.
4. Retain the current runner if the native path cannot enforce a required
   invariant. Diagnose the gap before changing the experimental system.
5. Decide whether full native-profile routing adds useful capability beyond role
   presets. If needed, implement and test the missing host integration separately;
   do not claim that installing the upstream plugin supplies absent core support.
6. Only then run the planned specialist ablations at matched resources.

This adds a compatibility gate before SRG-03/SRG-11 in
[OPTIMIZATION_PLAN.md](OPTIMIZATION_PLAN.md). It does not demonstrate that
profiles, native children or additional agents improve chemical decisions.
