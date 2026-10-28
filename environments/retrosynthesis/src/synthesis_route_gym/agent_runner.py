"""Agent Scientist execution using only the main profile and bounded environment tools.

Scientific evaluation lives outside the agent. The injected executor is the only
environment access given to the model; no terminal, file, web or evaluator tools
are exposed. Native execution requires the installed Agent Scientist runtime.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from threading import RLock
import time
from typing import Callable
from uuid import uuid4

from .agent_accounting import AgentBudget, BudgetExhausted, CheckpointError, SharedLedger
from .agent_transport import GuardedClient, WireGate, unwrap_client


from .scientific_execution import SCIENTIFIC_ACTIONS, APPLICATION_ACTIONS

ACTIONS = SCIENTIFIC_ACTIONS | APPLICATION_ACTIONS | frozenset({"reset", "inspect", "propose_route", "validate", "submit", "rank_routes", "review_routes", "capabilities"})
_BOUND_EXECUTOR: ContextVar[Callable | None] = ContextVar("srg_executor", default=None)
ROLE_INSTRUCTIONS = {
    "retrosynthesis_strategist": "Compare disconnections, unresolved precursors and inventory-constrained alternatives.",
    "condition_optimisation_scientist": "Assess condition evidence and missing measurements; never invent yields or experimental support.",
    "route_critic": "Challenge atom provenance, stereochemistry, constraints and each route's weakest step. Keep exact evidence distinct from analogies.",
    "main": "Choose and submit routes using the available environment tools. Retain uncertainty and evidence provenance.",
}


class RuntimeContractError(RuntimeError):
    """The host exposed a forbidden capability or changed the configured provider."""


@dataclass(frozen=True)
class MainProfile:
    home: Path
    model: str
    provider: str


def resolve_main_profile(profile_home: str | Path | None = None) -> MainProfile:
    """Read main/default directly; never follow the sticky active_profile file."""
    try:
        from sci_yaml import safe_load
    except ImportError:
        from yaml import safe_load

    home = Path(profile_home).expanduser().resolve() if profile_home else Path.home() / ".sci"
    config = safe_load((home / "config.yaml").read_text(encoding="utf-8"))
    model = config.get("model", {}) if isinstance(config, dict) else {}
    if not isinstance(model, dict):
        raise ValueError("Main profile requires explicit model.default and model.provider")
    name, provider = model.get("default"), model.get("provider")
    if not all(isinstance(value, str) and value.strip() for value in (name, provider)):
        raise ValueError("Main profile requires explicit model.default and model.provider; no fallback is permitted")
    return MainProfile(home, name.strip(), provider.strip())


@contextmanager
def bind_executor(executor: Callable[[str, dict], dict]):
    token = _BOUND_EXECUTOR.set(executor)
    try:
        yield
    finally:
        _BOUND_EXECUTOR.reset(token)


def dispatch_bound_action(action: str, arguments: dict):
    if action not in ACTIONS:
        raise ValueError(f"Action {action!r} is not allowed")
    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    executor = _BOUND_EXECUTOR.get()
    if executor is None:
        raise RuntimeError("No environment executor is bound to this session")
    return executor(action, arguments)


def has_bound_executor():
    """Whether the caller has explicitly attached a benchmark environment."""
    return _BOUND_EXECUTOR.get() is not None


def _validated_schemas(tool_schemas):
    names = [schema.get("name") for schema in tool_schemas]
    if not names or len(set(names)) != len(names):
        raise ValueError("Provide non-empty, unique environment tool schemas")
    for schema in tool_schemas:
        if schema.get("name") not in ACTIONS:
            raise ValueError(f"Tool {schema.get('name')!r} is not allowed")
        if not isinstance(schema.get("parameters"), dict):
            raise ValueError("Each tool needs a parameters JSON schema")
    return json.loads(json.dumps(tool_schemas))


def sanitize_run_artifact(value):
    """Copy public results without provider-opaque encrypted reasoning blobs."""
    if isinstance(value, dict):
        return {key: sanitize_run_artifact(item) for key, item in value.items()
                if not isinstance(key, str) or key.lower() not in {"encrypted_content", "encrypted_reasoning", "encrypted_reasoning_content"}}
    if isinstance(value, (list, tuple)):
        return [sanitize_run_artifact(item) for item in value]
    return value


def _usage_totals(runs):
    fields = ("input_tokens", "output_tokens", "total_tokens", "estimated_cost_usd")
    return {key: (sum(run["usage"][key] for run in runs)
                  if all(run.get("usage", {}).get(key) is not None for run in runs) else None)
            for key in fields}


def _compact_report(result, role, limit):
    text = result.get("final_response", "")
    text = text if isinstance(text, str) else ""
    return {"role": role, "completed": bool(result.get("completed")),
            "summary": text[:limit], "truncated": len(text) > limit,
            "evidence_status": "agent_proposal", "error_type": result.get("error_type")}


def _runtime_binding(prompt, schemas, profile, mode, limits, orchestration_policy=None):
    payload = {"prompt": prompt, "schemas": schemas, "model": profile.model,
               "provider": profile.provider, "profile_home": str(profile.home),
               "mode": mode, "budget": asdict(limits)}
    if orchestration_policy is not None:
        payload = {**payload, "orchestration_policy": orchestration_policy}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def run_agent_scientist(prompt, executor, *, tool_schemas, budget=None, mode="main",
                        profile_home=None, backend=None, resume_state=None, checkpoint=None,
                        orchestration_policy=None):
    """Run bounded roles and persist admissions before external effects.

    Resume restarts only an interrupted stage, retaining all consumed resources
    and unknown request reservations. Downtime counts against the fixed deadline.
    Checkpoints are host-private; they never become a research tool observation.
    """
    orchestrated = mode in {"main_role_prompt", "main_all_advisors", "main_adaptive"}
    if not orchestrated and mode not in {"main", "specialists", "main_strategist", "main_condition_scientist", "main_route_critic"}:
        raise ValueError("Unknown Agent Scientist execution mode")
    if orchestration_policy is not None and not orchestrated:
        raise ValueError("Orchestration policy requires an orchestration mode")
    if orchestrated:
        from .orchestration import normalize_policy
        orchestration_policy = normalize_policy(mode, orchestration_policy)
    if not isinstance(prompt, str) or not prompt.strip() or not callable(executor):
        raise ValueError("A non-empty prompt and callable executor are required")
    if checkpoint is not None and not callable(checkpoint):
        raise ValueError("checkpoint must be callable")
    schemas = _validated_schemas(tool_schemas)
    profile, limits = resolve_main_profile(profile_home), budget or AgentBudget()
    if mode == "specialists" and limits.max_model_calls is not None and limits.max_model_calls < 4:
        raise ValueError("Specialist comparison requires at least four model calls")
    binding = _runtime_binding(prompt, schemas, profile, mode, limits, orchestration_policy)
    roles = list(ROLE_INSTRUCTIONS) if mode == "specialists" else ["main"]
    state = {"runs": [], "next_role_index": 0, "active_role": None,
             "submission_status": "not_submitted", "submission": None, "stage_attempt": 0}
    assisted = orchestrated or mode in {"main_strategist", "main_condition_scientist", "main_route_critic"}
    advisor_key = {"main_condition_scientist":"condition_scientist", "main_route_critic":"route_critic"}.get(mode,"strategist")
    if orchestrated:
        advisor_key = "orchestration"
    runtime_schema = ({"main_strategist": "srg-agent-runtime-strategist-v1",
                       "main_condition_scientist": "srg-agent-runtime-condition-v1",
                       "main_route_critic": "srg-agent-runtime-critic-v1"}
                      .get(mode, "srg-agent-runtime-v1"))
    if assisted:
        if orchestrated:
            from . import orchestration_runtime as advisor_runtime
            runtime_schema = "srg-agent-runtime-orchestrated-v1"
        elif mode == "main_route_critic":
            from . import route_critic_runtime as advisor_runtime
        elif mode == "main_condition_scientist":
            from . import condition_scientist_runtime as advisor_runtime
        else:
            from . import strategist_runtime as advisor_runtime
        initial = advisor_runtime.initial_state(mode, orchestration_policy) if orchestrated else advisor_runtime.initial_state()
        state = {**state, advisor_key: initial}
    if resume_state is not None:
        saved = json.loads(json.dumps(resume_state, allow_nan=False))
        if saved.get("schema_version") != runtime_schema or saved.get("binding") != binding:
            raise ValueError("Runtime resume binding differs from task, profile, schemas or budget")
        state = {key: saved[key] for key in state}
        index = state["next_role_index"]
        if (isinstance(index, bool) or not isinstance(index, int) or not 0 <= index <= len(roles)
                or not isinstance(state["runs"], list) or len(state["runs"]) != index
                or [run.get("role") for run in state["runs"]] != roles[:index]):
            raise ValueError("Invalid runtime progress")
        if assisted:
            restored = (advisor_runtime.restore_state(state[advisor_key], mode=mode, policy=orchestration_policy)
                        if orchestrated else advisor_runtime.restore_state(state[advisor_key]))
            state = {**state, advisor_key: restored}
        ledger = SharedLedger.from_state(saved["ledger"], budget=limits)
    else:
        ledger = SharedLedger(limits)
    runtime = backend or NativeAgentBackend()

    def persist():
        if checkpoint is not None:
            value = {"schema_version": runtime_schema, "binding": binding,
                     **state, "ledger": ledger.export_state()}
            try:
                checkpoint(json.loads(json.dumps(value, allow_nan=False)))
            except Exception as exc:
                raise CheckpointError("Runtime checkpoint failed; execution stopped") from exc
    ledger._on_change = persist
    active_allowed = set()
    advice_lock = RLock()

    def update_advisor(value):
        nonlocal state
        state = {**state, advisor_key: value}
        persist()

    def execute_metered(name, arguments):
        if "submit" in active_allowed and ledger.finalization_due(for_tool=True) and name != "submit":
            ledger.finalization_only = True
            persist()
            raise BudgetExhausted("Finalization-only phase permits submit only")
        ledger.claim_tool_call()
        if name not in active_allowed or not isinstance(arguments, dict):
            raise ValueError("Tool call is outside the permitted environment contract")
        result = executor(name, arguments)
        if name == "submit" and isinstance(result, dict) and result.get("status") == "ok":
            state["submission_status"], state["submission"] = "submitted", result
        persist()
        if assisted:
            result = advisor_runtime.after_tool(name, arguments, result, state=state[advisor_key],
                update=update_advisor, runtime=runtime, profile=profile, ledger=ledger)
        return result

    def metered_executor(name, arguments):
        if not assisted:
            return execute_metered(name, arguments)
        with advice_lock:
            return execute_metered(name, arguments)

    persist()
    for index in range(state["next_role_index"], len(roles)):
        role = roles[index]
        ledger.set_stage(role)
        state["active_role"], state["stage_attempt"] = role, state["stage_attempt"] + 1
        remaining = None if limits.max_model_calls is None else limits.max_model_calls - ledger.snapshot()["model_calls"]
        quota = (None if remaining is None else
                 max(0, remaining if role == "main" else min(remaining, max(1, limits.max_model_calls // 6))))
        reports = "" if not state["runs"] else "\n\nSpecialist reports (proposals, not independent validation):\n" + json.dumps(
            [run["report"] for run in state["runs"]])
        condition_task = any(schema['name'] == 'submit' and 'candidate_id' in
                             schema['parameters'].get('properties', {}) for schema in schemas)
        instruction = ("Choose, observe and submit condition candidates using the available tools. "
                       "Retain uncertainty and distinguish predictions from measured observations."
                       if role == 'main' and condition_task else ROLE_INSTRUCTIONS[role])
        if mode == 'main_role_prompt':
            instruction += '\n' + advisor_runtime.role_prompt_instructions()
        stage_prompt = instruction + "\n\n" + prompt + reports
        stage_schemas = [s for s in schemas if s["name"] != "reset" and (role == "main" or s["name"] != "submit")]
        active_allowed = {s["name"] for s in stage_schemas}
        persist()
        try:
            if quota is not None and quota < 1:
                raise BudgetExhausted("Shared model_calls budget exhausted")
            ledger.check_time()
            result = runtime.run(profile=profile, prompt=stage_prompt, tool_schemas=stage_schemas,
                                 executor=metered_executor, ledger=ledger, role=role, model_call_limit=quota)
        except (CheckpointError, RuntimeContractError):
            raise
        except Exception as exc:
            result = {"completed": False, "final_response": "", "messages": [], "usage": {},
                      "model": profile.model, "provider": profile.provider,
                      "error_type": type(exc).__name__,
                      "error": str(exc) if isinstance(exc, BudgetExhausted) else "Runtime stage failed"}
        if result.get("model") != profile.model or result.get("provider") != profile.provider:
            raise RuntimeError("Runtime did not use the configured main profile model/provider")
        result = sanitize_run_artifact(result)
        ledger.settle_stage(result.get("usage", {}).get("total_tokens"), result.get("token_confirmations"),
                            stage_id=f"{role}:{state['stage_attempt']}")
        report = _compact_report(result, role, limits.specialist_report_chars)
        state["runs"] = [*state["runs"], {**result, "role": role, "report": report}]
        state["next_role_index"], state["active_role"] = index + 1, None
        persist()
    runs = state["runs"]
    completed = bool(runs and runs[-1]["role"] == "main" and runs[-1].get("completed"))
    submission_required = any(schema["name"] == "submit" for schema in schemas)
    advisor_runs = state[advisor_key]["runs"] if assisted else []
    extra = {advisor_key + "_runs": advisor_runs, advisor_key + "_state": state[advisor_key]} if assisted else {}
    if orchestrated:
        extra = {**extra, 'orchestration': advisor_runtime.summarize_state(state[advisor_key])}
    return {**extra, "mode": mode, "backend": "native_agent_scientist" if backend is None else "injected_test_backend",
            "model": profile.model, "provider": profile.provider,
            "completed": completed and (not submission_required or state["submission_status"] == "submitted"),
            "conversation_completed": completed, "submission_status": state["submission_status"],
            "end_policy": "agent_submission_or_recorded_failure_no_host_fallback",
            "resumed": resume_state is not None,
            "final_response": runs[-1]["final_response"] if runs else "", "runs": runs,
            "usage": _usage_totals(runs + advisor_runs), "ledger": ledger.snapshot()}


def _confirmed_response_tokens(response, provider, api_mode):
    usage = response.get("usage") if isinstance(response, dict) else getattr(response, "usage", None)
    if not usage:
        return None
    # Use the same native normalization as session_total_tokens, including cached
    # input. If unavailable or malformed, retain the full reservation.
    try:
        from agent.usage_pricing import normalize_usage
        total = normalize_usage(usage, provider=provider, api_mode=api_mode).total_tokens
    except (ImportError, AttributeError, TypeError, ValueError):
        return None
    return total if isinstance(total, int) and not isinstance(total, bool) and total > 0 else None


def _partial_result(agent, result):
    messages = result.get("messages") or getattr(agent, "_srg_last_messages", [])
    messages = messages if isinstance(messages, list) else []
    text = result.get("final_response", "")
    if not text:
        for message in reversed(messages):
            if isinstance(message, dict) and message.get("role") == "assistant":
                content = message.get("content", "")
                if isinstance(content, str) and content:
                    text = content
                    break
    return {**result, "partial": True, "messages": messages, "final_response": text}


class _StopAgent(BaseException):
    """Escape host retries once our authoritative budget or model fence closes."""


class NativeAgentBackend:
    """Real AIAgent runtime adapter; no credentials or alternate model are serialized."""

    def run(self, *, profile, prompt, tool_schemas, executor, ledger, role, model_call_limit):
        try:
            from run_agent import AIAgent
            from sci_constants import set_sci_home_override, reset_sci_home_override
            from agent.secret_scope import build_profile_secret_scope, set_secret_scope, reset_secret_scope
            from sci_cli.runtime_provider import resolve_runtime_provider
        except ImportError as exc:
            raise RuntimeError("Use the installed Agent Scientist Python runtime to run agents") from exc
        home_token = set_sci_home_override(profile.home)
        secret_token = None
        try:
            secret_token = set_secret_scope(build_profile_secret_scope(profile.home), profile_home=str(profile.home))
            runtime = resolve_runtime_provider(requested=profile.provider, target_model=profile.model)
            if runtime.get("provider") != profile.provider:
                raise RuntimeContractError("Provider resolution changed the configured main provider")
            if runtime.get("api_mode") not in {"chat_completions", "codex_responses", "anthropic_messages", "test"} or profile.provider == "moa":
                raise RuntimeContractError("Provider transport has no audited single-wire accounting contract")
            return self._execute(AIAgent, runtime, profile, prompt, tool_schemas,
                                 executor, ledger, role, model_call_limit)
        finally:
            if secret_token is not None:
                reset_secret_scope(secret_token)
            reset_sci_home_override(home_token)

    def _execute(self, base_class, runtime, profile, prompt, schemas, executor, ledger, role, quota):
        from tools.registry import registry
        from sci_constants import sci_home_key

        scope, toolset = sci_home_key(), "srg_episode_" + uuid4().hex[:10]
        registrations, names = [], set()
        try:
            for schema in schemas:
                name, action = toolset + "_" + schema["name"], schema["name"]
                handler = lambda args, action=action, **kw: json.dumps(executor(action, args), allow_nan=False)
                registry.register(name=name, toolset=toolset, schema={**schema, "name": name}, handler=handler, scope=scope)
                registrations.append((name, registry.snapshot_registration(name, scope=scope)))
                names.add(name)
            cls = self._metered_class(base_class, profile, ledger, quota)
            agent = cls(
                model=profile.model, provider=profile.provider, requested_provider=profile.provider,
                api_mode=runtime.get("api_mode"), base_url=runtime.get("base_url"), api_key=runtime.get("api_key"),
                max_iterations=quota, max_tokens=ledger.budget.max_output_tokens_per_call,
                run_budget_seconds=(None if ledger.budget.wall_seconds is None else
                    max(0.1, ledger.budget.wall_seconds * (1 if role == "main" else 1 - ledger.budget.finalization_wall_fraction) - ledger.snapshot()["elapsed_seconds"])),
                unbudgeted_run=ledger.budget.regime == 'unbudgeted',
                enabled_toolsets=[toolset], skip_memory=True, skip_context_files=True,
                skip_background_review=True, fallback_model=[], quiet_mode=True, platform="batch",
            )
            try:
                # Main profiles may defer all plugin schemas behind tool search.
                # Materialize only this episode's registered schemas, never the
                # global search bridge, so metering and capability limits hold.
                if set(agent.valid_tool_names) == {"tool_search", "tool_describe", "tool_call"}:
                    agent.tools = [{"type": "function", "function": {**s, "name": toolset + "_" + s["name"]}} for s in schemas]
                    agent.valid_tool_names = set(names)
                agent._skip_mcp_refresh = True
                if set(agent.valid_tool_names) != names:
                    raise RuntimeContractError("Agent exposed tools outside the environment contract: " + repr(sorted(agent.valid_tool_names)) + "; expected " + repr(sorted(names)))
                try:
                    result = agent.run_conversation(prompt, task_id=toolset + "_" + role)
                except _StopAgent as exc:
                    result = {"completed": False, "final_response": "", "error": str(exc)}
                if not result.get("completed"):
                    result = _partial_result(agent, result)
                return {**result, "token_confirmations": getattr(agent, "_srg_confirmations", {}),
                        "provider_request_failures": list(getattr(agent, "_srg_request_failures", ())), "model": agent.model, "provider": agent.provider,
                        "usage": {"input_tokens": getattr(agent, "session_input_tokens", None),
                                  "output_tokens": getattr(agent, "session_output_tokens", None),
                                  "total_tokens": getattr(agent, "session_total_tokens", None),
                                  "estimated_cost_usd": getattr(agent, "session_estimated_cost_usd", None)}}
            finally:
                agent.close()
        finally:
            for name, current in registrations:
                registry.restore_registration(name, current, None, scope=scope)

    @staticmethod
    def _metered_class(base_class, profile, ledger, quota):
        class MeteredAgent(base_class):
            _srg_calls = 0

            def _admit(self, request):
                if isinstance(request, dict):
                    self._srg_last_messages = request.get("messages", request.get("input", []))
                try:
                    if resolve_main_profile(profile.home) != profile or self.model != profile.model or self.provider != profile.provider:
                        raise BudgetExhausted("Configured main model/provider changed; restart the episode")
                    if quota is not None and self._srg_calls >= quota:
                        raise BudgetExhausted("Stage model-call allocation exhausted")
                    # Text-only requests: a UTF-8 byte per token plus framing
                    # margin is deliberately conservative until matched stage settlement.
                    input_bound = len(json.dumps(request, ensure_ascii=False).encode("utf-8")) + 1024
                    request_id = ledger.claim_model_call(estimated_input_tokens=input_bound,
                                            reserved_output_tokens=ledger.budget.max_output_tokens_per_call)
                    self._srg_calls += 1
                    return request_id
                except BudgetExhausted as exc:
                    raise _StopAgent(str(exc)) from None

            def _request(self, method, args, kwargs):
                outermost = not getattr(self, "_srg_request_depth", 0)
                if outermost:
                    request = args[0] if args else kwargs
                    request = self._finalization_request(request)
                    args, kwargs = ((request, *args[1:]), kwargs) if args else (args, request)
                    request_id = self._admit(request)
                    self._srg_wire_gate = WireGate()
                self._srg_request_depth = getattr(self, "_srg_request_depth", 0) + 1
                try:
                    response = method(*args, **kwargs)
                    if outermost:
                        total = _confirmed_response_tokens(response, self.provider, getattr(self, "api_mode", None))
                        if total is not None:
                            self._srg_confirmations = {**getattr(self, "_srg_confirmations", {}), request_id: total}
                            ledger.settle_request(request_id, total)
                    return response
                except Exception as exc:
                    if outermost:
                        category = "provider_stream_idle_timeout" if isinstance(exc, TimeoutError) and "SSE" in str(exc) else "provider_request_error"
                        diagnostic = {"request_id": request_id, "exception_type": type(exc).__name__, "category": category}
                        status = getattr(exc, "status_code", None)
                        if isinstance(status, int):
                            diagnostic = {**diagnostic, "http_status": status}
                        self._srg_request_failures = getattr(self, "_srg_request_failures", ()) + (diagnostic,)
                        ledger.record_request_failure(request_id, diagnostic)
                    raise
                finally:
                    self._srg_request_depth -= 1
                    if outermost:
                        self._srg_wire_gate.close()

            def _finalization_request(self, request):
                if not isinstance(request, dict) or ledger.budget.regime == 'unbudgeted':
                    return request
                proposed = len(json.dumps(request, ensure_ascii=False).encode("utf-8")) + 1024 + ledger.budget.max_output_tokens_per_call
                if not ledger.finalization_due(proposed_tokens=proposed):
                    return request
                tools = request.get("tools", [])
                submits = [tool for tool in tools if tool.get("function", tool).get("name", "").endswith("_submit")]
                if not submits:
                    return request
                ledger.finalization_only = True
                return {**request, "tools": submits}

            def _create_request_openai_client(self, *args, **kwargs):
                return GuardedClient(super()._create_request_openai_client(*args, **kwargs), self._srg_wire_gate)

            def _create_request_anthropic_client(self, *args, **kwargs):
                return GuardedClient(super()._create_request_anthropic_client(*args, **kwargs), self._srg_wire_gate)

            def _close_request_openai_client(self, client, *args, **kwargs):
                return super()._close_request_openai_client(unwrap_client(client), *args, **kwargs)

            def _abort_request_openai_client(self, client, *args, **kwargs):
                return super()._abort_request_openai_client(unwrap_client(client), *args, **kwargs)

            def _close_request_anthropic_client(self, client, *args, **kwargs):
                return super()._close_request_anthropic_client(unwrap_client(client), *args, **kwargs)

            def _abort_request_anthropic_client(self, client, *args, **kwargs):
                return super()._abort_request_anthropic_client(unwrap_client(client), *args, **kwargs)

            def _interruptible_api_call(self, *args, **kwargs):
                return self._request(super()._interruptible_api_call, args, kwargs)

            def _interruptible_streaming_api_call(self, *args, **kwargs):
                return self._request(super()._interruptible_streaming_api_call, args, kwargs)

            def _try_activate_fallback(self, *args, **kwargs):
                return False

            def _compress_context(self, *args, **kwargs):
                # The benchmark must never spend unmetered tokens on a separate
                # auxiliary model. An oversized task ends with an explicit result.
                raise _StopAgent("Context limit reached; auxiliary model calls are disabled")

        return MeteredAgent
