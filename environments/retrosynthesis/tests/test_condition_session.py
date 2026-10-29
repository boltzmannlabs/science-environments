"""A condition session preserves the main-profile bridge and durable allowance."""
import json
from types import SimpleNamespace
import pytest
from synthesis_route_gym import condition_session as module


class Episode:
    binding_fingerprint='a'*64
    def __init__(self):
        self.submitted=False; self.queries=0; self.cancelled=False
    def public_view(self):
        return {'schema_version':'srg-condition-view-v1','study_id':'study',
                'substrate':'CCBr','target':'CCO','domain_status':'registered_measured_study',
                'measurement':{'name':'yield','unit':'percent','evidence_kind':'measured_dataset_replay'},
                'candidates':[{'candidate_id':'a','conditions':{'base':'O'}}],
                'observations':[], 'predictions':[],
                'resources':{'initial_observations':0,'new_observations_used':self.queries,
                             'remaining_observations':1-self.queries,'remaining_actions':20,
                             'remaining_seconds':100},
                'submission':{'status':'selected' if self.submitted else 'not_submitted',
                              'candidate_id':'a' if self.submitted else None}}
    def dispatch(self,action,args,action_id=None):
        if action=='submit':self.submitted=True
        if action=='observe_condition':self.queries+=1
        return {'status':'ok','result':self.public_view(),'terminated':self.submitted,'truncated':False}
    def export(self):return {**self.public_view(),'events':[],'stop_reason':None}
    def cancel(self,reason):self.cancelled=True


def args(tmp_path,method='main'):
    home=tmp_path/'profile';home.mkdir(exist_ok=True)
    (home/'config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n')
    return SimpleNamespace(method=method,model_calls=24,max_actions=80,wall_seconds=600,
                           max_tokens=350000,scientist_python='/trusted/python',
                           scientist_source='/trusted/scientist',profile_home=str(home))


def test_prompt_stable_after_observations_and_no_private_answers():
    env=Episode(); initial=module.condition_prompt(env);env.queries=1
    assert module.condition_prompt(env)==initial
    assert 'condition' in initial.lower() and 'observed' in initial.lower()
    assert 'optimum' not in json.dumps(module.condition_tool_schemas())
    assert {s['name']for s in module.condition_tool_schemas()}=={
        'inspect','observe_condition','predict_reaction_yield','submit'}


@pytest.mark.parametrize('method',['main','main_condition_scientist'])
def test_bridge_uses_main_profile_and_condition_tools(tmp_path,monkeypatch,method):
    env=Episode();options=args(tmp_path,method);seen=[]
    def bridge(prompt,executor,**kw):
        seen.append(kw)
        assert kw['mode']==method and kw['profile_home']==options.profile_home
        assert kw['budget'].max_model_calls==24 and kw['budget'].max_total_tokens==350000
        assert 'model' not in kw and 'provider' not in kw
        kw['checkpoint']({'fixture':'checkpoint'})
        executor('observe_condition',{'candidate_id':'a'})
        kw['action_executor']('submit',{'candidate_id':'a'},action_id='submission')
        return {'completed':True,'conversation_completed':True}
    monkeypatch.setattr(module,'run_agent_scientist_bridge',bridge)
    result=module.run_condition_agent(options,env,tmp_path/'runtime')
    assert len(seen)==1 and result['submission_status']=='selected'
    assert result['episode']['submission']['candidate_id']=='a'
    # A completed episode returns the saved result without another provider call.
    assert module.run_condition_agent(options,env,tmp_path/'runtime',resume=True)['agent']['completed']
    assert len(seen)==1


def test_resume_keeps_checkpoint_and_rejects_configuration_change(tmp_path,monkeypatch):
    env=Episode();options=args(tmp_path);seen=[]
    def bridge(prompt,executor,**kw):
        seen.append(kw['resume_state'])
        kw['checkpoint']({'fixture':'consumed'})
        return {'completed':False}
    monkeypatch.setattr(module,'run_agent_scientist_bridge',bridge)
    module.run_condition_agent(options,env,tmp_path/'runtime')
    module.run_condition_agent(options,env,tmp_path/'runtime',resume=True)
    assert seen==[None,{'fixture':'consumed'}]
    options.method='main_condition_scientist'
    with pytest.raises(ValueError,match='binding'):
        module.run_condition_agent(options,env,tmp_path/'runtime',resume=True)
    assert len(seen)==2


def test_bridge_failure_is_retained_without_error_details(tmp_path,monkeypatch):
    def bridge(*a,**kw):raise module.BridgeError('private diagnostic')
    monkeypatch.setattr(module,'run_agent_scientist_bridge',bridge)
    result=module.run_condition_agent(args(tmp_path),Episode(),tmp_path/'runtime')
    assert result['agent']['completed'] is False
    assert 'private diagnostic' not in json.dumps(result)
    assert result['submission_status']=='not_submitted'
    assert result['agent']['model']=='main-model'
    assert result['agent']['provider']=='main-provider'
    assert result['agent']['resource_accounting']=='unknown_after_bridge_interruption'
    assert 'ledger' not in result['agent']


def test_closed_episode_without_result_retains_profile_identity(tmp_path,monkeypatch):
    env=Episode();env.submitted=True
    def unexpected(*args,**kwargs):pytest.fail('closed episode must not call provider')
    monkeypatch.setattr(module,'run_agent_scientist_bridge',unexpected)
    result=module.run_condition_agent(args(tmp_path),env,tmp_path/'runtime')
    assert result['agent']['model']=='main-model'
    assert result['agent']['provider']=='main-provider'
    assert result['agent']['resource_accounting']=='no_new_provider_request'


def test_changed_main_profile_rejects_resume_even_before_provider_call(tmp_path,monkeypatch):
    options=args(tmp_path);env=Episode()
    monkeypatch.setattr(module,'run_agent_scientist_bridge',lambda *a,**kw:{'completed':False})
    module.run_condition_agent(options,env,tmp_path/'runtime')
    from pathlib import Path
    (Path(options.profile_home)/'config.yaml').write_text('model:\n  default: different\n  provider: main-provider\n')
    with pytest.raises(ValueError,match='binding'):
        module.run_condition_agent(options,env,tmp_path/'runtime',resume=True)
