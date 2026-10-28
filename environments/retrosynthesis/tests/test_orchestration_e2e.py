"""Injected main and condition advisor complete a real local route episode."""
import json
import pytest
from synthesis_route_gym.agent_runner import run_agent_scientist, RuntimeContractError
from synthesis_route_gym.planning import environment_tool_schemas
from test_route_condition_environment import environment
from test_route_condition_advice import plan


class Backend:
    def __init__(self,expect_advice):
        self.expect_advice=expect_advice;self.calls=[];self.advice=None

    def run(self,**kw):
        self.calls.append(kw)
        request=kw['ledger'].claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if kw['role']=='main':
            args={'route_id':'r1','step_id':'s1'}
            assert kw['executor']('condition_options',args)['status']=='ok'
            for candidate in ('a','b'):
                result=kw['executor']('observe_route_condition',{**args,'candidate_id':candidate})
                assert result['status']=='ok'
            self.advice=result.get('route_condition_advice')
            if self.expect_advice:
                assert self.advice['status']=='accepted'
                next_action=self.advice['recommendation']['next_action']
                assert next_action['arguments']=={**args,'candidate_id':'c'}
                assert kw['executor'](next_action['action'],next_action['arguments'])['status']=='ok'
            else:
                assert self.advice is None
            report=kw['executor']('application_report',{'application':'condition_optimization',
                'route_ids':['r1'],'step_id':'s1','candidate_id':'a'})
            assert report['status']=='ok'
            assert report['result']['result']['route_step_yield_percent']is None
            assert kw['executor']('submit',{'route_ids':['r1']})['status']=='ok'
            output='Submitted the stored route; alternative measurements remain separate.'
        else:
            assert kw['role']=='condition_optimisation_scientist'
            assert kw['tool_schemas']==[] and kw['model_call_limit']==1
            with pytest.raises(RuntimeContractError):kw['executor']('observe_route_condition',{})
            context=json.loads(kw['prompt'].split('\nHost context: ',1)[1])
            assert context['catalog']['observation_count']==2
            assert context['catalog']['observation_resources']['calls_used']==2
            assert '88.456'not in json.dumps(context) and '99.567'not in json.dumps(context)
            output=json.dumps(plan(context))
        kw['ledger'].settle_request(request,12)
        return {'completed':True,'final_response':output,'messages':[],
            'model':kw['profile'].model,'provider':kw['profile'].provider,
            'usage':{'total_tokens':12},'token_confirmations':{request:12}}


def run(tmp_path,mode):
    env,_,_,_=environment(tmp_path);before=env.export()['routes']
    home=tmp_path/'profile';home.mkdir()
    (home/'config.yaml').write_text('model:\n  default: configured-main\n  provider: configured-provider\n')
    backend=Backend(mode=='main_all_advisors')
    result=run_agent_scientist('Use the registered condition study and submit the route.',env.dispatch,
        tool_schemas=environment_tool_schemas(),profile_home=home,backend=backend,mode=mode)
    assert result['completed'] and result['submission_status']=='submitted'
    assert env.export()['submitted_route_ids']==['r1']and env.export()['routes']==before
    assert len({id(call['profile'])for call in backend.calls})==1
    assert len({id(call['ledger'])for call in backend.calls})==1
    assert all(call['profile'].model=='configured-main'and call['profile'].provider=='configured-provider'for call in backend.calls)
    return env,backend,result


def test_real_condition_advisor_is_eligible_once_and_main_executes(tmp_path):
    env,backend,result=run(tmp_path,'main_all_advisors')
    assert [call['role']for call in backend.calls]==['main','condition_optimisation_scientist']
    assert result['ledger']['model_calls']==2 and result['ledger']['actual_tokens']==24
    assert result['ledger']['reserved_tokens']==0
    assert env.export()['scientific_usage']['observe_condition']==3
    assert result['orchestration']['consultations_used']==1
    assert result['orchestration']['advisor_status']=={'strategist':'not_invoked','condition_scientist':'accepted','route_critic':'not_invoked'}


def test_default_adaptive_does_not_promote_an_eligible_specialist(tmp_path):
    env,backend,result=run(tmp_path,'main_adaptive')
    assert [call['role']for call in backend.calls]==['main']
    assert result['ledger']['model_calls']==1 and result['ledger']['actual_tokens']==12
    assert result['ledger']['reserved_tokens']==0
    assert env.export()['scientific_usage']['observe_condition']==2
    assert result['orchestration']['consultations_used']==0
    assert result['orchestration_runs']==[]
