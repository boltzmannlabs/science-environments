"""A replaceable yield tool cannot promote predictions to scientific evidence."""
import json
import time
import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task
from synthesis_route_gym.tool_registry import ToolBinding, ToolRegistry


def task():
    return Task(task_id='public-yield-fixture', target='CCOC(C)=O', inventory=())


def candidate(ident='one', **changes):
    return {'id':ident, 'reactants':['CCO','CC(=O)O'], 'reagents':[],
            'product':'CCOC(C)=O', **changes}


def prediction(ident='one', **changes):
    return {'id':ident, 'status':'scored', 'predicted_yield_percent':70.0,
            'raw_yield_percent':70.0, 'reason':None, 'domain':'synthetic test',
            'model_version':'untrusted', **changes}


class Predictor:
    metadata = {'model_version':'yield-fixture-v1'}
    artifact = {'weights_sha256':'a'*64}
    configuration = {'device':'cpu', 'max_length':512}
    timeout_seconds = 2

    def predict(self, rows):
        return [prediction(row['id'], status='abstained', predicted_yield_percent=None,
                    raw_yield_percent=None, reason='outside_domain') if row['reagents']==['O']
                else prediction(row['id'], evidence_status='measured',
                    uncertainty_kind='experimentally_calibrated', private_label=99,
                    endpoint_scope='experimentally_validated') for row in rows]


def registry(change):
    return ToolRegistry({'predict_reaction_yield':ToolBinding(
        lambda args:{'predictions':[prediction(**change)]}, version='fixture', model_version='pinned')})


def test_public_yield_is_discoverable_but_unavailable_without_model():
    from synthesis_route_gym.agent_runner import ACTIONS
    from synthesis_route_gym.planning import environment_tool_schemas
    descriptor=next(r for r in ToolRegistry().describe() if r['name']=='predict_reaction_yield')
    assert descriptor['availability']=='not_configured'
    assert descriptor['evidence_kind']=='predicted_yield'
    assert 'predict_reaction_yield' in ACTIONS
    assert 'predict_reaction_yield' in {r['name'] for r in environment_tool_schemas()}
    env=SynthesisRouteEnv(task())
    result=env.dispatch('predict_reaction_yield',{'candidates':[candidate()]})
    assert result['status']=='unavailable'
    assert env.export()['scientific_usage']=={'predict_reaction_yield':1}


def test_predictions_abstentions_and_host_authority_are_preserved():
    env=SynthesisRouteEnv(task(),reaction_yield_predictor=Predictor())
    result=env.dispatch('predict_reaction_yield',{'candidates':[candidate(),candidate('two',reagents=['O'])]})
    assert result['status']=='ok',result
    envelope=result['result']
    rows=envelope['data']['predictions']
    assert [r['id'] for r in rows]==['one','two']
    assert [r['status'] for r in rows]==['scored','abstained']
    assert rows[1]['predicted_yield_percent'] is None and rows[1]['reason']=='outside_domain'
    assert all(r['evidence_status']=='predicted' and r['model_version']=='yield-fixture-v1' for r in rows)
    assert all(r['uncertainty_kind']=='not_calibrated' for r in rows)
    assert all(r['endpoint_scope']=='model_yield_not_experimental_feasibility' for r in rows)
    assert 'private_label' not in json.dumps(rows)
    assert envelope['usage']['backend_calls']==1
    assert envelope['provenance']['binding']['artifact_sha256']
    assert envelope['provenance']['binding']['timeout_seconds']==2
    assert env.export()['usage']['expansions']==0
    assert env.export()['routes']==[]


@pytest.mark.parametrize('change',[
    {'status':'scored','predicted_yield_percent':None}, {'raw_yield_percent':None},
    {'predicted_yield_percent':101}, {'predicted_yield_percent':-1},
    {'predicted_yield_percent':True}, {'raw_yield_percent':True},
    {'raw_yield_percent':float('nan')}, {'raw_yield_percent':float('inf')},
    {'status':'abstained','reason':'outside_domain'},
    {'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':None,'reason':None},
    {'status':'abstained','predicted_yield_percent':None,'raw_yield_percent':None,'reason':' '},
    {'status':'scored','reason':'outside_domain'}, {'id':'wrong'}, {'status':'measured'},
])
def test_invalid_yield_outputs_fail_closed(change):
    result=registry(change).invoke('predict_reaction_yield',{'candidates':[candidate()]})
    assert result['status']=='error' and result['data'] is None


def test_abstention_preserves_finite_out_of_range_raw_value_for_diagnostics():
    result=registry({'status':'abstained','predicted_yield_percent':None,
                     'raw_yield_percent':105.0,'reason':'outside_physical_yield_range'}).invoke(
        'predict_reaction_yield',{'candidates':[candidate()]})
    assert result['status']=='ok'
    row=result['data']['predictions'][0]
    assert row['predicted_yield_percent'] is None and row['raw_yield_percent']==105.0
    assert row['status']=='abstained' and row['evidence_status']=='predicted'


@pytest.mark.parametrize('rows',[
    [], [candidate(),candidate()], [candidate(label=1)], [candidate(product='invalid SMILES')],
    [candidate(reactants=[])], [candidate(reagents=[''])], [candidate(reactants='CCO')],
    [candidate(str(i)) for i in range(101)],
])
def test_invalid_requests_do_not_invoke_predictor(rows):
    result=registry({}).invoke('predict_reaction_yield',{'candidates':rows})
    assert result['status']=='error' and result['usage']['backend_calls']==0


def test_changed_model_and_runtime_configuration_change_identity(tmp_path):
    env=SynthesisRouteEnv(task(),reaction_yield_predictor=Predictor(),store=tmp_path/'episode')
    args={'candidates':[candidate()]}
    env.dispatch('predict_reaction_yield',args,action_id='first')
    resumed=SynthesisRouteEnv.resume(tmp_path/'episode',reaction_yield_predictor=Predictor())
    resumed.dispatch('predict_reaction_yield',args,action_id='first')
    assert resumed.export()['usage']['actions']==1
    assert resumed.export()['scientific_usage']=={'predict_reaction_yield':1}
    class ChangedWeights(Predictor):
        artifact={'weights_sha256':'b'*64}
    class ChangedRuntime(Predictor):
        configuration={'device':'cpu','max_length':256}
    for predictor in (None,ChangedWeights(),ChangedRuntime()):
        with pytest.raises(ValueError,match='configuration'):
            SynthesisRouteEnv.resume(tmp_path/'episode',reaction_yield_predictor=predictor)
    old=env._scientific_tools.cache_identity('predict_reaction_yield',args)
    new=SynthesisRouteEnv(task(),reaction_yield_predictor=ChangedWeights())._scientific_tools
    assert old != new.cache_identity('predict_reaction_yield',args)


def test_incomplete_and_reordered_predictions_fail_closed():
    class Incomplete(Predictor):
        def predict(self, rows): return []
    class Reordered(Predictor):
        def predict(self, rows): return [prediction(row['id']) for row in reversed(rows)]
    for predictor in (Incomplete(),Reordered()):
        result=SynthesisRouteEnv(task(),reaction_yield_predictor=predictor).dispatch(
            'predict_reaction_yield',{'candidates':[candidate(),candidate('two')]})
        assert result['status']=='error' and result['result']['data'] is None


def test_timeout_is_charged_without_accepting_late_prediction():
    class Slow(Predictor):
        timeout_seconds=.005
        def predict(self, rows):
            time.sleep(.04)
            return [prediction(row['id']) for row in rows]
    env=SynthesisRouteEnv(task(),reaction_yield_predictor=Slow())
    result=env.dispatch('predict_reaction_yield',{'candidates':[candidate()]})
    assert result['status']=='error' and result['result']['error']['code']=='tool_timeout'
    assert result['result']['usage']['backend_calls']==1
    assert env.export()['scientific_usage']=={'predict_reaction_yield':1}


def test_registry_and_predictor_cannot_be_mixed():
    with pytest.raises(ValueError,match='registry or component'):
        SynthesisRouteEnv(task(),scientific_tools=ToolRegistry(),reaction_yield_predictor=Predictor())


@pytest.mark.parametrize('timeout',[0,True,float('inf'),3601])
def test_invalid_predictor_timeout_rejected_before_episode_creation(timeout):
    class Invalid(Predictor):
        timeout_seconds=timeout
    with pytest.raises(ValueError,match='timeout'):
        SynthesisRouteEnv(task(),reaction_yield_predictor=Invalid())


def test_api_episode_accepts_public_yield_action():
    from fastapi.testclient import TestClient
    from synthesis_route_gym.api import create_app
    client=TestClient(create_app({'test-key':'tenant'},reaction_yield_predictor=Predictor()))
    headers={'Authorization':'Bearer test-key'}
    response=client.post('/v1/episodes',headers=headers,json={'task':task().model_dump(mode='json')})
    assert response.status_code==201,response.text
    ident=response.json()['data']['episode_id']
    result=client.post(f'/v1/episodes/{ident}/actions',headers=headers,
        json={'action':'predict_reaction_yield','arguments':{'candidates':[candidate()]}})
    assert result.status_code==200,result.text
    assert result.json()['data']['result']['data']['predictions'][0]['predicted_yield_percent']==70
