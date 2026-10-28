"""Strategist selection is explicit and preserves the main-profile session contract."""
import json

import pytest

from synthesis_route_gym.cli import _parser, execute, main
from synthesis_route_gym.schemas import Task


def arguments(task='task.json', output='result.json'):
    return ['agent', '--task', str(task), '--output', str(output),
            '--scientist-python', '/trusted/scientist/python',
            '--scientist-source', '/trusted/scientist/source']


def test_strategist_is_explicit_and_existing_methods_remain_available():
    parser = _parser()
    assert parser.parse_args(arguments()).method == 'main'
    for method in ('main', 'specialists', 'main_strategist'):
        assert parser.parse_args(arguments() + ['--method', method]).method == method


@pytest.mark.parametrize('extra', [
    ['--method', 'strategist'], ['--method'],
    ['--strategist-model', 'another-model'],
])
def test_invalid_or_model_override_options_are_rejected(extra):
    with pytest.raises(SystemExit) as raised:
        _parser().parse_args(arguments() + extra)
    assert raised.value.code == 2


@pytest.mark.parametrize('missing', ['--scientist-python', '--scientist-source'])
def test_strategist_requires_the_same_scientist_runtime_inputs(missing):
    argv = arguments() + ['--method', 'main_strategist']
    index = argv.index(missing)
    del argv[index:index+2]
    with pytest.raises(SystemExit) as raised:
        _parser().parse_args(argv)
    assert raised.value.code == 2


def test_strategist_cli_and_resume_preserve_profile_budget_and_runtime(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    task_path = tmp_path / 'task.json'
    task = Task(task_id='strategist-cli-fixture', target='CCO', inventory=(),
                budget={'max_actions':17, 'max_expansions':6,
                        'max_wall_seconds':600, 'max_llm_tokens':90000})
    task_path.write_text(task.model_dump_json())
    output = tmp_path / 'result.json'
    profile = tmp_path / 'main-profile'
    profile.mkdir()
    (profile/'config.yaml').write_text('model:\n  default: fixture-main\n  provider: fixture-provider\n')
    episode = tmp_path / 'episode'
    argv = arguments(task_path, output) + ['--method', 'main_strategist',
        '--profile-home', str(profile), '--model-calls', '9', '--timeout', '7',
        '--episode-dir', str(episode)]
    seen = []

    def bridge(prompt, executor, **kwargs):
        seen.append(kwargs)
        assert kwargs['mode'] == 'main_strategist'
        assert kwargs['profile_home'] == str(profile)
        assert kwargs['scientist_python'] == '/trusted/scientist/python'
        assert kwargs['scientist_source'] == '/trusted/scientist/source'
        limits = kwargs['budget']
        assert (limits.max_model_calls, limits.max_tool_calls) == (9, 17)
        assert (limits.wall_seconds, limits.max_total_tokens) == (600, 90000)
        assert 'model' not in kwargs and 'provider' not in kwargs
        if len(seen) == 1:
            assert kwargs['resume_state'] is None
            kwargs['checkpoint']({'fixture': 'saved-runtime-state'})
            return {'completed': False}
        assert kwargs['resume_state'] == {'fixture': 'saved-runtime-state'}
        kwargs['action_executor']('submit', {'route_ids': []}, action_id='final-submit')
        return {'completed': True}

    monkeypatch.setattr(session, 'run_agent_scientist_bridge', bridge)
    first = execute(_parser().parse_args(argv))
    assert first['method'] == 'main_strategist'
    assert first['submission_status'] == 'not_submitted'
    assert main(argv + ['--resume']) == 0
    resumed = json.loads(output.read_text())
    assert len(seen) == 2
    assert resumed['method'] == 'main_strategist'
    assert resumed['submission_status'] == 'submitted_empty'
    assert resumed['episode']['usage']['actions'] == 1


def test_main_method_cannot_resume_a_strategist_runtime(tmp_path, monkeypatch):
    import synthesis_route_gym.agent_session as session
    task_path = tmp_path / 'task.json'
    task_path.write_text(Task(task_id='strategist-mode-binding', target='CCO', inventory=()).model_dump_json())
    profile=tmp_path/'main-profile';profile.mkdir()
    (profile/'config.yaml').write_text('model:\n  default: fixture-main\n  provider: fixture-provider\n')
    argv = arguments(task_path, tmp_path/'out.json') + ['--method', 'main_strategist','--profile-home',str(profile)]
    monkeypatch.setattr(session, 'run_agent_scientist_bridge',
                        lambda *args, **kwargs: {'completed': False})
    execute(_parser().parse_args(argv))
    argv[argv.index('main_strategist')] = 'main'
    with pytest.raises(ValueError, match='binding'):
        execute(_parser().parse_args(argv + ['--resume']))
