"""Contract tests for agent orchestration; test doubles never call a model."""

import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from synthesis_route_gym.agent_runner import (
    AgentBudget, BudgetExhausted, SharedLedger, bind_executor,
    dispatch_bound_action, resolve_main_profile, run_agent_scientist,
    NativeAgentBackend, _StopAgent,
)


@pytest.fixture
def main_home(tmp_path):
    home = tmp_path / "main"
    home.mkdir()
    (home / "config.yaml").write_text(
        "model:\n  default: configured-model\n  provider: configured-provider\n"
    )
    return home


class RecordingBackend:
    def __init__(self):
        self.calls = []

    def run(self, **kwargs):
        self.calls.append(kwargs)
        kwargs["ledger"].claim_model_call()
        observation = kwargs["executor"]("inspect", {})
        return {
            "completed": True,
            "final_response": json.dumps(observation),
            "messages": [{"role": "assistant", "content": "ranked"}],
            "model": kwargs["profile"].model,
            "provider": kwargs["profile"].provider,
            "usage": {"input_tokens": 10, "output_tokens": 2, "total_tokens": 12},
        }


SCHEMAS = [{"name": "inspect", "description": "Inspect the route state.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False}}]


def test_reads_main_profile_dynamically_and_ignores_sticky_profile(main_home):
    (main_home / "active_profile").write_text("different-model-profile")
    profile = resolve_main_profile(main_home)
    assert (profile.model, profile.provider) == ("configured-model", "configured-provider")
    (main_home / "config.yaml").write_text("model:\n  default: changed\n  provider: same\n")
    assert resolve_main_profile(main_home).model == "changed"


@pytest.mark.parametrize("content", ["{}", "model: {}", "model:\n  default: only-model\n"])
def test_missing_main_model_fails_without_fallback(main_home, content):
    (main_home / "config.yaml").write_text(content)
    with pytest.raises(ValueError, match="model|provider"):
        resolve_main_profile(main_home)


def test_main_agent_uses_only_supplied_environment_tools(main_home):
    backend = RecordingBackend()
    result = run_agent_scientist(
        "Plan a route", lambda name, args: {"action": name},
        tool_schemas=SCHEMAS, profile_home=main_home, backend=backend,
    )
    assert result["mode"] == "main"
    assert result["model"] == "configured-model"
    assert result["usage"]["total_tokens"] == 12
    assert result["ledger"]["model_calls"] == 1
    assert result["ledger"]["tool_calls"] == 1
    assert len(backend.calls) == 1
    assert backend.calls[0]["tool_schemas"] == SCHEMAS


def test_specialists_use_same_model_and_shared_budget(main_home):
    backend = RecordingBackend()
    result = run_agent_scientist(
        "Compare routes", lambda name, args: {"ok": True},
        tool_schemas=SCHEMAS, profile_home=main_home, backend=backend,
        mode="specialists", budget=AgentBudget(max_model_calls=8),
    )
    assert [run["role"] for run in result["runs"]] == [
        "retrosynthesis_strategist", "condition_optimisation_scientist", "route_critic", "main"
    ]
    assert len({id(call["ledger"]) for call in backend.calls}) == 1
    assert all(call["profile"].model == "configured-model" for call in backend.calls)
    assert result["usage"]["total_tokens"] == 48
    assert result["ledger"]["model_calls"] == 4
    assert "Specialist reports" in backend.calls[-1]["prompt"]


def test_shared_ledger_enforces_tool_request_and_time_caps():
    now = [10.0]
    ledger = SharedLedger(AgentBudget(max_model_calls=1, max_tool_calls=1, wall_seconds=5),
                          clock=lambda: now[0])
    ledger.claim_model_call()
    with pytest.raises(BudgetExhausted):
        ledger.claim_model_call()
    ledger.claim_tool_call()
    with pytest.raises(BudgetExhausted):
        ledger.claim_tool_call()
    now[0] = 16
    with pytest.raises(BudgetExhausted, match="wall"):
        ledger.check_time()
    assert ledger.snapshot()["model_calls"] == 1


def test_refuses_tools_that_can_read_hidden_evaluator(main_home):
    schemas = [{"name": "terminal", "parameters": {"type": "object"}}]
    with pytest.raises(ValueError, match="not allowed"):
        run_agent_scientist("test", lambda *_: {}, tool_schemas=schemas,
                            profile_home=main_home, backend=RecordingBackend())


def test_mismatched_runtime_model_is_reported_as_failure(main_home):
    class WrongBackend(RecordingBackend):
        def run(self, **kwargs):
            return {**super().run(**kwargs), "model": "unapproved-model"}
    with pytest.raises(RuntimeError, match="configured main"):
        run_agent_scientist("test", lambda *_: {}, tool_schemas=SCHEMAS,
                            profile_home=main_home, backend=WrongBackend())


def test_unbound_plugin_fails_closed_and_scope_is_restored():
    with pytest.raises(RuntimeError, match="bound"):
        dispatch_bound_action("inspect", {})
    with bind_executor(lambda name, args: {"name": name, "arguments": args}):
        assert dispatch_bound_action("inspect", {"route_id": "r1"})["name"] == "inspect"
        with pytest.raises(ValueError, match="not allowed"):
            dispatch_bound_action("terminal", {})
    with pytest.raises(RuntimeError):
        dispatch_bound_action("inspect", {})


def test_plugin_registers_and_dispatches_environment_call():
    plugin_dir = Path(__file__).parents[1] / "integrations" / "agent_scientist"
    spec = importlib.util.spec_from_file_location("srg_plugin_test", plugin_dir / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    class Context:
        def register_tool(self, **kwargs):
            self.tool = kwargs
    ctx = Context()
    module.register(ctx)
    with bind_executor(lambda name, args: {"name": name}):
        result = json.loads(ctx.tool["handler"]({"action": "inspect", "arguments": {}}))
    assert result["name"] == "inspect"
    assert ctx.tool["toolset"] == "synthesis_route_gym"
    actions = ctx.tool["schema"]["parameters"]["properties"]["action"]["enum"]
    assert {"rank_routes", "predict_conditions"} <= set(actions)


@pytest.mark.parametrize("kwargs", [{"max_model_calls": 0}, {"max_tool_calls": True},
                                    {"max_output_tokens_per_call": -1}, {"wall_seconds": float("inf")}])
def test_rejects_invalid_budgets(kwargs):
    with pytest.raises(ValueError):
        AgentBudget(**kwargs)


def test_native_model_fence_stops_before_second_actual_request(main_home):
    class Runtime:
        model = "configured-model"
        provider = "configured-provider"
        def _interruptible_api_call(self, *args, **kwargs):
            return "real-call-boundary"
        def _interruptible_streaming_api_call(self, *args, **kwargs):
            return "stream-call-boundary"
    profile = resolve_main_profile(main_home)
    ledger = SharedLedger(AgentBudget(max_model_calls=2))
    cls = NativeAgentBackend._metered_class(Runtime, profile, ledger, quota=1)
    agent = cls()
    assert agent._interruptible_api_call({}) == "real-call-boundary"
    with pytest.raises(_StopAgent, match="allocation"):
        agent._interruptible_api_call({})
    assert ledger.snapshot()["model_calls"] == 1
    next_agent = cls()
    assert next_agent._interruptible_streaming_api_call({}) == "stream-call-boundary"
    assert ledger.snapshot()["model_calls"] == 2
    assert not next_agent._try_activate_fallback()
    with pytest.raises(_StopAgent, match="auxiliary"):
        next_agent._compress_context()


def test_native_model_fence_notices_configuration_change(main_home):
    class Runtime:
        model = "configured-model"
        provider = "configured-provider"
        def _interruptible_api_call(self, request):
            raise AssertionError("Must stop before provider")
    ledger = SharedLedger(AgentBudget())
    cls = NativeAgentBackend._metered_class(Runtime, resolve_main_profile(main_home), ledger, quota=1)
    (main_home / "config.yaml").write_text("model:\n  default: changed\n  provider: changed\n")
    with pytest.raises(_StopAgent, match="changed"):
        cls()._interruptible_api_call({})
    assert ledger.snapshot()["model_calls"] == 0


def test_tool_errors_consume_ledger_and_unknown_usage_stays_null(main_home):
    class InvalidCaller(RecordingBackend):
        def run(self, **kwargs):
            with pytest.raises(ValueError):
                kwargs["executor"]("terminal", {})
            return {"completed": False, "final_response": "", "messages": [],
                    "model": kwargs["profile"].model, "provider": kwargs["profile"].provider,
                    "usage": {}}
    result = run_agent_scientist("test", lambda *_: {}, tool_schemas=SCHEMAS,
                                profile_home=main_home, backend=InvalidCaller())
    assert result["ledger"]["tool_calls"] == 1
    assert result["usage"]["total_tokens"] is None
    assert not result["completed"]


def test_bad_runner_inputs_fail_before_agent_construction(main_home):
    kwargs = {"tool_schemas": SCHEMAS, "profile_home": main_home, "backend": RecordingBackend()}
    with pytest.raises(ValueError, match="mode"):
        run_agent_scientist("test", lambda *_: {}, mode="fake", **kwargs)
    with pytest.raises(ValueError, match="prompt"):
        run_agent_scientist("", lambda *_: {}, **kwargs)
    with pytest.raises(ValueError, match="four"):
        run_agent_scientist("test", lambda *_: {}, mode="specialists", budget=AgentBudget(max_model_calls=3), **kwargs)


@pytest.fixture
def native_host_double(monkeypatch):
    state = {"registrations": {}, "closed": False, "reset_home": False, "reset_secret": False}
    class Registry:
        def register(self, **kwargs):
            state["registrations"][kwargs["name"]] = kwargs
        def snapshot_registration(self, name, **kwargs):
            return state["registrations"][name]
        def restore_registration(self, name, current, previous, **kwargs):
            assert current is state["registrations"][name]
            del state["registrations"][name]
    class HostAgent:
        def __init__(self, **kwargs):
            state["constructor"] = kwargs
            self.model, self.provider = kwargs["model"], kwargs["provider"]
            self.valid_tool_names = set(state["registrations"])
            if state.get("bridge_only"):
                self.valid_tool_names = {"tool_search", "tool_describe", "tool_call"}
            if state.get("unexpected_tool"):
                self.valid_tool_names.add("terminal")
            self.session_input_tokens, self.session_output_tokens = 10, 2
            self.session_total_tokens, self.session_estimated_cost_usd = 12, 0.001
        def _interruptible_api_call(self, payload):
            return {"model": self.model, "usage": {"total_tokens": 12} if state.get("confirmed_usage") else None}
        def run_conversation(self, prompt, task_id):
            self._interruptible_api_call({})
            if state.get("cutoff"):
                self._interruptible_api_call({"messages": [{"role": "assistant", "content": "Candidate A needs evidence."}]})
            entry = next(iter(state["registrations"].values()))
            result = json.loads(entry["handler"]({}))
            return {"completed": True, "final_response": json.dumps(result),
                    "messages": [{"role": "assistant", "content": "done"}]}
        def close(self):
            state["closed"] = True
    constants = SimpleNamespace(
        set_sci_home_override=lambda home: str(home),
        reset_sci_home_override=lambda token: state.update(reset_home=True),
        sci_home_key=lambda: "temporary-test-scope",
    )
    secret_scope = SimpleNamespace(
        build_profile_secret_scope=lambda home: {}, set_secret_scope=lambda *args, **kw: "token",
        reset_secret_scope=lambda token: state.update(reset_secret=True),
    )
    resolver = SimpleNamespace(resolve_runtime_provider=lambda **kw: {
        "provider": state.get("runtime_provider", "configured-provider"), "api_mode": "test"})
    for name, value in {"run_agent": SimpleNamespace(AIAgent=HostAgent), "sci_constants": constants,
                        "agent.secret_scope": secret_scope, "sci_cli.runtime_provider": resolver,
                        "tools.registry": SimpleNamespace(registry=Registry())}.items():
        monkeypatch.setitem(sys.modules, name, value)
    return state


def test_native_adapter_binds_environment_cleans_up_and_returns_usage(main_home, native_host_double):
    result = run_agent_scientist("test", lambda name, args: {"action": name},
                                tool_schemas=SCHEMAS, profile_home=main_home)
    state = native_host_double
    assert result["usage"]["total_tokens"] == 12
    assert result["ledger"]["model_calls"] == 1
    assert state["constructor"]["fallback_model"] == []
    assert state["constructor"]["skip_context_files"] is True
    assert state["closed"] and state["reset_home"] and state["reset_secret"]
    assert state["registrations"] == {}


def test_native_adapter_rejects_unexpected_tools_and_cleans_up(main_home, native_host_double):
    native_host_double["unexpected_tool"] = True
    with pytest.raises(RuntimeError, match="outside"):
        run_agent_scientist("test", lambda *_: {}, tool_schemas=SCHEMAS, profile_home=main_home)
    assert native_host_double["closed"] and not native_host_double["registrations"]


def test_native_adapter_rejects_provider_fallback(main_home, native_host_double):
    native_host_double["runtime_provider"] = "wrong-provider"
    with pytest.raises(RuntimeError, match="changed"):
        run_agent_scientist("test", lambda *_: {}, tool_schemas=SCHEMAS, profile_home=main_home)
    assert native_host_double["reset_home"] and native_host_double["reset_secret"]


def test_specialists_cannot_submit_or_reset_shared_episode(main_home):
    class RoleChecker(RecordingBackend):
        def run(self, **kwargs):
            if kwargs['role'] != 'main':
                assert not {'reset', 'submit'} & {s['name'] for s in kwargs['tool_schemas']}
                with pytest.raises(ValueError):
                    kwargs['executor']('submit', {'route_ids': []})
            return super().run(**kwargs)
    schemas = SCHEMAS + [{"name": name, "parameters": {"type": "object"}} for name in ['reset', 'submit']]
    result = run_agent_scientist('test', lambda *_: {}, tool_schemas=schemas,
                                profile_home=main_home, mode='specialists', backend=RoleChecker())
    assert result['conversation_completed']
    assert not result['completed']  # No host fallback invents a submission.


def test_token_budget_reserves_before_call_and_counts_actual():
    ledger = SharedLedger(AgentBudget(max_total_tokens=100))
    ledger.claim_model_call(estimated_input_tokens=30, reserved_output_tokens=40)
    assert ledger.snapshot()['reserved_tokens'] == 70
    with pytest.raises(BudgetExhausted, match='token'):
        ledger.claim_model_call(estimated_input_tokens=20, reserved_output_tokens=20)
    ledger.record_actual_tokens(55)
    assert ledger.snapshot()['actual_tokens'] == 55
    assert ledger.snapshot()['model_calls'] == 1


def test_native_adapter_materializes_only_environment_bridge_tools(main_home, native_host_double):
    native_host_double["bridge_only"] = True
    result = run_agent_scientist("test", lambda *_: {}, tool_schemas=SCHEMAS, profile_home=main_home)
    assert result["completed"]


def test_nested_streaming_codex_transport_is_counted_once(main_home):
    class Runtime:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            return 'response'
        def _interruptible_streaming_api_call(self, request):
            return self._interruptible_api_call(request)
    ledger = SharedLedger(AgentBudget(max_model_calls=1))
    agent = NativeAgentBackend._metered_class(Runtime, resolve_main_profile(main_home), ledger, quota=1)()
    assert agent._interruptible_streaming_api_call({}) == 'response'
    assert ledger.snapshot()['model_calls'] == 1


def test_stage_settlement_releases_confirmed_usage_and_enforces_aggregate_cap():
    ledger = SharedLedger(AgentBudget(max_total_tokens=100))
    first = ledger.claim_model_call(estimated_input_tokens=60, reserved_output_tokens=20)
    ledger.settle_stage(20, {first: 20})
    assert ledger.snapshot()['reserved_tokens'] == 0
    assert ledger.snapshot()['actual_tokens'] == 20
    second = ledger.claim_model_call(estimated_input_tokens=60, reserved_output_tokens=20)
    ledger.settle_stage(30, {second: 30})
    assert ledger.snapshot()['actual_tokens'] == 50
    with pytest.raises(BudgetExhausted, match='token'):
        ledger.claim_model_call(estimated_input_tokens=51)


def test_unknown_failed_and_unmatched_usage_retain_reservations():
    ledger = SharedLedger(AgentBudget(max_total_tokens=500))
    failed = ledger.claim_model_call(estimated_input_tokens=80)
    good = ledger.claim_model_call(estimated_input_tokens=70)
    ledger.settle_stage(20, {good: 20})
    assert ledger.snapshot()['reserved_tokens'] == 80
    unknown = ledger.claim_model_call(estimated_input_tokens=60)
    ledger.settle_stage(None, {unknown: 10})
    assert ledger.snapshot()['reserved_tokens'] == 140
    mismatch = ledger.claim_model_call(estimated_input_tokens=50)
    ledger.settle_stage(30, {mismatch: 10})
    assert ledger.snapshot()['reserved_tokens'] == 190
    assert ledger.snapshot()['actual_tokens'] == 50
    ledger.settle_stage(20, {good: 20})  # Duplicate delivery is idempotent.
    assert ledger.snapshot()['actual_tokens'] == 50


def test_native_partial_result_keeps_last_request_messages(main_home, native_host_double):
    native_host_double['cutoff'] = True
    result = run_agent_scientist('test', lambda *_: {}, tool_schemas=SCHEMAS,
                                profile_home=main_home, budget=AgentBudget(max_model_calls=1))
    assert not result['completed']
    assert result['runs'][0]['partial']
    assert result['runs'][0]['messages'][-1]['content'] == 'Candidate A needs evidence.'
    assert result['runs'][0]['final_response'] == 'Candidate A needs evidence.'


def test_native_stage_settles_only_provider_confirmed_tokens(main_home, native_host_double, monkeypatch):
    native_host_double['confirmed_usage'] = True
    monkeypatch.setitem(sys.modules, 'agent.usage_pricing', SimpleNamespace(
        normalize_usage=lambda usage, **kwargs: SimpleNamespace(total_tokens=usage['total_tokens'])))
    result = run_agent_scientist('test', lambda *_: {}, tool_schemas=SCHEMAS, profile_home=main_home)
    assert result['ledger']['actual_tokens'] == 12
    assert result['ledger']['reserved_tokens'] == 0
    assert result['ledger']['reservation_tokens_total'] > 0
    assert result['ledger']['unsettled_requests'] == 0
    assert result['runs'][0]['token_confirmations'] == {1: 12}


def test_specialist_settlement_preserves_budget_for_main(main_home):
    class ConfirmedBackend:
        def run(self, **kwargs):
            request = kwargs['ledger'].claim_model_call(estimated_input_tokens=75)
            return {'model': kwargs['profile'].model, 'provider': kwargs['profile'].provider,
                    'completed': True, 'final_response': 'done', 'messages': [],
                    'usage': {'total_tokens': 5}, 'token_confirmations': {request: 5}}
    result = run_agent_scientist('test', lambda *_: {}, tool_schemas=SCHEMAS, mode='specialists',
        profile_home=main_home, backend=ConfirmedBackend(),
        budget=AgentBudget(max_model_calls=4, max_total_tokens=100))
    assert result['completed']
    assert result['ledger']['actual_tokens'] == 20
    assert result['ledger']['reservation_tokens_total'] == 300
    assert result['ledger']['reserved_tokens'] == 0


@pytest.mark.parametrize('scientific_action', ['rank_routes', 'predict_conditions'])
def test_scientific_ranking_tools_are_permitted_and_metered(main_home, scientific_action):
    class ScientificCaller(RecordingBackend):
        def run(self, **kwargs):
            kwargs['ledger'].claim_model_call()
            value = kwargs['executor'](scientific_action, {})
            return {'completed': True, 'final_response': json.dumps(value), 'messages': [],
                    'model': kwargs['profile'].model, 'provider': kwargs['profile'].provider,
                    'usage': {}}
    result = run_agent_scientist('test', lambda name, args: {'action': name},
        tool_schemas=[{'name': scientific_action, 'parameters': {'type': 'object'}}],
        profile_home=main_home, backend=ScientificCaller())
    assert json.loads(result['final_response'])['action'] == scientific_action
    assert result['ledger']['tool_calls'] == 1


def test_run_artifact_removes_opaque_reasoning_without_mutating_input():
    from synthesis_route_gym.agent_runner import sanitize_run_artifact
    original = {'messages': [{'type': 'reasoning', 'encrypted_content': 'opaque-secret',
                              'summary': []}, {'role': 'assistant', 'content': 'Visible answer'}]}
    result = sanitize_run_artifact(original)
    assert original['messages'][0]['encrypted_content'] == 'opaque-secret'
    assert 'encrypted_content' not in result['messages'][0]
    assert result['messages'][1]['content'] == 'Visible answer'


def test_native_provider_timeout_is_retained_as_structured_diagnostic(main_home):
    class Runtime:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            raise TimeoutError('Codex stream produced no SSE events after first event')
    ledger = SharedLedger(AgentBudget())
    agent = NativeAgentBackend._metered_class(Runtime, resolve_main_profile(main_home), ledger, quota=1)()
    with pytest.raises(TimeoutError):
        agent._interruptible_api_call({})
    assert agent._srg_request_failures == ({'request_id': 1, 'exception_type': 'TimeoutError',
                                         'category': 'provider_stream_idle_timeout'},)
    assert ledger.snapshot()['unsettled_requests'] == 1


def test_review_schema_requires_all_declared_properties():
    import ast
    source = Path(__file__).parents[1] / 'scripts' / 'review_aspirin_routes.py'
    module = ast.parse(source.read_text())
    submit = next(ast.literal_eval(node.value) for node in module.body if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'submit' for t in node.targets))
    def validate(schema):
        if schema.get('type') == 'object':
            assert set(schema.get('required', [])) == set(schema.get('properties', {}))
            for child in schema.get('properties', {}).values():
                validate(child)
        if schema.get('type') == 'array':
            validate(schema['items'])
    validate(submit['parameters'])
