"""Route-bound application actions share one metered, persistent environment."""
from copy import deepcopy
from datetime import datetime, timezone
import json
import pytest
from fastapi.testclient import TestClient

from synthesis_route_gym.api import create_app
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.evidence_contracts import SourceRecord
from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
from synthesis_route_gym.planning import environment_tool_schemas
from synthesis_route_gym.schemas import Task, RouteCandidate
from test_core import make_task, make_route
from test_portfolio_condition_binding import sample
from test_portfolio_impurities import annotation, step as impurity_step
from test_portfolio_biocatalysis import record as bio_record, step as bio_step, task as bio_task
from test_portfolio_process import fixture as process_fixture

APPS=('inventory_planning','condition_optimization','impurity_analysis','process_route_selection','biocatalytic_synthesis')
CONFIG={'schema_version':'srg-application-config-v1'}


def propose(env,route):
    raw=route.model_dump(mode='json')if isinstance(route,RouteCandidate)else route
    assert env.dispatch('propose_route',{'route':raw})['status']=='ok'
    return env


def condition_env(**kwargs):
    study,binding,step=sample()
    task=Task(task_id='condition-integration',target=step['product'],inventory=[{'smiles':s}for s in ('CCBr','O','N')])
    config={**CONFIG,'condition_binding':binding}
    env=SynthesisRouteEnv(task,condition_study=study,scientific_limits={'observation_calls':2},application_config=config,**kwargs)
    propose(env,{'route_id':'r1','target':task.target,'steps':[step]})
    return env,task,study,config


def bio_env(**kwargs):
    return propose(SynthesisRouteEnv(Task.model_validate(bio_task()),
        application_config={**CONFIG,'biocatalytic_records':[bio_record()]},**kwargs),
        {'route_id':'r1','target':'CCO','steps':[bio_step()]})


def report(env,application,route_ids=('r1',),step_id=None,**extra):
    args={'application':application,'route_ids':list(route_ids),**extra}
    if step_id is not None:args['step_id']=step_id
    return env.dispatch('application_report',args)


def walk(value,key):
    """Inspect public fields without depending on optional query wrappers."""
    if isinstance(value,dict):
        if key in value:yield value[key]
        for item in value.values():yield from walk(item,key)
    elif isinstance(value,list):
        for item in value:yield from walk(item,key)


def test_all_five_reports_are_readonly_and_metered():
    plain=propose(SynthesisRouteEnv(make_task(),application_config=CONFIG),make_route())
    condition,_,_,_=condition_env()
    t,r,d,b=process_fixture();process=propose(SynthesisRouteEnv(Task.model_validate(t),application_config={**CONFIG,'process_basis':b}),r)
    impurity=propose(SynthesisRouteEnv(Task.model_validate(bio_task()),application_config=CONFIG),
        {'route_id':'r1','target':'CCO','steps':[impurity_step()]})
    bio=bio_env()
    cases=[(plain,'inventory_planning','r1',None),(condition,'condition_optimization','r1','stored-step'),
      (impurity,'impurity_analysis','r1','s1'),(process,'process_route_selection','convergent',None),
      (bio,'biocatalytic_synthesis','r1','s1')]
    for env,app,ident,step in cases:
        before=env.export();response=report(env,app,[ident],step)
        assert response['status']=='ok',response
        value=response['result'];assert value['schema_version']=='srg-application-report-v1'
        assert value['application']==app and value['claims_experimental_validation']is False
        assert value['route_references'] and isinstance(value['input_event_references'],list)
        assert isinstance(value['result'],dict)
        after=env.export();assert after['routes']==before['routes'] and after['submitted_route_ids']==before['submitted_route_ids']
        assert after['scientific_usage']==before['scientific_usage']
        assert after['usage']['actions']==before['usage']['actions']+1
        assert not after['terminated'] and not after['truncated']


@pytest.mark.parametrize('args',[{}, {'application':'unknown','route_ids':['r1']},
 {'application':'inventory_planning','route_ids':[]},{'application':'inventory_planning','route_ids':['missing']},
 {'application':'inventory_planning','route_ids':['r1','r1']},{'application':'inventory_planning','route_ids':['r1']*4},
 {'application':'inventory_planning','route_ids':'r1'},{'application':'inventory_planning','route_ids':['r1'],'records':[]},
 {'application':'impurity_analysis','route_ids':['r1']},{'application':'impurity_analysis','route_ids':['r1'],'step_id':'missing'},
 {'application':'inventory_planning','route_ids':['r1'],'step_id':'ester'}])
def test_invalid_report_references_never_change_routes(args):
    env=propose(SynthesisRouteEnv(make_task(),application_config=CONFIG),make_route());before=env.export()
    result=env.dispatch('application_report',args)
    assert result['status']=='error'
    assert env.export()['routes']==before['routes']
    assert result['usage']['actions']==before['usage']['actions']+1


def test_conditions_are_redacted_paged_and_bound_to_stored_step():
    env,_,_,_=condition_env();args={'route_id':'r1','step_id':'stored-step','offset':0,'limit':1}
    response=env.dispatch('condition_options',args);assert response['status']=='ok'
    candidates=next(walk(response['result'],'candidates'));assert len(candidates)==1
    assert candidates[0]['candidate_id']=='a'
    serialized=json.dumps(response)
    assert '12.25'not in serialized and '87.75'not in serialized and 'yield_percent'not in serialized
    wrong=env.dispatch('condition_options',{**args,'step_id':'no-such-step'});assert wrong['status']=='error'
    injected=env.dispatch('condition_options',{**args,'product':'CCN'});assert injected['status']=='error'
    for bad in ({'offset':-1},{'limit':0},{'limit':True}):
        assert env.dispatch('condition_options',{**args,**bad})['status']=='error'


def test_condition_observation_once_resume_and_unchanged_step_yield(tmp_path):
    path=tmp_path/'condition';env,task,study,config=condition_env(store=path)
    args={'route_id':'r1','step_id':'stored-step','candidate_id':'a'}
    first=env.dispatch('observe_route_condition',args,action_id='observe-a');assert first['status']=='ok'
    assert 12.25 in list(walk(first['result'],'yield_percent'))
    actions=env.export()['usage']['actions'];assert env.dispatch('observe_route_condition',args,action_id='observe-a')==first
    assert env.export()['usage']['actions']==actions
    restored=SynthesisRouteEnv.resume(path,expected_task=task,condition_study=study,
        scientific_limits={'observation_calls':2},application_config=config)
    assert restored.dispatch('observe_route_condition',args,action_id='observe-a')==first
    summary=report(restored,'condition_optimization',step_id='stored-step');assert summary['status']=='ok'
    assert summary['result']['result']['best_observed_candidate_id']=='a'
    assert summary['result']['result']['route_step_yield_percent']is None
    assert '87.75'not in json.dumps(summary)
    second=restored.dispatch('observe_route_condition',{**args,'candidate_id':'b'});assert second['status']=='ok'
    assert 87.75 in list(walk(second['result'],'yield_percent'))
    assert restored.dispatch('observe_route_condition',args)['status']!='ok'
    assert report(restored,'condition_optimization',step_id='stored-step')['result']['result']['best_observed_candidate_id']=='b'


def test_condition_binding_reaction_mismatch_cannot_reveal_outcome():
    env,_,_,_=condition_env();changed=deepcopy(env.export()['routes'][0]);changed['route_id']='r2';changed['parent_route_id']='r1'
    changed['steps'][0]['reactants']=[{'smiles':'CCCBr'}];propose(env,changed)
    response=env.dispatch('observe_route_condition',{'route_id':'r2','step_id':'stored-step','candidate_id':'b'})
    assert response['status']!='ok' and '87.75'not in json.dumps(response)


def test_application_config_is_bound_across_resume(tmp_path):
    config={**CONFIG,'process_basis':{'purity_basis':'fixture','exclusions':['labor']}}
    env=propose(SynthesisRouteEnv(make_task(),store=tmp_path/'episode',application_config=config),make_route())
    first=env.dispatch('application_report',{'application':'inventory_planning','route_ids':['r1']},action_id='report')
    restored=SynthesisRouteEnv.resume(tmp_path/'episode',expected_task=make_task(),application_config=config)
    assert restored.dispatch('application_report',{'application':'inventory_planning','route_ids':['r1']},action_id='report')==first
    changed={**config,'process_basis':{'purity_basis':'different','exclusions':['labor']}}
    with pytest.raises(ValueError):SynthesisRouteEnv.resume(tmp_path/'episode',expected_task=make_task(),application_config=changed)


def test_impurity_prediction_uses_stored_chemistry_and_does_not_leak_to_revision():
    calls=[]
    def predictor(reactants,product,top_k):
        calls.append((reactants,product,top_k));return {'status':'ok','predicted_smiles':['CC(=O)O']}
    env=propose(SynthesisRouteEnv(Task.model_validate(bio_task()),impurity=predictor,application_config=CONFIG),
        {'route_id':'r1','target':'CCO','steps':[impurity_step()]})
    first=report(env,'impurity_analysis',step_id='s1')['result']['result']
    assert first['prediction_status']=='not_run' and first['predicted_impurities']is None
    assert env.dispatch('predict_route_impurities',{'route_id':'r1','step_id':'s1','top_k':3})['status']=='ok'
    assert calls==[('CCOC(C)=O.O','CCO',3)]
    supported=report(env,'impurity_analysis',step_id='s1')['result'];assert supported['input_event_references']
    assert supported['result']['prediction_status']=='ok' and supported['result']['predicted_impurities']==['CC(=O)O']
    changed=deepcopy(env.export()['routes'][0]);changed['route_id']='r2';changed['parent_route_id']='r1';changed['steps'][0]['conditions']=['changed']
    propose(env,changed);other=report(env,'impurity_analysis',['r2'],'s1')['result']['result']
    assert other['prediction_status']=='not_run' and other['predicted_impurities']is None
    assert env.dispatch('predict_route_impurities',{'route_id':'r1','step_id':'s1','product':'CCC'})['status']=='error'
    assert len(calls)==1


def test_failed_impurity_prediction_remains_failure_not_empty_success():
    env=propose(SynthesisRouteEnv(Task.model_validate(bio_task()),impurity=lambda *args:{'status':'unavailable'},application_config=CONFIG),
        {'route_id':'r1','target':'CCO','steps':[impurity_step()]})
    assert env.dispatch('predict_route_impurities',{'route_id':'r1','step_id':'s1'})['status']=='unavailable'
    result=report(env,'impurity_analysis',step_id='s1')['result']['result']
    assert result['prediction_status']=='unavailable' and result['predicted_impurities']is None


def test_bio_sources_require_retrieval_and_shared_budget():
    env=bio_env(source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':1})
    first=report(env,'biocatalytic_synthesis',step_id='s1');assert first['result']['result']['candidates']==[]
    args={'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1'}
    assert env.dispatch('retrieve_application_sources',args)['status']=='ok'
    result=report(env,'biocatalytic_synthesis',step_id='s1')['result'];assert result['input_event_references']
    candidate=result['result']['candidates'][0]
    assert candidate['match_kind']=='exact_substrates_product_projection'
    assert candidate['experimental_yield']is None and candidate['claims_activity']is False
    assert env.dispatch('retrieve_application_sources',args)['status']!='ok'
    closed=bio_env(scientific_limits={'retrieval_calls':1})
    assert closed.dispatch('retrieve_application_sources',args)['status']!='ok'
    assert report(closed,'biocatalytic_synthesis',step_id='s1')['result']['result']['candidates']==[]


def test_application_retrieval_shares_primitive_retrieval_allowance():
    now=datetime(2026,10,27,tzinfo=timezone.utc)
    source=SourceRecord(record_id='public',document_id='fixture',source_url='https://example.org/source',locator='row',
        reactants=['CCOC(C)=O','O'],product='CCO',claim_kind='proxy',retrieved_at=now,source_content_sha256='a'*64)
    corpus=FrozenEvidenceCorpus([source],mode='evidence_retrieval',now=now)
    env=bio_env(evidence_corpus=corpus,scientific_limits={'retrieval_calls':1})
    assert env.dispatch('retrieve_sources',{})['status']=='ok'
    request={'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1'}
    assert env.dispatch('retrieve_application_sources',request)['status']!='ok'
    assert report(env,'biocatalytic_synthesis',step_id='s1')['result']['result']['candidates']==[]


def test_impurity_annotation_is_hidden_until_retrieved_and_partial_scope_stays_partial():
    step=impurity_step();ann=annotation(step)
    env=propose(SynthesisRouteEnv(Task.model_validate(bio_task()),
        impurity=lambda *args:{'status':'ok','predicted_smiles':['CC(=O)O','CO']},
        source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':1},
        application_config={**CONFIG,'impurity_annotations':[ann]}),{'route_id':'r1','target':'CCO','steps':[step]})
    initial=report(env,'impurity_analysis',step_id='s1')['result']['result'];assert initial['annotation_results']==[]
    assert ann['source_locator']not in json.dumps(env.inspect())
    assert env.dispatch('predict_route_impurities',{'route_id':'r1','step_id':'s1'})['status']=='ok'
    assert env.dispatch('retrieve_application_sources',{'application':'impurity_analysis','route_id':'r1','step_id':'s1'})['status']=='ok'
    result=report(env,'impurity_analysis',step_id='s1')['result']['result'];assay=result['annotation_results'][0]
    assert assay['metrics']['precision']is None and assay['metrics']['false_positives']is None


def test_new_tool_schemas_are_strict_and_api_keeps_tenant_boundary():
    names={'application_report','condition_options','observe_route_condition','predict_route_impurities','retrieve_application_sources'}
    schemas={row['name']:row['parameters']for row in environment_tool_schemas()}
    assert names<=schemas.keys()
    assert all(schemas[name]['additionalProperties']is False for name in names)
    client=TestClient(create_app({'owner-a-token':'a','owner-b-token':'b'},application_config=CONFIG))
    headers={'Authorization':'Bearer owner-a-token'}
    response=client.post('/v1/episodes',headers=headers,json={'task':make_task().model_dump(mode='json')})
    ident=response.json()['data']['episode_id'];path=f'/v1/episodes/{ident}/actions'
    assert client.post(path,headers=headers,json={'action':'propose_route','arguments':{'route':make_route().model_dump(mode='json')}}).status_code==200
    request={'action':'application_report','arguments':{'application':'inventory_planning','route_ids':['r1']}}
    assert client.post(path,json=request).status_code==401
    assert client.post(path,headers={'Authorization':'Bearer owner-b-token'},json=request).status_code==404
    value=client.post(path,headers=headers,json=request)
    assert value.status_code==200 and value.json()['data']['status']=='ok'
    assert client.post('/v1/episodes',headers=headers,json={'task':make_task().model_dump(mode='json'),'application_config':CONFIG}).status_code==422


def test_unbound_primitive_prediction_and_observation_do_not_transfer_authority():
    env,_,_,_=condition_env()
    assert env.dispatch('observe_condition',{'candidate_id':'a'})['status']=='ok'
    bound=report(env,'condition_optimization',step_id='stored-step')['result']['result']
    assert bound['observation_count']==0 and bound['best_observed_candidate_id']is None
    assert '12.25'not in json.dumps(bound)
    assert env.dispatch('observe_route_condition',{'route_id':'r1','step_id':'stored-step','candidate_id':'a'})['status']!='ok'
    predictor=lambda *args:{'status':'ok','predicted_smiles':['CCO']}
    other=propose(SynthesisRouteEnv(make_task(),impurity=predictor,application_config=CONFIG),make_route())
    assert other.dispatch('predict_impurities',{'reactants':['CCO','CC(=O)O'],'product':'CCOC(C)=O'})['status']=='ok'
    result=report(other,'impurity_analysis',step_id='ester')['result']['result']
    assert result['prediction_status']=='not_run'


def test_source_retrieval_replay_survives_resume_without_another_charge(tmp_path):
    config={**CONFIG,'biocatalytic_records':[bio_record()]};path=tmp_path/'bio'
    env=bio_env(store=path,source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':1})
    request={'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1'}
    first=env.dispatch('retrieve_application_sources',request,action_id='sources');assert first['status']=='ok'
    before=env.export()['usage']['actions']
    restored=SynthesisRouteEnv.resume(path,expected_task=Task.model_validate(bio_task()),application_config=config,
        source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':1})
    assert restored.dispatch('retrieve_application_sources',request,action_id='sources')==first
    assert restored.export()['usage']['actions']==before
    assert len(report(restored,'biocatalytic_synthesis',step_id='s1')['result']['result']['candidates'])==1


@pytest.mark.parametrize('action,args',[
 ('predict_route_impurities',{'route_id':'r1','step_id':'s1','top_k':True}),
 ('retrieve_application_sources',{'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1','records':[]}),
 ('retrieve_application_sources',{'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1','records_path':'/private'}),
 ('retrieve_application_sources',{'application':'process_route_selection','route_id':'r1','step_id':'s1'})])
def test_query_boundaries_reject_model_supplied_data_and_paths(action,args):
    env=bio_env(source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':10})
    assert env.dispatch(action,args)['status']=='error'
    assert report(env,'biocatalytic_synthesis',step_id='s1')['result']['result']['candidates']==[]


@pytest.mark.parametrize('config',[
 {'schema_version':'wrong'}, {**CONFIG,'records_path':'/private'},
 {**CONFIG,'biocatalytic_records':[bio_record(),bio_record()]},
 {**CONFIG,'impurity_annotations':[annotation(),annotation()]},
 {**CONFIG,'process_basis':{'purity_basis':'x'*1_000_001}}])
def test_host_application_configuration_is_typed_bounded_and_unique(config):
    with pytest.raises(ValueError):SynthesisRouteEnv(make_task(),application_config=config)


def test_unobserved_conditions_cannot_be_selected_and_unknown_candidate_is_rejected():
    env,_,_,_=condition_env()
    result=report(env,'condition_optimization',step_id='stored-step',candidate_id='b')
    assert result['status']=='error' and '87.75'not in json.dumps(result)
    result=env.dispatch('observe_route_condition',{'route_id':'r1','step_id':'stored-step','candidate_id':'unknown'})
    assert result['status']=='error'
    other=report(env,'inventory_planning',candidate_id='a');assert other['status']=='error'


def test_ambiguous_steps_and_oversized_route_context_are_rejected():
    t=Task.model_validate(bio_task())
    duplicate={'route_id':'r1','target':'CCO','steps':[bio_step(),bio_step()]}
    env=propose(SynthesisRouteEnv(t,application_config=CONFIG),duplicate)
    assert report(env,'impurity_analysis',step_id='s1')['status']=='error'
    large={'route_id':'r2','target':'CCO','steps':[bio_step(step_id=f's{i}')for i in range(13)]}
    propose(env,large)
    assert report(env,'inventory_planning',['r2'])['status']=='error'
    assert env.dispatch('predict_route_impurities',{'route_id':'r2','step_id':'s0'})['status']=='error'


def test_source_pagination_and_route_revision_are_independently_bound():
    config={**CONFIG,'biocatalytic_records':[bio_record(),bio_record(record_id='fixture-second')]}
    env=propose(SynthesisRouteEnv(Task.model_validate(bio_task()),application_config=config,
        source_access_mode='evidence_retrieval',scientific_limits={'retrieval_calls':1}),
        {'route_id':'r1','target':'CCO','steps':[bio_step()]})
    response=env.dispatch('retrieve_application_sources',{'application':'biocatalytic_synthesis','route_id':'r1','step_id':'s1','offset':1,'limit':1})
    assert response['status']=='ok' and response['result']['record_count']==2
    assert [r['record_id']for r in response['result']['records']]==['fixture-second']
    seen=report(env,'biocatalytic_synthesis',step_id='s1')['result']['result']['candidates']
    assert [r['record_id']for r in seen]==['fixture-second']
    propose(env,{'route_id':'r2','parent_route_id':'r1','target':'CCO','steps':[bio_step()]})
    assert report(env,'biocatalytic_synthesis',['r2'],'s1')['result']['result']['candidates']==[]
