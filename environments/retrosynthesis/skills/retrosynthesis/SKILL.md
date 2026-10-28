---
name: retrosynthesis
description: Use a shared synthesis workspace to generate, import, validate and compare inventory-constrained routes while retaining Agent Scientist's existing chemistry tools.
---

Use Agent Scientist's main/default profile for every research and specialist LLM
role. This skill adds an environment to normal chemistry workflows; it does not
replace existing retrosynthesis tools or require a fixed sequence of tools.

## Normal Agent Scientist workflow

Use the supplied target, inventory, constraints and resource regime. Create a
session through `srg_action` and retain its returned session ID. Inspect state
before choosing the next action. Existing platform submission, polling, download
and chemistry protocols remain governed by their existing skills and permissions.

Choose the appropriate route-generation source: existing platform retrosynthesis,
the environment's configured local search, or explicit incremental expansions.
The CLI local-search default is breadth-first with LocalRetro proposals;
SynthChem A*, MCTS and portfolio are selectable. Creating a session does not
start search. Do not assume a scientific backend exists just because a tool is
registered: preserve unavailable/error results and explain missing configuration.

Use the normal plugin's supported `import_routes` contract for an existing tool's
completed route artifact. A job ID or completion status alone is not a route.
Select an explicit supported format; do not invent parser fields or silently
accept an unknown payload. Preserve all precursor obligations, repeated materials
and convergent branches. Imported route predictions retain their provenance but
cannot acquire evidence authority from a legacy `reference` flag.

Store canonical proposals with `propose_route`, inspect their findings and use
`validate` before submission. Revise with new route identifiers and explicit
parent identity. Missing starting materials, quantities, co-reagents, conditions
or evidence remain unresolved; do not hide them by dropping a branch or material.
Use the current tool schema for exact action names and argument contracts.

Use `predict_conditions` only for supplied chemical-role structures in the
configured predictor's domain. An optional reaction-yield tool predicts supplied
recipes, not general route feasibility. Use `rank_routes` to compare stored route
IDs; the score is a declared surrogate, not an overall yield or calibrated
probability of success. Report the weakest step and unresolved constraints.

Keep predicted reactions, analogous literature reactions, exact source records
and experimental observations distinct. An agent explanation is not independent
chemical review. Unknown yield, cost, availability and source support stay unknown.

Specialists are optional and experimental. Consult them only when permitted and
applicable; they advise while the main agent owns decisions. They use the same
main-profile LLM. Do not describe consultation or successful submission as proof
that delegation improves chemistry. In normal usage, the environment's action
ledger does not account for every LLM or external-tool call in an arbitrary
Agent Scientist workflow; report that boundary explicitly.

Submit route IDs through the environment; final prose alone is not a submission.
An empty or incomplete result is valid to report when no qualifying route is
available. Preserve failed actions, unresolved evidence and resource consumption.

## Controlled benchmark runs

When invoked through the dedicated benchmark runner, follow its supplied tool
schemas, evidence permissions and shared resource contract. Do not use tools
outside that run's allowlist, read evaluator files, invent hidden labels or reset
an episode to replenish allowance. Normal access to other skills does not override
a declared benchmark protocol. These restrictions apply to that benchmark
conversation, not to ordinary Agent Scientist sessions.

All specialist attempts and retries share the declared finite ledger in budgeted
runs. Unbudgeted runs remove aggregate research ceilings while retaining usage
records, task definitions and infrastructure restrictions. An external interruption
is not natural completion. Retain negative findings; keep main-only as the default
unless a properly controlled comparison justifies a specialist treatment.
