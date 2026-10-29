import json
import pytest
from test_core import make_task, make_route
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.observation import compact_observation, task_prompt


def test_summary_omits_inventory_payload_and_preserves_identity():
    env = SynthesisRouteEnv(make_task())
    result = compact_observation(env)
    assert 'inventory' not in result['task']
    assert result['inventory_count'] == len(env.task.inventory)
    assert len(result['task_sha256']) == 64
    assert result['task']['target'] == env.task.target
    assert 'inventory' not in json.loads(task_prompt(env).split('Task summary:\n')[1])['task']


def test_exact_inventory_lookup_and_pagination_preserve_salts_quantities():
    env = SynthesisRouteEnv(make_task())
    stock = env.task.inventory[0].smiles
    result = compact_observation(env, {'inventory_smiles': [stock, '[Na+].[Cl-]']})
    assert result['inventory_matches'][0]['item']['smiles'] == stock
    assert result['inventory_matches'][1]['item'] is None
    page = compact_observation(env, {'inventory_offset': 0, 'inventory_limit': 1})
    assert len(page['inventory_page']) == 1
    assert page['next_inventory_offset'] == (1 if len(env.task.inventory) > 1 else None)
    assert compact_observation(env, {'inventory_offset': 999})['inventory_page'] == []


def test_route_detail_is_opt_in_and_summary_has_route_ids():
    env = SynthesisRouteEnv(make_task())
    env.dispatch('propose_route', {'route': make_route().model_dump(mode='json')})
    assert compact_observation(env)['route_ids'] == ['r1']
    assert 'routes' not in compact_observation(env)
    assert compact_observation(env, {'route_ids': ['r1']})['routes'][0]['route_id'] == 'r1'
    with pytest.raises(ValueError):
        compact_observation(env, {'route_ids': ['missing']})


@pytest.mark.parametrize('args', [
    {'inventory_offset': -1}, {'inventory_limit': True}, {'inventory_limit': 201},
    {'inventory_smiles': 'C'}, {'inventory_smiles': ['bad smiles']},
    {'route_ids': ['r1'] * 21}, {'unknown': True}, {'route_ids': 'r1'},
])
def test_bad_observation_query_is_rejected(args):
    with pytest.raises(ValueError):
        compact_observation(SynthesisRouteEnv(make_task()), args)


def test_large_inventory_summary_is_bounded():
    from synthesis_route_gym.schemas import InventoryItem
    task = make_task().model_copy(update={'inventory': tuple(
        InventoryItem(smiles='C' * i) for i in range(1, 101))})
    env = SynthesisRouteEnv(task)
    assert len(json.dumps(compact_observation(env))) < 5000
    assert len(json.dumps(compact_observation(env))) < len(json.dumps(env.inspect())) / 3


def test_evidence_is_discoverable_in_bounded_pages():
    from synthesis_route_gym.schemas import EvidenceRecord
    task = make_task().model_copy(update={'evidence': tuple(
        EvidenceRecord(evidence_id=f'e{i}', kind='unresolved', source='fixture', locator=str(i)) for i in range(3))})
    env = SynthesisRouteEnv(task)
    page = compact_observation(env, {'evidence_offset': 0, 'evidence_limit': 2})
    assert [e['evidence_id'] for e in page['evidence_page']] == ['e0', 'e1']
    assert page['next_evidence_offset'] == 2
    assert compact_observation(env, {'evidence_ids':['e2']})['evidence'][0]['locator'] == '2'
    with pytest.raises(ValueError):
        compact_observation(env, {'evidence_limit': 21})
