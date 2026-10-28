"""Native Syntheseus tests use synthetic chemistry, never experimental truth."""
import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Task, InventoryItem, Budget, Constraints
from synthesis_route_gym.synthchem_search import run_synthchem_workflow

def run(choices, *, algorithm='portfolio',target='CCOC(C)=O',stock=('CCO','CC(=O)O'),**kwargs):
    kwargs = {'budget':Budget(max_expansions=20,max_wall_seconds=30),**kwargs}
    task=Task(task_id='native-search-fixture',target=target,
        inventory=tuple(InventoryItem(smiles=s) for s in stock),**kwargs)
    def expand(s,k):
        return {'status':'ok','predictions':[{'product':s,'reactants':r,'score':.5,
            'source':{'tool':'fixture','version':'1'}} for r in choices.get(s,[])][:k]}
    return run_synthchem_workflow(SynthesisRouteEnv(task,expand=expand),algorithm=algorithm)

@pytest.mark.parametrize('algorithm',['astar','mcts','portfolio'])
def test_native_search_builds_three_steps_and_keeps_evidence_predicted(algorithm):
    r=run({'CCOC(C)=O':[['CCO','CC(=O)O']],'CCO':[['C=C','O']],
           'CC(=O)O':[['CC=O','O']]},stock=('C=C','O','CC=O'),algorithm=algorithm)
    assert len(r['accepted_route_ids'])==1 and len(r['episode']['routes'][0]['steps'])==3
    assert r['episode']['assessments'][0]['solved'] is False
    assert r['submission_status']=='submitted'
    assert all(s['native_algorithm'] in ('RetroStarSearch','MolSetMCTS') for s in r['searches'])

def test_portfolio_shares_queries_and_merges_duplicate_routes():
    r=run({'CCOC(C)=O':[['CCO','CC(=O)O']]})
    assert [s['algorithm'] for s in r['searches']]==['astar','mcts']
    assert r['proposal_pool']['backend_calls']==1 and r['proposal_pool']['cache_hits']>=1
    assert len(r['accepted_route_ids'])==1
    assert r['route_provenance'][r['accepted_route_ids'][0]]==['astar','mcts']

@pytest.mark.parametrize('algorithm',['astar','mcts'])
def test_missing_branch_and_cycles_do_not_become_complete_routes(algorithm):
    r=run({'CCCC':[['CC','CCC']],'CC':[['CCC']],'CCC':[['CC']]},target='CCCC',stock=('C',),algorithm=algorithm)
    assert r['accepted_route_ids']==[]

@pytest.mark.parametrize('algorithm',['astar','mcts'])
def test_preserves_duplicate_salt_inputs_and_rejects_component_stock_substitution(algorithm):
    choices={'CCCC':[['CC','CC','[Cl-].[Na+]']]}
    r=run(choices,target='CCCC',stock=('CC','[Cl-].[Na+]'),algorithm=algorithm)
    assert len(r['accepted_route_ids'])==1
    inputs=r['episode']['routes'][0]['steps'][0]['reactants']
    assert sum(v['smiles']=='CC' for v in inputs)==2
    assert any(v['smiles']=='[Cl-].[Na+]' for v in inputs)
    assert not run(choices,target='CCCC',stock=('CC','[Cl-]','[Na+]'),algorithm=algorithm)['accepted_route_ids']

def test_graph_solution_does_not_override_requested_quantities():
    r=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},target_amount_mmol=1)
    assert any(p['graph_has_solution'] for p in r['searches'])
    assert r['accepted_route_ids']==[] and r['rejected_routes']

def test_step_limit_and_material_exclusion_remain_authoritative():
    choices={'CCOC(C)=O':[['CCO','CC(=O)O']],'CCO':[['C=C','O']]}
    assert not run(choices,stock=('C=C','O','CC(=O)O'),constraints=Constraints(max_steps=1))['accepted_route_ids']
    assert not run(choices,constraints=Constraints(forbidden_smiles=('CCO',)))['accepted_route_ids']

def test_target_in_stock_is_not_counted_as_synthesis():
    r=run({},stock=('CCOC(C)=O',))
    assert not r['accepted_route_ids'] and r['episode']['usage']['expansions']==0
    assert r['stop_reason']=='target_in_stock_no_synthesis'

def test_action_and_expansion_caps_and_empty_submission():
    r=run({},budget=Budget(max_actions=1,max_expansions=1))
    assert r['episode']['usage']['actions']==1 and r['submission_status']=='submitted'
    assert r['episode']['usage']['expansions']==0
    r=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},budget=Budget(max_expansions=1))
    assert r['episode']['usage']['expansions']==1

@pytest.mark.parametrize('options',[{'algorithm':'bad'},{'expansion_top_k':True},
    {'expansion_top_k':0},{'max_graph_nodes':False},{'max_graph_nodes':0},
    {'finalization_reserve_seconds':float('nan')},{'finalization_reserve_seconds':True}])
def test_invalid_search_configuration_fails_before_expansion(options):
    e=SynthesisRouteEnv(Task(task_id='bad',target='CC',inventory=()))
    with pytest.raises(ValueError): run_synthchem_workflow(e,**options)
    assert e.export()['usage']['actions']==0

def test_complete_conditions_requirement_is_not_silently_bypassed():
    r=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},constraints=Constraints(require_complete_conditions=True))
    assert not r['accepted_route_ids']


def test_found_route_has_reserved_registration_and_submission_actions():
    r=run({'CCCC':[['CC','CC'],['CCC','C']]},target='CCCC',stock=('CC',),
          budget=Budget(max_actions=3,max_expansions=20),algorithm='astar')
    assert r['accepted_route_ids']
    assert [e['action'] for e in r['episode']['events']]==['expand','propose_route','submit']


@pytest.mark.parametrize('algorithm',['astar','mcts','portfolio'])
def test_non_greedy_alternative_and_convergent_shared_intermediate(algorithm):
    r=run({'CCCC':[['CCCCC'],['CC','CCC']],'CC':[['C']],'CCC':[['CC','C']]},
          target='CCCC',stock=('C',),algorithm=algorithm,budget=Budget(max_expansions=20,max_wall_seconds=30))
    assert r['accepted_route_ids']
    route=r['episode']['routes'][0]
    assert len(route['steps'])==len({s['product'] for s in route['steps']})==3


@pytest.mark.parametrize('algorithm',['astar','mcts','portfolio'])
@pytest.mark.parametrize('limit',[2,3])
def test_native_graph_node_limit_is_a_hard_cap(algorithm,limit):
    t=Task(task_id='graph-cap',target='CCCC',inventory=(InventoryItem(smiles='C'),),
           budget=Budget(max_expansions=4,max_wall_seconds=10))
    def many(s,k):
        return {'status':'ok','predictions':[{'product':s,'reactants':r,
            'source':{'tool':'fixture','version':'1'}} for r in [['C','C','C','C'],['CC','CC'],['CCC','C']]]}
    r=run_synthchem_workflow(SynthesisRouteEnv(t,expand=many),algorithm=algorithm,max_graph_nodes=limit)
    assert all(p['graph_nodes']<=limit for p in r['searches'] if p['status']=='completed')


def test_failed_astar_expansion_can_be_retried_by_mcts():
    calls=[]
    t=Task(task_id='retry',target='CC',inventory=(InventoryItem(smiles='C'),),
           budget=Budget(max_expansions=4,max_wall_seconds=10))
    def flaky(s,k):
        calls.append(s)
        if len(calls)==1: raise RuntimeError('fixture failure')
        return {'status':'ok','predictions':[{'product':s,'reactants':['C','C'],
            'source':{'tool':'fixture','version':'1'}}]}
    r=run_synthchem_workflow(SynthesisRouteEnv(t,expand=flaky))
    assert r['accepted_route_ids'] and len(calls)==2
    assert r['proposal_pool']['failed_expansions']==1


def test_closed_episode_is_reported_without_false_submission():
    t=Task(task_id='closed',target='CC',inventory=())
    e=SynthesisRouteEnv(t); e.dispatch('submit',{'route_ids':[]})
    r=run_synthchem_workflow(e)
    assert r['submission_status']=='not_submitted_episode_closed'
    assert r['episode']['usage']['actions']==1


def test_zero_step_constraint_returns_empty_submission_without_expansion():
    r=run({},constraints=Constraints(max_steps=0))
    assert r['stop_reason']=='step_limit' and r['submission_status']=='submitted'
    assert r['episode']['usage']['expansions']==0


def test_missing_native_dependency_is_explicit_and_does_not_fallback(monkeypatch):
    import builtins
    from synthesis_route_gym.synthchem_native import require_native
    original=builtins.__import__
    def unavailable(name,*args,**kwargs):
        if name.startswith('syntheseus'): raise ImportError('fixture dependency unavailable')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',unavailable)
    with pytest.raises(RuntimeError,match='unavailable'): require_native()


def test_unvalidated_native_version_is_rejected(monkeypatch):
    import synthesis_route_gym.synthchem_native as native
    monkeypatch.setattr(native,'version',lambda name:'999')
    with pytest.raises(RuntimeError,match='validated'): native.require_native()


def test_oversized_extracted_route_is_rejected_without_losing_other_candidates():
    from synthesis_route_gym.synthchem_search import _collect
    from synthesis_route_gym.planning import _step
    e=SynthesisRouteEnv(Task(task_id='oversized',target='CC',inventory=(InventoryItem(smiles='C'),)))
    step=_step({'product':'CC','reactants':['C','C'],'source':{'tool':'fixture','version':'1'}})
    candidates,rejected=_collect(e,[{'steps':tuple([step]*101),'review_penalty':0},
        {'steps':(step,),'review_penalty':0}],'astar',{})
    assert len(candidates)==1 and rejected[0]['reason']=='invalid_route_contract'
