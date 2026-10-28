"""Route review stays a metered, read-only public action across local interfaces."""
import json
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from synthesis_route_gym.api import create_app
from synthesis_route_gym.cli import _parser
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.evidence_contracts import SourceRecord
from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
from synthesis_route_gym.planning import environment_tool_schemas
from test_core import make_task, make_route, make_step


def prepared(**kwargs):
    env=SynthesisRouteEnv(make_task(),**kwargs)
    assert env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')})['status']=='ok'
    return env


def test_review_is_readonly_metered_and_exact_action_replay_survives_resume(tmp_path):
    env=prepared(store=tmp_path/'episode')
    before=env.export()
    result=env.dispatch('review_routes',{'route_ids':['r1']},action_id='review-1')
    assert result['status']=='ok'
    assert result['result']['schema_version']=='srg-route-review-v1'
    assert result['result']['routes']==before['routes']
    assert result['result']['task_sha256']==env._task_sha256
    assert env.export()['routes']==before['routes']
    assert result['usage']['actions']==before['usage']['actions']+1
    assert not result['terminated'] and not result['truncated']
    restored=SynthesisRouteEnv.resume(tmp_path/'episode',expected_task=make_task())
    assert restored.dispatch('review_routes',{'route_ids':['r1']},action_id='review-1')==result
    assert restored.export()['usage']['actions']==result['usage']['actions']


@pytest.mark.parametrize('args',[{}, {'route_ids':[]},{'route_ids':['missing']},
    {'route_ids':['r1','r1']},{'route_ids':'r1'},{'route_ids':[True]},
    {'route_ids':['r1']*4},{'route_ids':['r1'],'sources':[]}])
def test_invalid_review_queries_consume_action_without_changing_routes(args):
    env=prepared();before=env.export()
    result=env.dispatch('review_routes',args)
    assert result['status']=='error'
    assert env.export()['routes']==before['routes']
    assert result['usage']['actions']==before['usage']['actions']+1


def test_review_never_reads_unretrieved_sources_or_private_attestations():
    now=datetime(2026,10,27,tzinfo=timezone.utc)
    source=SourceRecord(record_id='public-source',document_id='fixture',source_url='https://example.org/source',
        locator='fixture record',reactants=['CCO','CC(=O)O'],product='CCOC(C)=O',claim_kind='proxy',
        retrieved_at=now,source_content_sha256='a'*64)
    corpus=FrozenEvidenceCorpus([source],mode='evidence_retrieval',now=now)
    env=prepared(evidence_corpus=corpus,scientific_limits={'retrieval_calls':1})
    first=env.dispatch('review_routes',{'route_ids':['r1']})
    assert first['status']=='ok' and first['result']['sources']==[]
    assert env.dispatch('retrieve_sources',{'product':source.product})['status']=='ok'
    second=env.dispatch('review_routes',{'route_ids':['r1']})
    assert [r['record_id']for r in second['result']['sources']]==['public-source']
    assert all(r['verification_status']=='not_attested'for r in second['result']['sources'])
    assert not env._assess(env._route('r1')).solved


def test_review_then_revision_and_submission_use_existing_route_rules():
    env=prepared()
    assert env.dispatch('review_routes',{'route_ids':['r1']})['status']=='ok'
    revised=make_route(route_id='r2',parent_route_id='r1',steps=(make_step(conditions=('Unverified proposal',)),))
    assert env.dispatch('propose_route',{'route':revised.model_dump(mode='json')})['status']=='ok'
    packet=env.dispatch('review_routes',{'route_ids':['r2']})['result']
    assert packet['routes'][0]['parent_route_id']=='r1'
    submitted=env.dispatch('submit',{'route_ids':['r2']})
    assert submitted['result']['accepted_route_ids']==['r2']
    assert submitted['result']['independently_solved']is None


def test_schema_and_cli_expose_optional_critic_without_changing_default():
    schema=next(row for row in environment_tool_schemas()if row['name']=='review_routes')
    assert schema['parameters']['properties']['route_ids']['maxItems']==3
    common=['agent','--task','task.json','--output','out.json','--scientist-python','python','--scientist-source','source']
    assert _parser().parse_args(common).method=='main'
    assert _parser().parse_args(common+['--method','main_route_critic']).method=='main_route_critic'


def test_component_predictor_history_reaches_review_with_original_domain_limits():
    from synthesis_route_gym.schemas import Task,RouteCandidate
    class Predictor:
        metadata={'model_version':'software-fixture'}
        def predict(self,rows):return [{'predicted_yield_percent':12}for row in rows]
    roles={'aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}
    task=Task(task_id='component-fixture',target='CNc1ccccc1',
              inventory=[{'smiles':s}for s in [*roles.values(),'CN']])
    route=RouteCandidate(route_id='component-route',target=task.target,steps=[{
        'step_id':'step','product':task.target,'reactants':[{'smiles':roles['aryl halide']},{'smiles':'CN'}],
        'reagents':[{'smiles':roles[k]}for k in ['ligand','additive','base']],
        'condition_inputs':roles,'source_tool':'software-fixture','source_version':'1'}])
    env=SynthesisRouteEnv(task,condition_ranker=Predictor())
    env.dispatch('propose_route',{'route':route.model_dump(mode='json')})
    assert env.dispatch('predict_conditions',{'candidates':[{'id':'condition-a',**roles}]})['status']=='ok'
    packet=env.dispatch('review_routes',{'route_ids':[route.route_id]})['result']
    assert [r['action']for r in packet['tool_results']]==['predict_conditions']
    assert any(f['category']=='model_domain_mismatch' and f['severity']=='review'for f in packet['facts'])


def test_local_api_review_keeps_authentication_and_owner_isolation():
    client=TestClient(create_app({'fixture-one':'owner-one','fixture-two':'owner-two'}))
    headers={'Authorization':'Bearer fixture-one'}
    episode=client.post('/v1/episodes',json={'task':make_task().model_dump(mode='json')},headers=headers).json()['data']['episode_id']
    path=f'/v1/episodes/{episode}/actions'
    client.post(path,json={'action':'propose_route','arguments':{'route':make_route().model_dump(mode='json')}},headers=headers)
    request={'action':'review_routes','arguments':{'route_ids':['r1']}}
    assert client.post(path,json=request).status_code==401
    assert client.post(path,json=request,headers={'Authorization':'Bearer fixture-two'}).status_code==404
    response=client.post(path,json=request,headers=headers)
    assert response.status_code==200 and response.json()['data']['result']['schema_version']=='srg-route-review-v1'
    assert 'private'not in json.dumps(response.json()['data']['result'])
