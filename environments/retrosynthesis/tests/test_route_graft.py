"""Stored intermediate preparations can revise an existing route without evidence promotion."""

from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.planning import _step
from synthesis_route_gym.schemas import InventoryItem, RouteCandidate, Task


def _route(route_id, target, rows, source):
    steps = tuple(_step({'product': product, 'reactants': reactants,
                          'source': {'tool': source, 'version': 'fixture-1'}})
                  for product, reactants in rows)
    return RouteCandidate(route_id=route_id, target=target, steps=steps)


def _environment():
    task = Task(task_id='graft-fixture', target='CCOC(C)=O',
                inventory=tuple(InventoryItem(smiles=s)
                                for s in ('C=C', 'O', 'CC(=O)O', 'CC')))
    environment = SynthesisRouteEnv(task)
    parent = _route('parent', task.target,
                    [('CCOC(C)=O', ['CCO', 'CC(=O)O']), ('CCO', ['C=C', 'O'])], 'expand')
    donor = _route('donor', 'CCO', [('CCO', ['CC', 'O'])], 'submitted_hypothesis')
    for route in (parent, donor):
        assert environment.dispatch('propose_route', {'route': route.model_dump(mode='json')})['status'] == 'ok'
    return environment


def test_graft_replaces_exact_intermediate_and_preserves_prediction_sources():
    environment = _environment()
    response = environment.dispatch('graft_route', {'parent_route_id': 'parent',
        'donor_route_id': 'donor', 'intermediate': 'CCO'})
    assert response['status'] == 'ok'
    result = response['result']
    assert result['assessment']['graph_valid']
    assert result['assessment']['inventory_complete']
    assert result['route_id'] != 'parent'
    route = next(row for row in environment.export()['routes'] if row['route_id'] == result['route_id'])
    assert route['parent_route_id'] == 'parent'
    assert {step['source_tool'] for step in route['steps']} == {'expand', 'submitted_hypothesis'}
    assert all(not step['evidence_ids'] for step in route['steps'])
    assert environment.export()['assessments'][-1]['solved'] is False
    assert environment.export()['usage']['actions'] == 3


def test_graft_rejects_wrong_intermediate_and_no_connectivity_change():
    environment = _environment()
    bad = environment.dispatch('graft_route', {'parent_route_id': 'parent',
        'donor_route_id': 'donor', 'intermediate': 'CCN'})
    assert bad['status'] == 'error'
    same = _route('same-donor', 'CCO', [('CCO', ['C=C', 'O'])], 'submitted_hypothesis')
    environment.dispatch('propose_route', {'route': same.model_dump(mode='json')})
    unchanged = environment.dispatch('graft_route', {'parent_route_id': 'parent',
        'donor_route_id': 'same-donor', 'intermediate': 'CCO'})
    assert unchanged['status'] == 'error'
    assert len(environment.export()['routes']) == 3
