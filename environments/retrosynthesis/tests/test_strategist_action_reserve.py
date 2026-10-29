"""Post-pilot RED gate: preserve an action round as well as final submission."""
import json

import pytest

from synthesis_route_gym.agent_accounting import AgentBudget, SharedLedger
from synthesis_route_gym.agent_runner import run_agent_scientist
from synthesis_route_gym import strategist_runtime


def resources(remaining):
    return {'remaining_model_calls':remaining, 'remaining_tool_calls':20,
            'remaining_tokens':100000, 'remaining_seconds':100}


@pytest.mark.parametrize(('remaining','finalization_reserve','expected'), [
    (2,1,False), (3,1,True), (3,2,False), (4,2,True),
])
def test_admission_reserves_action_round_plus_finalization(remaining,finalization_reserve,expected):
    budget=AgentBudget(max_model_calls=10,wall_seconds=200,
                       finalization_model_calls=finalization_reserve)
    ledger=SharedLedger(budget)
    assert strategist_runtime._admissible(ledger,resources(remaining),'bounded advice prompt') is expected


def test_no_advisor_without_action_round_while_main_can_submit(tmp_path,monkeypatch):
    (tmp_path/'config.yaml').write_text('model:\n  default: main-model\n  provider: main-provider\n')
    monkeypatch.setattr(strategist_runtime,'observer_state',lambda:{'count':0})
    monkeypatch.setattr(strategist_runtime,'observe',
        lambda state,*_: {'count':state['count']+1})
    monkeypatch.setattr(strategist_runtime,'build_context',
        lambda state,remaining:{'frontier':['CCO'],'resources':remaining} if state['count']>=2 else None)
    monkeypatch.setattr(strategist_runtime,'context_fingerprint',lambda _: 'a'*64)
    monkeypatch.setattr(strategist_runtime,'parse_plan',lambda text,_: json.loads(text))
    roles=[]
    class Backend:
        def run(self,**kwargs):
            roles.append(kwargs['role'])
            ledger=kwargs['ledger']
            request=ledger.claim_model_call()
            if kwargs['role']=='main':
                kwargs['executor']('inspect',{})
                kwargs['executor']('expand',{'smiles':'CCO'})
                final_request=ledger.claim_model_call()
                ledger.settle_request(final_request,10)
                kwargs['executor']('submit',{'route_ids':[]})
                confirmations={request:10,final_request:10}
                response='Main submitted within its preserved budget.'
            else:
                confirmations={request:10}
                response='{"next_expansion_targets":["CCO"]}'
            ledger.settle_request(request,10)
            return {'completed':True,'final_response':response,
                    'model':kwargs['profile'].model,'provider':kwargs['profile'].provider,
                    'usage':{'input_tokens':sum(confirmations.values()),'output_tokens':0,
                             'total_tokens':sum(confirmations.values()),'estimated_cost_usd':0},
                    'token_confirmations':confirmations}
    schemas=[{'name':name,'parameters':{'type':'object'}} for name in ('inspect','expand','submit')]
    result=run_agent_scientist('Preserve the action and submission rounds.',
        lambda *_: {'status':'ok','result':{}},tool_schemas=schemas,profile_home=tmp_path,
        mode='main_strategist',backend=Backend(),budget=AgentBudget(max_model_calls=3))
    assert result['completed'] and result['submission_status']=='submitted'
    assert roles==['main']
    assert result['strategist_runs']==[]
    assert result['strategist_state']['consultation']['status']=='skipped_budget'
