"""Durable episodes preserve allowances and never replay uncertain work."""
import json
import threading
import time

import pytest

from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.episode_store import EpisodeStore, StoreConflict
from synthesis_route_gym.schemas import Budget
from test_core import make_task, make_route


def test_resume_preserves_routes_budget_and_idempotent_submission(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    env = SynthesisRouteEnv(make_task(), store=store)
    args = {'route': make_route().model_dump(mode='json')}
    first = env.dispatch('propose_route', args, action_id='proposal-1')
    recovered = SynthesisRouteEnv.resume(store)
    assert recovered.dispatch('propose_route', args, action_id='proposal-1') == first
    assert recovered.inspect()['usage']['actions'] == 1
    result = recovered.dispatch('submit', {'route_ids': ['r1']}, action_id='submit-1')
    again = SynthesisRouteEnv.resume(store)
    assert again.dispatch('submit', {'route_ids': ['r1']}, action_id='submit-1') == result
    assert again.inspect()['usage']['actions'] == 2
    with pytest.raises(ValueError, match='payload'):
        again.dispatch('submit', {'route_ids': []}, action_id='submit-1')


def test_downtime_counts_and_resuming_does_not_reset_limits(tmp_path):
    now = [100.0]
    store = EpisodeStore(tmp_path / 'episode')
    env = SynthesisRouteEnv(make_task(budget=Budget(max_actions=2, max_wall_seconds=10)),
                            store=store, clock=lambda: 0.0, wall_clock=lambda: now[0])
    env.dispatch('inspect', {}, action_id='a')
    now[0] = 111.0
    recovered = SynthesisRouteEnv.resume(store, clock=lambda: 0.0, wall_clock=lambda: now[0])
    assert recovered.dispatch('inspect', {}, action_id='b')['status'] == 'budget_exhausted'
    assert recovered.inspect()['usage']['actions'] == 1
    assert recovered.inspect()['usage']['wall_seconds'] >= 11
    with pytest.raises(ValueError, match='reset'):
        recovered.reset()


def test_pending_is_written_before_callback_and_interrupted_work_never_repeats(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    calls = []
    def crash(*_):
        state, revision = store.load()
        assert state['pending_action']['action_id'] == 'expand-1'
        assert state['usage']['actions'] == state['usage']['expansions'] == 1
        calls.append(1)
        raise SystemExit('simulated interruption')
    env = SynthesisRouteEnv(make_task(), store=store, expand=crash)
    # BaseException propagates, leaving the durable pending reservation.
    with pytest.raises(SystemExit):
        env.dispatch('expand', {'smiles': 'CCO'}, action_id='expand-1')
    recovered = SynthesisRouteEnv.resume(store, expand=crash)
    reply = recovered.dispatch('expand', {'smiles': 'CCO'}, action_id='expand-1')
    assert reply['status'] == 'interrupted'
    assert calls == [1]
    assert recovered.inspect()['usage']['expansions'] == 1
    assert recovered.inspect()['truncated']


def test_cancel_is_bounded_and_late_result_cannot_mutate_state(tmp_path):
    entered, release, callback_finished = (threading.Event() for _ in range(3))
    def blocked(*_):
        entered.set()
        release.wait(10)
        callback_finished.set()
        return {'status': 'ok', 'predictions': [{'late': True}]}
    env = SynthesisRouteEnv(make_task(), store=EpisodeStore(tmp_path / 'episode'), expand=blocked)
    results = []
    thread = threading.Thread(target=lambda: results.append(env.dispatch('expand', {'smiles': 'CCO'}, action_id='work')))
    thread.start()
    try:
        assert entered.wait(5)
        env.cancel('operator stopped')
        thread.join(5)
        # Cancellation must return while the external callback remains blocked.
        # This checks the property without making fsync/scheduler latency an SLA.
        assert not thread.is_alive() and not callback_finished.is_set()
        assert results[0]['status'] == 'cancelled'
        before = env.export()
    finally:
        release.set()
        thread.join(5)
    assert callback_finished.wait(5)
    assert env.export()['events'] == before['events']
    assert env.inspect()['truncated']


def test_stale_writer_cannot_repeat_an_external_effect(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    calls = []
    def expand(*_):
        calls.append(1)
    env = SynthesisRouteEnv(make_task(), store=store, expand=expand)
    stale = SynthesisRouteEnv.resume(store, expand=expand)
    env.dispatch('inspect', {}, action_id='new')
    with pytest.raises(StoreConflict):
        stale.dispatch('expand', {'smiles': 'CCO'}, action_id='stale')
    assert calls == []


def test_store_detects_tampering_and_refuses_identity_change(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    SynthesisRouteEnv(make_task(), store=store)
    with pytest.raises(ValueError, match='task'):
        SynthesisRouteEnv.resume(store, expected_task=make_task(target='CC'))
    path = sorted((tmp_path / 'episode' / 'revisions').glob('*.json'))[-1]
    state = json.loads(path.read_text())
    state['state']['usage']['actions'] = 0.25
    path.write_text(json.dumps(state))
    with pytest.raises(ValueError, match='hash'):
        store.load()


def test_store_refuses_existing_path_and_changed_head(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    SynthesisRouteEnv(make_task(), store=store)
    with pytest.raises(FileExistsError):
        SynthesisRouteEnv(make_task(), store=store)
    state, revision = store.load()
    store.commit(state, expected_revision=revision)
    with pytest.raises(StoreConflict):
        store.commit(state, expected_revision=revision)


def test_blocked_callback_reaches_deadline_without_waiting_for_completion(tmp_path):
    release, entered, callback_finished = (threading.Event() for _ in range(3))
    now = [0.0]
    def blocked(*_):
        # Expire only after admission, independent of setup/checkpoint I/O time.
        now[0] = 0.2
        entered.set()
        release.wait(10)
        callback_finished.set()
        return {'status': 'ok'}
    clock, wall_clock = lambda: now[0], lambda: 100.0 + now[0]
    env = SynthesisRouteEnv(make_task(budget=Budget(max_wall_seconds=0.1)),
                            store=EpisodeStore(tmp_path / 'episode'),
                            expand=blocked, clock=clock, wall_clock=wall_clock)
    try:
        response = env.dispatch('expand', {'smiles': 'CCO'}, action_id='slow')
        assert response['status'] == 'budget_exhausted'
        assert entered.is_set() and not callback_finished.is_set()
        recovered = SynthesisRouteEnv.resume(tmp_path / 'episode', expand=env._expand,
                                            clock=clock, wall_clock=wall_clock)
        assert recovered.inspect()['usage']['expansions'] == 1
        assert recovered.dispatch('expand', {'smiles': 'CCO'}, action_id='slow') == response
    finally:
        release.set()


def test_concurrent_duplicate_call_has_one_effect(tmp_path):
    entered, release = threading.Event(), threading.Event()
    calls, results = [], []
    def expand(*_):
        calls.append(1)
        entered.set()
        release.wait(1)
        return {'status': 'ok', 'predictions': []}
    env = SynthesisRouteEnv(make_task(), store=tmp_path / 'episode', expand=expand)
    def execute():
        results.append(env.dispatch('expand', {'smiles': 'CCO'}, action_id='same'))
    first, second = threading.Thread(target=execute), threading.Thread(target=execute)
    first.start()
    assert entered.wait(1)
    second.start()
    release.set()
    first.join(1)
    second.join(1)
    assert len(results) == 2 and results[0] == results[1]
    assert calls == [1]
    assert env.inspect()['usage']['actions'] == 1


def test_cancelled_episode_remains_closed_after_restart(tmp_path):
    env = SynthesisRouteEnv(make_task(), store=tmp_path / 'episode')
    env.cancel('operator requested')
    resumed = SynthesisRouteEnv.resume(tmp_path / 'episode')
    assert resumed.inspect()['truncated']
    assert resumed.dispatch('expand', {'smiles': 'CCO'})['status'] == 'closed'
    with pytest.raises(ValueError, match='Cancellation'):
        resumed.cancel('')
    with pytest.raises(ValueError, match='action_id'):
        resumed.dispatch('inspect', {}, action_id=True)


@pytest.mark.parametrize('change', [
    lambda s: {**s, 'usage': {**s['usage'], 'actions': 0}},
    lambda s: {**s, 'deadline_at': s['deadline_at'] + 10},
    lambda s: {**s, 'task_sha256': 'wrong'},
    lambda s: {**s, 'submitted_route_ids': ['unknown']},
    lambda s: {**s, 'events': [{**s['events'][0], 'status': 'forged'}]},
])
def test_rehashed_malformed_state_fails_closed(tmp_path, change):
    store = EpisodeStore(tmp_path / 'episode')
    env = SynthesisRouteEnv(make_task(), store=store)
    env.dispatch('inspect', {}, action_id='a')
    state, revision = store.load()
    store.commit(change(state), expected_revision=revision)
    with pytest.raises(ValueError, match='checkpoint'):
        SynthesisRouteEnv.resume(store)


def test_store_rejects_symlink_or_orphan_revision(tmp_path):
    path = tmp_path / 'episode'
    store = EpisodeStore(path)
    SynthesisRouteEnv(make_task(), store=store)
    alias = tmp_path / 'alias'
    alias.symlink_to(path, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        EpisodeStore(alias)
    (path / 'revisions' / 'orphan.json').write_text('{}')
    with pytest.raises(ValueError, match='Uncommitted'):
        store.load()


def test_backward_wall_clock_refuses_resume(tmp_path):
    SynthesisRouteEnv(make_task(), store=tmp_path / 'episode', wall_clock=lambda: 100)
    with pytest.raises(ValueError, match='clock'):
        SynthesisRouteEnv.resume(tmp_path / 'episode', wall_clock=lambda: 90)


def test_elapsed_monotonic_time_plus_downtime_is_preserved(tmp_path):
    monotonic, wall = [0.0], [100.0]
    env = SynthesisRouteEnv(make_task(), store=tmp_path / 'episode',
                            clock=lambda: monotonic[0], wall_clock=lambda: wall[0])
    monotonic[0] = 8.0
    env.dispatch('inspect', {}, action_id='a')
    wall[0] = 105.0
    resumed = SynthesisRouteEnv.resume(tmp_path / 'episode', clock=lambda: 0.0, wall_clock=lambda: wall[0])
    assert resumed.inspect()['usage']['wall_seconds'] >= 13.0


def test_forged_receipt_fingerprint_is_rejected(tmp_path):
    store = EpisodeStore(tmp_path / 'episode')
    env = SynthesisRouteEnv(make_task(), store=store)
    env.dispatch('inspect', {}, action_id='a')
    state, revision = store.load()
    receipt = {**state['receipts']['a'], 'payload_sha256': 'forged'}
    store.commit({**state, 'receipts': {'a': receipt}}, expected_revision=revision)
    with pytest.raises(ValueError, match='receipt'):
        SynthesisRouteEnv.resume(store)
