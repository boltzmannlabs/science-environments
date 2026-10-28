"""One route-condition consultation shares the ledger and survives interruption."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from synthesis_route_gym.agent_accounting import AgentBudget,SharedLedger,CheckpointError
from synthesis_route_gym.agent_runner import RuntimeContractError
from synthesis_route_gym import route_condition_runtime as module
from test_route_condition_advice import catalog,plan,response

ARGS={'route_id':'r1','step_id':'s1','offset':0,'limit':20}
PROFILE=SimpleNamespace(model='main-profile-model',provider='main-profile-provider')


class Backend:
    def __init__(self,mode='accepted'):self.mode=mode;self.calls=[]
    def run(self,**kw):
        self.calls.append(kw);assert kw['tool_schemas']==[]and kw['model_call_limit']==1
        assert kw['role']=='condition_optimisation_scientist'and kw['profile']is PROFILE
        with pytest.raises(RuntimeContractError):kw['executor']('observe_route_condition',{})
        request=kw['ledger'].claim_model_call(estimated_input_tokens=20,reserved_output_tokens=20)
        if self.mode=='interrupt':raise KeyboardInterrupt()
        if self.mode=='error':raise OSError('private source path secret')
        if self.mode=='checkpoint':raise CheckpointError('storage failed')
        ctx=json.loads(kw['prompt'].split('\nHost context: ',1)[1])
        text=json.dumps(plan(ctx))if self.mode!='malformed'else'not-json'
        if self.mode=='padded':text=' '*17000+text
        kw['ledger'].settle_request(request,12)
        return {'completed':True,'final_response':text,'usage':{'input_tokens':10,'output_tokens':2,'total_tokens':12},
            'token_confirmations':{request:12},'model':'wrong'if self.mode=='profile'else PROFILE.model,'provider':PROFILE.provider}


class Harness:
    def __init__(self,mode='accepted',budget=None,state=None):
        self.state=module.initial_state()if state is None else state;self.saved=[];self.backend=Backend(mode)
        self.ledger=SharedLedger(budget or AgentBudget())
    def update(self,state):self.state=deepcopy(state);self.saved.append(deepcopy(state))
    def invoke(self,value=None,*,action='condition_options',args=None,patch=None):
        return module.after_tool(action,ARGS if args is None else args,response(catalog()if value is None else value,**(patch or{})),
            state=self.state,update=self.update,runtime=self.backend,profile=PROFILE,ledger=self.ledger)


def test_one_consultation_only_and_main_executes_recommendation():
    h=Harness();result=h.invoke();advice=result['route_condition_advice']
    assert advice['status']=='accepted'and advice['recommendation']['next_action']['arguments']['candidate_id']=='c'
    assert h.ledger.snapshot()['model_calls']==1 and h.ledger.snapshot()['actual_tokens']==12
    assert h.ledger._role=='main'and len(h.backend.calls)==1
    assert any(v['consultation']and v['consultation']['status']=='pending'for v in h.saved)
    assert 'route_condition_advice'not in h.invoke()
    assert len(h.backend.calls)==1


@pytest.mark.parametrize('mode,status',[('malformed','rejected'),('error','failed')])
def test_bad_advice_consumed_with_unknown_usage_preserved(mode,status):
    h=Harness(mode);result=h.invoke();assert result['route_condition_advice']['status']==status
    h.invoke();assert len(h.backend.calls)==1 and h.ledger._role=='main'
    assert 'private source'not in json.dumps(h.state)
    if mode=='error':assert h.ledger.snapshot()['reserved_tokens']==40


@pytest.mark.parametrize('mode,exception',[('profile',RuntimeContractError),('checkpoint',CheckpointError)])
def test_contract_failures_propagate_and_restore_main_stage(mode,exception):
    h=Harness(mode)
    with pytest.raises(exception):h.invoke()
    assert h.ledger._role=='main'and h.state['consultation']['status']=='pending'


def test_interruption_is_consumed_and_redelivered_without_new_request():
    h=Harness('interrupt')
    with pytest.raises(KeyboardInterrupt):h.invoke()
    assert h.state['consultation']['status']=='pending'and h.ledger.snapshot()['reserved_tokens']==40
    restored=module.restore_state(h.state);assert restored['consultation']['status']=='interrupted'
    resumed=Harness(state=restored);result=resumed.invoke({},action='inspect',args={})
    assert result['route_condition_advice']['status']=='interrupted'and resumed.backend.calls==[]
    assert 'route_condition_advice'not in resumed.invoke({},action='inspect',args={})


def test_restored_accepted_plan_validated_and_detached():
    h=Harness();h.invoke();restored=module.restore_state(h.state);again=Harness(state=restored)
    result=again.invoke({},action='inspect',args={});assert not again.backend.calls
    result['route_condition_advice']['recommendation']['next_action']['arguments']['candidate_id']='fake'
    assert again.state['consultation']['recommendation']['next_action']['arguments']['candidate_id']=='c'


@pytest.mark.parametrize('field',['plan','recommendation','context_sha256'])
def test_changed_accepted_advice_rejected(field):
    h=Harness();h.invoke();state=deepcopy(h.state);state['consultation'][field]='forged'
    with pytest.raises(ValueError):module.restore_state(state)


@pytest.mark.parametrize('budget',[AgentBudget(max_model_calls=2),AgentBudget(max_tool_calls=2),AgentBudget(max_total_tokens=6000)])
def test_finalization_resources_are_reserved(budget):
    h=Harness(budget=budget);out=h.invoke()
    assert out['route_condition_advice']['status']=='skipped_budget'and not h.backend.calls


@pytest.mark.parametrize('action,patch',[('submit',{}),('condition_options',{'terminated':True}),('condition_options',{'truncated':True})])
def test_closed_response_never_invokes_or_redelivers(action,patch):
    h=Harness();h.invoke(action=action,patch=patch);assert not h.backend.calls
    first=Harness();first.invoke();restored=Harness(state=module.restore_state(first.state))
    result=restored.invoke(action=action,patch=patch)
    assert 'route_condition_advice'not in result and not restored.backend.calls


def test_insufficient_feedback_does_not_consume_consultation():
    h=Harness();h.invoke(catalog(observed=('a',)))
    assert h.state['consultation']is None and not h.backend.calls
    assert h.invoke()['route_condition_advice']['status']=='accepted'


def test_malformed_catalog_disables_without_exposing_details():
    h=Harness();out=h.invoke({'schema_version':'bad','private':'secret'})
    assert 'route_condition_advice'not in out and not h.backend.calls
    assert h.state['consultation']['status']=='disabled_observation'
    assert 'secret'not in json.dumps(h.state)


def test_checkpoint_failure_before_request_prevents_admission():
    h=Harness()
    def update(value):
        if value['consultation']is not None:raise CheckpointError('save failed')
        h.update(value)
    with pytest.raises(CheckpointError):
        module.after_tool('condition_options',ARGS,response(catalog()),state=h.state,update=update,
            runtime=h.backend,profile=PROFILE,ledger=h.ledger)
    assert not h.backend.calls


@pytest.mark.parametrize('patch',[{'schema_version':'bad'},{'runs':[{}]},{'delivery_pending':True},
    {'observer':{}},{'extra':True},{'delivery_pending':'yes'}])
def test_invalid_checkpoint_rejected(patch):
    with pytest.raises(ValueError):module.restore_state({**module.initial_state(),**patch})


def test_padded_valid_advice_saved_canonically():
    h=Harness('padded');h.invoke();run=h.state['runs'][0]
    assert run['raw_response_chars']>17000 and run['response_truncated']is False
    assert len(run['final_response'])<16000
    assert module.restore_state(h.state)['consultation']['status']=='accepted'


def test_independent_role_settlement_identity():
    h=Harness();h.invoke()
    assert 'route_condition_optimisation_scientist:advice:1'in h.ledger.export_state()['stages']


@pytest.mark.parametrize('replacement',['empty','changed_config'])
def test_restored_advice_must_match_its_saved_public_observer(replacement):
    from synthesis_route_gym import route_condition_advice as contract
    from test_route_condition_advice import ingest
    h=Harness();h.invoke();state=deepcopy(h.state)
    state['observer']=contract.initial_state()if replacement=='empty'else ingest({**catalog(),'application_configuration_sha256':'e'*64})
    with pytest.raises(ValueError):module.restore_state(state)
