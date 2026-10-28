"""Absent research ceilings retain real accounting and private query boundaries."""
from dataclasses import replace
import json
import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Budget
from synthesis_route_gym.scientific_execution import ScientificLimits
from synthesis_route_gym.condition_episode import ConditionEpisode
from synthesis_route_gym.episode_store import EpisodeStore
from synthesis_route_gym.application_actions import _observation_resources
from test_core import make_task
from test_condition_episode import study


def unlimited_task():
    return make_task(budget=Budget.unbudgeted())


def test_unbudgeted_route_actions_expansions_time_and_restore(tmp_path):
    now = [0.]
    options = dict(clock=lambda: now[0], wall_clock=lambda: 1000 + now[0],
                   expand=lambda *args: {'status': 'ok', 'predictions': []})
    path = tmp_path / 'episode.json'
    env = SynthesisRouteEnv(unlimited_task(), **options)
    now[0] = 10**7
    for index in range(205):
        result = env.dispatch('expand', {'smiles': 'CCO'}, action_id=str(index))
        assert result['status'] == 'ok' and not result['truncated']
    assert result['usage']['expansions'] == 205
    assert env.dispatch('expand', {'smiles': 'CCO'}, action_id='204') == result
    # Persistence is a separate boundary: avoid rewriting the entire historical
    # hash chain hundreds of times just to exercise absent admission ceilings.
    env = SynthesisRouteEnv(unlimited_task(), store=path, **options)
    now[0] += 10**7
    assert env.dispatch('expand', {'smiles':'CCO'}, action_id='persisted')['status'] == 'ok'
    saved, _ = EpisodeStore(path).load()
    assert saved['checkpoint_version'] == 3 and saved['deadline_at'] is None
    now[0] += 10**7
    resumed = SynthesisRouteEnv.resume(path, expected_task=unlimited_task(), **options)
    assert resumed.dispatch('capabilities', {})['status'] == 'ok'
    assert resumed.inspect()['usage']['wall_seconds'] >= 2 * 10**7
    assert resumed.inspect()['usage']['expansions'] == 1
    assert resumed.dispatch('submit', {'route_ids': []})['terminated']
    json.dumps(resumed.export(), allow_nan=False)


def test_unbudgeted_scientific_limits_and_mixed_regimes():
    assert ScientificLimits(None, None).observation_calls is None
    assert ScientificLimits(0, 0).retrieval_calls == 0
    for value in (True, -1, 1.5, float('inf')):
        with pytest.raises(ValueError):
            ScientificLimits(value, None)
    with pytest.raises(ValueError, match='unbudgeted'):
        SynthesisRouteEnv(unlimited_task(), scientific_limits=ScientificLimits(1, 0))
    with pytest.raises(ValueError, match='budgeted'):
        SynthesisRouteEnv(make_task(), scientific_limits=ScientificLimits(None, 0))


def test_unbudgeted_condition_pool_stays_private_and_accounted(tmp_path):
    source = study(budget=None)
    assert source.view()['remaining_budget'] is None
    assert len(source.view()['observations']) == 1
    with pytest.raises(ValueError, match='Unknown'):
        source.observe('outside')
    assert len(source.observe('b').observe('c').view()['observations']) == 3
    now = [0.]
    options = dict(study_id='unlimited', regime='unbudgeted', max_actions=None,
                   wall_seconds=None, clock=lambda: now[0], wall_clock=lambda: 1000 + now[0])
    path = tmp_path / 'conditions.json'
    env = ConditionEpisode(source, **options)
    now[0] = 10**7
    for _ in range(85):
        assert env.dispatch('inspect', {})['status'] == 'ok'
    resource = env.public_view()['resources']
    assert resource['regime'] == 'unbudgeted'
    assert resource['remaining_actions'] is resource['remaining_seconds'] is resource['remaining_observations'] is None
    env = ConditionEpisode(source, store=path, **options)
    now[0] += 10**7
    assert env.dispatch('observe_condition', {'candidate_id': 'b'}, 'b')['status'] == 'ok'
    saved, _ = EpisodeStore(path).load()
    assert saved['schema_version'] == 'srg-condition-episode-v2' and saved['deadline'] is None
    now[0] += 10**7
    resumed = ConditionEpisode.resume(path, source, **options)
    assert resumed.public_view()['usage']['wall_seconds'] >= 2 * 10**7
    assert resumed.dispatch('observe_condition', {'candidate_id': 'c'}, 'c')['status'] == 'ok'
    assert resumed.public_view()['resources']['remaining_candidates'] == 0
    assert resumed.export()['stop_reason'] == 'candidate_space_exhausted'
    assert resumed.export()['submission']['status'] == 'not_submitted'


def test_unbudgeted_condition_resources_preserve_actual_counts():
    from types import SimpleNamespace
    env = SimpleNamespace(_events=({'action': 'observe_condition', 'arguments': {'candidate_id': 'b'}},),
                          _pending=None, _scientific_usage={'observe_condition': 1},
                          _scientific_limits=ScientificLimits(0, None))
    resource = _observation_resources(env, study(budget=None))
    assert resource['regime'] == 'unbudgeted'
    assert resource['call_limit'] is resource['remaining_calls'] is None
    assert resource['calls_used'] == 1 and resource['attempted_candidate_ids'] == ['a', 'b']


@pytest.mark.parametrize('changes', [dict(max_actions=80), dict(wall_seconds=600), dict(study=study())])
def test_condition_mixed_regime_rejected(changes):
    args = dict(study=study(budget=None), study_id='x', regime='unbudgeted', max_actions=None, wall_seconds=None)
    with pytest.raises(ValueError):
        ConditionEpisode(**(args | changes))
