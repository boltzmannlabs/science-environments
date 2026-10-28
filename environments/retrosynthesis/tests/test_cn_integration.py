"""The source-scoped C–N scorer remains a predicted, optional host tool."""
import json
import time
import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task
from synthesis_route_gym.tool_registry import ToolRegistry, ToolBinding


def candidate(ident='one', **changes):
    return {'id':ident,'aryl':'Brc1ccccc1','amine':'CN','catalyst':'[Pd]',
            'base':'N','solvent':'O','product':'CNc1ccccc1',**changes}


def task():
    return Task(task_id='cn-tool-fixture',target='CNc1ccccc1',inventory=())


def prediction(ident='one', **changes):
    return {'id':ident,'status':'scored','hit_score':0.7,'reason':None,
            'model_version':'backend-untrusted-version','domain':'source-scoped fixture',
            'calibration_kind':'uncalibrated_forest_score','evidence_status':'predicted',**changes}


class Predictor:
    metadata = {'model_version':'cn-fixture-v1'}
    _artifact = {'schema_version':'synthetic-test','metadata':metadata}
    def predict(self, rows):
        return [prediction(status='abstained',hit_score=None,reason='outside_domain')
                if row['amine']=='O' else prediction(private_training_label=1,
                measured_yield_percent=99,evidence_status='measured') for row in rows]


def test_cn_capability_is_explicit_unavailable_without_host_model():
    env=SynthesisRouteEnv(task())
    result=env.dispatch('score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='unavailable'
    assert result['result']['capability']=='score_cn_conditions'
    assert env.export()['scientific_usage']['score_cn_conditions']==1
    descriptor=next(r for r in ToolRegistry().describe() if r['name']=='score_cn_conditions')
    assert descriptor['availability']=='not_configured'
    assert descriptor['evidence_kind']=='predicted_screen_hit'


def test_mixed_prediction_and_abstention_are_projected_pinned_and_metered():
    env=SynthesisRouteEnv(task(),cn_condition_model=Predictor())
    result=env.dispatch('score_cn_conditions',{'candidates':[candidate(),candidate('two',amine='O')]})
    assert result['status']=='ok'
    data=result['result']['data']['predictions']
    assert [r['id'] for r in data]==['one','two']
    assert [r['status'] for r in data]==['scored','abstained']
    assert data[1]['hit_score'] is None and data[1]['reason']=='outside_domain'
    assert all(r['evidence_status']=='predicted' and r['model_version']=='cn-fixture-v1' for r in data)
    assert 'private_training_label' not in json.dumps(data) and 'measured_yield_percent' not in json.dumps(data)
    assert result['result']['provenance']['binding']['artifact_sha256']
    assert result['result']['usage']['backend_calls']==1
    assert env.export()['usage']['expansions']==0


@pytest.mark.parametrize('change',[{'status':'scored','hit_score':None},
    {'status':'abstained','hit_score':0.1,'reason':'outside_domain'},
    {'status':'abstained','hit_score':None,'reason':None},
    {'status':'abstained','hit_score':None,'reason':' '},
    {'hit_score':float('nan')},{'hit_score':True},{'hit_score':1.1},
    {'id':'wrong'},{'status':'measured'}])
def test_invalid_cn_outputs_fail_closed(change):
    registry=ToolRegistry({'score_cn_conditions':ToolBinding(
        lambda args:{'status':'ok','predictions':[prediction(**change)]},version='test',model_version='pinned')})
    result=registry.invoke('score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='error' and result['data'] is None


@pytest.mark.parametrize('candidates',[[candidate(),candidate()],[],
    [candidate(product='not SMILES')],[candidate(label=1)]])
def test_invalid_cn_requests_never_call_backend(candidates):
    def unexpected(_): raise AssertionError('invalid request invoked backend')
    result=ToolRegistry({'score_cn_conditions':ToolBinding(unexpected,version='test')}).invoke(
        'score_cn_conditions',{'candidates':candidates})
    assert result['status']=='error' and result['usage']['backend_calls']==0


def test_resume_preserves_cn_accounting_and_rejects_changed_model(tmp_path):
    env=SynthesisRouteEnv(task(),cn_condition_model=Predictor(),store=tmp_path/'episode')
    env.dispatch('score_cn_conditions',{'candidates':[candidate()]},action_id='one')
    resumed=SynthesisRouteEnv.resume(tmp_path/'episode',cn_condition_model=Predictor())
    assert resumed.export()['scientific_usage']=={'score_cn_conditions':1}
    resumed.dispatch('score_cn_conditions',{'candidates':[candidate()]},action_id='one')
    assert resumed.export()['usage']['actions']==1
    with pytest.raises(ValueError,match='configuration'):
        SynthesisRouteEnv.resume(tmp_path/'episode')


def test_cn_timeout_uses_common_contract_and_keeps_charge():
    def slow(args):
        time.sleep(.04)
        return {'status':'ok','predictions':[prediction()]}
    registry=ToolRegistry({'score_cn_conditions':ToolBinding(slow,version='test',timeout_seconds=.005)})
    env=SynthesisRouteEnv(task(),scientific_tools=registry)
    result=env.dispatch('score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='error' and result['result']['error']['code']=='tool_timeout'
    assert result['result']['usage']['backend_calls']==1
    assert env.export()['scientific_usage']['score_cn_conditions']==1


def test_cn_configuration_cannot_be_mixed_with_custom_registry():
    with pytest.raises(ValueError,match='registry or component'):
        SynthesisRouteEnv(task(),scientific_tools=ToolRegistry(),cn_condition_model=Predictor())


def test_cn_action_is_in_agent_schema_without_replacing_doyle():
    from synthesis_route_gym.agent_runner import ACTIONS
    from synthesis_route_gym.planning import environment_tool_schemas
    schemas={r['name']:r for r in environment_tool_schemas()}
    assert 'score_cn_conditions' in ACTIONS and 'score_cn_conditions' in schemas
    assert 'predict_conditions' in ACTIONS and 'predict_conditions' in schemas
    assert schemas['score_cn_conditions']['parameters']['additionalProperties'] is False


def test_api_episode_accepts_cn_action_with_host_model():
    from fastapi.testclient import TestClient
    from synthesis_route_gym.api import create_app
    client=TestClient(create_app({'test-key':'tenant'},cn_condition_model=Predictor()))
    headers={'Authorization':'Bearer test-key'}
    created=client.post('/v1/episodes',headers=headers,json={'task':task().model_dump(mode='json')})
    assert created.status_code==201,created.text
    ident=created.json()['data']['episode_id']
    result=client.post(f'/v1/episodes/{ident}/actions',headers=headers,
        json={'action':'score_cn_conditions','arguments':{'candidates':[candidate()]}})
    assert result.status_code==200,result.text
    assert result.json()['data']['result']['data']['predictions'][0]['hit_score']==0.7


def synthetic_artifact(score=0.8):
    from synthesis_route_gym.cn_model import CN_ROLES, FEATURE_VERSION, MODEL_SCHEMA
    row=candidate()
    return {'schema_version':MODEL_SCHEMA,'feature_version':FEATURE_VERSION,'n_features':768,
        'metadata':{'model_version':'integration-fixture-v1',
          'training_component_smiles':{role:[row[role]] for role in CN_ROLES},
          'substrate_similarity_threshold':0.2,
          'endpoint':'source_reported_CAD_response_gte_10_not_isolated_yield_or_general_feasibility'},
        'calibration':None,'trees':[{'left':[-1],'right':[-1],'feature':[-2],
                                    'threshold':[-2.0],'value':[score]}]}


def test_real_json_model_cli_replay_end_to_end(tmp_path):
    import subprocess
    import sys
    model=tmp_path/'cn.json'; model.write_text(json.dumps(synthetic_artifact()))
    task_path=tmp_path/'task.json'; task_path.write_text(task().model_dump_json())
    actions=tmp_path/'actions.json'; actions.write_text(json.dumps([
        {'action':'score_cn_conditions','arguments':{'candidates':[
            candidate(),candidate('outside',catalyst='[Ni]')]}},
        {'action':'submit','arguments':{'route_ids':[]}}]))
    output=tmp_path/'report.json'
    result=subprocess.run([sys.executable,'-m','synthesis_route_gym','replay',
        '--task',str(task_path),'--actions',str(actions),'--cn-condition-model',str(model),
        '--output',str(output)],capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    report=json.loads(output.read_text())
    predictions=report['events'][0]['result']['data']['predictions']
    assert predictions[0]['hit_score']==0.8 and predictions[0]['evidence_status']=='predicted'
    assert predictions[0]['raw_hit_score']==0.8
    assert predictions[1]['raw_hit_score'] is None
    assert predictions[1]['status']=='abstained' and predictions[1]['hit_score'] is None
    assert report['scientific_usage']['score_cn_conditions']==1
    assert report['submitted_route_ids']==[]


def test_cli_invalid_cn_json_fails_before_creating_report(tmp_path):
    import subprocess
    import sys
    task_path=tmp_path/'task.json'; task_path.write_text(task().model_dump_json())
    model=tmp_path/'bad.json'; model.write_text('{"schema_version":"bad"}')
    output=tmp_path/'report.json'
    result=subprocess.run([sys.executable,'-m','synthesis_route_gym','plan',
        '--task',str(task_path),'--cn-condition-model',str(model),'--output',str(output)],
        capture_output=True,text=True,timeout=30)
    assert result.returncode!=0
    assert not output.exists()


def test_resume_rejects_changed_artifact_even_with_same_model_version(tmp_path):
    from synthesis_route_gym.cn_model import CNConditionModel
    env=SynthesisRouteEnv(task(),cn_condition_model=CNConditionModel(synthetic_artifact()),store=tmp_path/'episode')
    env.dispatch('score_cn_conditions',{'candidates':[candidate()]})
    with pytest.raises(ValueError,match='configuration'):
        SynthesisRouteEnv.resume(tmp_path/'episode',
            cn_condition_model=CNConditionModel(synthetic_artifact(score=0.1)))


def test_incomplete_host_predictions_fail_closed():
    class Incomplete(Predictor):
        def predict(self,rows): return []
    result=SynthesisRouteEnv(task(),cn_condition_model=Incomplete()).dispatch(
        'score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='error' and result['result']['data'] is None


@pytest.mark.parametrize('raw_score',[float('nan'),float('inf'),True,-0.1,1.1,'0.5'])
def test_invalid_raw_cn_scores_fail_closed(raw_score):
    registry=ToolRegistry({'score_cn_conditions':ToolBinding(
        lambda args:{'status':'ok','predictions':[prediction(raw_hit_score=raw_score)]},
        version='test',model_version='pinned')})
    result=registry.invoke('score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='error' and result['data'] is None


def test_abstention_cannot_contain_raw_score():
    registry=ToolRegistry({'score_cn_conditions':ToolBinding(
        lambda args:{'status':'ok','predictions':[prediction(status='abstained',
            hit_score=None,raw_hit_score=0.2,reason='outside_domain')]},
        version='test',model_version='pinned')})
    result=registry.invoke('score_cn_conditions',{'candidates':[candidate()]})
    assert result['status']=='error' and result['data'] is None


def test_raw_score_projection_preserves_score_without_calibration_claim():
    registry=ToolRegistry({'score_cn_conditions':ToolBinding(
        lambda args:{'status':'ok','predictions':[prediction(hit_score=0.3,raw_hit_score=0.8,
            calibration_kind='heldout_isotonic_not_transfer_guarantee')]},
        version='test',model_version='pinned')})
    result=registry.invoke('score_cn_conditions',{'candidates':[candidate()]})
    row=result['data']['predictions'][0]
    assert row['hit_score']==0.3 and row['raw_hit_score']==0.8
    assert row['evidence_status']=='predicted'
