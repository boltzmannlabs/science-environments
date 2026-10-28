import copy
import json
import subprocess
import sys
import pytest
from synthesis_route_gym.orchestration import normalize_policy, policy_fingerprint, role_prompt_instructions
from synthesis_route_gym import orchestration_runtime as host

ROLES = ('strategist', 'condition_scientist', 'route_critic')

def test_default_policies_and_prompt():
    assert normalize_policy('main_adaptive')['enabled_roles'] == []
    assert normalize_policy('main_all_advisors')['enabled_roles'] == list(ROLES)
    assert normalize_policy('main_role_prompt')['max_consultations'] == 0
    assert 'same main' in role_prompt_instructions().lower()

@pytest.mark.parametrize('mode,policy', [
    ('invalid', None), ('main_adaptive', {'promoted':True}),
    ('main_adaptive', {'enabled_roles':['strategist'], 'max_consultations':1}),
    ('main_adaptive', {'experimental':True,'enabled_roles':['unknown'],'max_consultations':1}),
    ('main_adaptive', {'experimental':True,'enabled_roles':['strategist','strategist'],'max_consultations':1}),
    ('main_adaptive', {'experimental':True,'enabled_roles':list(ROLES),'max_consultations':3}),
    ('main_role_prompt', {'experimental':True,'enabled_roles':['strategist'],'max_consultations':1}),
    ('main_all_advisors', {'max_consultations':1}),
    ('main_adaptive', {'experimental':'yes'}), ('main_adaptive', {'max_consultations':True}),
])
def test_invalid_policy_rejected(mode, policy):
    with pytest.raises(ValueError): normalize_policy(mode,policy)

def test_normalized_policy_immutable_and_hash_stable():
    raw={'experimental':True,'enabled_roles':['strategist'],'max_consultations':1}
    original=copy.deepcopy(raw)
    normalized=normalize_policy('main_adaptive',raw)
    assert raw==original
    assert normalize_policy('main_adaptive',normalized)==normalized
    assert policy_fingerprint(normalized)==policy_fingerprint(dict(reversed(list(normalized.items()))))

class Child:
    def __init__(self,role): self.role=role; self.calls=[]
    def initial_state(self):
        return {'observer':{'count':0},'consultation':None,'runs':[],'delivery_pending':False}
    def restore_state(self,state):
        state=copy.deepcopy(state)
        if state['consultation'] and state['consultation']['status']=='pending':
            state['consultation']['status']='interrupted'
            state['runs']=[{'role':self.role,'completed':False}]
            state['delivery_pending']=True
        return state
    def observe(self,state,action,args,response):return {'count':state['count']+1}
    def build_context(self,state,resources):return {'context':self.role}
    def context_fingerprint(self,context):return self.role
    def after_tool(self,action,args,response,*,state,update,runtime,profile,ledger):
        if state['consultation']:
            update({**state,'delivery_pending':False})
            return {**response,'delivered':self.role}
        self.calls.append((runtime,profile,ledger,state['observer']['count']))
        current={**state,'observer':self.observe(state['observer'],action,args,response),
                 'consultation':{'status':'pending','evidence_status':'agent_proposal'}}
        update(current)
        if runtime=='interrupt':raise KeyboardInterrupt()
        update({**current,'consultation':{'status':'accepted','evidence_status':'agent_proposal'},
                'runs':[{'role':self.role,'completed':True}]})
        return {**response,'delivered':self.role}

class Ledger:
    finalization_only=False
    class budget:
        regime='budgeted'
        max_model_calls=20;max_tool_calls=30;max_total_tokens=200000;wall_seconds=1800
    def snapshot(self):return {'model_calls':1,'tool_calls':1,'charged_tokens':100,'elapsed_seconds':1}

@pytest.fixture
def children(monkeypatch):
    values={role:Child(role) for role in ROLES}
    monkeypatch.setattr(host,'_module',lambda role:values[role])
    return values

def tick(state,*,action='review_routes',runtime='backend',ledger=None):
    saved=[]
    result=host.after_tool(action,{}, {'status':'ok','result':{}},state=state,
        update=lambda value:saved.append(copy.deepcopy(value)),runtime=runtime,profile='main-profile',ledger=ledger or Ledger())
    return saved[-1],result,saved

def test_default_never_forces_advisors(children):
    state=host.initial_state('main_adaptive')
    before=copy.deepcopy(state)
    after,_,_=tick(state)
    assert state==before
    assert not any(child.calls for child in children.values())
    assert after['decision_count']==1
    assert host.summarize_state(after)['consultations_used']==0

def test_all_sequential_once_and_flattened(children):
    state=host.initial_state('main_all_advisors')
    for index in range(5):
        state,result,saved=tick(state)
        assert sum(len(child.calls)for child in children.values())==min(index+1,3)
    assert state['consultation_order']==list(ROLES)
    assert [run['role']for run in state['runs']]==list(ROLES)
    assert [children[r].calls[0][3]for r in ROLES]==[0,1,0]
    assert all(child.calls[0][:2]==('backend','main-profile')for child in children.values())
    assert host.summarize_state(state)['consultations_used']==3

def test_adaptive_explicit_optin_cap(children):
    state=host.initial_state('main_adaptive',{'experimental':True,'enabled_roles':['route_critic'],'max_consultations':1})
    for _ in range(3):state,_,_=tick(state)
    assert len(children['route_critic'].calls)==1
    assert not children['strategist'].calls

@pytest.mark.parametrize('action',['submit'])
def test_closed_never_calls(children,action):
    state,_,_=tick(host.initial_state('main_all_advisors'),action=action)
    state,_,_=tick(state)
    assert state['closed'] and not any(child.calls for child in children.values())

def test_finalization_and_ineligible_dont_call(children):
    ledger=Ledger();ledger.finalization_only=True
    state,_,_=tick(host.initial_state('main_all_advisors'),ledger=ledger)
    assert not any(c.calls for c in children.values())
    for child in children.values(): child.build_context=lambda *args:None
    state,_,_=tick(state)
    assert not any(c.calls for c in children.values())

def test_pending_consumed_resume_and_policy_pinned(children):
    state=host.initial_state('main_all_advisors');saved=[]
    with pytest.raises(KeyboardInterrupt):
        host.after_tool('review_routes',{}, {'status':'ok','result':{}},state=state,
            update=lambda value:saved.append(copy.deepcopy(value)),runtime='interrupt',profile='main-profile',ledger=Ledger())
    assert saved[-1]['advisors']['strategist']['consultation']['status']=='pending'
    resumed=host.restore_state(saved[-1],mode='main_all_advisors')
    assert resumed['advisors']['strategist']['consultation']['status']=='interrupted'
    assert len(resumed['runs'])==1
    resumed,_,_=tick(resumed)
    assert len(children['strategist'].calls)==1
    with pytest.raises(ValueError):host.restore_state(saved[-1],mode='main_adaptive')

@pytest.mark.parametrize('field,value',[('policy_sha256','changed'),('decision_count',True),('closed',0),('schema_version','v0'),('runs',[{}]),('consultation_order',['invented'])])
def test_restore_rejects_tampering(children,field,value):
    state=host.initial_state('main_adaptive');state[field]=value
    with pytest.raises(ValueError):host.restore_state(state)

def test_bounded_decisions(children):
    state=host.initial_state('main_role_prompt')
    for _ in range(270):state,_,_=tick(state)
    assert len(state['decisions'])<=256 and state['decision_count']==270
    assert state['decisions_truncated']
    assert host.restore_state(state)==state

def test_invalid_observation_disables_only_child(children):
    def broken(*args):raise ValueError('private detail')
    children['strategist'].observe=broken
    state,_,_=tick(host.initial_state('main_all_advisors'))
    assert state['advisors']['strategist']['consultation']['status']=='disabled_observation'
    assert len(children['condition_scientist'].calls)==1
    assert 'private detail' not in json.dumps(state)

def test_native_import_is_rdkit_free():
    code='import sys; import synthesis_route_gym.orchestration_runtime; assert not any(k.startswith("rdkit") for k in sys.modules)'
    result=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
    assert result.returncode==0,result.stderr

@pytest.mark.parametrize('change',[{'extra':True},{'index':True},{'action':[]},{'reasons':dict.fromkeys(ROLES,[])},{'eligible_roles':['unknown']},{'input_sha256':'x'}])
def test_strict_decision_schema(children,change):
    state,_,_=tick(host.initial_state('main_adaptive'))
    state['decisions'][0].update(change)
    with pytest.raises(ValueError):host.restore_state(state)

def test_restore_rejects_extra_top_keys_and_oversized_state(children):
    state=host.initial_state('main_adaptive')
    with pytest.raises(ValueError):host.restore_state({**state,'unknown':1})
    state['advisors']['strategist']['observer']['huge']='x'*2000000
    with pytest.raises(ValueError):host.restore_state(state)

def test_resume_delivery_and_invalid_review(children):
    state=host.initial_state('main_all_advisors')
    state,_,_=tick(state,action='inspect')
    state,_,_=tick(state,action='inspect')
    assert not children['route_critic'].calls
    state['advisors']['strategist']['delivery_pending']=True
    state,answer,_=tick(state,action='inspect')
    assert answer['delivered']=='strategist'
    assert not state['advisors']['strategist']['delivery_pending']

@pytest.mark.parametrize('policy',[
    {'enabled_roles':['strategist'],'experimental':True,'max_consultations':0},
    {'enabled_roles':['strategist'],'experimental':True,'max_consultations':2},
    {'priority':['strategist','strategist','route_critic']},
    'invalid',
])
def test_remaining_policy_bounds(policy):
    with pytest.raises(ValueError):normalize_policy('main_adaptive',policy)

def test_policy_model_is_frozen():
    from synthesis_route_gym.orchestration import OrchestrationPolicy
    value=OrchestrationPolicy()
    with pytest.raises(ValueError):value.experimental=True
    assert normalize_policy('main_adaptive',value)['experimental'] is False

def test_explicit_policy_resume_and_policy_digest_tamper(children):
    policy={'experimental':True,'enabled_roles':['strategist'],'max_consultations':1}
    state=host.initial_state('main_adaptive',policy)
    assert host.restore_state(state,policy=policy)==state
    with pytest.raises(ValueError):host.restore_state(state,policy={})
    state['policy']['policy_id']='different'
    with pytest.raises(ValueError):host.restore_state(state)

def test_context_binding_invalid_checkpoint(children):
    state,_,_=tick(host.initial_state('main_all_advisors'))
    state['decisions'][0]['context_sha256']=None
    with pytest.raises(ValueError):host.restore_state(state)

def test_disabled_role_consumption_and_allowance_rejected(children):
    state,_,_=tick(host.initial_state('main_all_advisors'))
    state['mode']='main_adaptive'
    state['policy']=normalize_policy('main_adaptive')
    state['policy_sha256']=policy_fingerprint(state['policy'])
    with pytest.raises(ValueError):host.restore_state(state)
    state['policy']=normalize_policy('main_adaptive',{'enabled_roles':['condition_scientist'],'experimental':True,'max_consultations':1})
    state['policy_sha256']=policy_fingerprint(state['policy'])
    with pytest.raises(ValueError):host.restore_state(state)

def test_corrupt_advisor_is_valueerror(children):
    state=host.initial_state('main_adaptive');state['advisors']['strategist']=None
    with pytest.raises(ValueError):host.restore_state(state)


def test_role_prompt_control_preserves_substantive_specialist_rules():
    prompt=role_prompt_instructions().lower()
    required=(
        'compare only observed alternatives', 'unexpanded frontier', 'do not repeat failed branches',
        'known to be in inventory', 'at most two', 'exact route and step',
        'eligible unqueried candidate', 'revealed measurement source ids',
        'unchanged route', 'newly conducted experiment', 'unknown candidate outcomes remain unknown',
        'missing conditions', 'do not prove a reaction impossible',
        'connectivity match', 'deterministic error', 'at most eight',
        'stereochemistry', 'quantity_conflict', 'model_domain_mismatch',
        'at most one recheck', 'no extra resources',
    )
    for rule in required:assert rule in prompt,rule
    assert 'exactly one json' not in prompt and 'you have no tools' not in prompt
    documentation=role_prompt_instructions.__doc__
    assert 'not an exact prompt-matched causal control' in documentation
    for module in ('strategist_runtime','route_condition_runtime','route_critic_runtime'):
        assert module in documentation
