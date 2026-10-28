"""Quantity-aware inventory report invariants; fixtures are not chemistry claims."""
from copy import deepcopy
import json
import pytest
from synthesis_route_gym.portfolio_inventory import build_inventory_report
from synthesis_route_gym.schemas import Task, RouteCandidate
from synthesis_route_gym.validation import assess_route
from test_core import make_task, make_route


def convergent_fixture():
    task = Task(task_id='inventory-convergent-software-fixture', target='CCCCCO', target_amount_mmol=1,
                inventory=[{'smiles': 'CCCC', 'available_mmol': 3},
                           {'smiles': 'C', 'available_mmol': 1},
                           {'smiles': 'O', 'available_mmol': 1}])
    def step(ident, product, amount, inputs, **kw):
        return {'step_id': ident, 'product': product, 'product_amount_mmol': amount,
                'reactants': [{'smiles': s, 'amount_mmol': n} for s, n in inputs],
                'source_tool': 'software_graph_fixture_not_experiment', 'source_version': '1', **kw}
    base = RouteCandidate(route_id='convergent', target=task.target, steps=[
        step('shared', 'CC', 3, [('CCCC', 3)]),
        step('left', 'CCC', 1, [('CC', 2), ('C', 1)]),
        step('right', 'CCO', 1, [('CC', 1), ('O', 1)]),
        step('merge', task.target, 1, [('CCC', 1), ('CCO', 1)])])
    short = base.model_dump(mode='json'); short['route_id'] = 'short'; short['parent_route_id'] = 'convergent'
    short['steps'][0]['product_amount_mmol'] = 2
    blocked = base.model_dump(mode='json'); blocked['route_id'] = 'equipment'; blocked['parent_route_id'] = 'convergent'
    blocked['steps'][-1]['required_equipment'] = ['unavailable_vessel']
    return task, [base, RouteCandidate.model_validate(short), RouteCandidate.model_validate(blocked)]


def test_shared_intermediate_is_aggregated_without_yield_inference():
    task, routes = convergent_fixture()
    result = build_inventory_report(task, routes)
    assert result['schema_version'] == 'srg-inventory-report-v1'
    assert result['eligible_route_ids'] == ['convergent']
    assert result['ineligible_route_ids'] == ['short', 'equipment']
    row = result['routes'][0]
    shared = next(v for v in row['internal_requirements'] if v['smiles'] == 'CC')
    assert shared['declared_demand_mmol'] == 3
    assert shared['available_mmol'] == 3
    assert shared['consumer_step_ids'] == ['left', 'right']
    assert row['convergent_step_ids'] == ['merge']
    assert row['shared_intermediate_smiles'] == ['CC']
    assert row['route_yield'] is None
    assert row['quantity_status'] == 'complete'
    assert result['routes'][1]['quantity_status'] == 'insufficient'
    assert 'equipment_unavailable' in result['routes'][2]['blocking_codes']
    assert result['experimental_validation'] is False


def test_unknown_amounts_do_not_become_zero_and_no_scale_is_explicit():
    task, routes = convergent_fixture(); raw = routes[0].model_dump(mode='json')
    raw['steps'][1]['reactants'][0]['amount_mmol'] = None
    result = build_inventory_report(task, [raw]); shared = next(v for v in result['routes'][0]['internal_requirements'] if v['smiles'] == 'CC')
    assert shared['declared_demand_mmol'] is None and shared['known_demand_subtotal_mmol'] == 1
    assert result['eligible_route_ids'] == []
    assert result['routes'][0]['quantity_status'] == 'unknown'
    unscaled = build_inventory_report(make_task(), [make_route()])
    assert unscaled['routes'][0]['quantity_status'] == 'not_requested'
    assert unscaled['routes'][0]['quantity_verification'] == 'not_requested'


def test_supply_gates_and_repeated_external_demands():
    task, routes = convergent_fixture(); raw = routes[0].model_dump(mode='json')
    raw['steps'][0]['reagents'] = [{'smiles': 'O', 'amount_mmol': 0.5}]
    result = build_inventory_report(task, [raw]); water = next(v for v in result['routes'][0]['external_requirements'] if v['smiles'] == 'O')
    assert water['declared_demand_mmol'] == 1.5 and water['quantity_status'] == 'insufficient'
    absent = task.model_dump(mode='json'); absent['inventory'] = absent['inventory'][:-1]
    result = build_inventory_report(absent, [routes[0]])
    assert result['routes'][0]['missing_materials'] == ['O']
    assert 'material_unavailable' in result['routes'][0]['blocking_codes']


def test_assessments_are_verified_but_never_upgrade_source_authority():
    task, routes = convergent_fixture(); checked = assess_route(task, routes[0]).model_dump(mode='json')
    supplied = {**checked, 'evidence_status': {s.step_id: 'measured' for s in routes[0].steps},
                'conditions_evidence': {s.step_id: 'same' for s in routes[0].steps}, 'weak_steps': []}
    result = build_inventory_report(task, [routes[0]], assessments=[supplied])
    assert result['routes'][0]['evidence_status'] == checked['evidence_status']
    assert result['routes'][0]['source_support_status'] == 'not_independently_verified'
    with pytest.raises(ValueError):
        build_inventory_report(task, [routes[0]], assessments=[{**checked, 'graph_valid': False}])
    with pytest.raises(ValueError):
        build_inventory_report(task, [routes[0]], assessments=[{**checked, 'route_id': 'other'}])
    with pytest.raises(ValueError):
        build_inventory_report(task, [routes[0]], assessments=[])


def test_task_route_and_event_inputs_are_immutable():
    task, routes = convergent_fixture(); raw_task = task.model_dump(mode='json'); raw_routes = [r.model_dump(mode='json') for r in routes]
    events = [{'index': 0, 'action': 'expand', 'status': 'ok', 'result': {'tool_result': {'usage': {'backend_calls': 1}}}},
              {'index': 1, 'action': 'expand', 'status': 'error', 'result': {}},
              {'index': 2, 'action': 'validate', 'status': 'ok', 'result': {}}]
    before = deepcopy((raw_task, raw_routes, events)); result = build_inventory_report(raw_task, raw_routes, events=events)
    assert (raw_task, raw_routes, events) == before
    assert result['search_accounting']['recorded_actions'] == 3
    assert result['search_accounting']['expansion_attempts'] == 2
    assert result['search_accounting']['successful_expansions'] == 1
    assert result['search_accounting']['failed_actions'] == 1
    assert result['search_accounting']['actual_backend_calls'] is None
    result['routes'][0]['external_requirements'].clear()
    assert (raw_task, raw_routes, events) == before


def test_top_k_preserves_input_preference_and_never_claims_optimality():
    task, routes = convergent_fixture(); data = task.model_dump(mode='json'); data['budget']['top_k'] = 1
    second = routes[0].model_dump(mode='json'); second['route_id'] = 'another'
    result = build_inventory_report(data, [second, routes[0]])
    assert result['eligible_route_ids'] == ['another', 'convergent']
    assert result['top_k_route_ids'] == ['another']
    assert result['ranking_basis'] == 'input_preference_among_deterministically_eligible_records'


@pytest.mark.parametrize('routes', [[], 'x', {}, [True]])
def test_bad_route_collections_fail(routes):
    with pytest.raises((ValueError, TypeError)):
        build_inventory_report(make_task(), routes)


def test_duplicate_routes_too_many_routes_and_step_ids_fail():
    task, routes = convergent_fixture()
    for bad in ([routes[0], routes[0]], routes + [routes[0]]):
        with pytest.raises(ValueError): build_inventory_report(task, bad)
    raw = routes[0].model_dump(mode='json'); raw['steps'][1]['step_id'] = 'shared'
    with pytest.raises(ValueError): build_inventory_report(task, [raw])


def test_graph_invalid_and_acquisition_only_stay_ineligible():
    task = make_task(); raw = make_route().model_dump(mode='json'); raw['steps'][0]['reactants'] = [{'smiles': task.target}]
    result = build_inventory_report(task, [raw]); assert not result['eligible_route_ids']
    acquisition_task = task.model_copy(update={'inventory': tuple()})
    result = build_inventory_report(acquisition_task, [make_route(steps=())]); assert not result['eligible_route_ids']


@pytest.mark.parametrize('events', ['x', [{}], [{'index': 1, 'action': 'expand', 'status': 'ok'}],
    [{'index': 0, 'action': 'expand', 'status': 'surprise'}]])
def test_bad_event_metadata_fails(events):
    with pytest.raises(ValueError): build_inventory_report(make_task(), [make_route()], events=events)


def test_existing_host_assessment_model_and_result_json_are_supported():
    task, routes = convergent_fixture()
    result = build_inventory_report(task, [routes[0]], assessments=[assess_route(task, routes[0])])
    assert json.loads(json.dumps(result, allow_nan=False)) == result


def test_boolean_or_string_amounts_are_rejected_before_pydantic_coercion():
    task, routes = convergent_fixture()
    for value in (True, '1'):
        raw = routes[0].model_dump(mode='json'); raw['steps'][0]['product_amount_mmol'] = value
        with pytest.raises(ValueError): build_inventory_report(task, [raw])


def test_oversized_route_and_wrong_assessment_step_keys_are_rejected():
    task, routes = convergent_fixture(); raw = routes[0].model_dump(mode='json')
    raw['steps'] = [{**raw['steps'][0], 'step_id': f'step-{i}'} for i in range(13)]
    with pytest.raises(ValueError): build_inventory_report(task, [raw])
    checked = assess_route(task, routes[0]).model_dump(mode='json')
    for key in ('evidence_status', 'conditions_evidence'):
        with pytest.raises(ValueError): build_inventory_report(task, [routes[0]], assessments=[{**checked, key: {}}])


def test_undeclared_condition_inputs_are_not_ignored():
    task, routes = convergent_fixture(); raw = routes[0].model_dump(mode='json')
    raw['steps'][0]['condition_inputs'] = {'base': 'N'}
    result = build_inventory_report(task, [raw]); row = result['routes'][0]
    nitrogen = next(v for v in row['external_requirements'] if v['smiles'] == 'N')
    assert nitrogen['declared_demand_mmol'] is None
    assert row['missing_materials'] == ['N']
    assert 'undeclared_condition_material' in row['blocking_codes']


@pytest.mark.parametrize('result', [None, {'tool_result': None}, {'usage': {'backend_calls': True}}])
def test_malformed_or_missing_backend_usage_remains_unknown(result):
    report = build_inventory_report(make_task(), [make_route()], events=[{'index': 0, 'action': 'expand', 'status': 'error', 'result': result}])
    assert report['search_accounting']['actual_backend_calls'] is None
    assert report['search_accounting']['unconfirmed_expansion_results'] == 1
