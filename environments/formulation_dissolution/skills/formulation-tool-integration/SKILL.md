---
name: formulation-tool-integration
description: Integrate documented authorized scientific tools into formulation-optimization-gym with typed evidence, bounded retries and auditable budgets. Use for connector contracts and orchestration.
---

# Formulation tool integration

Inspect `tools/boltzmann_adapters.py`, `configs/tools.example.yaml`, `environment/actions.py` and [implementation plan](../../docs/implementation_plan.md) T05–T06. Registry starts empty. Recheck current tools rather than assuming old report availability.

## Establish the contract

Discover tools before asking for information an available service can supply. Prefer a relevant plugin when sufficient. If Boltzmann remains locked and access is requested, use its supported masked-key authorization flow; never request a key in chat, inspect secret files or bypass access with guessed endpoints.

Record actual tool name, schema/version, scope, authentication outside the repository, processing/retention terms, limits, timeout and retry/idempotency semantics. Check destination permission before sending controlled records. Connector activation alone does not establish dissolution capability.

## Implement

- Preserve task/case/candidate/method identity and units. Validate output identity/shape, evidence type, tool/model version, sources and applicability.
- The registry currently permits predicted observations only. Add separately typed retrieval/analysis interfaces when needed; do not force measurements or arbitrary statistics into prediction contracts.
- Keep unavailable tools `tool_unavailable`. Auth, malformed response and timeout outcomes remain sanitized failures; no scientific zero or success fallback.
- Account for each actual invocation attempt/cost before dispatch; stop on budget exhaustion. Distinguish mocks from live scientific calls.
- Timeout is not cancellation. Document cancellation, quarantine late results and do not repeat unknown-outcome calls unless the actual contract guarantees safe retry. Use idempotency identifiers only when supported.
- Route approved calls through actions in `run.py`, persist provenance and resume without duplicate calls. Accepting adapters without invoking them does not implement orchestration.
- Use state copies/new objects for scientific transitions and preserve previous state on validation failure. Keep secrets/confidential payloads out of user-facing errors.

## Verify and deliver

Test unavailable tool, success, auth failure, invalid units/identity, malformed output, timeout/late completion, retry safety and attempt-level budget exhaustion with documented mocks first. An authorized live read-only contract check does not validate scientific accuracy.

Deliver capability/contract matrix, implementation paths, checks run, actual live calls/costs and unresolved gaps. Claim live integration or benefit only after observing it. Manufacturing execution, spending and regulated writes are not incidental integration features.
