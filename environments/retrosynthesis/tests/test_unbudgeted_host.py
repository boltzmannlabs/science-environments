"""Host boundaries opt in explicitly without weakening evidence permissions."""
import json
from dataclasses import replace
import pytest
from fastapi.testclient import TestClient
from test_core import make_task, make_route


def test_task_conversion_preserves_inputs_and_rejects_implicit_reverse():
    from synthesis_route_gym.host_policy import task_regime
    original = make_task()
    converted = task_regime(original, 'unbudgeted')
    assert original.budget.max_actions == 200
    assert converted.budget.regime == 'unbudgeted'
    assert converted.budget.max_actions is None
    assert converted.inventory == original.inventory
    assert converted.constraints == original.constraints
    assert task_regime(converted, None) == converted
    with pytest.raises(ValueError):
        task_regime(converted, 'budgeted')
    with pytest.raises(ValueError):
        task_regime(original, 'infinite')


def test_science_conversion_retains_disabled_permissions_and_candidate_pool():
    from synthesis_route_gym.host_policy import science_regime
    from synthesis_route_gym.scientific_execution import ScientificLimits
    from synthesis_route_gym.portfolio_conditions import FiniteConditionStudy, ConditionRecord
    study = FiniteConditionStudy((ConditionRecord('a', (('base', 'N'),), 12),), (), 1,
                                 'https://example.org', 'fixture', 'a'*64, 'CCO')
    source = {'scientific_limits': ScientificLimits(0, 1), 'condition_study': study,
              'source_access_mode': 'closed_information'}
    result = science_regime(source, 'unbudgeted')
    assert result['scientific_limits'].retrieval_calls == 0
    assert result['scientific_limits'].observation_calls is None
    assert result['source_access_mode'] == 'closed_information'
    assert result['condition_study'] == replace(study, budget=None)
    assert source['condition_study'].budget == 1
    assert science_regime(source, 'budgeted') == source


def test_cli_unbudgeted_replay_and_conflicting_limits(tmp_path):
    from synthesis_route_gym.cli import _parser, execute
    task = tmp_path/'task.json'
    task.write_text(make_task().model_dump_json())
    actions = tmp_path/'actions.json'
    actions.write_text(json.dumps([
        {'action': 'propose_route', 'arguments': {'route': make_route().model_dump(mode='json')}},
        {'action': 'submit', 'arguments': {'route_ids': ['r1']}}]))
    common = ['--task', str(task), '--output', str(tmp_path/'out.json'), '--budget-regime', 'unbudgeted']
    result = execute(_parser().parse_args(['replay', *common, '--actions', str(actions)]))
    assert result['terminated'] and not result['truncated']
    assert result['task']['budget']['regime'] == 'unbudgeted'
    with pytest.raises(ValueError, match='unbudgeted'):
        execute(_parser().parse_args(['plan', *common, '--max-frontier-states', '100']))
    with pytest.raises(ValueError, match='unbudgeted'):
        execute(_parser().parse_args(['agent', *common, '--model-calls', '10',
                                      '--scientist-python', 'python', '--scientist-source', '.']))


def test_api_unbudgeted_requires_host_optin_and_has_no_episode_expiry():
    from synthesis_route_gym.api import create_app
    from synthesis_route_gym.schemas import Budget
    task = make_task(budget=Budget.unbudgeted()).model_dump(mode='json')
    headers = {'Authorization': 'Bearer local-fixture-token'}
    closed = TestClient(create_app({'local-fixture-token': 'user'}))
    assert closed.post('/v1/episodes', json={'task': task}, headers=headers).status_code == 422
    now = [0.0]
    client = TestClient(create_app({'local-fixture-token': 'user'}, allow_unbudgeted=True,
                                   clock=lambda: now[0]))
    result = client.post('/v1/episodes', json={'task': task}, headers=headers)
    assert result.status_code == 201, result.text
    episode_id = result.json()['data']['episode_id']
    now[0] = 1e9
    assert client.get(f'/v1/episodes/{episode_id}', headers=headers).status_code == 200


def test_unbudgeted_handoff_is_not_budget_exhausted(tmp_path, monkeypatch):
    from synthesis_route_gym.schemas import Budget
    from synthesis_route_gym.handoff_runner import run_handoff
    from test_handoff import payload
    from test_handoff_runner import args, submit
    from synthesis_route_gym.agent_runner import MainProfile
    monkeypatch.setattr('synthesis_route_gym.handoff_runner.resolve_main_profile',
                        lambda home: MainProfile(tmp_path, 'fixture', 'fixture'))
    request = {**payload(), 'budget': Budget.unbudgeted().model_dump(mode='json')}
    result = run_handoff(args(model_calls=None), request, tmp_path/'run', agent_runner=submit)
    assert result['feedback']['execution_status'] == 'completed'
    assert result['feedback']['submission_status'] == 'submitted_routes'
    with pytest.raises(ValueError, match='allowance'):
        run_handoff(args(model_calls=3), request, tmp_path/'bad', agent_runner=submit)


def test_tool_timeout_remains_finite_in_unbudgeted_mode():
    from synthesis_route_gym.host_policy import tool_timeout
    assert tool_timeout(60, None) == 60
    assert tool_timeout(60, 10) == 10
    for value in (None, 0, -1, float('inf'), True):
        with pytest.raises(ValueError):
            tool_timeout(value, None)
