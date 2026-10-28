"""Route Critic advice shares the main profile and cannot execute actions."""
import copy
import json
import pytest
from synthesis_route_gym.agent_runner import AgentBudget, RuntimeContractError, run_agent_scientist
from synthesis_route_gym import route_critic_runtime as module

SCHEMAS=[{'name':n,'parameters':{'type':'object','properties':{}}}for n in ('inspect','review_routes','validate','submit')]
REPORT={'schema_version':'srg-route-critic-report-v1','context_sha256':'context-one','findings':[],
        'recommended_recheck_id':None,'evidence_status':'agent_proposal'}
@pytest.fixture
def home(tmp_path):
    (tmp_path/'config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n');return tmp_path
@pytest.fixture
def policy(monkeypatch):
    monkeypatch.setattr(module,'build_context',lambda packet,resources:{'packet':packet,'resources':resources})
    monkeypatch.setattr(module,'context_fingerprint',lambda context:'context-one')
    def parse(text,context):
        value=json.loads(text)
        if value!=REPORT:raise ValueError('invalid report')
        return value
    monkeypatch.setattr(module,'parse_report',parse)
    monkeypatch.setattr(module,'hydrate_report',lambda report,context:{**report,'host_facts':['known']})
class Backend:
    def __init__(self,*,malformed=False,failure=False,mismatch=False,interrupt=False,actions=None):
        self.calls=[];self.observations=[]
        self.malformed,self.failure,self.mismatch,self.interrupt=malformed,failure,mismatch,interrupt
        self.actions=actions or ['inspect','review_routes','validate']
    def run(self,**kw):
        self.calls.append(kw);ledger=kw['ledger']
        request=ledger.claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if kw['role']=='route_critic':
            assert kw['tool_schemas']==[] and kw['model_call_limit']==1
            with pytest.raises(RuntimeContractError):kw['executor']('validate',{'route_id':'r1'})
            if self.interrupt:raise KeyboardInterrupt()
            if self.failure:raise OSError('private secret must not appear')
            text='not-json'if self.malformed else json.dumps(REPORT)
        else:
            for action in self.actions:self.observations.append(kw['executor'](action,{'route_ids':['r1']}))
            assert ledger._role=='main'
            kw['executor']('submit',{'route_ids':['r1']});text='submitted'
        ledger.settle_request(request,12)
        return {'completed':True,'final_response':text,'messages':[],
            'model':'wrong'if self.mismatch and kw['role']=='route_critic'else kw['profile'].model,
            'provider':kw['profile'].provider,'token_confirmations':{request:12},
            'usage':{'input_tokens':10,'output_tokens':2,'total_tokens':12,'estimated_cost_usd':0.0}}
def execute(name,args):
    return {'status':'ok','result':{'schema_version':'srg-route-review-v1','routes':[{'route_id':'r1'}]},
            'terminated':name=='submit','truncated':False}
def run(home,backend,**kwargs):
    return run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,profile_home=home,
                              mode='main_route_critic',backend=backend,**kwargs)
def test_single_review_consultation_shares_profile_and_ledger(home,policy):
    backend=Backend(actions=['inspect','review_routes','review_routes','validate']);result=run(home,backend)
    assert [r['role']for r in backend.calls]==['main','route_critic']
    assert len({id(r['profile'])for r in backend.calls})==len({id(r['ledger'])for r in backend.calls})==1
    assert result['completed'] and result['conversation_completed']
    assert len(result['route_critic_runs'])==len(result['runs'])==1
    advice=backend.observations[1]['route_critic_advice']
    assert advice['status']=='accepted' and advice['report']==REPORT
    assert advice['recommendation']['host_facts']==['known'] and advice['evidence_status']=='agent_proposal'
    assert all('route_critic_advice'not in v for i,v in enumerate(backend.observations)if i!=1)
    assert result['ledger']['model_calls']==2 and result['ledger']['tool_calls']==5
    assert result['ledger']['actual_tokens']==result['usage']['total_tokens']==24
    assert result['route_critic_runs'][0]['prompt_sha256'] and 'messages'not in result['route_critic_runs'][0]
@pytest.mark.parametrize('kind,status',[('malformed','rejected'),('failure','failed')])
def test_failed_report_consumed_without_stopping_main(home,policy,kind,status):
    backend=Backend(**{kind:True});result=run(home,backend)
    assert result['completed'] and len(result['route_critic_runs'])==1
    advice=backend.observations[1]['route_critic_advice']
    assert advice['status']==status and advice['report']is None
    assert 'private secret'not in json.dumps(result)
    if kind=='failure':assert result['ledger']['reserved_tokens']==40

def test_profile_mismatch_fails_closed(home,policy):
    backend=Backend(mismatch=True)
    with pytest.raises(RuntimeContractError):run(home,backend)
    assert backend.calls[0]['ledger']._role=='main'
@pytest.mark.parametrize('budget',[AgentBudget(max_model_calls=3),AgentBudget(max_tool_calls=4),AgentBudget(max_total_tokens=6000)])
def test_guard_preserves_main_action_and_finalization(home,policy,budget):
    backend=Backend();result=run(home,backend,budget=budget)
    assert [r['role']for r in backend.calls]==['main'] and result['completed']
    assert result['route_critic_state']['consultation']['status']=='skipped_budget'
def test_three_remaining_model_calls_admits_advice(home,policy):
    assert run(home,Backend(),budget=AgentBudget(max_model_calls=4))['route_critic_state']['consultation']['status']=='accepted'
def test_pending_consultation_consumed_across_resume(home,policy):
    checkpoints=[];backend=Backend(interrupt=True)
    with pytest.raises(KeyboardInterrupt):run(home,backend,checkpoint=lambda s:checkpoints.append(copy.deepcopy(s)))
    saved=checkpoints[-1]
    assert saved['schema_version']=='srg-agent-runtime-critic-v1'
    assert saved['route_critic']['consultation']['status']=='pending' and saved['ledger']['counts']['model_calls']==2
    resumed=Backend();result=run(home,resumed,resume_state=saved)
    assert [r['role']for r in resumed.calls]==['main'] and result['completed'] and result['ledger']['model_calls']==3
    assert resumed.observations[0]['route_critic_advice']['status']=='interrupted'
def test_completed_resume_never_repeats_calls(home,policy):
    checkpoints=[];first=run(home,Backend(),checkpoint=lambda s:checkpoints.append(copy.deepcopy(s)))
    backend=Backend();again=run(home,backend,resume_state=checkpoints[-1])
    assert not backend.calls and again['usage']==first['usage']
def test_main_prompt_and_tools_identical(home,policy):
    assisted=Backend();run(home,assisted)
    direct=Backend();run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,profile_home=home,backend=direct)
    assert assisted.calls[0]['prompt']==direct.calls[0]['prompt'] and assisted.calls[0]['tool_schemas']==direct.calls[0]['tool_schemas']
def test_only_review_routes_triggers(home,policy):
    backend=Backend(actions=['inspect','validate']);result=run(home,backend)
    assert len(backend.calls)==1 and not result['route_critic_runs']
@pytest.mark.parametrize('change',[{'status':'error'},{'terminated':True},{'truncated':True}])
def test_failed_or_closed_response_does_not_trigger(home,policy,change):
    backend=Backend()
    def executor(action,args):return {**execute(action,args),**change}if action=='review_routes'else execute(action,args)
    result=run_agent_scientist('same main prompt',executor,tool_schemas=SCHEMAS,profile_home=home,mode='main_route_critic',backend=backend)
    assert len(backend.calls)==1 and not result['route_critic_runs']
def test_context_error_disables_without_provider_call(home,policy,monkeypatch):
    def bad(*_):raise ValueError('private host detail')
    monkeypatch.setattr(module,'build_context',bad);backend=Backend();result=run(home,backend)
    assert result['route_critic_state']['consultation']['status']=='disabled_observation'
    assert len(backend.calls)==1 and 'private host detail'not in json.dumps(result)
def test_checkpoint_failure_before_admission_prevents_child_request(home,policy):
    from synthesis_route_gym.agent_accounting import CheckpointError
    backend=Backend()
    def save(state):
        if state['route_critic']['consultation']is not None:raise OSError('storage failure')
    with pytest.raises(CheckpointError):run(home,backend,checkpoint=save)
    assert [r['role']for r in backend.calls]==['main']
@pytest.mark.parametrize('change',[{}, {'schema_version':'wrong'}, {'delivery_pending':'yes'}, {'runs':[{}]}])
def test_restore_rejects_invalid_state(change):
    state=module.initial_state()if change else {}
    with pytest.raises(ValueError):module.restore_state({**state,**change})
@pytest.mark.parametrize('field',['report','recommendation','context_sha256'])
def test_restore_rejects_changed_accepted_payload(home,policy,field):
    state=copy.deepcopy(run(home,Backend())['route_critic_state']);state['consultation'][field]={'forged':True}
    with pytest.raises(ValueError):module.restore_state(state)
def test_accepted_resume_delivers_once_without_retry(home,policy):
    state=module.restore_state(run(home,Backend())['route_critic_state']);updates=[];backend=Backend()
    response=module.after_tool('inspect',{},execute('inspect',{}),state=state,update=updates.append,runtime=backend,profile=object(),ledger=object())
    assert response['route_critic_advice']['status']=='accepted' and not backend.calls and updates[-1]['delivery_pending']is False
@pytest.mark.parametrize('seconds,finalization',[(0,False),(500,True)])
def test_time_and_finalization_guards(seconds,finalization):
    from synthesis_route_gym.agent_runner import SharedLedger
    ledger=SharedLedger(AgentBudget());ledger.finalization_only=finalization
    resources={'remaining_model_calls':4,'remaining_tool_calls':5,'remaining_tokens':100000,'remaining_seconds':seconds}
    assert not module._admissible(ledger,resources,'bounded prompt')
def test_failed_restore_inconsistent_report_rejected():
    state={**module.initial_state(),'consultation':{'status':'failed','report':{},'evidence_status':'agent_proposal'},'runs':[{'role':'route_critic'}]}
    with pytest.raises(ValueError):module.restore_state(state)

def test_advice_payload_is_detached_from_checkpoint(home,policy):
    backend=Backend();result=run(home,backend)
    backend.observations[1]['route_critic_advice']['recommendation']['host_facts'].append('forged')
    assert result['route_critic_state']['consultation']['recommendation']['host_facts']==['known']

def test_canonical_report_survives_padded_response_and_resume(home,policy):
    class PaddedBackend(Backend):
        def run(self,**kw):
            result=super().run(**kw)
            return {**result,'final_response':' '*17000+result['final_response']}if kw['role']=='route_critic'else result
    checkpoints=[];result=run(home,PaddedBackend(),checkpoint=lambda s:checkpoints.append(copy.deepcopy(s)))
    stored=result['route_critic_runs'][0]
    assert json.loads(stored['final_response'])==REPORT and len(stored['final_response'])<16000
    assert stored['raw_response_chars']>17000 and stored['response_truncated']is False
    backend=Backend();again=run(home,backend,resume_state=checkpoints[-1])
    assert again['completed'] and not backend.calls

@pytest.mark.parametrize('remaining,reserve,expected',[(2,1,False),(3,1,True),(3,2,False),(4,2,True)])
def test_reserves_include_main_action_round(remaining,reserve,expected):
    from synthesis_route_gym.agent_runner import SharedLedger
    ledger=SharedLedger(AgentBudget(max_model_calls=10,wall_seconds=200,finalization_model_calls=reserve))
    resources={'remaining_model_calls':remaining,'remaining_tool_calls':20,'remaining_tokens':100000,'remaining_seconds':100}
    assert module._admissible(ledger,resources,'bounded context')is expected

def test_checkpoint_cannot_resume_in_another_mode(home,policy):
    saved=[];run(home,Backend(),checkpoint=lambda s:saved.append(copy.deepcopy(s)))
    for mode in ['main','main_strategist','main_condition_scientist']:
        with pytest.raises(ValueError,match='binding'):
            run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,profile_home=home,
                               mode=mode,backend=Backend(),resume_state=saved[-1])

@pytest.mark.parametrize('state',[
    {'consultation':None,'runs':[],'delivery_pending':True},
    {'consultation':{'status':'trusted','evidence_status':'experimental'},'runs':[],'delivery_pending':False},
])
def test_restore_rejects_delivery_without_advice_and_invalid_authority(state):
    with pytest.raises(ValueError):module.restore_state({**module.initial_state(),**state})

def test_child_checkpoint_failure_propagates_and_restores_main_role(home,policy):
    from synthesis_route_gym.agent_accounting import CheckpointError
    class FailingBackend(Backend):
        def run(self,**kw):
            if kw['role']=='route_critic':raise CheckpointError('durable accounting unavailable')
            return super().run(**kw)
    backend=FailingBackend()
    with pytest.raises(CheckpointError):run(home,backend)
    assert backend.calls[0]['ledger']._role=='main'

def test_native_backend_route_critic_has_no_registered_tools(home,monkeypatch):
    from types import SimpleNamespace
    import sys
    from synthesis_route_gym.agent_runner import NativeAgentBackend,SharedLedger,resolve_main_profile
    seen={}
    class Registry:
        def register(self,**kw):raise AssertionError('tool-free critic must not register tools')
    class Agent:
        def __init__(self,**kw):
            seen['init']=kw;self.model=kw['model'];self.provider=kw['provider']
            self.valid_tool_names={'tool_search','tool_describe','tool_call'}
            self.session_input_tokens=0;self.session_output_tokens=0
            self.session_total_tokens=0;self.session_estimated_cost_usd=0
        def run_conversation(self,prompt,task_id):
            assert self.tools==[] and self.valid_tool_names==set()
            return {'completed':True,'final_response':'{}'}
        def close(self):seen['closed']=True
    monkeypatch.setitem(sys.modules,'tools.registry',SimpleNamespace(registry=Registry()))
    monkeypatch.setitem(sys.modules,'sci_constants',SimpleNamespace(sci_home_key=lambda:'main'))
    result=NativeAgentBackend()._execute(Agent,{},resolve_main_profile(home),'advice',[],lambda *_:None,
                                       SharedLedger(AgentBudget()),'route_critic',1)
    assert result['completed'] and seen['closed']
    assert len(seen['init']['enabled_toolsets'])==1 and seen['init']['fallback_model']==[]
    assert seen['init']['skip_memory'] and seen['init']['skip_context_files']

def test_real_contract_host_packet_and_shared_runtime(home):
    from synthesis_route_gym.route_review import build_route_review
    from synthesis_route_gym.route_critic import context_fingerprint
    from synthesis_route_gym.schemas import Task,RouteCandidate
    from synthesis_route_gym.validation import assess_route
    task=Task.model_validate({'task_id':'synthetic-runtime','target':'CC=O','inventory':[{'smiles':'CCO'}]})
    route=RouteCandidate.model_validate({'route_id':'r1','target':'CC=O','steps':[{'step_id':'s1','product':'CC=O',
        'reactants':[{'smiles':'CCO'}],'reagents':[{'smiles':'O'}],'source_tool':'synthetic','source_version':'v1'}]})
    packet=build_route_review(task,[route],[assess_route(task,route)])
    checkpoints=[]
    def executor(action,args):
        return {'status':'ok','result':packet if action=='review_routes'else{},'terminated':action=='submit','truncated':False}
    class RealBackend:
        def run(self,**kw):
            request=kw['ledger'].claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
            if kw['role']=='route_critic':
                context=json.loads(kw['prompt'].split('\nHost context: ',1)[1]);fact=next(f for f in context['packet']['facts']if f['severity']=='error')
                report={'schema_version':'srg-route-critic-report-v1','context_sha256':context_fingerprint(context),
                    'findings':[{'route_id':fact['route_id'],'step_id':fact['step_id'],'category':fact['category'],
                    'severity':'error','supporting_fact_ids':[fact['fact_id']],'source_record_ids':[],
                    'requested_revision':'revise_route','rationale':'Resolve the explicit unavailable material.'}],
                    'recommended_recheck_id':context['packet']['recheck_menu'][0]['recheck_id'],'evidence_status':'agent_proposal'}
                text=json.dumps(report)
            else:
                response=kw['executor']('review_routes',{'route_ids':['r1']})
                advice=response['route_critic_advice'];assert advice['status']=='accepted'
                assert advice['recommendation']['findings'][0]['supporting_facts']
                kw['executor']('submit',{'route_ids':[]});text='Submitted empty shortlist.'
            kw['ledger'].settle_request(request,20)
            return {'completed':True,'final_response':text,'model':kw['profile'].model,'provider':kw['profile'].provider,
                    'token_confirmations':{request:20},'usage':{'input_tokens':15,'output_tokens':5,'total_tokens':20,'estimated_cost_usd':0}}
    result=run_agent_scientist('Synthetic route check',executor,tool_schemas=SCHEMAS,profile_home=home,
        mode='main_route_critic',backend=RealBackend(),checkpoint=lambda s:checkpoints.append(copy.deepcopy(s)))
    assert result['completed'] and result['ledger']['model_calls']==2 and result['ledger']['actual_tokens']==40
    assert module.restore_state(result['route_critic_state'])['consultation']['status']=='accepted'

def test_exhausted_context_is_budget_skip_not_invalid_packet(home,policy,monkeypatch):
    monkeypatch.setattr(module,'build_context',lambda *_:None)
    backend=Backend();result=run(home,backend)
    assert len(backend.calls)==1 and result['completed']
    assert result['route_critic_state']['consultation']['status']=='skipped_budget'
    assert backend.observations[1]['route_critic_advice']['report']is None
