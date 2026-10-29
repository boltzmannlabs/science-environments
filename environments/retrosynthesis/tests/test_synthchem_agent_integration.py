"""Main-profile hypotheses can be revised into a route through normal sessions."""

import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from synthesis_route_gym.interactive_session import InteractiveSessions
from synthesis_route_gym.planning import _step
from synthesis_route_gym.schemas import Budget, InventoryItem, RouteCandidate, Task


def _call(host, action, arguments, sid=None):
    return host.handle({'profile': 'main', 'action': action,
                        'arguments': arguments, 'session_id': sid})


def _hypothesis(product, reactants):
    return {'product': product, 'candidates': [{
        'status': 'hypothesis', 'reactants': reactants,
        'rationale': 'Unverified precursor hypothesis'}]}


def test_agent_iterates_on_unresolved_intermediate_and_submits_two_step_route():
    task = Task(task_id='synthchem-agent-flow', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O')),
                budget=Budget(max_actions=30, max_expansions=8, max_wall_seconds=30))
    host = InteractiveSessions()
    sid = _call(host, 'reset', {'task': task.model_dump(mode='json')})['session_id']
    root = _call(host, 'propose_expansion',
                 _hypothesis('CCOC(C)=O', ['CCO', 'CC(=O)O']), sid)
    assert root['observation']['status'] == 'ok'

    first = _call(host, 'generate_routes', {'proposal_mode': 'agent_only'}, sid)
    assert first['search_policy'] == 'synthchem_portfolio'
    assert first['route_ids'] == []
    assert 'CCO' in first['unresolved_products']
    assert first['submitted'] is False

    child = _call(host, 'propose_expansion', _hypothesis('CCO', ['C=C', 'O']), sid)
    assert child['observation']['status'] == 'ok'
    second = _call(host, 'generate_routes', {'proposal_mode': 'agent_only'}, sid)
    assert second['route_ids']
    assert second['submitted'] is False
    assert second['backend_failures'] == []
    route_id = second['route_ids'][0]
    assert _call(host, 'validate', {'route_id': route_id}, sid)['observation']['result']['inventory_complete']
    submitted = _call(host, 'submit', {'route_ids': [route_id]}, sid)['observation']
    assert submitted['result']['accepted_route_ids'] == [route_id]
    route = next(row for row in host.sessions[('main', sid)][0].export()['routes']
                 if row['route_id'] == route_id)
    assert len(route['steps']) == 2
    assert {step['source_tool'] for step in route['steps']} == {'submitted_hypothesis'}
    assert host.sessions[('main', sid)][0].export()['assessments'][0]['solved'] is False


def test_hybrid_search_combines_model_root_with_agent_intermediate():
    task = Task(task_id='synthchem-hybrid-flow', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O')),
                budget=Budget(max_actions=30, max_expansions=8, max_wall_seconds=30))

    def model(product, top_k):
        proposals = [['CCO', 'CC(=O)O']] if product == 'CCOC(C)=O' else []
        return {'status': 'ok', 'predictions': [
            {'product': product, 'reactants': reactants} for reactants in proposals[:top_k]]}

    host = InteractiveSessions(expand=model)
    sid = _call(host, 'reset', {'task': task.model_dump(mode='json')})['session_id']
    assert _call(host, 'propose_expansion', _hypothesis('CCO', ['C=C', 'O']), sid)['observation']['status'] == 'ok'
    generated = _call(host, 'generate_routes', {}, sid)
    assert generated['search_policy'] == 'synthchem_portfolio'
    assert generated['proposal_mode'] == 'hybrid'
    assert generated['route_ids']
    assert generated['submitted'] is False
    route = next(row for row in host.sessions[('main', sid)][0].export()['routes']
                 if row['route_id'] == generated['route_ids'][0])
    assert {step['source_tool'] for step in route['steps']} == {'expand', 'submitted_hypothesis'}
    assert all(step['evidence_ids'] == [] for step in route['steps'])


def test_registered_agent_route_can_be_searched_after_model_expansion_budget_is_spent():
    task = Task(task_id='agent-retry-after-model-budget', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O')),
                budget=Budget(max_actions=30, max_expansions=1, max_wall_seconds=30))
    host = InteractiveSessions(expand=lambda product, top_k: {'status': 'ok', 'predictions': []})
    sid = _call(host, 'reset', {'task': task.model_dump(mode='json')})['session_id']
    assert _call(host, 'expand', {'smiles': task.target}, sid)['observation']['status'] == 'ok'
    assert _call(host, 'propose_expansion',
                 _hypothesis('CCOC(C)=O', ['CCO', 'CC(=O)O']), sid)['observation']['status'] == 'ok'
    assert _call(host, 'propose_expansion',
                 _hypothesis('CCO', ['C=C', 'O']), sid)['observation']['status'] == 'ok'
    generated = _call(host, 'generate_routes', {'proposal_mode': 'agent_only'}, sid)
    assert generated['route_ids']
    assert host.sessions[('main', sid)][0].export()['usage']['expansions'] == 1


def test_successful_model_proposals_are_reused_after_agent_revision():
    task = Task(task_id='synthchem-model-reuse', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O')),
                budget=Budget(max_actions=30, max_expansions=2, max_wall_seconds=30))
    calls = []

    def model(product, top_k):
        calls.append(product)
        reactants = ['CCO', 'CC(=O)O'] if product == task.target else None
        return {'status': 'ok', 'predictions': ([{'product': product,
                'reactants': reactants}] if reactants else [])}

    host = InteractiveSessions(expand=model)
    sid = _call(host, 'reset', {'task': task.model_dump(mode='json')})['session_id']
    first = _call(host, 'generate_routes', {}, sid)
    assert first['route_ids'] == []
    assert 'CCO' in first['unresolved_products']
    initial_calls = len(calls)
    assert initial_calls == 2
    assert _call(host, 'propose_expansion',
                 _hypothesis('CCO', ['C=C', 'O']), sid)['observation']['status'] == 'ok'

    second = _call(host, 'generate_routes', {}, sid)
    assert second['route_ids']
    assert len(calls) == initial_calls
    assert host.sessions[('main', sid)][0].export()['usage']['expansions'] == initial_calls


def test_plugin_ipc_supports_agent_only_route_generation_without_local_model(monkeypatch):
    plugin_path = Path(__file__).resolve().parents[1] / 'integrations' / 'agent_scientist' / '__init__.py'
    spec = importlib.util.spec_from_file_location('retro_plugin_test', plugin_path)
    plugin = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(plugin)
    monkeypatch.setenv('SRG_CHEMISTRY_PYTHON', sys.executable)
    monkeypatch.setenv('SRG_PACKAGE_ROOT', str(plugin_path.parents[2]))
    monkeypatch.setitem(sys.modules, 'sci_constants', SimpleNamespace(sci_home_key=lambda: 'main'))
    registered = {}
    plugin.register(SimpleNamespace(register_tool=lambda **kwargs: registered.update(kwargs)))
    tool = registered['handler']
    task = Task(task_id='agent-ipc', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s) for s in ('C=C', 'O', 'CC(=O)O', 'CC')),
                budget=Budget(max_actions=30, max_expansions=8, max_wall_seconds=30))

    def call(action, arguments, sid=None):
        payload = {'action': action, 'arguments': arguments}
        return json.loads(tool({**payload, **({'session_id': sid} if sid else {})}))

    try:
        started = call('reset', {'task': task.model_dump(mode='json')})
        assert 'session_id' in started, started
        sid = started['session_id']
        assert call('propose_expansion', _hypothesis('CCOC(C)=O', ['CCO', 'CC(=O)O']), sid)['observation']['status'] == 'ok'
        assert call('propose_expansion', _hypothesis('CCO', ['C=C', 'O']), sid)['observation']['status'] == 'ok'
        result = call('generate_routes', {'proposal_mode': 'agent_only'}, sid)
        assert result['route_ids'] and result['submitted'] is False
        donor = RouteCandidate(route_id='ipc-donor', target='CCO', steps=(
            _step({'product': 'CCO', 'reactants': ['CC', 'O'],
                   'source': {'tool': 'test-donor', 'version': '1'}}),))
        assert call('propose_route', {'route': donor.model_dump(mode='json')}, sid)['observation']['status'] == 'ok'
        grafted = call('graft_route', {'parent_route_id': result['route_ids'][0],
                       'donor_route_id': 'ipc-donor', 'intermediate': 'CCO'}, sid)
        assert grafted['observation']['status'] == 'ok'
        revised_id = grafted['observation']['result']['route_id']
        assert call('submit', {'route_ids': [revised_id]}, sid)['observation']['result']['accepted_route_ids'] == [revised_id]
    finally:
        plugin._close_clients()
