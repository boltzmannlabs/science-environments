"""Advisor observations expose charged attempts, without revealing hidden outcomes."""
import json
from test_application_integration import condition_env


ARGS = {'route_id': 'r1', 'step_id': 'stored-step'}


def test_catalog_exposes_real_allowance_and_page_identity():
    env, _, _, _ = condition_env()
    catalog = env.dispatch('condition_options', {**ARGS, 'offset': 1, 'limit': 1})['result']
    assert catalog['offset'] == 1
    assert catalog['application_configuration_sha256'] == env._application_fingerprint
    assert catalog['observation_resources'] == {
        'schema_version': 'srg-route-observation-resources-v1', 'calls_used': 0,
        'call_limit': 2, 'remaining_calls': 2, 'attempted_candidate_ids': []}
    assert 'yield_percent' not in json.dumps(catalog)


def test_post_observation_catalog_includes_current_measurement_once():
    env, _, _, _ = condition_env()
    response = env.dispatch('observe_route_condition', {**ARGS, 'candidate_id': 'a'}, action_id='one')
    catalog = response['result']['condition_catalog']
    assert catalog['offset'] == 0 and catalog['candidate_count'] == 2
    assert [row['candidate_id'] for row in catalog['observations']] == ['a']
    assert catalog['observation_resources']['calls_used'] == 1
    assert catalog['observation_resources']['attempted_candidate_ids'] == ['a']
    assert catalog['observation_resources']['remaining_calls'] == 1
    assert '87.75' not in json.dumps(response)
    assert env.dispatch('observe_route_condition', {**ARGS, 'candidate_id': 'a'}, action_id='one') == response


def test_failed_primitive_attempt_consumes_shared_allowance():
    env, _, _, _ = condition_env()
    assert env.dispatch('observe_condition', {'candidate_id': 'missing'})['status'] == 'error'
    catalog = env.dispatch('condition_options', ARGS)['result']
    assert catalog['observation_resources']['calls_used'] == 1
    assert catalog['observation_resources']['remaining_calls'] == 1
    assert catalog['observation_resources']['attempted_candidate_ids'] == ['missing']
    assert catalog['observations'] == []


def test_duplicate_attempt_never_restores_observation_allowance():
    env, _, _, _ = condition_env()
    env.dispatch('observe_route_condition', {**ARGS, 'candidate_id': 'a'})
    assert env.dispatch('observe_route_condition', {**ARGS, 'candidate_id': 'a'})['status'] == 'error'
    catalog = env.dispatch('condition_options', ARGS)['result']
    assert catalog['observation_resources']['remaining_calls'] == 0
    assert catalog['observation_resources']['calls_used'] == 2
    assert catalog['observation_resources']['attempted_candidate_ids'] == ['a']


def test_failed_admitted_query_keeps_catalog_and_accounting():
    env, _, _, _ = condition_env()
    env.dispatch('observe_condition', {'candidate_id': 'missing'})
    env.dispatch('observe_condition', {'candidate_id': 'missing-again'})
    response = env.dispatch('observe_route_condition', {**ARGS, 'candidate_id': 'b'})
    assert response['status'] == 'error'
    catalog = response['result']['condition_catalog']
    assert catalog['observation_resources']['calls_used'] == 3
    assert catalog['observation_resources']['remaining_calls'] == 0
    assert catalog['observations'] == []
    assert '87.75' not in json.dumps(catalog)
