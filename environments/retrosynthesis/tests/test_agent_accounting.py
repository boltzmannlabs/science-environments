"""Step 3 failure and recovery contracts; all providers are local doubles."""
import json
import sys
from types import SimpleNamespace

import pytest

from synthesis_route_gym.agent_runner import (
    AgentBudget, BudgetExhausted, NativeAgentBackend, SharedLedger,
    resolve_main_profile, run_agent_scientist,
)


@pytest.fixture
def home(tmp_path):
    (tmp_path / 'config.yaml').write_text('model:\n  default: configured-model\n  provider: configured-provider\n')
    return tmp_path


SCHEMAS = [{'name': 'inspect', 'parameters': {'type': 'object'}}]


def reply(kw, **overrides):
    return {'model': kw['profile'].model, 'provider': kw['profile'].provider,
            'completed': True, 'final_response': 'proposal only', 'messages': [],
            'usage': {}, **overrides}


def test_request_usage_releases_reservation_before_next_request(home, monkeypatch):
    monkeypatch.setitem(sys.modules, 'agent.usage_pricing', SimpleNamespace(
        normalize_usage=lambda usage, **kw: SimpleNamespace(total_tokens=usage['total_tokens'])))
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            return {'usage': {'total_tokens': 10}}
    ledger = SharedLedger(AgentBudget(max_total_tokens=3200))
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 2)()
    agent._interruptible_api_call({})
    assert ledger.snapshot()['reserved_tokens'] == 0
    agent._interruptible_api_call({})
    ledger.settle_stage(20, agent._srg_confirmations, stage_id='main')
    assert ledger.snapshot()['actual_tokens'] == 20
    assert ledger.snapshot()['model_calls'] == 2


def test_repeated_settlement_is_idempotent_but_conflicting_usage_rejected():
    ledger = SharedLedger(AgentBudget(max_total_tokens=100))
    request = ledger.claim_model_call(estimated_input_tokens=60)
    ledger.settle_request(request, 20)
    ledger.settle_request(request, 20)
    ledger.settle_stage(20, {request: 20}, stage_id='one')
    ledger.settle_stage(20, {request: 20}, stage_id='one')
    assert ledger.snapshot()['charged_tokens'] == 20
    with pytest.raises(ValueError, match='conflict'):
        ledger.settle_request(request, 21)


def test_unresolved_request_survives_resume_and_downtime_counts():
    now, wall = [5.0], [1000.0]
    budget = AgentBudget(wall_seconds=20, max_total_tokens=100)
    ledger = SharedLedger(budget, clock=lambda: now[0], wall_clock=lambda: wall[0])
    ledger.claim_model_call(estimated_input_tokens=50)
    ledger.claim_tool_call()
    now[0], wall[0] = 10, 1005
    saved = json.loads(json.dumps(ledger.export_state()))
    now[0], wall[0] = 30, 1012
    resumed = SharedLedger.from_state(saved, clock=lambda: now[0], wall_clock=lambda: wall[0])
    assert resumed.snapshot()['model_calls'] == resumed.snapshot()['tool_calls'] == 1
    assert resumed.snapshot()['charged_tokens'] == 50
    assert resumed.snapshot()['elapsed_seconds'] >= 12
    with pytest.raises(BudgetExhausted):
        resumed.claim_model_call(estimated_input_tokens=51)
    wall[0], now[0] = 1021, 39
    with pytest.raises(BudgetExhausted, match='wall'):
        resumed.check_time()


def test_resume_rejects_budget_changes_corrupt_counts_and_clock_rollback():
    ledger = SharedLedger(AgentBudget(), wall_clock=lambda: 1000)
    ledger.claim_model_call(estimated_input_tokens=10)
    state = ledger.export_state()
    with pytest.raises(ValueError, match='budget'):
        SharedLedger.from_state(state, budget=AgentBudget(max_model_calls=99), wall_clock=lambda: 1001)
    broken = {**state, 'counts': {**state['counts'], 'reserved_tokens': 0}}
    with pytest.raises(ValueError):
        SharedLedger.from_state(broken, wall_clock=lambda: 1001)
    with pytest.raises(ValueError, match='clock'):
        SharedLedger.from_state(state, wall_clock=lambda: 999)


def test_finalization_allowance_stops_optional_work_but_allows_main():
    budget = AgentBudget(max_model_calls=4, max_tool_calls=3, max_total_tokens=100,
                         finalization_model_calls=2, finalization_tool_calls=1,
                         finalization_token_fraction=0.3)
    ledger = SharedLedger(budget)
    ledger.set_stage('retrosynthesis_strategist')
    ledger.claim_model_call(estimated_input_tokens=60)
    with pytest.raises(BudgetExhausted, match='finalization'):
        ledger.claim_model_call(estimated_input_tokens=11)
    ledger.claim_tool_call()
    ledger.claim_tool_call()
    with pytest.raises(BudgetExhausted, match='finalization'):
        ledger.claim_tool_call()
    ledger.set_stage('main')
    ledger.claim_model_call(estimated_input_tokens=40)
    ledger.claim_tool_call()
    assert ledger.snapshot()['charged_tokens'] == 100


def test_specialist_reports_are_bounded_and_never_copy_history(home):
    seen = []
    class Backend:
        def run(self, **kw):
            seen.append(kw['prompt'])
            request = kw['ledger'].claim_model_call()
            return reply(kw, final_response='x' * 20000,
                         messages=[{'role': 'tool', 'content': 'PRIVATE-HISTORY-MARKER'}],
                         completed=False, usage={'total_tokens': 1}, token_confirmations={request: 1})
    result = run_agent_scientist('task', lambda *_: {}, tool_schemas=SCHEMAS,
        profile_home=home, backend=Backend(), mode='specialists',
        budget=AgentBudget(specialist_report_chars=200))
    assert len(seen) == 4
    assert len(seen[-1]) < 2000
    assert all('PRIVATE-HISTORY-MARKER' not in prompt for prompt in seen)
    assert result['runs'][0]['report']['truncated']


def test_runner_checkpoints_before_effect_and_resume_does_not_repeat_finished_roles(home):
    checkpoints, roles = [], []
    class Crash(BaseException):
        pass
    class Backend:
        def run(self, **kw):
            roles.append(kw['role'])
            request = kw['ledger'].claim_model_call(estimated_input_tokens=5)
            assert checkpoints[-1]['ledger']['counts']['model_calls'] == len(roles)
            if len(roles) == 2:
                raise Crash()
            return reply(kw, usage={'total_tokens': 2}, token_confirmations={request: 2})
    options = dict(tool_schemas=SCHEMAS, profile_home=home, mode='specialists',
                   budget=AgentBudget(max_model_calls=8), checkpoint=lambda s: checkpoints.append(s))
    with pytest.raises(Crash):
        run_agent_scientist('task', lambda *_: {}, backend=Backend(), **options)
    saved = json.loads(json.dumps(checkpoints[-1]))
    class Finish:
        def run(self, **kw):
            roles.append(kw['role'])
            request = kw['ledger'].claim_model_call(estimated_input_tokens=5)
            return reply(kw, usage={'total_tokens': 2}, token_confirmations={request: 2})
    result = run_agent_scientist('task', lambda *_: {}, backend=Finish(), resume_state=saved, **options)
    assert roles.count('retrosynthesis_strategist') == 1
    assert result['ledger']['model_calls'] == 5
    assert result['ledger']['reserved_tokens'] == 5
    assert result['ledger']['actual_tokens'] == 8
    assert result['resumed']
    with pytest.raises(ValueError, match='binding'):
        run_agent_scientist('different task', lambda *_: {}, backend=Finish(), resume_state=saved, **options)


def test_provider_error_is_recorded_and_main_still_runs(home):
    class Backend:
        def run(self, **kw):
            kw['ledger'].claim_model_call(estimated_input_tokens=1)
            if kw['role'] != 'main':
                raise TimeoutError('secret credential-bearing provider URL')
            return reply(kw)
    result = run_agent_scientist('task', lambda *_: {}, tool_schemas=SCHEMAS,
        profile_home=home, backend=Backend(), mode='specialists')
    assert result['runs'][-1]['role'] == 'main'
    assert result['runs'][0]['error_type'] == 'TimeoutError'
    assert 'secret credential' not in json.dumps(result)
    assert result['ledger']['unsettled_requests'] == 4


def test_failed_checkpoint_stops_before_effect(home):
    effects = []
    class Backend:
        def run(self, **kw):
            kw['ledger'].claim_model_call(estimated_input_tokens=1)
            effects.append('provider')
            return reply(kw)
    def checkpoint(state):
        if state['ledger']['counts']['model_calls']:
            raise OSError('disk full')
    with pytest.raises(RuntimeError, match='checkpoint'):
        run_agent_scientist('task', lambda *_: {}, tool_schemas=SCHEMAS,
            profile_home=home, backend=Backend(), checkpoint=checkpoint)
    assert effects == []


def test_conversation_success_without_submit_is_not_completed(home):
    class Backend:
        def run(self, **kw):
            kw['ledger'].claim_model_call()
            return reply(kw)
    schemas = SCHEMAS + [{'name': 'submit', 'parameters': {'type': 'object'}}]
    result = run_agent_scientist('task', lambda *_: {}, tool_schemas=schemas,
                                profile_home=home, backend=Backend())
    assert result['conversation_completed'] and not result['completed']
    assert result['submission_status'] == 'not_submitted'


def test_main_final_call_offers_only_submit(home):
    captured = []
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            captured.append(request)
            return {}
    ledger = SharedLedger(AgentBudget(max_model_calls=1))
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 1)()
    request = {'messages': [], 'tools': [
        {'type': 'function', 'function': {'name': 'srg_123_expand'}},
        {'type': 'function', 'function': {'name': 'srg_123_submit'}}]}
    agent._interruptible_api_call(request)
    assert [t['function']['name'] for t in captured[0]['tools']] == ['srg_123_submit']
    assert len(request['tools']) == 2


def test_internal_wire_retry_is_blocked_but_new_outer_attempt_is_charged(home):
    calls = []
    class Client:
        max_retries = 0
        def __init__(self):
            self.responses = SimpleNamespace(create=lambda **kw: calls.append(kw) or {})
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _create_request_openai_client(self, **kw):
            return Client()
        def _interruptible_api_call(self, request):
            first = self._create_request_openai_client(reason='first')
            first.responses.create(model=self.model)
            second = self._create_request_openai_client(reason='probe')
            with pytest.raises(RuntimeError, match='wire'):
                second.responses.create(model=self.model)
            self.previous = first
            return {}
    ledger = SharedLedger(AgentBudget(max_model_calls=2))
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 2)()
    agent._interruptible_api_call({})
    stale = agent.previous
    agent._interruptible_api_call({})
    with pytest.raises(RuntimeError, match='wire'):
        stale.responses.create(model='configured-model')
    assert len(calls) == 2
    assert ledger.snapshot()['model_calls'] == 2


def test_request_client_lifecycle_unwraps_and_sdk_retries_fail_closed(home):
    raw = SimpleNamespace(max_retries=0, responses=SimpleNamespace(create=lambda **kw: {}))
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _create_request_openai_client(self, **kw):
            return raw
        def _close_request_openai_client(self, client, **kw):
            assert client is raw
        def _abort_request_openai_client(self, client, **kw):
            assert client is raw
        def _interruptible_api_call(self, request):
            client = self._create_request_openai_client()
            client.responses.create()
            self._close_request_openai_client(client)
            self._abort_request_openai_client(client)
            return {}
    ledger = SharedLedger(AgentBudget())
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 2)()
    agent._interruptible_api_call({})
    raw.max_retries = 2
    with pytest.raises(RuntimeError, match='retries'):
        agent._interruptible_api_call({})


@pytest.mark.parametrize('changes', [
    {'finalization_model_calls': -1}, {'finalization_tool_calls': True},
    {'finalization_token_fraction': 1}, {'finalization_wall_fraction': float('nan')},
    {'specialist_report_chars': 0}, {'wall_seconds': 0}, {'wall_seconds': True},
    {'max_model_calls': 1, 'finalization_model_calls': 2},
])
def test_invalid_finalization_budgets_rejected(changes):
    with pytest.raises(ValueError):
        AgentBudget(**changes)


def test_optional_wall_reserve_and_main_last_tool_are_protected(home):
    now = [0.0]
    ledger = SharedLedger(AgentBudget(wall_seconds=10, finalization_wall_fraction=0.2), clock=lambda: now[0])
    ledger.set_stage('route_critic')
    now[0] = 8.1
    with pytest.raises(BudgetExhausted, match='finalization'):
        ledger.claim_model_call()
    ledger.set_stage('main')
    ledger.claim_model_call()
    assert ledger.finalization_due()


def test_main_optional_tool_cannot_consume_submission_allowance(home):
    seen = []
    class Backend:
        def run(self, **kw):
            kw['ledger'].claim_model_call()
            kw['executor']('inspect', {})
            with pytest.raises(BudgetExhausted, match='Finalization'):
                kw['executor']('inspect', {})
            kw['executor']('submit', {'route_ids': []})
            return reply(kw)
    def execute(name, args):
        seen.append(name)
        return {'status': 'ok', 'result': args}
    result = run_agent_scientist('task', execute, tool_schemas=SCHEMAS + [
        {'name': 'submit', 'parameters': {'type': 'object'}}], profile_home=home,
        backend=Backend(), budget=AgentBudget(max_tool_calls=2))
    assert seen == ['inspect', 'submit']
    assert result['completed'] and result['submission_status'] == 'submitted'
    assert result['ledger']['tool_calls'] == 2


def test_settlement_validation_and_unmatched_telemetry_idempotency():
    ledger = SharedLedger(AgentBudget())
    with pytest.raises(ValueError):
        ledger.claim_model_call(estimated_input_tokens=True)
    with pytest.raises(ValueError):
        ledger.settle_request(1, 3)
    ledger.claim_model_call(estimated_input_tokens=30)
    ledger.settle_stage(20, {'1': 20}, stage_id='stage')
    ledger.settle_stage(20, {'1': 20}, stage_id='stage')
    with pytest.raises(ValueError, match='conflict'):
        ledger.settle_stage(21, {1: 21}, stage_id='stage')
    with pytest.raises(ValueError):
        ledger.settle_stage(1, {2: 1})
    with pytest.raises(ValueError):
        ledger.settle_stage(40, {1: 20, '1': 20})
    with pytest.raises(ValueError):
        ledger.set_stage('')
    ledger.settle_stage(7, stage_id='missing-confirmation')
    ledger.settle_stage(7, stage_id='missing-confirmation')
    assert ledger.snapshot()['actual_tokens'] == 27


def test_completed_resume_makes_no_calls_and_preserves_submission(home):
    checkpoints, calls = [], []
    class Backend:
        def run(self, **kw):
            calls.append(kw['role'])
            kw['ledger'].claim_model_call()
            kw['executor']('submit', {'route_ids': []})
            return reply(kw)
    options = dict(tool_schemas=[{'name': 'submit', 'parameters': {'type': 'object'}}],
                   profile_home=home, backend=Backend(), checkpoint=checkpoints.append)
    first = run_agent_scientist('task', lambda *_: {'status': 'ok'}, **options)
    second = run_agent_scientist('task', lambda *_: {'status': 'ok'}, resume_state=checkpoints[-1], **options)
    assert calls == ['main']
    assert first['completed'] and second['completed']
    assert second['ledger']['model_calls'] == 1


def test_transport_options_retain_gate_and_anthropic_lifecycle(home):
    from synthesis_route_gym.agent_transport import GuardedClient, WireGate, unwrap_client
    calls = []
    class Client:
        max_retries = 0
        messages = SimpleNamespace(stream=lambda **kw: calls.append('stream'))
        def with_options(self, **kwargs):
            return self
    raw = Client()
    wrapped = GuardedClient(raw, WireGate())
    wrapped.with_options(timeout=1).messages.stream()
    with pytest.raises(RuntimeError, match='wire'):
        wrapped.messages.stream()
    assert unwrap_client(raw) is raw
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _create_request_anthropic_client(self, **kwargs):
            return raw
        def _close_request_anthropic_client(self, client):
            assert client is raw
        def _abort_request_anthropic_client(self, client):
            assert client is raw
        def _interruptible_api_call(self, request):
            client = self._create_request_anthropic_client()
            client.messages.stream()
            self._close_request_anthropic_client(client)
            self._abort_request_anthropic_client(client)
            return {}
    ledger = SharedLedger(AgentBudget())
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 1)()
    agent._interruptible_api_call({})
    assert calls == ['stream', 'stream']


def test_optional_request_cannot_straddle_token_finalization_reserve(home):
    captured = []
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            captured.append(request)
            return {}
    ledger = SharedLedger(AgentBudget(max_model_calls=10, max_total_tokens=3500,
                                     finalization_token_fraction=0.2))
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 10)()
    request = {'tools': [{'type': 'function', 'function': {'name': 'srg_expand'}},
                         {'type': 'function', 'function': {'name': 'srg_submit'}}]}
    agent._interruptible_api_call(request)
    assert [t['function']['name'] for t in captured[0]['tools']] == ['srg_submit']


def test_penultimate_request_can_finish_its_tools_without_spending_final_call(home):
    actions = []
    class Backend:
        def run(self, **kw):
            kw['ledger'].claim_model_call()
            kw['executor']('inspect', {})
            kw['ledger'].claim_model_call()
            kw['executor']('submit', {'route_ids': []})
            return reply(kw)
    def execute(name, args):
        actions.append(name)
        return {'status': 'ok'}
    result = run_agent_scientist('task', execute, tool_schemas=SCHEMAS + [
        {'name': 'submit', 'parameters': {'type': 'object'}}], profile_home=home,
        backend=Backend(), budget=AgentBudget(max_model_calls=2))
    assert result['completed']
    assert actions == ['inspect', 'submit']


def test_request_failure_is_durable_before_outer_retry(home):
    checkpoints = []
    class Provider:
        model, provider = 'configured-model', 'configured-provider'
        def _interruptible_api_call(self, request):
            raise TimeoutError('private provider URL')
    ledger = SharedLedger(AgentBudget())
    ledger._on_change = lambda: checkpoints.append(ledger.export_state())
    agent = NativeAgentBackend._metered_class(Provider, resolve_main_profile(home), ledger, 1)()
    with pytest.raises(TimeoutError):
        agent._interruptible_api_call({})
    failure = checkpoints[-1]['requests']['1']['failure']
    assert failure['exception_type'] == 'TimeoutError'
    assert 'private provider' not in json.dumps(checkpoints)
    assert checkpoints[-1]['counts']['reserved_tokens'] > 0
