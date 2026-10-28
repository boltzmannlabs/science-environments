"""Synthetic fixtures reproduce the existing REBOLT rd3t output schema."""
from copy import deepcopy
import json

import pytest

from synthesis_route_gym.route_import import import_routes
from synthesis_route_gym.schemas import RouteCandidate, Task
from synthesis_route_gym.validation import assess_route


def leaf(smiles, ident):
    return {'id':ident,'smile':smiles,'reference':'False',
            'building_block':'True','terminal':'True'}


def molecule(product, children, ident=0):
    return {'id':ident,'smile':product,'reference':'False','building_block':'False',
            'step_yield':0.92,'path_yield':0.91,'pathway_score':0.99,
            'children':[{'id':ident+1,'smile':product,'reference':'True',
                         'building_block':'False','terminal':'False','children':children}]}


def platform():
    return {'top1':{'path':molecule('CCO',[leaf('CC=O',2),leaf('[H][H]',3)]),'idx':1}}


def canonical():
    return [{'route_id':'provided','target':'CCO','steps':[{
        'step_id':'s1','product':'CCO','reactants':[{'smiles':'CC=O'},{'smiles':'[H][H]'}],
        'source_tool':'external','source_version':'v1','evidence_ids':['claimed-measurement'],
        'predicted_yield':0.5}]}]


def call(payload=None, **kwargs):
    return import_routes(platform() if payload is None else payload,target='CCO',
                         format='rebolt-scored-paths-v1',**kwargs)


def test_rebolt_duplicate_reaction_node_becomes_one_predicted_step():
    raw=platform(); before=deepcopy(raw)
    result=call(raw,provenance={'job_name':'retrosynthesis','doc_id':'job1'})
    assert raw==before
    assert result['schema_version']=='srg-route-import-v1'
    assert result['evidence_status']=='predicted'
    assert result['provenance']['doc_id']=='job1'
    assert len(result['provenance']['payload_sha256'])==64
    route=RouteCandidate.model_validate(result['routes'][0])
    assert len(route.steps)==1
    step=route.steps[0]
    assert {u.smiles for u in step.reactants}=={'CC=O','[H][H]'}
    assert step.predicted_yield is None and not step.evidence_ids
    assert step.product_amount_mmol is None and not step.conditions_complete
    task=Task(task_id='t',target='CCO',inventory=[{'smiles':'CC=O'},{'smiles':'[H][H]'}])
    assessment=assess_route(task,route)
    assert assessment.graph_valid and assessment.inventory_complete
    assert set(assessment.evidence_status.values())=={'predicted'}


def test_shared_convergent_intermediate_deduplicates_producer_not_obligations():
    shared=molecule('CO',[leaf('C',20),leaf('O',21)],10)
    raw={'top1':{'path':molecule('CCOC',[
        molecule('CCO',[shared,leaf('C',30)],2),shared]),'idx':1}}
    route=RouteCandidate.model_validate(import_routes(raw,target='CCOC',format='rebolt-scored-paths-v1')['routes'][0])
    assert len(route.steps)==3
    assert sum(u.smiles=='CO' for s in route.steps for u in s.reactants)==2


def test_canonical_routes_preserve_unknowns_and_strip_untrusted_evidence():
    raw=canonical()
    result=import_routes(raw,target='[CH3:1][CH2:2][OH:3]',format='srg-route-candidates-v1')
    assert result['routes'][0]['route_id']=='provided'
    assert result['routes'][0]['steps'][0]['predicted_yield']==0.5
    assert result['routes'][0]['steps'][0]['evidence_ids']==[]
    assert raw[0]['steps'][0]['evidence_ids']==['claimed-measurement']
    assert result['warnings']


def test_deterministic_payload_identity_and_route_ids():
    first=call();second=call(json.loads(json.dumps(platform())))
    assert first==second


@pytest.mark.parametrize('change',[
    lambda p:p.update({'unknown':p['top1']}),
    lambda p:p['top1'].update({'idx':True}),
    lambda p:p['top1']['path'].update({'smile':'bad smiles'}),
    lambda p:p['top1']['path'].update({'children':[]}),
    lambda p:p['top1']['path']['children'][0].update({'smile':'CCN'}),
    lambda p:p['top1']['path']['children'][0].update({'reference':'False'}),
    lambda p:p['top1']['path']['children'][0].update({'children':[]}),
    lambda p:p['top1']['path']['children'][0]['children'][0].update({'children':[leaf('O',50)]}),
    lambda p:p['top1']['path']['children'][0]['children'][0].update({'reference':'True'}),
    lambda p:p['top1']['path']['children'].append(leaf('C',99)),
])
def test_ambiguous_or_malformed_platform_graph_rejected(change):
    raw=platform();change(raw)
    with pytest.raises(ValueError):call(raw)


def test_bad_second_route_rejects_entire_batch():
    raw=platform();raw['top2']={'path':leaf('CCN',30),'idx':2}
    with pytest.raises(ValueError,match='target'):call(raw)


def test_cycles_conflicting_producers_and_disconnected_steps_rejected():
    cycle=platform();cycle['top1']['path']['children'][0]['children']=[molecule('CC=O',[leaf('CCO',40)],20)]
    with pytest.raises(ValueError,match='cycle'):call(cycle)
    conflicting={'top1':{'idx':1,'path':molecule('CCOC',[
        molecule('CO',[leaf('C',10),leaf('O',11)],2),
        molecule('CO',[leaf('COC',30)],20)])}}
    with pytest.raises(ValueError,match='conflicting'):
        import_routes(conflicting,target='CCOC',format='rebolt-scored-paths-v1')
    raw=canonical();raw[0]['steps'].append({**raw[0]['steps'][0],'step_id':'s2','product':'CCN'})
    with pytest.raises(ValueError,match='graph'):
        import_routes(raw,target='CCO',format='srg-route-candidates-v1')


@pytest.mark.parametrize('payload,fmt',[
    ({},'unknown'),({},'rebolt-scored-paths-v1'),([], 'srg-route-candidates-v1'),
    ({'routes':canonical()},'srg-route-candidates-v1'),
    (canonical()*101,'srg-route-candidates-v1'),
    ([canonical()[0],canonical()[0]],'srg-route-candidates-v1'),
])
def test_version_shape_count_and_duplicate_ids_fail_closed(payload,fmt):
    with pytest.raises(ValueError):import_routes(payload,target='CCO',format=fmt)


@pytest.mark.parametrize('provenance',[
    {'api_key':'secret'}, {'doc_id':''}, {'doc_id':5},
    {'source_url':'https://user:pass@example.org/output'},
    {'job_name':'another-tool'}, {'doc_id':'x'*257},
])
def test_provenance_accepts_only_bounded_nonsecret_job_identifiers(provenance):
    with pytest.raises(ValueError):call(provenance=provenance)


def test_size_depth_and_nonfinite_values_fail_closed():
    raw=platform();raw['top1']['path']['comment']='x'*2_000_001
    with pytest.raises(ValueError,match='size'):call(raw)
    raw=platform();raw['top1']['path']['score']=float('nan')
    with pytest.raises(ValueError):call(raw)
    deep=leaf('C',0)
    for _ in range(110):deep=molecule('C', [deep])
    with pytest.raises(ValueError):call({'top1':{'path':deep,'idx':1}})


def test_acquisition_leaf_is_allowed_but_platform_stock_claim_is_not_adopted():
    result=call({'top1':{'path':leaf('CCO',1),'idx':1}})
    route=RouteCandidate.model_validate(result['routes'][0]);assert not route.steps
    assert not assess_route(Task(task_id='t',target='CCO',inventory=[]),route).inventory_complete
