"""Real advisor admission, ledger accounting and failed consultation integration."""
import copy
from types import SimpleNamespace
import pytest
from synthesis_route_gym import orchestration_runtime as host, strategist_runtime, route_critic_runtime
from synthesis_route_gym.agent_accounting import AgentBudget, SharedLedger
from synthesis_route_gym.agent_runner import RuntimeContractError


class DormantCondition:
    def initial_state(self):return {'observer':{},'consultation':None,'runs':[],'delivery_pending':False}
    def observe(self,state,*args):return dict(state)
    def build_context(self,*args):return None
    def restore_state(self,state):return copy.deepcopy(state)


@pytest.fixture
def real_strategist(monkeypatch):
    modules={'strategist':strategist_runtime,'route_critic':route_critic_runtime,'condition_scientist':DormantCondition()}
    monkeypatch.setattr(host,'_module',lambda role:modules[role])
    monkeypatch.setattr(strategist_runtime,'observer_state',lambda:{'count':0})
    monkeypatch.setattr(strategist_runtime,'observe',lambda state,*args:{'count':state['count']+1})
    monkeypatch.setattr(strategist_runtime,'build_context',lambda state,resources:{'frontier':['CCO'],'resources':resources})
    return modules


class Backend:
    def __init__(self,kind='rejected'):self.calls=[];self.kind=kind
    def run(self,**kwargs):
        self.calls.append(kwargs)
        assert kwargs['role']=='retrosynthesis_strategist'
        assert kwargs['tool_schemas']==[]
        with pytest.raises(RuntimeContractError):kwargs['executor']('expand',{})
        ledger=kwargs['ledger']
        request=ledger.claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if self.kind=='interrupt':raise KeyboardInterrupt()
        if self.kind=='failed':raise OSError('secret provider detail')
        ledger.settle_request(request,12)
        return {'model':'wrong' if self.kind=='mismatch' else kwargs['profile'].model,
                'provider':kwargs['profile'].provider,'completed':True,'messages':[],
                'final_response':'invalid plan','usage':{'total_tokens':12},'token_confirmations':{request:12}}


def execute(state,backend,ledger,saved):
    profile=SimpleNamespace(model='main-model',provider='main-provider')
    answer=host.after_tool('inspect',{}, {'status':'ok','result':{}},state=state,
        update=lambda value:saved.append(copy.deepcopy(value)),runtime=backend,profile=profile,ledger=ledger)
    assert all(call['profile'] is profile and call['ledger'] is ledger for call in backend.calls)
    return answer


@pytest.mark.parametrize('kind',['rejected','failed'])
def test_real_advisor_failure_and_accounting(real_strategist,kind):
    state=host.initial_state('main_all_advisors');ledger=SharedLedger(AgentBudget());backend=Backend(kind);saved=[]
    answer=execute(state,backend,ledger,saved)
    assert answer['orchestration_advice']['consultation']['status']==kind
    assert len(saved[-1]['runs'])==1 and ledger.snapshot()['model_calls']==1
    assert ledger._role=='main'
    assert 'secret provider detail' not in str(saved[-1])
    execute(saved[-1],Backend(),ledger,saved)
    assert ledger.snapshot()['model_calls']==1
    restored=host.restore_state(saved[-1],mode='main_all_advisors')
    assert len(restored['runs'])==1
    assert saved[-1]['decisions'][0]['context_sha256']==saved[-1]['advisors']['strategist']['consultation']['context_sha256']


def test_real_pending_consumed_and_mismatch_fail_closed(real_strategist):
    for kind,error in [('interrupt',KeyboardInterrupt),('mismatch',RuntimeContractError)]:
        state=host.initial_state('main_all_advisors');ledger=SharedLedger(AgentBudget());saved=[]
        with pytest.raises(error):execute(state,Backend(kind),ledger,saved)
        assert saved[-1]['advisors']['strategist']['consultation']['status']=='pending'
        resumed=host.restore_state(saved[-1],mode='main_all_advisors')
        assert resumed['runs'][0]['error_type']=='InterruptedConsultation'
        backend=Backend();execute(resumed,backend,ledger,saved)
        assert not backend.calls and ledger.snapshot()['model_calls']==1
        assert ledger._role=='main'


def test_real_admission_reserves_main_finalization(real_strategist):
    state=host.initial_state('main_all_advisors');ledger=SharedLedger(AgentBudget(max_model_calls=2));saved=[];backend=Backend()
    answer=execute(state,backend,ledger,saved)
    assert not backend.calls and saved[-1]['runs']==[]
    assert answer['orchestration_advice']['consultation']['status']=='skipped_budget'
    assert host.summarize_state(saved[-1])['consultations_used']==0


def test_disabled_restored_advisor_cannot_starve_later_saved_advice(real_strategist):
    state=host.initial_state('main_all_advisors')
    state['advisors']['strategist']['consultation']={
        'status':'disabled_observation','plan':None,'evidence_status':'agent_proposal',
        'reason':'Bounded observation unavailable.'}
    critic=state['advisors']['route_critic']
    critic['consultation']={'status':'failed','report':None,'evidence_status':'agent_proposal',
                            'reason':'Prior consultation failed.'}
    critic['runs']=[{'role':'route_critic','completed':False,'usage':{}}]
    state['consultation_order']=['strategist','route_critic']
    state['runs']=copy.deepcopy(critic['runs'])
    resumed=host.restore_state(state,mode='main_all_advisors')
    saved=[];backend=Backend();ledger=SharedLedger(AgentBudget())
    answer=execute(resumed,backend,ledger,saved)
    assert answer['route_critic_advice']['status']=='failed'
    assert not saved[-1]['advisors']['strategist']['delivery_pending']
    assert not saved[-1]['advisors']['route_critic']['delivery_pending']
    assert not backend.calls and ledger.snapshot()['model_calls']==0
