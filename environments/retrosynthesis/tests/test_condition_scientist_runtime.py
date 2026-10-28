"""Nested advice shares the main ledger and cannot execute chemistry actions."""
import copy
import json
import pytest
from synthesis_route_gym.agent_runner import AgentBudget, RuntimeContractError, run_agent_scientist
from synthesis_route_gym import condition_scientist_runtime
SCHEMAS = [{'name': name, 'parameters': {'type': 'object', 'properties': {'candidate_id': {'type': ['string', 'null']}} if name == 'submit' else {}}} for name in ('inspect', 'observe_condition', 'submit')]
@pytest.fixture
def home(tmp_path):
    (tmp_path/'config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n')
    return tmp_path
@pytest.fixture
def policy(monkeypatch):
    monkeypatch.setattr(condition_scientist_runtime, 'observer_state', lambda: {'count': 0})
    monkeypatch.setattr(condition_scientist_runtime, 'observe', lambda state, action, args, response: {'count':state['count']+1})
    monkeypatch.setattr(condition_scientist_runtime, 'build_context', lambda state, resources: {'candidate_ids':['c3'],'resources':resources} if state['count']>=2 else None)
    monkeypatch.setattr(condition_scientist_runtime, 'context_fingerprint', lambda context: 'context-one')
    def parse(text, context):
        value=json.loads(text)
        if value != {'decision':'observe','next_candidate_id':'c3'}:raise ValueError('invalid plan')
        return value
    monkeypatch.setattr(condition_scientist_runtime, 'parse_plan', parse)
    monkeypatch.setattr(condition_scientist_runtime, 'hydrate_plan', lambda plan, context: {**plan, 'selected_conditions': {'ligand': 'known'}})
class Backend:
    def __init__(self, *, malformed=False, failure=False, mismatch=False, interrupt=False):
        self.calls=[];self.observations=[]
        self.malformed,self.failure,self.mismatch,self.interrupt=malformed,failure,mismatch,interrupt
    def run(self, **kw):
        self.calls.append(kw)
        ledger=kw['ledger']
        request=ledger.claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if kw['role']=='condition_optimisation_scientist':
            assert kw['tool_schemas']==[] and kw['model_call_limit']==1
            with pytest.raises(RuntimeContractError):kw['executor']('observe_condition',{'candidate_id':'c3'})
            if self.interrupt:raise KeyboardInterrupt()
            if self.failure:raise OSError('private provider secret must not appear')
            text='not-json' if self.malformed else '{"decision":"observe","next_candidate_id":"c3"}'
        else:
            for action in ['inspect','observe_condition','observe_condition']:
                self.observations.append(kw['executor'](action,{}))
            assert ledger._role=='main'
            kw['executor']('submit',{'candidate_id':None})
            text='submitted'
        ledger.settle_request(request,12)
        return {'completed':True,'final_response':text,'messages':[],
                'model':'different' if self.mismatch and kw['role']!='main' else kw['profile'].model,
                'provider':kw['profile'].provider,'token_confirmations':{request:12},
                'usage':{'input_tokens':10,'output_tokens':2,'total_tokens':12,'estimated_cost_usd':0.0}}

def execute(name,args):return {'status':'ok','result':{'action':name}}
def run(home,backend,**kwargs):
    return run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,
        profile_home=home,mode='main_condition_scientist',backend=backend,**kwargs)
def test_nested_advice_shares_profile_and_accounts_once(home,policy):
    backend=Backend();result=run(home,backend)
    assert [r['role']for r in backend.calls]==['main','condition_optimisation_scientist']
    assert len({id(r['profile'])for r in backend.calls})==1
    assert len({id(r['ledger'])for r in backend.calls})==1
    assert result['completed']
    assert len(result['runs'])==1 and len(result['condition_scientist_runs'])==1
    assert result['condition_scientist_runs'][0]['context']['candidate_ids']==['c3']
    assert result['condition_scientist_runs'][0]['prompt_sha256']
    assert 'messages'not in result['condition_scientist_runs'][0]
    assert result['usage']['total_tokens']==24
    assert result['ledger']['actual_tokens']==24
    assert result['ledger']['model_calls']==2
    assert result['ledger']['tool_calls']==4
    assert backend.observations[1]['condition_scientist_advice']['status']=='accepted'
    assert backend.observations[1]['condition_scientist_advice']['evidence_status']=='agent_proposal'
    assert 'condition_scientist_advice'not in backend.observations[2]
@pytest.mark.parametrize('kind',['malformed','failure'])
def test_failed_advice_never_stops_main_or_claims_success(home,policy,kind):
    backend=Backend(**{kind:True});result=run(home,backend)
    assert result['completed'] and len(result['condition_scientist_runs'])==1
    advice=backend.observations[1]['condition_scientist_advice']
    assert advice['status'] in {'rejected','failed'} and advice.get('plan')is None
    assert 'private provider secret'not in json.dumps(result)
    assert result['ledger']['model_calls']==2
    if kind=='failure':assert result['ledger']['reserved_tokens']==40

def test_profile_mismatch_fails_closed_and_restores_main_stage(home,policy):
    backend=Backend(mismatch=True)
    with pytest.raises(RuntimeContractError):run(home,backend)
    assert backend.calls[0]['ledger']._role=='main'

def test_guard_protects_main_finalization(home,policy):
    backend=Backend();result=run(home,backend,budget=AgentBudget(max_model_calls=2))
    assert [r['role']for r in backend.calls]==['main']
    assert result['condition_scientist_runs']==[]
    assert result['completed']

def test_pending_advice_consumed_across_resume(home,policy):
    checkpoints=[];backend=Backend(interrupt=True)
    with pytest.raises(KeyboardInterrupt):
        run(home,backend,checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    saved=checkpoints[-1]
    assert saved['condition_scientist']['consultation']['status']=='pending'
    assert saved['ledger']['counts']['model_calls']==2
    resumed=Backend();result=run(home,resumed,resume_state=saved)
    assert [r['role']for r in resumed.calls]==['main']
    assert result['completed'] and result['ledger']['model_calls']==3
    assert resumed.observations[0]['condition_scientist_advice']['status']=='interrupted'

def test_completed_resume_does_not_repeat_parent_or_advisor(home,policy):
    checkpoints=[];backend=Backend()
    first=run(home,backend,checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    resumed=Backend();again=run(home,resumed,resume_state=checkpoints[-1])
    assert not resumed.calls
    assert again['usage']==first['usage']
    assert again['ledger']['model_calls']==2

def test_main_mode_prompt_and_schema_unchanged(home,policy):
    assisted=Backend();run(home,assisted)
    direct=Backend();run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,profile_home=home,backend=direct)
    assert assisted.calls[0]['prompt']==direct.calls[0]['prompt']
    assert assisted.calls[0]['tool_schemas']==direct.calls[0]['tool_schemas']

@pytest.mark.parametrize('budget',[
    AgentBudget(max_tool_calls=4),
    AgentBudget(max_total_tokens=6000),
])
def test_other_budget_guards_skip_consultation(home,policy,budget):
    backend=Backend();result=run(home,backend,budget=budget)
    assert [r['role']for r in backend.calls]==['main']
    assert result['condition_scientist_state']['consultation']['status']=='skipped_budget'


def test_no_trigger_adds_no_advice(home,policy,monkeypatch):
    monkeypatch.setattr(condition_scientist_runtime,'build_context',lambda *_:None)
    backend=Backend();result=run(home,backend)
    assert not result['condition_scientist_runs']
    assert all('condition_scientist_advice'not in r for r in backend.observations)


def test_checkpoint_failure_before_consultation_prevents_child_request(home,policy):
    from synthesis_route_gym.agent_accounting import CheckpointError
    backend=Backend()
    def save(state):
        if state['condition_scientist']['consultation'] is not None:raise OSError('storage failed')
    with pytest.raises(CheckpointError):run(home,backend,checkpoint=save)
    assert [r['role']for r in backend.calls]==['main']


def test_restore_rejects_invalid_advisor_state():
    for state in [{},{'schema_version':'srg-condition-scientist-runtime-v1','observer':{},'runs':[],
                     'consultation':{'status':'trusted','evidence_status':'experimental'}}]:
        with pytest.raises(ValueError):condition_scientist_runtime.restore_state(state)


def test_native_backend_tool_free_context_registers_no_tools(home,monkeypatch):
    from types import SimpleNamespace
    import sys
    from synthesis_route_gym.agent_runner import NativeAgentBackend, SharedLedger, resolve_main_profile
    seen={}
    class Registry:
        def register(self,**kw):raise AssertionError('no tool registration allowed')
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
    profile=resolve_main_profile(home);ledger=SharedLedger(AgentBudget())
    result=NativeAgentBackend()._execute(Agent,{},profile,'advice',[],lambda *_:None,ledger,
                                        'condition_optimisation_scientist',1)
    assert result['completed'] and seen['closed']
    assert len(seen['init']['enabled_toolsets'])==1
    assert seen['init']['fallback_model']==[]
    assert seen['init']['skip_memory'] and seen['init']['skip_context_files']

@pytest.mark.parametrize('change',[
    {'runs':[]},
    {'consultation':{'status':'accepted','plan':None,'evidence_status':'agent_proposal'}},
    {'delivery_pending':'yes'},
])
def test_resume_rejects_inconsistent_completed_advice(home,policy,change):
    saved=[];run(home,Backend(),checkpoint=lambda state:saved.append(copy.deepcopy(state)))
    latest=saved[-1]
    latest['condition_scientist']={**latest['condition_scientist'],**change}
    with pytest.raises(ValueError,match='Condition Scientist'):
        run(home,Backend(),resume_state=latest)


def test_optional_observer_failure_preserves_main_tool_result(home,policy,monkeypatch):
    def invalid(*_):raise ValueError('host molecule exceeds observer projection')
    monkeypatch.setattr(condition_scientist_runtime,'observe',invalid)
    backend=Backend();result=run(home,backend)
    assert result['completed']
    assert [r['role']for r in backend.calls]==['main']
    assert backend.observations[0]==execute('inspect',{})
    assert result['condition_scientist_state']['consultation']['status']=='disabled_observation'


def test_accepted_whitespace_padded_plan_resumes_from_canonical_json(home,policy):
    class PaddedBackend(Backend):
        def run(self,**kwargs):
            result=super().run(**kwargs)
            if kwargs['role']=='condition_optimisation_scientist':
                result={**result,'final_response':' '*17000+result['final_response']}
            return result
    checkpoints=[]
    first=run(home,PaddedBackend(),checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    assert first['condition_scientist_state']['consultation']['status']=='accepted'
    stored=first['condition_scientist_runs'][0]
    assert json.loads(stored['final_response'])=={'decision':'observe','next_candidate_id':'c3'}
    assert len(stored['final_response'])<16000
    assert stored['raw_response_chars']>17000 and stored['raw_response_sha256']
    assert stored['response_truncated'] is False
    resumed=Backend();again=run(home,resumed,resume_state=checkpoints[-1])
    assert not resumed.calls and again['completed']
    assert again['condition_scientist_state']['consultation']['plan']==first['condition_scientist_state']['consultation']['plan']


def test_advice_observation_is_detached_from_host_checkpoint_state(home,policy):
    backend=Backend();result=run(home,backend)
    backend.observations[1]['condition_scientist_advice']['plan']['next_candidate_id']='forged'
    assert result['condition_scientist_state']['consultation']['plan']['next_candidate_id']=='c3'


@pytest.mark.parametrize(('remaining','reserve','expected'),[
    (2,1,False),(3,1,True),(3,2,False),(4,2,True),
])
def test_condition_admission_preserves_main_action_round(remaining,reserve,expected):
    from synthesis_route_gym.agent_accounting import SharedLedger
    ledger=SharedLedger(AgentBudget(max_model_calls=10,wall_seconds=200,
                                    finalization_model_calls=reserve))
    resources={'remaining_model_calls':remaining,'remaining_tool_calls':20,
               'remaining_tokens':100000,'remaining_seconds':100}
    assert condition_scientist_runtime._admissible(ledger,resources,'bounded context') is expected


def test_hydrated_recommendation_is_copied_from_host_and_validated_on_resume(home,policy):
    checkpoints=[];backend=Backend()
    result=run(home,backend,checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    observed=backend.observations[1]['condition_scientist_advice']
    assert observed['recommendation']['selected_conditions']=={'ligand':'known'}
    observed['recommendation']['selected_conditions']['ligand']='forged'
    assert result['condition_scientist_state']['consultation']['recommendation']['selected_conditions']=={'ligand':'known'}
    changed=copy.deepcopy(checkpoints[-1])
    changed['condition_scientist']['consultation']['recommendation']['selected_conditions']['ligand']='forged'
    with pytest.raises(ValueError,match='persisted'):
        run(home,Backend(),resume_state=changed)


def test_condition_prefix_matches_main_and_preserves_route_prompt(home,policy):
    from synthesis_route_gym.agent_runner import ROLE_INSTRUCTIONS
    condition=Backend();run(home,condition)
    assert 'Choose and submit routes' not in condition.calls[0]['prompt']
    assert 'condition candidates' in condition.calls[0]['prompt']
    route_schemas=[{'name':name,'parameters':{'type':'object'}}
                   for name in ('inspect','observe_condition','submit')]
    route=Backend()
    run_agent_scientist('route task',execute,tool_schemas=route_schemas,
                       profile_home=home,backend=route)
    assert route.calls[0]['prompt']==ROLE_INSTRUCTIONS['main']+'\n\nroute task'


def test_condition_checkpoint_cannot_resume_as_route_mode(home,policy):
    saved=[]
    run(home,Backend(),checkpoint=lambda state:saved.append(copy.deepcopy(state)))
    assert saved[-1]['schema_version']=='srg-agent-runtime-condition-v1'
    for mode in ('main','main_strategist'):
        with pytest.raises(ValueError,match='binding'):
            run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,
                profile_home=home,mode=mode,backend=Backend(),resume_state=saved[-1])


def test_invalid_context_disables_advisor_without_stopping_main(home,policy,monkeypatch):
    def invalid(*_):raise ValueError('private source details')
    monkeypatch.setattr(condition_scientist_runtime,'build_context',invalid)
    backend=Backend();result=run(home,backend)
    assert result['completed']
    assert [row['role']for row in backend.calls]==['main']
    assert result['condition_scientist_state']['consultation']['status']=='disabled_observation'
    assert 'private source details'not in json.dumps(result)


def test_real_condition_episode_and_contract_execute_advice_without_leaking_outcomes(home):
    from synthesis_route_gym.condition_episode import ConditionEpisode
    from synthesis_route_gym.condition_scientist import context_fingerprint
    from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy
    study=FiniteConditionStudy(tuple(ConditionRecord(key,(('base',base),),value)
        for key,base,value in [('a','N',10.),('b','O',40.),('c','S',75.),('d','CC',86.)]),
        ('a',),4,'https://example.org/synthetic-fixture','host-private-source-locator','a'*64,'CCO')
    predictions=[{'candidate_id':'d','prediction_id':'pred-d','status':'scored','value':90.,
                  'unit':'percent','domain':'transfer_not_established','uncertainty':'not_calibrated',
                  'model_version':'public-fixture-v1'}]
    env=ConditionEpisode(study,study_id='fixture-study',predictions=predictions,target='CC=O')
    checkpoints=[]
    class CompleteBackend:
        def run(self,**kw):
            ident=kw['ledger'].claim_model_call()
            if kw['role']=='condition_optimisation_scientist':
                context=json.loads(kw['prompt'].split('\nHost context: ',1)[1])
                view=context['view']
                assert {row['candidate_id']for row in view['observations']}=={'a','b','c'}
                assert 'host-private-source-locator'not in json.dumps(context)
                plan={'schema_version':'srg-condition-plan-v1','context_sha256':context_fingerprint(context),
                      'decision':'observe','next_candidate_id':'d',
                      'cited_observation_ids':[view['observations'][-1]['source_record_id']],
                      'cited_prediction_ids':['pred-d'],'rationale':'Compare the remaining measured recipe.',
                      'evidence_status':'agent_proposal'}
                text=json.dumps(plan)
            else:
                assert 'condition candidates' in kw['prompt']
                kw['executor']('inspect',{})
                first=kw['executor']('observe_condition',{'candidate_id':'b'})
                assert 'condition_scientist_advice'not in first
                second=kw['executor']('observe_condition',{'candidate_id':'c'})
                advice=second['condition_scientist_advice']
                assert advice['status']=='accepted'
                assert advice['recommendation']['selected_conditions']=={'base':'CC'}
                assert advice['recommendation']['cited_predictions'][0]['uncertainty']=='not_calibrated'
                kw['executor']('observe_condition',{'candidate_id':advice['plan']['next_candidate_id']})
                kw['executor']('submit',{'candidate_id':'d'})
                text='Selected observed candidate d.'
            kw['ledger'].settle_request(ident,20)
            return {'completed':True,'final_response':text,'model':kw['profile'].model,
                    'provider':kw['profile'].provider,'token_confirmations':{ident:20},
                    'usage':{'input_tokens':15,'output_tokens':5,'total_tokens':20,'estimated_cost_usd':0}}
    result=run_agent_scientist('Condition study fixture',env.dispatch,tool_schemas=SCHEMAS,
        profile_home=home,mode='main_condition_scientist',backend=CompleteBackend(),
        checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    assert result['completed'] and result['ledger']['model_calls']==2
    assert result['ledger']['actual_tokens']==40 and result['ledger']['unsettled_requests']==0
    assert env.public_view()['resources']['new_observations_used']==3
    assert env.export()['submission']=={'status':'selected','candidate_id':'d'}
    restored=condition_scientist_runtime.restore_state(checkpoints[-1]['condition_scientist'])
    assert restored['consultation']['recommendation']==result['condition_scientist_state']['consultation']['recommendation']


def test_unknown_chemistry_scope_suppresses_real_contract_advisor(home):
    from test_condition_scientist import envelope, view
    calls=[]
    class MainOnlyBackend:
        def run(self,**kwargs):
            calls.append(kwargs['role'])
            ident=kwargs['ledger'].claim_model_call()
            inspected=kwargs['executor']('inspect',{})
            assert 'condition_scientist_advice'not in inspected
            kwargs['executor']('submit',{'candidate_id':None})
            kwargs['ledger'].settle_request(ident,10)
            return {'completed':True,'final_response':'Abstained outside registered study.',
                    'model':kwargs['profile'].model,'provider':kwargs['profile'].provider,
                    'token_confirmations':{ident:10},'usage':{'input_tokens':8,'output_tokens':2,
                                                           'total_tokens':10,'estimated_cost_usd':0}}
    def unavailable(action,args):
        if action=='inspect':return envelope(view(domain_status='unrelated_chemistry'))
        return {'status':'ok','result':{'submission':{'status':'abstained','candidate_id':None}},'terminated':True}
    result=run_agent_scientist('Unrelated chemistry fixture.',unavailable,tool_schemas=SCHEMAS,
        profile_home=home,mode='main_condition_scientist',backend=MainOnlyBackend())
    assert result['completed'] and calls==['main'] and not result['condition_scientist_runs']


def test_contract_valid_abstention_remains_proposal(home):
    from test_condition_scientist import envelope, view
    from synthesis_route_gym.condition_scientist import context_fingerprint
    state=view();calls=[]
    class AbstainingBackend:
        def run(self,**kwargs):
            calls.append(kwargs['role']);ident=kwargs['ledger'].claim_model_call()
            if kwargs['role']=='condition_optimisation_scientist':
                context=json.loads(kwargs['prompt'].split('\nHost context: ',1)[1])
                text=json.dumps({'schema_version':'srg-condition-plan-v1',
                    'context_sha256':context_fingerprint(context),'decision':'abstain','next_candidate_id':None,
                    'cited_observation_ids':['record-b'],'cited_prediction_ids':[],
                    'rationale':'Measurements do not establish a preferable next candidate.',
                    'evidence_status':'agent_proposal'})
            else:
                result=kwargs['executor']('inspect',{})
                advice=result['condition_scientist_advice']
                assert advice['status']=='accepted' and advice['plan']['decision']=='abstain'
                assert advice['recommendation']['selected_conditions']is None
                assert advice['recommendation']['evidence_status']=='agent_proposal'
                kwargs['executor']('submit',{'candidate_id':'b'});text='Submitted existing observed candidate.'
            kwargs['ledger'].settle_request(ident,10)
            return {'completed':True,'final_response':text,'model':kwargs['profile'].model,
                    'provider':kwargs['profile'].provider,'token_confirmations':{ident:10},
                    'usage':{'input_tokens':8,'output_tokens':2,'total_tokens':10,'estimated_cost_usd':0}}
    result=run_agent_scientist('Condition study fixture.',lambda name,args:envelope(state),
        tool_schemas=SCHEMAS,profile_home=home,mode='main_condition_scientist',backend=AbstainingBackend())
    assert result['completed'] and calls==['main','condition_optimisation_scientist']
