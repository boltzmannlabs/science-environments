"""Scientific action contracts inside durable public episodes."""
import json
import pytest
from test_core import make_task
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.tool_registry import ToolRegistry, ToolBinding


def registry(callback=None, version='fixture-v1', name='forward_check', **kw):
    return ToolRegistry({name: ToolBinding(callback=callback or (lambda args: {'predictions': []}), version=version, **kw)})


def test_capability_discovery_and_unavailable_are_explicit():
    env = SynthesisRouteEnv(make_task())
    result = env.dispatch('capabilities', {})
    assert result['status'] == 'ok'
    assert any(x['name'] == 'forward_check' for x in result['result']['capabilities'])
    result = env.dispatch('forward_check', {'reactants':['CCO'], 'product':'CC=O'})
    assert result['status'] == 'unavailable'
    assert result['result']['data'] is None
    assert result['result']['evidence_kind'] != 'measured'


def test_predicted_fields_are_projected_and_per_action_usage_persists(tmp_path):
    backend = lambda args: {'predictions':[{'product':'CC=O','score':.8}], 'private_rows':'SECRET'}
    tools = registry(backend)
    env = SynthesisRouteEnv(make_task(), scientific_tools=tools, store=tmp_path/'ep')
    result = env.dispatch('forward_check', {'reactants':['CCO'], 'product':'CC=O'}, action_id='check')
    assert result['status'] == 'ok'
    assert 'SECRET' not in json.dumps(result)
    assert env.export()['scientific_usage']['forward_check'] == 1
    resumed = SynthesisRouteEnv.resume(tmp_path/'ep', scientific_tools=tools)
    assert resumed.dispatch('forward_check', {'reactants':['CCO'], 'product':'CC=O'}, action_id='check') == result
    assert resumed.export()['scientific_usage']['forward_check'] == 1
    with pytest.raises(ValueError, match='scientific'):
        SynthesisRouteEnv.resume(tmp_path/'ep', scientific_tools=registry(backend,version='changed'))


def test_invalid_and_unavailable_attempts_are_charged():
    env = SynthesisRouteEnv(make_task())
    result = env.dispatch('forward_check', {'reactants':['not smiles'], 'product':'CCO'})
    assert result['status'] == 'error'
    assert env.export()['scientific_usage']['forward_check'] == 1
    assert result['result']['error']['code']


def test_existing_expansion_contract_keeps_legacy_shape_and_adds_envelope():
    def expand(smiles, k):
        return {'status':'ok', 'predictions':[{'product':smiles,'reactants':['CCO','CC(=O)O'], 'score':.5}],
                'private_rows':[{'answer':'NEVER-EXPOSE'}]}
    env = SynthesisRouteEnv(make_task(), expand=expand)
    result = env.dispatch('expand', {'smiles':'CCOC(C)=O'})
    assert result['status'] == 'ok'
    assert result['result']['predictions'][0]['evidence_status'] == 'predicted'
    assert result['result']['tool_result']['status'] == 'ok'
    assert 'NEVER-EXPOSE' not in json.dumps(result)


def test_tool_timeout_is_bounded_and_late_output_is_discarded():
    import threading,time
    release = threading.Event()
    def slow(args):
        release.wait(2)
        return {'predictions':[]}
    tools = registry(slow, timeout_seconds=.03)
    env = SynthesisRouteEnv(make_task(), scientific_tools=tools)
    before = time.monotonic()
    try:
        result = env.dispatch('forward_check', {'reactants':['CCO'], 'product':'CC=O'})
        assert time.monotonic()-before < .5
        assert result['status'] == 'error'
        assert result['result']['error']['code'] == 'tool_timeout'
        assert env.export()['scientific_usage']['forward_check'] == 1
    finally:
        release.set()


def test_native_tool_schemas_and_actions_include_canonical_scientific_operations():
    from synthesis_route_gym.agent_runner import ACTIONS
    from synthesis_route_gym.planning import environment_tool_schemas
    from synthesis_route_gym.scientific_execution import SCIENTIFIC_ACTIONS
    names = {s['name'] for s in environment_tool_schemas()}
    assert {'capabilities', *SCIENTIFIC_ACTIONS} <= names <= ACTIONS
    assert 'verify_source' not in names


def test_alias_has_same_budget_counter_and_rejects_paths():
    tools = registry()
    env = SynthesisRouteEnv(make_task(), scientific_tools=tools)
    result = env.dispatch('forward_consistency', {'reactants':['CCO'], 'product':'CC=O'})
    assert result['status'] == 'ok'
    assert env.export()['scientific_usage'] == {'forward_check':1}
    result = env.dispatch('retrieve_sources', {'records_path':'/private/evaluator.json'})
    assert result['status'] == 'error'
    assert '/private/' not in json.dumps(result)


def test_local_api_exposes_bounded_capabilities_without_configuration_setters():
    from fastapi.testclient import TestClient
    from synthesis_route_gym.api import create_app
    client = TestClient(create_app({'test-key':'owner'}))
    headers={'Authorization':'Bearer test-key'}
    created=client.post('/v1/episodes',headers=headers,json={'task':make_task().model_dump(mode='json')})
    ident=created.json()['data']['episode_id']
    result=client.post(f'/v1/episodes/{ident}/actions',headers=headers,json={'action':'capabilities','arguments':{}})
    assert result.status_code == 200
    assert result.json()['data']['result']['capabilities']
    bad=client.post(f'/v1/episodes/{ident}/actions',headers=headers,json={'action':'retrieve_sources','arguments':{'records_path':'/hidden'}})
    assert bad.status_code == 400
    assert '/hidden' not in bad.text


def test_retrieval_is_budgeted_and_only_claims_enter_observations(tmp_path):
    from test_evidence_contracts import record, NOW, attestation
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    source = record()
    corpus = FrozenEvidenceCorpus([source],mode='evidence_retrieval',attestations=[attestation(source)],now=NOW)
    limits = {'retrieval_calls':1}
    env = SynthesisRouteEnv(make_task(),evidence_corpus=corpus,scientific_limits=limits,store=tmp_path/'ep')
    result = env.dispatch('retrieve_sources',{'product':'CC=O'},action_id='source-query')
    assert result['status']=='ok'
    row=result['result']['data']['records'][0]
    assert row['evidence_status']=='source_claim' and row['verification_status']=='not_attested'
    restored=SynthesisRouteEnv.resume(tmp_path/'ep',evidence_corpus=corpus,scientific_limits=limits)
    assert restored.dispatch('retrieve_sources',{'product':'CC=O'},action_id='source-query')==result
    refused=restored.dispatch('source_retrieval',{'product':'CC=O'})
    assert refused['result']['error']['code']=='access_budget_exhausted'
    assert restored.export()['scientific_usage']['retrieve_sources']==2
    closed=FrozenEvidenceCorpus([source],now=NOW)
    result=SynthesisRouteEnv(make_task(),evidence_corpus=closed,scientific_limits=limits).dispatch('retrieve_sources',{})
    assert result['status']=='unavailable'


def test_condition_observation_budget_survives_resume_and_hides_other_yields(tmp_path):
    from synthesis_route_gym.portfolio_conditions import ConditionRecord,FiniteConditionStudy
    study=FiniteConditionStudy((ConditionRecord('one',(('ligand','P'),),10),ConditionRecord('two',(('ligand','N'),),99)),(),1,
                              'https://example.org/data','row table','a'*64,'CCO')
    limits={'observation_calls':1}
    env=SynthesisRouteEnv(make_task(),condition_study=study,scientific_limits=limits,store=tmp_path/'ep')
    result=env.dispatch('observe_condition',{'candidate_id':'one'},action_id='one')
    assert result['status']=='ok'
    assert result['result']['data']['yield_percent']==10
    assert '99' not in json.dumps(result['result']['data'])
    assert 'optimum' not in json.dumps(result)
    restored=SynthesisRouteEnv.resume(tmp_path/'ep',condition_study=study,scientific_limits=limits)
    refused=restored.dispatch('condition_observation',{'candidate_id':'two'})
    assert refused['result']['error']['code']=='access_budget_exhausted'
    assert '99' not in json.dumps(refused['result'].get('data'))


def test_host_replay_allowance_cannot_exceed_original_study_budget():
    from synthesis_route_gym.portfolio_conditions import ConditionRecord,FiniteConditionStudy
    study=FiniteConditionStudy((ConditionRecord('one',(('ligand','P'),),10),ConditionRecord('two',(('ligand','N'),),99)),(),1,
                              'https://example.org/data','row table','a'*64,'CCO')
    with pytest.raises(ValueError,match='study budget'):
        SynthesisRouteEnv(make_task(),condition_study=study,scientific_limits={'observation_calls':2})
    used=study.observe('one')
    with pytest.raises(ValueError,match='study budget'):
        SynthesisRouteEnv(make_task(),condition_study=used,scientific_limits={'observation_calls':1})


def test_route_ranking_uses_one_metered_validated_prediction_batch():
    from test_ranking import coupling_step
    from synthesis_route_gym.schemas import Task,RouteCandidate
    step={**coupling_step(),'step_id':'s','source_tool':'fixture','source_version':'1'}
    task=Task(task_id='ranking',target=step['product'],inventory=[])
    route=RouteCandidate(route_id='r1',target=step['product'],steps=[step])
    class Model:
        metadata={'model_version':'test'}
        def predict(self,rows):
            return [{'predicted_yield_percent':42,'private':'HIDDEN'} for _ in rows]
    env=SynthesisRouteEnv(task,condition_ranker=Model())
    env.dispatch('propose_route',{'route':route.model_dump(mode='json')})
    result=env.dispatch('rank_routes',{'route_ids':['r1']})
    assert result['status']=='ok'
    assert env.export()['scientific_usage']['predict_conditions']==1
    assert result['result']['ranking'][0]['bottleneck_predicted_yield']==.42
    assert result['result']['scientific_calls'][0]['capability']=='predict_conditions'
    assert 'HIDDEN' not in json.dumps(result)


def test_condition_candidate_discovery_never_exposes_unqueried_yields():
    from synthesis_route_gym.portfolio_conditions import ConditionRecord,FiniteConditionStudy
    study=FiniteConditionStudy((ConditionRecord('one',(('ligand','P'),),10),ConditionRecord('two',(('ligand','N'),),99)),(),1,
                              'https://example.org/data','row table','a'*64,'CCO')
    env=SynthesisRouteEnv(make_task(),condition_study=study,scientific_limits={'observation_calls':1})
    result=env.dispatch('inspect',{'condition_offset':0,'condition_limit':1})
    assert result['status']=='ok'
    page=result['result']['condition_candidates']
    assert page==[{'candidate_id':'one','conditions':{'ligand':'P'}}]
    assert result['result']['next_condition_offset']==1
    assert 'yield' not in json.dumps(page)
    assert result['result']['condition_candidate_count']==2


def test_resume_rejects_usage_and_retrieval_identity_rollback(tmp_path):
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    from synthesis_route_gym.episode_store import EpisodeStore
    corpus=FrozenEvidenceCorpus([record()],mode='evidence_retrieval',now=NOW)
    limits={'retrieval_calls':1}
    store=EpisodeStore(tmp_path/'ep')
    env=SynthesisRouteEnv(make_task(),evidence_corpus=corpus,scientific_limits=limits,store=store)
    env.dispatch('retrieve_sources',{})
    state,rev=store.load()
    store.commit({**state,'scientific_usage':{}},expected_revision=rev)
    with pytest.raises(ValueError,match='scientific'):
        SynthesisRouteEnv.resume(store,evidence_corpus=corpus,scientific_limits=limits)


def test_standalone_condition_api_projects_untrusted_predictor_fields():
    from fastapi.testclient import TestClient
    from synthesis_route_gym.api import create_app
    class Model:
        metadata={'model_version':'fixture'}
        def predict(self,rows):
            return [{'predicted_yield_percent':30,'private_training_rows':'HIDDEN',
                     'evidence_status':'measured'} for _ in rows]
    client=TestClient(create_app({'test':'owner'},condition_ranker=Model()))
    result=client.post('/v1/conditions/rank',headers={'Authorization':'Bearer test'},json={'candidates':[
        {'candidate_id':'one','aryl halide':'Clc1ccccc1','ligand':'P','additive':'O','base':'N'}]})
    assert result.status_code==200
    assert 'HIDDEN' not in result.text
    assert result.json()['data']['ranked_candidates'][0]['evidence_status']=='predicted'
    assert result.json()['data']['tool_result']['capability']=='predict_conditions'


def test_closed_policy_fences_even_custom_source_callbacks():
    called=[]
    tools=registry(lambda args: called.append(args),name='retrieve_sources',authority='source_retrieval')
    env=SynthesisRouteEnv(make_task(),scientific_tools=tools,scientific_limits={'retrieval_calls':10})
    result=env.dispatch('retrieve_sources',{})
    assert result['status']=='unavailable'
    assert result['result']['error']['code']=='closed_information'
    assert called==[]
    assert env.export()['source_access_mode']=='closed_information'


def test_late_source_result_rolls_back_discovered_ids_and_remains_resumable(tmp_path):
    from test_evidence_contracts import record,NOW
    from synthesis_route_gym.evidence_corpus import FrozenEvidenceCorpus
    from synthesis_route_gym.episode_store import EpisodeStore
    from synthesis_route_gym.schemas import Budget
    corpus=FrozenEvidenceCorpus([record()],mode='evidence_retrieval',now=NOW)
    limits={'retrieval_calls':1};now=[0.0]
    store=EpisodeStore(tmp_path/'ep')
    task=make_task(budget=Budget(max_wall_seconds=10))
    env=SynthesisRouteEnv(task,evidence_corpus=corpus,scientific_limits=limits,store=store,clock=lambda:now[0])
    original=env._call_bounded
    def late(*args,**kwargs):
        result=original(*args,**kwargs)
        now[0]=11.0
        return result
    env._call_bounded=late
    result=env.dispatch('retrieve_sources',{})
    assert result['status']=='budget_exhausted'
    state,_=store.load()
    assert state['retrieved_source_ids']==[]
    restored=SynthesisRouteEnv.resume(store,evidence_corpus=corpus,scientific_limits=limits)
    assert restored.inspect()['truncated']
    assert restored.export()['scientific_usage']['retrieve_sources']==1
