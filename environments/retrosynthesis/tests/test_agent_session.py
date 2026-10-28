"""Durable bridge orchestration without live models."""
from types import SimpleNamespace
import pytest
from test_core import make_task
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.agent_session import run_persistent_agent


@pytest.fixture(autouse=True)
def isolated_main_profile(tmp_path,monkeypatch):
    from synthesis_route_gym.agent_runner import MainProfile
    monkeypatch.setattr('synthesis_route_gym.agent_session.resolve_main_profile',
        lambda home:MainProfile(tmp_path/'profile','fixture-model','fixture-provider'))


def config():
    return SimpleNamespace(model_calls=12, scientist_python='/trusted/python', scientist_source='/trusted/source',
                           profile_home=None, method='main')


def test_checkpoints_survive_restart_and_resume_consumption(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task(), store=tmp_path/'env')
    def first(prompt, executor, **kw):
        assert 'Task summary:' in prompt
        kw['checkpoint']({'ledger': {'actual_tokens': 123, 'model_calls': 1}})
        return {'completed': False}
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', first)
    run_persistent_agent(config(), env, tmp_path/'runtime')
    def second(prompt, executor, **kw):
        assert kw['resume_state']['ledger']['actual_tokens'] == 123
        kw['action_executor']('submit', {'route_ids': []}, action_id='submit-1')
        return {'completed': True}
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', second)
    resumed = SynthesisRouteEnv.resume(tmp_path/'env', expected_task=make_task())
    report = run_persistent_agent(config(), resumed, tmp_path/'runtime', resume=True)
    assert report['episode']['terminated']
    assert report['submission_status'] == 'submitted_empty'


def test_resume_closed_episode_does_not_spawn_or_fabricate_submission(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task(), store=tmp_path/'env')
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: {'completed':False})
    run_persistent_agent(config(), env, tmp_path/'runtime')
    env.cancel('test')
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: pytest.fail('closed episode launched'))
    report = run_persistent_agent(config(), env, tmp_path/'runtime', resume=True)
    assert report['submission_status'] == 'not_submitted'


def test_bridge_failure_returns_auditable_partial_report(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    from synthesis_route_gym.agent_bridge import BridgeError
    env = SynthesisRouteEnv(make_task(), store=tmp_path/'env')
    def failed(*a, **kw):
        kw['checkpoint']({'ledger': {'reserved_tokens': 1000}})
        kw['cancel']('bridge_interrupted')
        raise BridgeError('runtime timeout')
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', failed)
    report = run_persistent_agent(config(), env, tmp_path/'runtime')
    assert report['agent']['error_type'] == 'BridgeError'
    assert report['runtime_checkpoint']['ledger']['reserved_tokens'] == 1000
    assert report['submission_status'] == 'not_submitted'


def test_changed_mode_cannot_resume_runtime(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task())
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: {'completed':False})
    run_persistent_agent(config(), env, tmp_path/'runtime')
    args = config(); args.method = 'specialists'
    with pytest.raises(ValueError, match='binding'):
        run_persistent_agent(args, env, tmp_path/'runtime', resume=True)


def test_changed_chemistry_configuration_cannot_resume(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task())
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: {'completed':False})
    args = config(); args.timeout = 30; args.condition_model = None
    run_persistent_agent(args, env, tmp_path/'runtime')
    args.timeout = 60
    with pytest.raises(ValueError, match='binding'):
        run_persistent_agent(args, env, tmp_path/'runtime', resume=True)


def test_changed_model_bytes_cannot_resume(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task())
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: {'completed':False})
    model = tmp_path/'model.json'; model.write_text('{}')
    args = config(); args.condition_model = str(model)
    run_persistent_agent(args, env, tmp_path/'runtime')
    model.write_text('{"changed":true}')
    with pytest.raises(ValueError, match='binding'):
        run_persistent_agent(args, env, tmp_path/'runtime', resume=True)


def test_expired_environment_never_launches_model(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    now = [0.0]
    env = SynthesisRouteEnv(make_task(), clock=lambda: now[0])
    now[0] = env.task.budget.max_wall_seconds + 1
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: pytest.fail('expired environment launched'))
    report = run_persistent_agent(config(), env, tmp_path/'runtime')
    assert report['episode']['truncated']
    assert report['submission_status'] == 'not_submitted'


def test_host_policy_forwarded_and_changed_policy_cannot_resume(tmp_path, monkeypatch):
    import json
    import synthesis_route_gym.agent_session as session
    env = SynthesisRouteEnv(make_task())
    seen = []
    def bridge(*args, **kwargs):
        seen.append(kwargs['orchestration_policy'])
        return {'completed': False}
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', bridge)
    args = config(); args.method = 'main_adaptive'
    policy = tmp_path / 'policy.json'; policy.write_text('{}')
    args.orchestration_policy = str(policy)
    run_persistent_agent(args, env, tmp_path / 'runtime')
    assert seen[0]['enabled_roles'] == []
    policy.write_text(json.dumps({'enabled_roles': ['route_critic'], 'experimental': True, 'max_consultations': 1}))
    with pytest.raises(ValueError, match='binding'):
        run_persistent_agent(args, env, tmp_path / 'runtime', resume=True)
    assert len(seen) == 1


def test_main_mode_rejects_orchestration_policy_before_bridge(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    monkeypatch.setattr(session, 'run_agent_scientist_bridge', lambda *a, **kw: pytest.fail('policy bypass'))
    args = config(); policy = tmp_path / 'policy.json'; policy.write_text('{}')
    args.orchestration_policy = str(policy)
    with pytest.raises(ValueError, match='mode'):
        run_persistent_agent(args, SynthesisRouteEnv(make_task()), tmp_path / 'runtime')
