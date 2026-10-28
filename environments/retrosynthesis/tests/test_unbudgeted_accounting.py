"""Explicit unlimited budgets preserve accounting, identity and legacy behavior."""
import copy
import json
from dataclasses import asdict, replace

import pytest

from synthesis_route_gym.agent_accounting import AgentBudget, BudgetExhausted, SharedLedger
from synthesis_route_gym.schemas import Budget, Task


TASK_LIMITS = ('max_actions', 'max_expansions', 'max_wall_seconds', 'max_llm_tokens')
AGENT_LIMITS = ('max_model_calls', 'max_tool_calls', 'wall_seconds', 'max_total_tokens')


def test_finite_task_budget_keeps_historical_serialization():
    expected = '{"max_actions":200,"max_expansions":1000,"max_wall_seconds":1800.0,"max_llm_tokens":100000,"top_k":10}'
    assert Budget().model_dump_json() == expected
    assert Budget(regime='budgeted').model_dump() == json.loads(expected)
    task = Task(task_id='legacy', target='CCO', inventory=())
    assert task.model_dump()['budget'] == json.loads(expected)
    assert 'regime' not in task.model_dump_json()


def test_task_unbudgeted_factory_roundtrips_explicit_nulls():
    budget = Budget.unbudgeted(top_k=7)
    assert budget.regime == 'unbudgeted' and budget.top_k == 7
    assert all(getattr(budget, key) is None for key in TASK_LIMITS)
    assert Budget.model_validate_json(budget.model_dump_json()) == budget
    assert budget.model_dump()['regime'] == 'unbudgeted'


@pytest.mark.parametrize('key', TASK_LIMITS)
def test_task_disallows_missing_or_mixed_regimes(key):
    with pytest.raises(ValueError):
        Budget(**{key: None})
    with pytest.raises(ValueError):
        Budget(**{**{name: None for name in TASK_LIMITS}, 'regime': 'unbudgeted', key: 1})


@pytest.mark.parametrize('key', (*TASK_LIMITS, 'top_k'))
@pytest.mark.parametrize('value', [True, False, float('nan'), float('inf'), -1, '5'])
def test_task_budget_rejects_coercion_and_nonfinite(key, value):
    with pytest.raises(ValueError):
        Budget(**{key: value})


def test_agent_factory_preserves_protocol_bounds():
    budget = AgentBudget.unbudgeted(specialist_report_chars=333)
    assert budget.regime == 'unbudgeted'
    assert budget.specialist_report_chars == 333
    assert budget.max_output_tokens_per_call is None
    assert all(getattr(budget, key) is None for key in AGENT_LIMITS)
    assert AgentBudget(**asdict(budget)) == budget
    assert AgentBudget.unbudgeted(max_output_tokens_per_call=4096).max_output_tokens_per_call == 4096


@pytest.mark.parametrize('key', AGENT_LIMITS)
def test_agent_disallows_missing_or_mixed_regimes(key):
    with pytest.raises(ValueError):
        AgentBudget(**{key: None})
    with pytest.raises(ValueError):
        replace(AgentBudget.unbudgeted(), **{key: 1})


@pytest.mark.parametrize('changes', [
    {'regime': 'other'}, {'regime': True}, {'max_output_tokens_per_call': None},
    {'max_model_calls': True}, {'wall_seconds': float('inf')}, {'wall_seconds': True},
    {'max_output_tokens_per_call': 0}, {'specialist_report_chars': False},
])
def test_invalid_agent_budgets(changes):
    with pytest.raises(ValueError):
        AgentBudget(**changes)


def test_unbudgeted_ledger_crosses_legacy_limits_without_finalizing():
    now, wall = [0.0], [1000.0]
    ledger = SharedLedger(AgentBudget.unbudgeted(), clock=lambda: now[0], wall_clock=lambda: wall[0])
    ledger.set_stage('route_critic')
    for _ in range(90):
        request = ledger.claim_model_call(estimated_input_tokens=3000, reserved_output_tokens=10000)
        ledger.settle_request(request, 3000)
        ledger.claim_tool_call()
    now[0], wall[0] = 10000, 11000
    ledger.check_time()
    assert not ledger.finalization_due()
    ledger.set_stage('main')
    assert not ledger.finalization_due(999999999)
    snapshot = ledger.snapshot()
    assert snapshot['model_calls'] == snapshot['tool_calls'] == 90
    assert snapshot['actual_tokens'] == 270000
    assert snapshot['elapsed_seconds'] == 10000
    assert snapshot['reserved_tokens'] == 0
    assert snapshot['limits']['max_model_calls'] is None


def test_unknown_output_bound_remains_explicit_until_settlement():
    ledger = SharedLedger(AgentBudget.unbudgeted())
    request = ledger.claim_model_call(estimated_input_tokens=18, reserved_output_tokens=None)
    ledger.record_request_failure(request, {'category': 'transport', 'secret': 'must-not-copy'})
    assert ledger.snapshot()['unsettled_unknown_output_bounds'] == 1
    assert ledger.snapshot()['reserved_tokens'] == 18
    saved = ledger.export_state()
    assert saved['requests'][str(request)]['output_bound_unknown'] is True
    assert saved['requests'][str(request)]['failure'] == {'category': 'transport'}
    resumed = SharedLedger.from_state(json.loads(json.dumps(saved)))
    assert resumed.snapshot()['unsettled_unknown_output_bounds'] == 1
    resumed.settle_request(request, 100)
    assert resumed.snapshot().get('unsettled_unknown_output_bounds', 0) == 0
    assert resumed.snapshot()['actual_tokens'] == 100
    with pytest.raises(ValueError):
        SharedLedger(AgentBudget()).claim_model_call(reserved_output_tokens=None)


def test_unbudgeted_v2_checkpoint_charges_downtime_with_no_deadline():
    now, wall = [0.0], [1000.0]
    ledger = SharedLedger(AgentBudget.unbudgeted(), clock=lambda: now[0], wall_clock=lambda: wall[0])
    request = ledger.claim_model_call(estimated_input_tokens=7)
    ledger.record_request_failure(request, {'category': 'transport'})
    now[0], wall[0] = 5, 1005
    saved = json.loads(json.dumps(ledger.export_state(), allow_nan=False))
    assert saved['schema_version'] == 'srg-ledger-v2'
    assert saved['deadline_unix'] is None
    now[0], wall[0] = 20, 5005
    restored = SharedLedger.from_state(saved, clock=lambda: now[0], wall_clock=lambda: wall[0])
    assert restored.snapshot()['elapsed_seconds'] == 4005
    restored.claim_tool_call()
    restored.settle_request(request, 3)
    assert restored.snapshot()['charged_tokens'] == 3
    now[0], wall[0] = 25, 5010
    assert restored.snapshot()['elapsed_seconds'] == 4010


def test_legacy_v1_checkpoint_remains_finite():
    ledger = SharedLedger(AgentBudget(max_model_calls=1), wall_clock=lambda: 1000)
    ledger.claim_model_call()
    saved = ledger.export_state()
    assert saved['schema_version'] == 'srg-ledger-v1'
    saved['budget'].pop('regime', None)
    restored = SharedLedger.from_state(saved, wall_clock=lambda: 1001)
    assert restored.budget.regime == 'budgeted'
    with pytest.raises(BudgetExhausted):
        restored.claim_model_call()


@pytest.mark.parametrize('mutation', ['deadline', 'version', 'implicit', 'finalization', 'counts', 'unknown_flag'])
def test_unbudgeted_checkpoint_rejects_ambiguous_or_corrupt_state(mutation):
    ledger = SharedLedger(AgentBudget.unbudgeted(), wall_clock=lambda: 1000)
    ledger.claim_model_call(reserved_output_tokens=None)
    state = copy.deepcopy(ledger.export_state())
    if mutation == 'deadline':
        state['deadline_unix'] = 999999
    elif mutation == 'version':
        state['schema_version'] = 'srg-ledger-v1'
    elif mutation == 'implicit':
        state['budget'].pop('regime')
    elif mutation == 'finalization':
        state['finalization_only'] = True
    elif mutation == 'counts':
        state['counts']['reserved_tokens'] = 1
    else:
        state['requests']['1']['output_bound_unknown'] = 1
    with pytest.raises(ValueError):
        SharedLedger.from_state(state, wall_clock=lambda: 1001)


def test_checkpoint_regime_change_is_rejected():
    state = SharedLedger(AgentBudget.unbudgeted()).export_state()
    with pytest.raises(ValueError, match='budget'):
        SharedLedger.from_state(state, budget=AgentBudget())


def test_shared_resource_projection_and_admission():
    from synthesis_route_gym.resource_policy import advisor_admissible, agent_resources
    ledger = SharedLedger(AgentBudget.unbudgeted())
    resources = agent_resources(ledger)
    assert resources == {'regime': 'unbudgeted', 'remaining_model_calls': None,
        'remaining_tool_calls': None, 'remaining_tokens': None, 'remaining_seconds': None}
    assert advisor_admissible(ledger, resources, 'proposal')
    with pytest.raises(ValueError):
        advisor_admissible(ledger, {**resources, 'remaining_tokens': 1}, 'proposal')
    with pytest.raises(ValueError):
        advisor_admissible(ledger, {key: value for key, value in resources.items() if key != 'regime'}, 'proposal')
    finite = SharedLedger(AgentBudget())
    assert 'regime' not in agent_resources(finite)
    assert advisor_admissible(finite, agent_resources(finite), 'proposal')
    finite.finalization_only = True
    assert not advisor_admissible(finite, agent_resources(finite), 'proposal')


@pytest.mark.parametrize('limit,used,expected', [(None, 5, None), (10, 3, 7), (10, 20, 0), (1.5, .5, 1)])
def test_remaining(limit, used, expected):
    from synthesis_route_gym.resource_policy import remaining
    assert remaining(limit, used) == expected


@pytest.mark.parametrize('limit,used', [(True, 0), (1, True), (float('inf'), 0), (None, float('nan')), (-1, 0), (1, -1)])
def test_remaining_rejects_bad_values(limit, used):
    from synthesis_route_gym.resource_policy import remaining
    with pytest.raises(ValueError):
        remaining(limit, used)


@pytest.mark.parametrize('changes', [{'max_model_calls': 3}, {'max_tool_calls': 4},
    {'wall_seconds': 5}, {'max_total_tokens': 6}, {'regime': 'budgeted'}])
def test_unbudgeted_factory_refuses_contradictory_arguments(changes):
    with pytest.raises(ValueError):
        AgentBudget.unbudgeted(**changes)


@pytest.mark.parametrize('key,value', [('remaining_model_calls', 2), ('remaining_tool_calls', 2),
    ('remaining_tokens', 1), ('remaining_seconds', 1)])
def test_finite_advisor_guards_still_apply(key, value):
    from synthesis_route_gym.resource_policy import advisor_admissible, agent_resources
    ledger = SharedLedger(AgentBudget())
    assert not advisor_admissible(ledger, {**agent_resources(ledger), key: value}, 'proposal')


@pytest.mark.parametrize('resources', [None, {}, {'regime': 'budgeted'},
    dict.fromkeys(('remaining_model_calls', 'remaining_tool_calls', 'remaining_tokens', 'remaining_seconds'))])
def test_advisor_rejects_invalid_finite_resource_projection(resources):
    from synthesis_route_gym.resource_policy import advisor_admissible
    with pytest.raises(ValueError):
        advisor_admissible(SharedLedger(AgentBudget()), resources, 'proposal')


def test_advisor_rejects_nontext_prompt_even_if_unbudgeted():
    from synthesis_route_gym.resource_policy import advisor_admissible, agent_resources
    ledger = SharedLedger(AgentBudget.unbudgeted())
    with pytest.raises(ValueError):
        advisor_admissible(ledger, agent_resources(ledger), None)


def test_unbudgeted_resume_rejects_missing_requests_and_preserves_failure_accounting():
    ledger = SharedLedger(AgentBudget.unbudgeted(), wall_clock=lambda: 1000)
    request = ledger.claim_model_call(estimated_input_tokens=23, reserved_output_tokens=None)
    ledger.record_request_failure(request, {'category': 'transport'})
    state = ledger.export_state()
    broken = {**state, 'counts': {**state['counts'], 'model_calls': 10000}}
    with pytest.raises(ValueError, match='identities'):
        SharedLedger.from_state(broken, wall_clock=lambda: 1001)
    resumed = SharedLedger.from_state(state, wall_clock=lambda: 1002)
    assert resumed.snapshot()['unsettled_requests'] == 1
    assert resumed.snapshot()['reserved_tokens'] == 23
    assert resumed.export_state()['requests']['1']['failure'] == {'category': 'transport'}
