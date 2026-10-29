"""Synthetic source-selection and independently labeled critic controls."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from synthesis_route_gym.critic_development import (
    CATEGORIES, build_case, case_inputs_digest, load_critic_case,
    select_sources, validate_critic_labels,
)
from synthesis_route_gym.validation import assess_route

NOW='2026-10-26T21:00:00+00:00'


def source(index):
    stereo=index==3
    target='C[C@H](O)F' if stereo else 'C'*(index+2)+'=O'
    return {'source_family':'paroutes' if index<4 else 'doyle',
        'source_case_id':f'source-{index}','target':target,
        'source_url':'https://example.org/source','source_content_sha256':'a'*64,
        'source_locator':f'row {index}','claim_kind':'proxy' if index<4 else 'measured',
        'source_provenance':[{'artifact_path':'source.json','artifact_sha256':'b'*64,'locator':str(index)}],
        'edges':[{'product':target,'reactants':['CC(O)F' if stereo else 'C'*(index+2)+'O'],
                  'reagents':[],'conditions':[]}]}


def pair(index=0):
    return build_case(source(index),source((index+1)%8),index=index,retrieved_at=NOW)


def accepted(task,route):
    a=assess_route(task,route)
    return a.graph_valid and a.inventory_complete and a.constraint_compliant and a.quantity_status in {'complete','not_requested'}


@pytest.mark.parametrize('index',range(8))
def test_three_candidates_have_independent_labels_and_only_declared_hard_error(index,tmp_path):
    public,labels=pair(index);validate_critic_labels(public,labels)
    path=tmp_path/'case.json';path.write_text(json.dumps(public))
    loaded=load_critic_case(path)
    assert len(loaded['routes'])==3 and len({r.route_id for r in loaded['routes']})==3
    assert loaded['task'].budget.top_k==3 and loaded['task'].budget.max_actions==80
    assert loaded['task'].budget.max_llm_tokens==350000
    assert loaded['task'].budget.max_wall_seconds==600
    assert sum(v['hard_valid'] for v in labels['routes'].values())==2
    assert sum(v['retain'] for v in labels['routes'].values())==(2 if index<4 else 1)
    for route in loaded['routes']:
        assert accepted(loaded['task'],route)==labels['routes'][route.route_id]['hard_valid']
    assert loaded['evidence_corpus'].retrieve()['status']=='ok'
    for row in loaded['evidence_corpus'].retrieve()['records']:
        assert row['verification_status']=='not_attested'


def test_all_categories_covered_with_review_only_uncertainty_and_no_leaked_labels():
    categories=set()
    for index in range(8):
        public,labels=pair(index);text=json.dumps(public)
        for value in labels['routes'].values():
            categories.update(value['expected_categories'])
        assert all(key not in text for key in ['expected_categories','mutation_kind','hard_valid','source_consistent','retain'])
        assert 'yield_percent' not in text and 'synthetic-test' not in text if index!=4 else True
        assert public['data_role']=='previously_used_development'
        assert len(public['label_sha256'])==64
    assert categories==set(CATEGORIES)


def test_builder_is_repeatable_and_does_not_mutate_source_specs():
    first,second=source(1),source(2);before=deepcopy((first,second))
    assert build_case(first,second,index=1,retrieved_at=NOW)==build_case(first,second,index=1,retrieved_at=NOW)
    assert (first,second)==before


def test_public_ids_do_not_encode_mutation_role_and_have_stable_hashed_order():
    public,labels=pair()
    assert all(route['route_id'].startswith('route-') for route in public['routes'])
    assert [r['route_id'] for r in public['routes']]==sorted(r['route_id'] for r in public['routes'])
    assert all(len(r['route_id'])==30 for r in public['routes'])


def test_synthetic_quantities_explicit_and_not_source_measurements():
    public,labels=pair(4)
    assert public['task']['target_amount_mmol']==1
    assert all('synthetic-test' in row['source'] for row in public['task']['inventory'])
    assert all(s['conditions_scope']=='unknown' for s in public['sources'])
    assert any('counterfactual' in value for value in public['limitations'])


@pytest.mark.parametrize('change',[
    lambda p:p['task'].update(target='C'),
    lambda p:p['routes'][0]['steps'][0].update(predicted_yield=0.5),
    lambda p:p['sources'][0].update(product='C'),
    lambda p:p.update(data_role='final'),
    lambda p:p.update(hidden_answers={'valid':True}),
    lambda p:p.update(label_sha256='bad'),
])
def test_public_tampering_and_privileged_fields_rejected(tmp_path,change):
    public,_=pair();change(public);path=tmp_path/'case.json';path.write_text(json.dumps(public))
    with pytest.raises(ValueError):load_critic_case(path)


def test_loader_verifies_external_digest_and_never_opens_private_labels(tmp_path):
    public,_=pair();path=tmp_path/'case.json';path.write_text(json.dumps(public))
    sha=hashlib.sha256(path.read_bytes()).hexdigest()
    assert load_critic_case(path,expected_sha256=sha)['public']==public
    with pytest.raises(ValueError):load_critic_case(path,expected_sha256='0'*64)
    assert not (tmp_path/'labels.json').exists()


@pytest.mark.parametrize('change',[
    lambda labels:labels.update(case_inputs_sha256='0'*64),
    lambda labels:labels.update(case_id='wrong'),
    lambda labels:labels['routes'].pop(next(iter(labels['routes']))),
    lambda labels:next(iter(labels['routes'].values())).update(expected_error_categories=['made_up']),
    lambda labels:next(iter(labels['routes'].values())).update(hard_valid='yes'),
])
def test_private_labels_are_typed_and_bound(change):
    public,labels=pair();change(labels)
    with pytest.raises(ValueError):validate_critic_labels(public,labels)


def test_duplicate_json_keys_and_oversized_documents_rejected(tmp_path):
    p=tmp_path/'case.json';p.write_text('{"case_id":"a","case_id":"b"}')
    with pytest.raises(ValueError):load_critic_case(p)
    p.write_bytes(b' '*2097153)
    with pytest.raises(ValueError):load_critic_case(p)


def selection_inputs():
    routes={'sources':[{'task_id':f'route-{i}','target':source(i)['target'],
        'source_locator':f'paroutes#/{i}','reference_route_id':f'ref-{i}',
        'reference_edges':[{k:v for k,v in source(i)['edges'][0].items() if k in {'product','reactants'}}],
        'reference_inventory_closed':True} for i in range(4)]}
    cases=[];studies={}
    for i in range(5):
        sid=f'study-{i}';target='C'*(i+2)+'=O'
        row={'candidate_id':f'candidate-{i}','recipe':{'id':f'candidate-{i}',
             'reactants':['C'*(i+2)+'O'],'reagents':[],'product':target},'conditions':{'base':'O'}}
        studies[sid]={'study_id':sid,'target':target,'source_url':'https://example.org/data',
            'dataset_sha256':'c'*64,'candidates':[row]}
        cases.append({'study_id':sid,'candidate_id':row['candidate_id'],'source_match':True,
                      'submission_status':'selected','source':{'csv_line':i+2},'submitted_yield_percent':33})
    provenance={'paroutes':{'artifact_path':'route-review.json','artifact_sha256':'a'*64},
                'doyle':{'artifact_path':'condition-review.json','artifact_sha256':'b'*64}}
    return routes,{'cases':cases},studies,provenance


def test_selection_uses_ids_and_chemistry_not_outcomes_or_input_order():
    routes,review,studies,prov=selection_inputs();before=deepcopy((routes,review,studies,prov))
    first=select_sources(routes,review,studies,provenance=prov)
    changed={**review,'cases':[{**c,'submitted_yield_percent':'hidden-non-numeric'}for c in reversed(review['cases'])]}
    assert first==select_sources({**routes,'sources':list(reversed(routes['sources']))},changed,
                                dict(reversed(list(studies.items()))),provenance=prov)
    assert len(first)==8 and len({s['source_case_id']for s in first})==8
    assert source(3)['target']==first[3]['target']
    assert (routes,review,studies,prov)==before


def test_selection_rejects_missing_corrupt_or_duplicate_source_records():
    routes,review,studies,prov=selection_inputs()
    for bad in [{**routes,'sources':routes['sources'][:3]},
                {**routes,'sources':[routes['sources'][0]]*4}]:
        with pytest.raises(ValueError):select_sources(bad,review,studies,provenance=prov)
    bad=deepcopy(studies);bad['study-0']['candidates'][0]['recipe']['product']='C'
    with pytest.raises(ValueError):select_sources(routes,review,bad,provenance=prov)
