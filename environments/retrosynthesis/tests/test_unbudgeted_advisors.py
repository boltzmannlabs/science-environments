"""Explicit unlimited resources retain bounded, evidence-grounded advice policy."""
from copy import deepcopy
import json
import pytest
from synthesis_route_gym import condition_scientist as condition
from synthesis_route_gym import route_condition_advice as route_condition
from synthesis_route_gym import route_critic as critic
from synthesis_route_gym import strategist
from test_condition_scientist import view, state as condition_state, plan as condition_plan
from test_route_condition_advice import catalog, ingest, plan as route_plan
from test_strategist import result, expansion, plan as strategist_plan, stalled, RESOURCES

UNLIMITED = {**dict.fromkeys(RESOURCES), 'regime': 'unbudgeted'}


def unlimited_catalog(**kwargs):
    value = catalog(**kwargs)
    return {**value, 'observation_resources': {**value['observation_resources'],
        'regime': 'unbudgeted', 'call_limit': None, 'remaining_calls': None}}


def unlimited_view():
    value = view()
    return {**value, 'resources': {**value['resources'], 'regime': 'unbudgeted',
        'remaining_observations': None, 'remaining_actions': None, 'remaining_seconds': None}}


def test_unlimited_condition_context_plan_and_identity():
    current = condition.build_context(condition_state(unlimited_view()), UNLIMITED)
    assert current['resources'] == UNLIMITED
    assert condition.parse_plan(json.dumps(condition_plan(current)), current)['next_candidate_id'] == 'c'
    changed = deepcopy(current)
    changed['resources'] = RESOURCES
    assert condition.context_fingerprint(current) != condition.context_fingerprint(changed)


def test_unlimited_condition_finite_pool_is_checked():
    raw = unlimited_view()
    raw['resources']['remaining_candidates'] = 2
    assert condition.build_context(condition_state(raw), UNLIMITED)['view']['resources']['remaining_candidates'] == 2
    raw['resources']['remaining_candidates'] = 3
    with pytest.raises(ValueError):
        condition_state(raw)


def test_critic_unlimited_context_retains_typed_evidence():
    from test_route_critic import packet, report
    current = critic.build_context(packet(), UNLIMITED)
    assert current['resources'] == UNLIMITED
    parsed = critic.parse_report(json.dumps(report(current)), current)
    assert critic.hydrate_report(parsed, current)['findings'][0]['supporting_facts']


@pytest.mark.parametrize('model', [condition.RuntimeResources, critic.Resources])
def test_resource_contract_explicit_nulls_and_finite_compatibility(model):
    assert model.model_validate(RESOURCES).model_dump(mode='json') == RESOURCES
    assert model.model_validate(UNLIMITED).model_dump(mode='json') == UNLIMITED
    for bad in (dict.fromkeys(RESOURCES), {**UNLIMITED, 'remaining_tokens': 1},
                {**UNLIMITED, 'regime': 'budgeted'}, {**UNLIMITED, 'regime': 'unknown'}):
        with pytest.raises(ValueError):
            model.model_validate(bad)


def test_unlimited_condition_observer_rejects_regime_switch_but_accepts_counts():
    before = condition_state(unlimited_view())
    later = unlimited_view()
    later['revision'] += 1
    later['resources']['new_observations_used'] += 1
    later['usage']['observation_calls'] += 1
    after = condition.observe(before, 'inspect', {}, {'status': 'ok', 'result': later})
    assert after['view']['resources']['new_observations_used'] == 3
    with pytest.raises(ValueError):
        condition.observe(before, 'inspect', {}, {'status': 'ok', 'result': view()})


def test_unlimited_route_feedback_uses_finite_candidates_and_actual_charges():
    value = unlimited_catalog()
    current = route_condition.build_context(ingest(value), UNLIMITED)
    assert current['resources'] == UNLIMITED
    assert route_condition.parse_plan(json.dumps(route_plan(current)), current)['next_candidate_id'] == 'c'
    after = ingest(unlimited_catalog(used=7, attempted=('a', 'b', 'c')), state=ingest(value))
    assert route_condition.eligibility(after)['eligible']
    exhausted = ingest(unlimited_catalog(used=8, attempted=('a', 'b', 'c', 'd')))
    assert route_condition.eligibility(exhausted)['reason'] == 'no_unqueried_candidate'
    assert not route_condition.eligibility(ingest(unlimited_catalog(observed=('a',))))['eligible']
    with pytest.raises(ValueError):
        ingest(catalog(), state=ingest(value))


def test_unlimited_route_observation_requires_explicit_regime():
    raw = unlimited_catalog()
    del raw['observation_resources']['regime']
    with pytest.raises(ValueError):
        ingest(raw)


def test_unlimited_strategist_host_expansion_budget_and_plan():
    state = strategist.observe(strategist.observer_state(), 'inspect', {}, result({'task': {
        'target': 'CCOC', 'constraints': {'max_steps': 4},
        'budget': {'regime': 'unbudgeted', 'max_expansions': None}}}))
    state = expansion(state, 'CCOC', ('CCO', 'C'))
    state = expansion(expansion(state, 'CCO', status='error'), 'CCO', status='error')
    current = strategist.build_context(state, UNLIMITED)
    assert current['resources'] == {**UNLIMITED, 'remaining_expansions': None}
    assert strategist.parse_plan(json.dumps(strategist_plan(current)), current)['action_allowance'] == 1
    with pytest.raises(ValueError):
        strategist.observe(state, 'inspect', {}, result({'task': {'target': 'CCOC',
            'constraints': {}, 'budget': {'max_expansions': 12}}}))


def test_zero_remains_exhausted_and_unknown_is_not_unlimited():
    assert strategist.build_context(stalled(), {**RESOURCES, 'remaining_tool_calls': 0}) is None
    assert condition.build_context(condition_state(), {**RESOURCES, 'remaining_seconds': 0}) is None
    assert route_condition.build_context(ingest(), {**RESOURCES, 'remaining_tokens': 0}) is None
    with pytest.raises(ValueError):
        strategist.build_context(stalled(), dict.fromkeys(RESOURCES))


@pytest.mark.parametrize('kind', ['normal', 'error', 'malformed'])
def test_unlimited_runtime_same_profile_one_shot_and_failed_calls_consumed(kind):
    from synthesis_route_gym.agent_accounting import AgentBudget
    from test_route_condition_runtime import Harness
    from synthesis_route_gym import route_condition_runtime
    h = Harness(kind, budget=AgentBudget.unbudgeted())
    answer = h.invoke(unlimited_catalog())
    assert answer['route_condition_advice']['status'] == {
        'normal': 'accepted', 'error': 'failed', 'malformed': 'rejected'}[kind]
    assert h.ledger.snapshot()['model_calls'] == 1
    assert h.backend.calls[0]['model_call_limit'] == 1
    assert h.backend.calls[0]['tool_schemas'] == []
    h.invoke(unlimited_catalog())
    assert len(h.backend.calls) == 1
    restored = route_condition_runtime.restore_state(h.state)
    assert restored['consultation']['status'] == answer['route_condition_advice']['status']


@pytest.mark.parametrize('role', ['strategist', 'condition_scientist', 'route_critic'])
def test_each_unlimited_advisor_uses_actual_context_and_shared_profile(role):
    import importlib
    from types import SimpleNamespace
    from synthesis_route_gym.agent_accounting import AgentBudget, SharedLedger
    from test_route_critic import packet, report
    module = importlib.import_module('synthesis_route_gym.' + role + '_runtime')
    ledger = SharedLedger(AgentBudget.unbudgeted())
    profile = SimpleNamespace(model='main-profile-model', provider='main-profile-provider')
    state = module.initial_state()
    if role == 'strategist':
        state['observer'] = stalled()
        payload, action, factory = {}, 'inspect', strategist_plan
    elif role == 'condition_scientist':
        payload, action, factory = unlimited_view(), 'inspect', condition_plan
    else:
        payload, action, factory = packet(), 'review_routes', report
    calls = []

    class Backend:
        def run(self, **kwargs):
            calls.append(kwargs)
            assert kwargs['ledger'] is ledger and kwargs['profile'] is profile
            assert kwargs['model_call_limit'] == 1 and kwargs['tool_schemas'] == []
            current = json.loads(kwargs['prompt'].split('Host context: ', 1)[1])
            assert current['resources']['remaining_model_calls'] is None
            request = ledger.claim_model_call(estimated_input_tokens=20, reserved_output_tokens=20)
            ledger.settle_request(request, 12)
            return {'model': profile.model, 'provider': profile.provider, 'completed': True,
                'final_response': json.dumps(factory(current)), 'messages': [],
                'usage': {'total_tokens': 12}, 'token_confirmations': {request: 12}}

    saved = []
    response = {'status': 'ok', 'result': payload}
    module.after_tool(action, {}, response, state=state, update=saved.append,
                      runtime=Backend(), profile=profile, ledger=ledger)
    assert saved[-1]['consultation']['status'] == 'accepted'
    assert ledger.snapshot()['model_calls'] == 1 and ledger.snapshot()['actual_tokens'] == 12
    restored = module.restore_state(saved[-1])
    module.after_tool(action, {}, response, state=restored, update=saved.append,
                      runtime=Backend(), profile=profile, ledger=ledger)
    assert len(calls) == 1 and ledger._role == 'main'


@pytest.mark.parametrize('mode,expected', [('main_all_advisors', 1), ('main_adaptive', 0)])
def test_unlimited_orchestration_preserves_role_policy(mode, expected):
    from synthesis_route_gym import orchestration_runtime as host
    from test_route_condition_runtime import Harness, PROFILE, ARGS
    from synthesis_route_gym.agent_accounting import AgentBudget
    h = Harness(budget=AgentBudget.unbudgeted())
    saved = []
    host.after_tool('condition_options', ARGS, {'status': 'ok', 'result': unlimited_catalog()},
        state=host.initial_state(mode), update=saved.append,
        runtime=h.backend, profile=PROFILE, ledger=h.ledger)
    assert len(h.backend.calls) == expected
    assert h.ledger.snapshot()['model_calls'] == expected
    restored = host.restore_state(saved[-1], mode=mode)
    host.after_tool('condition_options', ARGS, {'status': 'ok', 'result': unlimited_catalog()},
        state=restored, update=saved.append, runtime=h.backend, profile=PROFILE, ledger=h.ledger)
    assert len(h.backend.calls) == expected
