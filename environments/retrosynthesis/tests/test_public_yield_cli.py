"""Explicit local public-model configuration and metered yield CLI execution."""
import json
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest

from synthesis_route_gym.cli import _parser, execute, main
from synthesis_route_gym.schemas import Task


def files(tmp_path):
    task = tmp_path / 'task.json'
    task.write_text(Task(task_id='public-yield-cli', target='CCOC(C)=O', inventory=()).model_dump_json())
    inputs = tmp_path / 'candidates.json'
    inputs.write_text(json.dumps({'candidates': [{'id': 'one', 'reactants': ['CCO', 'CC(=O)O'],
        'reagents': ['OS(=O)(=O)O'], 'product': 'CCOC(C)=O'}]}))
    return task, inputs, tmp_path / 'output.json'


def install_predictor(monkeypatch, predictor):
    paths = []
    def load(path):
        paths.append(path)
        return predictor
    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.public_yield',
        SimpleNamespace(ReactionT5YieldPredictor=SimpleNamespace(from_manifest=load)))
    return paths


@pytest.mark.parametrize('command', ['plan', 'replay', 'agent'])
def test_public_model_option_is_explicit_and_default_is_disabled(command):
    argv = [command, '--task', 'task.json', '--output', 'out.json']
    if command == 'replay':
        argv += ['--actions', 'actions.json']
    if command == 'agent':
        argv += ['--scientist-python', '/science/python', '--scientist-source', '/science']
    assert _parser().parse_args(argv).reaction_yield_model is None
    assert _parser().parse_args(argv + ['--reaction-yield-model', 'manifest.json']).reaction_yield_model == 'manifest.json'


def test_predict_yield_dispatches_through_environment_and_returns_episode(tmp_path, monkeypatch):
    import synthesis_route_gym.environment as environment
    task, inputs, output = files(tmp_path)
    predictor, calls = object(), []
    paths = install_predictor(monkeypatch, predictor)
    class Environment:
        def __init__(self, task, **kwargs):
            calls.append(('construct', task.task_id, kwargs))
        def dispatch(self, name, arguments):
            calls.append(('dispatch', name, arguments))
            return {'status': 'ok', 'result': {'fixture': True}}
        def export(self):
            return {'usage': {'actions': 1}, 'scientific_usage': {'predict_reaction_yield': 1}}
    monkeypatch.setattr(environment, 'SynthesisRouteEnv', Environment)
    result = execute(_parser().parse_args(['predict-yield', '--task', str(task), '--model', 'manifest.json',
        '--input', str(inputs), '--output', str(output)]))
    assert paths == ['manifest.json']
    assert calls[0] == ('construct', 'public-yield-cli', {'reaction_yield_predictor': predictor})
    assert calls[1] == ('dispatch', 'predict_reaction_yield', json.loads(inputs.read_text()))
    assert result['action_result']['status'] == 'ok'
    assert result['episode']['usage']['actions'] == 1
    assert result['episode']['scientific_usage'] == {'predict_reaction_yield': 1}


@pytest.mark.parametrize('resume', [False, True])
def test_agent_passes_same_explicit_model_to_new_and_resumed_episode(tmp_path, monkeypatch, resume):
    import synthesis_route_gym.cli as cli
    import synthesis_route_gym.environment as environment
    task, _, output = files(tmp_path)
    predictor, calls = object(), []
    paths = install_predictor(monkeypatch, predictor)
    class Environment:
        def __init__(self, *args, **kwargs):
            calls.append(('new', args, kwargs))
        @classmethod
        def resume(cls, *args, **kwargs):
            calls.append(('resume', args, kwargs))
            return object()
    monkeypatch.setattr(environment, 'SynthesisRouteEnv', Environment)
    monkeypatch.setattr(cli, '_agent', lambda args, env: {'invoked': True})
    argv = ['agent', '--task', str(task), '--output', str(output), '--scientist-python', '/science/python',
        '--scientist-source', '/science', '--reaction-yield-model', 'manifest.json']
    if resume:
        argv += ['--resume']
    assert execute(_parser().parse_args(argv)) == {'invoked': True}
    assert paths == ['manifest.json']
    assert calls[0][0] == ('resume' if resume else 'new')
    assert calls[0][2]['reaction_yield_predictor'] is predictor


def test_predict_yield_bad_manifest_preserves_previous_output(tmp_path, monkeypatch, capsys):
    task, inputs, output = files(tmp_path)
    output.write_text('previous artifact')
    def fail(path):
        raise ValueError('Invalid local yield manifest')
    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.public_yield',
        SimpleNamespace(ReactionT5YieldPredictor=SimpleNamespace(from_manifest=fail)))
    assert main(['predict-yield', '--task', str(task), '--model', 'bad.json', '--input', str(inputs),
        '--output', str(output)]) == 1
    assert output.read_text() == 'previous artifact'
    assert 'Invalid local yield manifest' in capsys.readouterr().err


@pytest.mark.parametrize('missing', ['--task', '--model', '--input', '--output'])
def test_predict_yield_requires_explicit_local_inputs(missing):
    options = {'--task': 'task.json', '--model': 'model.json', '--input': 'input.json', '--output': 'out.json'}
    argv = ['predict-yield'] + [part for key, value in options.items() if key != missing for part in (key, value)]
    with pytest.raises(SystemExit):
        _parser().parse_args(argv)


class Predictor:
    metadata = {'model_version': 'cli-fixture-v1'}
    artifact = {'fixture': 'public-yield-cli'}
    configuration = {'fixture': True}
    timeout_seconds = 1
    def predict(self, rows):
        return [{'id': row['id'], 'status': 'scored', 'predicted_yield_percent': 61.0,
            'raw_yield_percent': 61.0, 'reason': None, 'domain': 'synthetic CLI fixture',
            'uncertainty_kind': 'not_calibrated'} for row in rows]


@pytest.mark.parametrize('command', ['predict-yield', 'replay'])
def test_cli_public_prediction_real_environment_metering_and_projection(tmp_path, monkeypatch, command):
    task, inputs, output = files(tmp_path)
    paths = install_predictor(monkeypatch, Predictor())
    argv = [command, '--task', str(task), '--output', str(output)]
    if command == 'predict-yield':
        argv += ['--model', 'manifest.json', '--input', str(inputs)]
    else:
        actions = tmp_path / 'actions.json'
        actions.write_text(json.dumps([{'action': 'predict_reaction_yield', 'arguments': json.loads(inputs.read_text())}]))
        argv += ['--reaction-yield-model', 'manifest.json', '--actions', str(actions)]
    assert main(argv) == 0
    assert paths == ['manifest.json']
    report = json.loads(output.read_text())
    episode = report['episode'] if command == 'predict-yield' else report
    assert episode['usage']['actions'] == 1 and episode['usage']['expansions'] == 0
    assert episode['scientific_usage'] == {'predict_reaction_yield': 1}
    prediction = episode['events'][0]['result']['data']['predictions'][0]
    assert prediction['predicted_yield_percent'] == 61.0
    assert prediction['model_version'] == 'cli-fixture-v1'
    assert prediction['evidence_status'] == 'predicted'


def test_predict_yield_invalid_candidate_is_metered_without_model_call(tmp_path, monkeypatch):
    task, inputs, output = files(tmp_path)
    inputs.write_text(json.dumps({'candidates': [{'id': 'invalid', 'reactants': ['invalid SMILES'], 'product': 'CCO'}]}))
    class NoInference(Predictor):
        def predict(self, rows):
            raise AssertionError('Invalid request reached model')
    install_predictor(monkeypatch, NoInference())
    result = execute(_parser().parse_args(['predict-yield', '--task', str(task), '--model', 'manifest.json',
        '--input', str(inputs), '--output', str(output)]))
    assert result['action_result']['status'] == 'error'
    assert result['action_result']['result']['usage']['backend_calls'] == 0
    assert result['episode']['usage']['actions'] == 1
    assert result['episode']['scientific_usage'] == {'predict_reaction_yield': 1}


def test_actual_predict_yield_cli_process_writes_accounted_prediction(tmp_path):
    task, inputs, output = files(tmp_path)
    launcher = '''
import sys
from types import SimpleNamespace
from synthesis_route_gym.cli import main
class Predictor:
    metadata={'model_version':'subprocess-fixture-v1'}
    artifact={'fixture':'cli-subprocess'}
    configuration={'fixture':True}
    timeout_seconds=1
    def predict(self,rows):
        return [{'id':row['id'],'status':'scored','predicted_yield_percent':42.0,
            'raw_yield_percent':42.0,'reason':None,'domain':'synthetic CLI fixture',
            'uncertainty_kind':'not_calibrated'} for row in rows]
sys.modules['synthesis_route_gym.public_yield']=SimpleNamespace(
    ReactionT5YieldPredictor=SimpleNamespace(from_manifest=lambda path:Predictor()))
raise SystemExit(main(sys.argv[1:]))
'''
    result = subprocess.run([sys.executable, '-c', launcher, 'predict-yield', '--task', str(task),
        '--input', str(inputs), '--model', 'synthetic-host-manifest.json', '--output', str(output)],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text())
    assert report['action_result']['status'] == 'ok'
    assert report['action_result']['result']['data']['predictions'][0]['predicted_yield_percent'] == 42.0
    assert report['episode']['usage']['actions'] == 1
    assert report['episode']['scientific_usage'] == {'predict_reaction_yield': 1}


@pytest.mark.parametrize('failure, expected_status, error_code', [
    ('backend', 'error', 'backend_failed'),
    ('timeout', 'error', 'tool_timeout'),
    ('unavailable', 'unavailable', 'not_configured'),
])
def test_predict_yield_failure_exits_nonzero_and_preserves_accounting(
        tmp_path, monkeypatch, capsys, failure, expected_status, error_code):
    task, inputs, output = files(tmp_path)
    class FailingPredictor(Predictor):
        timeout_seconds = 0.01
        def predict(self, rows):
            if failure == 'timeout':
                time.sleep(0.2)
                return super().predict(rows)
            raise RuntimeError('Synthetic backend failure')
    install_predictor(monkeypatch, None if failure == 'unavailable' else FailingPredictor())
    code = main(['predict-yield', '--task', str(task), '--model', 'manifest.json',
        '--input', str(inputs), '--output', str(output)])
    assert code != 0
    summary = json.loads(capsys.readouterr().out)
    assert summary == {'status': expected_status, 'output': str(output.resolve())}
    report = json.loads(output.read_text())
    assert report['action_result']['status'] == expected_status
    assert report['action_result']['result']['error']['code'] == error_code
    assert report['episode']['usage']['actions'] == 1
    assert report['episode']['scientific_usage'] == {'predict_reaction_yield': 1}


def test_replay_keeps_successful_command_status_when_scientific_action_fails(tmp_path, monkeypatch, capsys):
    task, inputs, output = files(tmp_path)
    install_predictor(monkeypatch, None)
    actions = tmp_path / 'actions.json'
    actions.write_text(json.dumps([{'action': 'predict_reaction_yield', 'arguments': json.loads(inputs.read_text())}]))
    assert main(['replay', '--task', str(task), '--output', str(output), '--actions', str(actions),
        '--reaction-yield-model', 'manifest.json']) == 0
    assert json.loads(capsys.readouterr().out)['status'] == 'ok'
    assert json.loads(output.read_text())['events'][0]['status'] == 'unavailable'
