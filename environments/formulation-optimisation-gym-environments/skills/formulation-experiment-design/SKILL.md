---
name: formulation-experiment-design
description: Prepare evidence-linked formulation experiment proposals and reconcile approval-bound results in formulation-optimization-gym. Use for protocol planning and intake; laboratory execution stays external.
---

# Formulation experiment design

Read `agents/experimental_design.py`, `schemas/experiment.schema.json`, `environment/actions.py` and [implementation plan](../../docs/implementation_plan.md) T07/T10. Existing contracts are a starting point; unchecked approval strings do not establish authorization.

## Prepare the proposal

Require selected case, supported question, relevant method/criteria, source-linked constraints, responsible laboratory and budget. Model-informed proposals also require applicable evaluated models. A discriminating proposal can be based on verified evidence without a predictive model.

Link hypotheses and alternative explanations to evidence and the response that would distinguish them. A recall reason is not a demonstrated cause.

Use approved factor ranges and response definitions. Include controls, replicate/randomization rationale, justified blocking, method version, uncertainty/missing-data handling, analysis/stop rules, cost/resources, candidate/protocol identifiers and reviewers. Do not invent numerical recipes, laboratory settings, replicate counts or assumed power.

Complete a reviewable proposal before any required physical-execution approval. Reuse an existing approval only within its actual scope. If only planning was requested, the completed proposal completes that task.

## Bind approval and results

For prospective physical work, require approval linked to case, candidate/protocol content or hashes, method, approver/time, validity, scope, budget and execution organization. Scope-changing revisions need a matching decision, not an unrelated reused approval ID.

The environment does not execute laboratory work. Keep proposed, approved, externally executed and results-verified events separate. Spend, regulated updates and manufacturing changes require authorization for the actual action.

After external execution, reconcile run/confirmation, `confirmed_by`, source records, units and method against the protocol. Retain individual observations and deviations. Import measured results through [data intake](../formulation-data-intake/SKILL.md); predictions cannot complete experiments.

Historical authorized records follow their own intake path and need no fabricated prospective execution events.

## Verify and deliver

Persist approval/confirmation/reviewer identities. Test mismatched case/protocol, expired/withdrawn approval, duplicate confirmation, overspend, missing source and predicted-as-measured rejection before implementing success.

Deliver proposal, approval readiness/gaps, actual external execution status, reconciliation manifest and independent findings. Without verified external execution and measurements, report a proposal rather than completed experiment or confirmed optimization.
