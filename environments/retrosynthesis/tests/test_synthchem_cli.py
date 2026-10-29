"""Explicit native search selection and CLI execution with synthetic reactions."""
import json
import subprocess
import sys
from types import SimpleNamespace

import pytest

from synthesis_route_gym.cli import _parser, execute, main
from synthesis_route_gym.schemas import Budget, InventoryItem, Task


def write_task(tmp_path):
    task = Task(task_id='native-cli-fixture', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O')),
                budget=Budget(max_actions=20, max_expansions=8, max_wall_seconds=30, top_k=1))
    path = tmp_path / 'task.json'
    path.write_text(task.model_dump_json())
    return path


def command(task_path, output, policy):
    return ['plan', '--task', str(task_path), '--output', str(output),
            '--search-policy', policy, '--expansion-top-k', '4', '--max-frontier-states', '500']


@pytest.mark.parametrize('algorithm', ['portfolio', 'astar', 'mcts'])
def test_cli_routes_native_policy_with_exact_limits(tmp_path, monkeypatch, algorithm):
    calls = []

    def native(env, **kwargs):
        calls.append((env.task.task_id, kwargs))
        return {'fixture': algorithm}

    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.synthchem_search',
                        SimpleNamespace(run_synthchem_workflow=native))
    args = _parser().parse_args(command(write_task(tmp_path), tmp_path / 'out.json',
                                       'synthchem_' + algorithm))
    assert execute(args) == {'fixture': algorithm}
    assert calls == [('native-cli-fixture', {'algorithm': algorithm,
                                            'expansion_top_k': 4, 'max_graph_nodes': 500})]


def test_cli_prefers_synthchem_and_declares_native_graph_limit(capsys):
    args = _parser().parse_args(['plan', '--task', 'task.json', '--output', 'out.json'])
    assert args.search_policy == 'synthchem_portfolio'
    assert args.expansion_backend == 'localretro' and args.aizynth_config is None
    with pytest.raises(SystemExit) as stopped:
        _parser().parse_args(['plan', '--help'])
    assert stopped.value.code == 0
    assert 'native graph' in capsys.readouterr().out.lower()


@pytest.mark.parametrize('policy', ['synthchem', 'synthchem_unknown', 'astar'])
def test_cli_rejects_ambiguous_or_unknown_native_policy(policy):
    with pytest.raises(SystemExit):
        _parser().parse_args(['plan', '--task', 't', '--output', 'o', '--search-policy', policy])


def test_cli_native_dependency_failure_preserves_existing_output(tmp_path, monkeypatch, capsys):
    def unavailable(*args, **kwargs):
        raise RuntimeError('Install synthesis-route-gym[search] for native Syntheseus search')

    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.synthchem_search',
                        SimpleNamespace(run_synthchem_workflow=unavailable))
    output = tmp_path / 'out.json'
    output.write_text('previous result')
    assert main(command(write_task(tmp_path), output, 'synthchem_portfolio')) == 1
    assert output.read_text() == 'previous result'
    assert 'synthesis-route-gym[search]' in capsys.readouterr().err


@pytest.mark.parametrize('algorithm', ['portfolio', 'astar', 'mcts'])
def test_actual_cli_native_search_returns_two_step_fixture(tmp_path, algorithm):
    # Exercise the real native search, CLI parser, environment and output writer.
    # Only the scientific expansion backend is replaced; no source labels or model calls.
    launcher = '''
import sys
from synthesis_route_gym.adapters import LocalRetroAdapter
from synthesis_route_gym.cli import main
def expand(self, smiles, top_k):
    rows = {'CCOC(C)=O': [['CCO', 'CC(=O)O']], 'CCO': [['C=C', 'O']]}
    return {'status': 'ok', 'predictions': [
        {'product': smiles, 'reactants': reactants, 'score': 0.8,
         'source': {'tool': 'cli-fixture', 'version': '1'}}
        for reactants in rows.get(smiles, [])][:top_k]}
LocalRetroAdapter.expand = expand
raise SystemExit(main(sys.argv[1:]))
'''
    output = tmp_path / 'result.json'
    completed = subprocess.run([sys.executable, '-c', launcher,
                                *command(write_task(tmp_path), output, 'synthchem_' + algorithm)],
                               capture_output=True, text=True, timeout=40)
    assert completed.returncode == 0, completed.stderr
    report = json.loads(output.read_text())
    episode = report['episode']
    assert episode['terminated'] and not episode['truncated']
    assert len(episode['submitted_route_ids']) == 1
    submitted = next(route for route in episode['routes']
                     if route['route_id'] == episode['submitted_route_ids'][0])
    assert len(submitted['steps']) == 2
    # Provenance is set by the trusted tool binding, not the backend's self-label.
    assert {step['source_tool'] for step in submitted['steps']} == {'expand'}
    assert all(step['source_version'] for step in submitted['steps'])
    assert episode['usage']['expansions'] == 2
    submission = next(event for event in reversed(episode['events']) if event['action'] == 'submit')
    assert submission['result']['accepted_route_ids'] == episode['submitted_route_ids']


def test_cli_selects_template_backend_without_loading_localretro(tmp_path, monkeypatch):
    import synthesis_route_gym.adapters as adapters
    calls = []

    class TemplateAdapter:
        def __init__(self, **kwargs):
            calls.append(kwargs)

        def expand(self, smiles, top_k):
            calls.append((smiles, top_k))
            return {'status': 'ok', 'predictions': []}

    def forbidden(**kwargs):
        raise AssertionError('LocalRetro loaded for template backend')

    def native(env, **kwargs):
        result = env.dispatch('expand', {'smiles': env.task.target, 'top_k': 4})
        return {'status': result['status'], 'usage': env.search_status()['usage']}

    monkeypatch.setattr(adapters, 'AiZynthFinderAdapter', TemplateAdapter)
    monkeypatch.setattr(adapters, 'LocalRetroAdapter', forbidden)
    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.synthchem_search',
                        SimpleNamespace(run_synthchem_workflow=native))
    config = tmp_path / 'models.yml'
    config.write_text('expansion: fixture')
    args = _parser().parse_args(command(write_task(tmp_path), tmp_path / 'out.json', 'synthchem_portfolio') +
        ['--expansion-backend', 'aizynthfinder', '--aizynth-config', str(config),
         '--chemistry-python', '/fixture/python', '--timeout', '90'])
    result = execute(args)
    assert result['status'] == 'ok' and result['usage']['expansions'] == 1
    assert calls == [{'config_path': str(config), 'python_executable': '/fixture/python',
                       'timeout_seconds': 30}, ('CCOC(C)=O', 4)]


@pytest.mark.parametrize('configuration', [None, 'missing.yml'])
def test_cli_requires_existing_template_configuration_before_backend(tmp_path, monkeypatch, configuration):
    import synthesis_route_gym.adapters as adapters

    def forbidden(**kwargs):
        raise AssertionError('Backend constructed before configuration validation')

    monkeypatch.setattr(adapters, 'AiZynthFinderAdapter', forbidden)
    argv = command(write_task(tmp_path), tmp_path / 'out.json', 'synthchem_portfolio') + [
        '--expansion-backend', 'aizynthfinder']
    if configuration:
        argv += ['--aizynth-config', str(tmp_path / configuration)]
    with pytest.raises(ValueError, match='AiZynthFinder.*configuration|aizynth-config'):
        execute(_parser().parse_args(argv))


def test_cli_template_backend_uses_current_python_when_not_explicit(tmp_path, monkeypatch):
    import synthesis_route_gym.adapters as adapters
    calls = []
    monkeypatch.setattr(adapters, 'AiZynthFinderAdapter', lambda **kwargs:
                        calls.append(kwargs) or SimpleNamespace(expand=lambda *args: {}))
    monkeypatch.setitem(sys.modules, 'synthesis_route_gym.synthchem_search',
                        SimpleNamespace(run_synthchem_workflow=lambda *args, **kwargs: {}))
    config = tmp_path / 'models.yml'; config.write_text('fixture')
    execute(_parser().parse_args(command(write_task(tmp_path), tmp_path / 'out.json', 'synthchem_astar') +
        ['--expansion-backend', 'aizynthfinder', '--aizynth-config', str(config)]))
    assert calls[0]['python_executable'] == sys.executable
