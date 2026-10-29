"""Public-input, budget and failure behavior for the SynthChem proposal adapter."""
from types import SimpleNamespace
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task, InventoryItem, Budget
from synthesis_route_gym.synthchem_pool import EnvironmentProposalPool

def env(expand=None, **changes):
    task=Task(task_id='pool-fixture',target='CCO',inventory=(InventoryItem(smiles='CC'),),**changes)
    return SynthesisRouteEnv(task,expand=expand)

def good(s,k):
    return {'status':'ok','predictions':[{'product':s,'reactants':['CC','O'],
        'score':.5,'source':{'tool':'fixture','version':'1'}}]}

def test_shared_pool_hits_do_not_charge_or_expose_mutable_cache():
    e=env(good); p=EnvironmentProposalPool(e,10,100,1.0)
    first=p.expand('CCO'); first[0]['reactants'].append('N')
    assert p.expand('OCC')[0]['reactants']==['CC','O']
    assert e.export()['usage']['expansions']==1
    assert p.manifest()['cache_hits']==p.manifest()['backend_calls']==1

def test_failures_are_retained_and_never_cached_as_empty_chemistry():
    calls=[]
    def fail_then_good(s,k):
        calls.append(s)
        if len(calls)==1: raise RuntimeError('failed backend')
        return good(s,k)
    p=EnvironmentProposalPool(env(fail_then_good),10,100,1.0)
    assert p.expand('CCO')==[]
    assert p.expand('CCO')
    assert len(calls)==2 and p.manifest()['failed_expansions']==1

def test_phase_and_global_quotas_preserve_submission_action():
    e=env(good,budget=Budget(max_actions=4,max_expansions=2)); p=EnvironmentProposalPool(e,10,100,1.0)
    p.set_phase(1,p.deadline)
    assert p.expand('CCO') and not p.expand('CCC')
    p.set_phase(2,p.deadline); p.expand('CCC')
    assert e.export()['usage']['actions']==2
    assert not p.expand('CCCC')
    assert e.dispatch('submit',{'route_ids':[]})['status']=='ok'

def test_structural_rejections_do_not_admit_noops_or_missing_elements():
    def bad(s,k):
        return {'status':'ok','predictions':[{'product':s,'reactants':r,'source':{'tool':'fixture','version':'1'}}
            for r in [[s],['CC'],['CC','O']]]}
    p=EnvironmentProposalPool(env(bad),10,100,1.0)
    assert len(p.expand('CCO'))==1
    assert p.manifest()['rejected_predictions']==2

def test_inventory_salts_and_reactant_multiplicity_are_preserved():
    def salt(s,k):
        return {'status':'ok','predictions':[{'product':s,'reactants':['CC','CC','[Cl-].[Na+]','O'],
            'source':{'tool':'fixture','version':'1'}}]}
    row=EnvironmentProposalPool(env(salt),10,100,1.0).expand('CCO')[0]
    assert row['reactants'].count('CC')==2 and '[Cl-].[Na+]' in row['reactants']

def test_cache_capacity_does_not_cache_failed_admission():
    p=EnvironmentProposalPool(env(good),10,1,1.0)
    p.expand('CCO'); p.expand('CCCO'); p.expand('CCCO')
    assert p.manifest()['cached_products']==1 and p.manifest()['cache_capacity_skips']==2

def test_expired_phase_does_not_dispatch_backend():
    e=env(good); p=EnvironmentProposalPool(e,10,100,1.0); p.set_phase(10,0.0)
    assert p.expand('CCO')==[] and e.export()['usage']['expansions']==0

def test_successful_empty_model_response_can_be_cached():
    p=EnvironmentProposalPool(env(lambda s,k:{'status':'ok','predictions':[]}),10,100,1.0)
    assert p.expand('CCO')==p.expand('CCO')==[]
    assert p.manifest()['cache_hits']==1


def _with_agent_rows(environment, proposals):
    return SimpleNamespace(
        proposal_bank=proposals,
        task=environment.task,
        search_status=environment.search_status,
        expansion_cache_identity=environment.expansion_cache_identity,
        dispatch=environment.dispatch,
    )


def _agent_row(product, reactants):
    return {'product': product, 'reactants': reactants,
            'source': {'tool': 'submitted_hypothesis', 'version': 'host-registered-v1'}}


def test_agent_only_pool_uses_registered_hypotheses_without_model_calls():
    environment = env()
    wrapped = _with_agent_rows(environment, {'CCO': [_agent_row('CCO', ['CC', 'O'])]})
    pool = EnvironmentProposalPool(wrapped, 2, 100, 1.0, proposal_mode='agent_only')
    assert pool.expand('CCO')[0]['source']['tool'] == 'submitted_hypothesis'
    assert environment.export()['usage']['expansions'] == 0
    assert pool.manifest()['backend_calls'] == 0


def test_hybrid_pool_keeps_both_sources_and_deduplicates_same_reaction():
    environment = env(good)
    proposals = {'CCO': [_agent_row('CCO', ['C', 'CO']),
                         _agent_row('CCO', ['CC', 'O'])]}
    wrapped = _with_agent_rows(environment, proposals)
    pool = EnvironmentProposalPool(wrapped, 2, 100, 1.0, proposal_mode='hybrid')
    rows = pool.expand('CCO')
    assert len(rows) == 2
    assert {row['source']['tool'] for row in rows} == {'expand', 'submitted_hypothesis'}
    assert pool.manifest()['backend_calls'] == 1
    assert pool.manifest()['agent_proposals_used'] == 1


def test_agent_fallback_uses_model_when_available_and_agent_when_empty():
    proposals = {'CCO': [_agent_row('CCO', ['C', 'CO'])]}
    model = EnvironmentProposalPool(_with_agent_rows(env(good), proposals), 2, 100, 1.0,
                                    proposal_mode='agent_fallback')
    assert {row['source']['tool'] for row in model.expand('CCO')} == {'expand'}
    no_model = EnvironmentProposalPool(_with_agent_rows(env(), proposals), 2, 100, 1.0,
                                       proposal_mode='agent_fallback')
    assert {row['source']['tool'] for row in no_model.expand('CCO')} == {'submitted_hypothesis'}
    assert no_model.manifest()['unresolved_products'] == []


def test_pool_reports_unresolved_products_for_main_agent_revision():
    pool = EnvironmentProposalPool(_with_agent_rows(env(), {}), 2, 100, 1.0,
                                   proposal_mode='hybrid')
    assert pool.expand('CCO') == []
    assert pool.manifest()['unresolved_products'] == ['CCO']


def test_historical_model_result_refreshes_for_wider_request_if_budget_allows():
    environment = env(good, budget=Budget(max_actions=8, max_expansions=2))
    first = environment.dispatch('expand', {'smiles': 'CCO', 'top_k': 1})
    wrapped = _with_agent_rows(environment, {})
    wrapped.model_bank = {'CCO': {'top_k': 1, 'predictions': first['result']['predictions']}}
    pool = EnvironmentProposalPool(wrapped, 2, 100, 1.0)
    assert pool.expand('CCO')
    assert pool.manifest()['backend_calls'] == 1
    assert environment.export()['usage']['expansions'] == 2


def test_historical_model_result_survives_exhausted_backend_allowance():
    environment = env(good, budget=Budget(max_actions=8, max_expansions=1))
    first = environment.dispatch('expand', {'smiles': 'CCO', 'top_k': 1})
    wrapped = _with_agent_rows(environment, {})
    wrapped.model_bank = {'CCO': {'top_k': 1, 'predictions': first['result']['predictions']}}
    pool = EnvironmentProposalPool(wrapped, 2, 100, 1.0)
    assert pool.expand('CCO')
    assert pool.manifest()['backend_calls'] == 0
    assert pool.manifest()['historical_model_reuses'] == 1
    assert environment.export()['usage']['expansions'] == 1
