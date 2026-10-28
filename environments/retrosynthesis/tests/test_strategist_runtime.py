"""Nested advice shares the main ledger and cannot execute chemistry actions."""
import copy
import json
import pytest
from synthesis_route_gym.agent_runner import AgentBudget, RuntimeContractError, run_agent_scientist
from synthesis_route_gym import strategist_runtime
SCHEMAS = [{'name': name, 'parameters': {'type': 'object'}} for name in ('inspect', 'expand', 'submit')]
@pytest.fixture
def home(tmp_path):
    (tmp_path/'config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n')
    return tmp_path
@pytest.fixture
def policy(monkeypatch):
    monkeypatch.setattr(strategist_runtime, 'observer_state', lambda: {'count': 0})
    monkeypatch.setattr(strategist_runtime, 'observe', lambda state, action, args, response: {'count':state['count']+1})
    monkeypatch.setattr(strategist_runtime, 'build_context', lambda state, resources: {'frontier':['CCO'],'resources':resources} if state['count']>=2 else None)
    monkeypatch.setattr(strategist_runtime, 'context_fingerprint', lambda context: 'context-one')
    def parse(text, context):
        value=json.loads(text)
        if value != {'next_expansion_targets':['CCO']}:raise ValueError('invalid plan')
        return value
    monkeypatch.setattr(strategist_runtime, 'parse_plan', parse)
class Backend:
    def __init__(self, *, malformed=False, failure=False, mismatch=False, interrupt=False):
        self.calls=[];self.observations=[]
        self.malformed,self.failure,self.mismatch,self.interrupt=malformed,failure,mismatch,interrupt
    def run(self, **kw):
        self.calls.append(kw)
        ledger=kw['ledger']
        request=ledger.claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if kw['role']=='retrosynthesis_strategist':
            assert kw['tool_schemas']==[] and kw['model_call_limit']==1
            with pytest.raises(RuntimeContractError):kw['executor']('expand',{'smiles':'CCO'})
            if self.interrupt:raise KeyboardInterrupt()
            if self.failure:raise OSError('private provider secret must not appear')
            text='not-json' if self.malformed else '{"next_expansion_targets":["CCO"]}'
        else:
            for action in ['inspect','expand','expand']:
                self.observations.append(kw['executor'](action,{}))
            assert ledger._role=='main'
            kw['executor']('submit',{'route_ids':[]})
            text='submitted'
        ledger.settle_request(request,12)
        return {'completed':True,'final_response':text,'messages':[],
                'model':'different' if self.mismatch and kw['role']!='main' else kw['profile'].model,
                'provider':kw['profile'].provider,'token_confirmations':{request:12},
                'usage':{'input_tokens':10,'output_tokens':2,'total_tokens':12,'estimated_cost_usd':0.0}}

def execute(name,args):return {'status':'ok','result':{'action':name}}
def run(home,backend,**kwargs):
    return run_agent_scientist('same main prompt',execute,tool_schemas=SCHEMAS,
        profile_home=home,mode='main_strategist',backend=backend,**kwargs)
def test_nested_advice_shares_profile_and_accounts_once(home,policy):
    backend=Backend();result=run(home,backend)
    assert [r['role']for r in backend.calls]==['main','retrosynthesis_strategist']
    assert len({id(r['profile'])for r in backend.calls})==1
    assert len({id(r['ledger'])for r in backend.calls})==1
    assert result['completed']
    assert len(result['runs'])==1 and len(result['strategist_runs'])==1
    assert result['strategist_runs'][0]['context']['frontier']==['CCO']
    assert result['strategist_runs'][0]['prompt_sha256']
    assert 'messages'not in result['strategist_runs'][0]
    assert result['usage']['total_tokens']==24
    assert result['ledger']['actual_tokens']==24
    assert result['ledger']['model_calls']==2
    assert result['ledger']['tool_calls']==4
    assert backend.observations[1]['strategist_advice']['status']=='accepted'
    assert backend.observations[1]['strategist_advice']['evidence_status']=='agent_proposal'
    assert 'strategist_advice'not in backend.observations[2]
@pytest.mark.parametrize('kind',['malformed','failure'])
def test_failed_advice_never_stops_main_or_claims_success(home,policy,kind):
    backend=Backend(**{kind:True});result=run(home,backend)
    assert result['completed'] and len(result['strategist_runs'])==1
    advice=backend.observations[1]['strategist_advice']
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
    assert result['strategist_runs']==[]
    assert result['completed']

def test_pending_advice_consumed_across_resume(home,policy):
    checkpoints=[];backend=Backend(interrupt=True)
    with pytest.raises(KeyboardInterrupt):
        run(home,backend,checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    saved=checkpoints[-1]
    assert saved['strategist']['consultation']['status']=='pending'
    assert saved['ledger']['counts']['model_calls']==2
    resumed=Backend();result=run(home,resumed,resume_state=saved)
    assert [r['role']for r in resumed.calls]==['main']
    assert result['completed'] and result['ledger']['model_calls']==3
    assert resumed.observations[0]['strategist_advice']['status']=='interrupted'

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
    assert result['strategist_state']['consultation']['status']=='skipped_budget'


def test_no_trigger_adds_no_advice(home,policy,monkeypatch):
    monkeypatch.setattr(strategist_runtime,'build_context',lambda *_:None)
    backend=Backend();result=run(home,backend)
    assert not result['strategist_runs']
    assert all('strategist_advice'not in r for r in backend.observations)


def test_checkpoint_failure_before_consultation_prevents_child_request(home,policy):
    from synthesis_route_gym.agent_accounting import CheckpointError
    backend=Backend()
    def save(state):
        if state['strategist']['consultation'] is not None:raise OSError('storage failed')
    with pytest.raises(CheckpointError):run(home,backend,checkpoint=save)
    assert [r['role']for r in backend.calls]==['main']


def test_restore_rejects_invalid_advisor_state():
    for state in [{},{'schema_version':'srg-strategist-runtime-v1','observer':{},'runs':[],
                     'consultation':{'status':'trusted','evidence_status':'experimental'}}]:
        with pytest.raises(ValueError):strategist_runtime.restore_state(state)


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
                                        'retrosynthesis_strategist',1)
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
    latest['strategist']={**latest['strategist'],**change}
    with pytest.raises(ValueError,match='Strategist'):
        run(home,Backend(),resume_state=latest)


def test_real_environment_observer_and_parent_execute_validated_advice(home):
    from synthesis_route_gym.environment import SynthesisRouteEnv
    from synthesis_route_gym.schemas import Task,InventoryItem
    from synthesis_route_gym.strategist import context_fingerprint
    task=Task(task_id='advice-engineering-fixture',target='CCOC(C)=O',
              inventory=(InventoryItem(smiles='CCO'),InventoryItem(smiles='CC(=O)O')))
    def expand(smiles,k):
        return {'status':'ok','predictions':[{'product':smiles,'reactants':['CCO','CC=O'],
            'source':{'tool':'fixture','version':'1'},'score':.2}]} if smiles==task.target else {'status':'ok','predictions':[]}
    env=SynthesisRouteEnv(task,expand=expand)
    class CompleteBackend:
        def run(self,**kw):
            ident=kw['ledger'].claim_model_call()
            if kw['role']=='retrosynthesis_strategist':
                context=json.loads(kw['prompt'].split('\nHost context: ',1)[1])
                assert context['frontier']==[{'inventory_status':'unavailable','smiles':'CC=O'}]
                plan={'schema_version':'srg-strategist-plan-v1','context_sha256':context_fingerprint(context),
                      'candidate_route_ids':[],'next_expansion_targets':['CC=O'],
                      'alternative_disconnection_ids':[context['alternatives'][0]['id']],
                      'relevant_constraint_keys':['max_steps'],'action_allowance':1,
                      'rationale':'Resolve observed missing material; chemistry remains predicted.',
                      'evidence_status':'agent_proposal'}
                text=json.dumps(plan)
            else:
                kw['executor']('inspect',{})
                kw['executor']('expand',{'smiles':task.target})
                kw['executor']('inspect',{'inventory_smiles':['CCO','CC=O']})
                advice=kw['executor']('expand',{'smiles':task.target})['strategist_advice']
                assert advice['status']=='accepted'
                kw['executor']('expand',{'smiles':advice['plan']['next_expansion_targets'][0]})
                kw['executor']('submit',{'route_ids':[]})
                text='Empty submission preserves uncertainty.'
            kw['ledger'].settle_request(ident,20)
            return {'completed':True,'final_response':text,'model':kw['profile'].model,'provider':kw['profile'].provider,
                    'usage':{'input_tokens':15,'output_tokens':5,'total_tokens':20,'estimated_cost_usd':0},
                    'token_confirmations':{ident:20}}
    result=run_agent_scientist('Plan',env.dispatch,tool_schemas=SCHEMAS,profile_home=home,
                              mode='main_strategist',backend=CompleteBackend())
    assert result['completed'] and result['ledger']['model_calls']==2
    assert result['ledger']['actual_tokens']==40
    assert env.export()['scientific_usage']['expand']==3
    assert env.export()['submitted_route_ids']==[]


def test_optional_observer_failure_preserves_main_tool_result(home,policy,monkeypatch):
    def invalid(*_):raise ValueError('host molecule exceeds observer projection')
    monkeypatch.setattr(strategist_runtime,'observe',invalid)
    backend=Backend();result=run(home,backend)
    assert result['completed']
    assert [r['role']for r in backend.calls]==['main']
    assert backend.observations[0]==execute('inspect',{})
    assert result['strategist_state']['consultation']['status']=='disabled_observation'


def test_accepted_whitespace_padded_plan_resumes_from_canonical_json(home,policy):
    class PaddedBackend(Backend):
        def run(self,**kwargs):
            result=super().run(**kwargs)
            if kwargs['role']=='retrosynthesis_strategist':
                result={**result,'final_response':' '*17000+result['final_response']}
            return result
    checkpoints=[]
    first=run(home,PaddedBackend(),checkpoint=lambda state:checkpoints.append(copy.deepcopy(state)))
    assert first['strategist_state']['consultation']['status']=='accepted'
    stored=first['strategist_runs'][0]
    assert json.loads(stored['final_response'])=={'next_expansion_targets':['CCO']}
    assert len(stored['final_response'])<16000
    assert stored['raw_response_chars']>17000 and stored['raw_response_sha256']
    assert stored['response_truncated'] is False
    resumed=Backend();again=run(home,resumed,resume_state=checkpoints[-1])
    assert not resumed.calls and again['completed']
    assert again['strategist_state']['consultation']['plan']==first['strategist_state']['consultation']['plan']


def test_advice_observation_is_detached_from_host_checkpoint_state(home,policy):
    backend=Backend();result=run(home,backend)
    backend.observations[1]['strategist_advice']['plan']['next_expansion_targets'].append('forged')
    assert result['strategist_state']['consultation']['plan']['next_expansion_targets']==['CCO']
