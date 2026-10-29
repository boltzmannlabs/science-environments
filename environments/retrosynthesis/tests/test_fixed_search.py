"""Behavioral regressions for the bounded fixed-search policy (synthetic chemistry)."""
from copy import deepcopy
import pytest
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.schemas import Budget, Constraints, InventoryItem, Task
from synthesis_route_gym.fixed_search import run_best_first_workflow


def task(*, target='CCOC(C)=O', stock=('CCO', 'CC(=O)O'), **kwargs):
    return Task(task_id='fixed-search-test', target=target,
                inventory=tuple(InventoryItem(smiles=s) for s in stock), **kwargs)


def backend(choices, calls=None):
    def expand(smiles, top_k):
        if calls is not None:
            calls.append(smiles)
        return {'status':'ok','predictions':[{'product':smiles,'reactants':r,'score':0.8,
            'source':{'tool':'fixture','version':'1'}} for r in choices.get(smiles,[])][:top_k]}
    return expand


def accepted(result):
    event = next(e for e in reversed(result['episode']['events']) if e['action']=='submit')
    return event['result']['accepted_route_ids']


def run(choices, **kwargs):
    return run_best_first_workflow(SynthesisRouteEnv(task(**kwargs), expand=backend(choices)))


def test_three_step_search_resolves_all_precursors():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']], 'CCO':[['C=C','O']],
                'CC(=O)O':[['CC=O','O']]}, stock=('C=C','O','CC=O'))
    assert len(accepted(result))==1
    assert len(result['episode']['routes'][0]['steps'])==3
    assert result['episode']['usage']['expansions']==3
    assert result['episode']['assessments'][0]['solved'] is False


def test_shared_producer_allowed_when_second_branch_reuses_earlier_intermediate():
    result=run({'CCCC':[['CC','CCC']], 'CC':[['C']], 'CCC':[['CC','C']]},
               target='CCCC',stock=('C',))
    assert len(accepted(result))==1
    assert len(result['episode']['routes'][0]['steps'])==3
    assert result['episode']['usage']['expansions']==3


def test_cycle_is_rejected_even_when_it_points_to_previously_expanded_branch():
    result=run({'CCCC':[['CC','CCC']], 'CC':[['CCC']], 'CCC':[['CC']]},
               target='CCCC',stock=('C',))
    assert accepted(result)==[]
    assert result['metrics']['cycle_prunes']>=1


def test_invalid_alternative_does_not_fill_success_quota():
    result=run({'CCOC(C)=O':[['CC'],['CCO','CC(=O)O']]},
               stock=('CC','CCO','CC(=O)O'), budget=Budget(top_k=1))
    assert len(accepted(result))==1
    assert all(a['graph_valid'] for a in result['episode']['assessments'])
    assert result['metrics']['invalid_prunes']>=1


def test_missing_branch_cannot_be_submitted():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},stock=('CCO',))
    assert accepted(result)==[]
    assert result['episode']['usage']['expansions']==2


def test_excluded_material_and_zero_stock_do_not_pass():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},
               constraints=Constraints(forbidden_smiles=('CCO',)))
    assert accepted(result)==[]
    t=task().model_copy(update={'inventory':(InventoryItem(smiles='CCO',available_mmol=0),
                                            InventoryItem(smiles='CC(=O)O'))})
    result=run_best_first_workflow(SynthesisRouteEnv(t,expand=backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})))
    assert accepted(result)==[]


def test_requested_quantities_remain_unknown_and_cannot_be_accepted():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},target_amount_mmol=1)
    assert accepted(result)==[]
    assert result['metrics']['rejected_candidates']==1


def test_duplicates_do_not_consume_state_capacity_or_quota():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']]*5},budget=Budget(top_k=3))
    assert len(accepted(result))==1
    assert result['search_states']==2
    assert result['metrics']['duplicate_states']==4


def test_action_reservation_protects_submission():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']]},budget=Budget(max_actions=3,top_k=1))
    assert len(accepted(result))==1
    assert result['episode']['usage']['actions']==3
    assert result['episode']['terminated'] and not result['episode']['truncated']
    result=run({},budget=Budget(max_actions=1))
    assert accepted(result)==[]
    assert result['episode']['usage']['expansions']==0


def test_expansion_budget_still_allows_submission_of_completed_frontier():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O'],['CCO','O','CC']]},
               stock=('CCO','CC(=O)O'), budget=Budget(max_expansions=1))
    assert len(accepted(result))==1
    assert result['episode']['usage']['expansions']==1
    assert result['stop_reason']=='expansion_budget'


def test_backend_failure_is_reported_and_not_cached():
    result=run_best_first_workflow(SynthesisRouteEnv(task(),expand=lambda *_: {'status':'error'}))
    assert accepted(result)==[]
    assert result['metrics']['failed_expansions']==1
    assert not result['expansion_cache']['entries']


def test_cache_replay_is_explicit_pinned_and_input_is_not_mutated():
    calls=[]
    callback=backend({'CCOC(C)=O':[['CCO','CC(=O)O']]},calls)
    first=run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback))
    cache=deepcopy(first['expansion_cache'])
    second=run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback),
                                  expansion_cache=cache,cache_mode='shared_precomputed')
    assert len(calls)==1
    assert len(accepted(second))==1
    assert second['metrics']['precomputed_cache_hits']==1
    assert second['episode']['usage']['expansions']==0
    assert second['cache_accounting']['precomputation_backend_calls']==1
    assert cache==first['expansion_cache']
    with pytest.raises(ValueError,match='cache'):
        run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback),expansion_cache=cache)


def test_cache_model_stock_and_topk_changes_do_not_hit():
    callback=backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})
    first=run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback))
    variants=[(task(stock=('CCO','CC(=O)O','C')),{},10),
              (task(),{'backend_versions':{'expand':{'model_version':'changed'}}},10),
              (task(),{},5)]
    for t,options,k in variants:
        result=run_best_first_workflow(SynthesisRouteEnv(t,expand=callback,**options),
            expansion_cache=first['expansion_cache'],cache_mode='shared_precomputed', expansion_top_k=k)
        assert result['metrics']['precomputed_cache_hits']==0
        assert result['episode']['usage']['expansions']==1


def test_tampered_cache_output_is_rejected():
    callback=backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})
    first=run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback))
    cache=deepcopy(first['expansion_cache'])
    key=next(iter(cache['entries']))
    cache['entries'][key]['data']['predictions'][0]['evidence_status']='measured'
    with pytest.raises(ValueError,match='cache'):
        run_best_first_workflow(SynthesisRouteEnv(task(),expand=callback),
            expansion_cache=cache,cache_mode='shared_precomputed')


def test_stock_target_is_acquisition_not_synthetic_success():
    result=run({},target='CCO',stock=('CCO',))
    assert accepted(result)==[]
    assert result['metrics']['rejected_candidates']==1


@pytest.mark.parametrize('name,value',[('expansion_top_k',True),('expansion_top_k',0),
    ('max_frontier_states',0),('max_frontier_states',1.5),('cache_mode','unknown'),('cache_mode',{})])
def test_invalid_limits_fail_before_actions(name,value):
    env=SynthesisRouteEnv(task(),expand=backend({}))
    with pytest.raises(ValueError):
        run_best_first_workflow(env,**{name:value})
    assert env.inspect()['usage']['actions']==0


def test_duplicate_reactants_preserve_multiplicity_in_submitted_route():
    result=run({'CCCC':[['CC','CC']]},target='CCCC',stock=('CC',))
    assert len(accepted(result))==1
    step=result['episode']['routes'][0]['steps'][0]
    assert [x['smiles'] for x in step['reactants']]==['CC','CC']


def test_shared_expansion_is_reused_between_distinct_routes():
    result=run({'CCCC':[['CC','O'],['CC','CO']], 'CC':[['C']]},
               target='CCCC',stock=('C','O','CO'))
    assert len(accepted(result))==2
    assert result['episode']['usage']['expansions']==2
    assert result['metrics']['cache_hits']==1
    assert result['metrics']['precomputed_cache_hits']==0


def test_forbidden_smarts_and_complete_conditions_prune_predictions():
    choices={'CCOC(C)=O':[['CCO','CC(=O)O']]}
    for constraints in (Constraints(forbidden_smarts=('[OX2H]',)),
                        Constraints(require_complete_conditions=True)):
        result=run(choices,constraints=constraints)
        assert accepted(result)==[]
        assert result['metrics']['invalid_prunes']==1


def test_finite_stock_does_not_imply_undeclared_stoichiometry():
    t=task(target_amount_mmol=5).model_copy(update={'inventory':(
        InventoryItem(smiles='CCO',available_mmol=0.1),
        InventoryItem(smiles='CC(=O)O',available_mmol=0.1))})
    result=run_best_first_workflow(SynthesisRouteEnv(t,expand=backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})))
    assert accepted(result)==[]
    assert result['episode']['assessments'][0]['quantity_status']=='unknown'


def test_insufficient_stock_target_is_not_submitted():
    t=task(target='CCO',stock=('CCO',),target_amount_mmol=5).model_copy(update={
        'inventory':(InventoryItem(smiles='CCO',available_mmol=0.1),)})
    result=run_best_first_workflow(SynthesisRouteEnv(t,expand=backend({})))
    assert accepted(result)==[]
    assert result['episode']['assessments'][0]['quantity_status']=='insufficient'


def test_frontier_capacity_and_visit_budget_are_bounded():
    choices={'CCCC':[['C'],['CC'],['CCC'],['C=C']]}
    result=run_best_first_workflow(SynthesisRouteEnv(
        task(target='CCCC',stock=('C','CC','CCC','C=C')),expand=backend(choices)),
        max_frontier_states=2)
    assert result['search_states']==2
    assert result['metrics']['frontier_capacity_prunes']==2
    assert result['stop_reason']=='frontier_state_budget'
    assert len(accepted(result))==1


def test_step_limit_prunes_incomplete_routes():
    result=run({'CCOC(C)=O':[['CCO','CC(=O)O']], 'CCO':[['C=C','O']]},
        stock=('C=C','O','CC(=O)O'),constraints=Constraints(max_steps=1))
    assert accepted(result)==[]
    assert result['metrics']['step_limit_prunes']==1


def test_ties_are_stable_and_independent_of_prediction_order():
    choices={'CCCC':[['CCC'],['CC'],['C']]}
    first=run(choices,target='CCCC',stock=('C','CC','CCC'))
    second=run({'CCCC':list(reversed(choices['CCCC']))},target='CCCC',stock=('C','CC','CCC'))
    assert accepted(first)==accepted(second)


def test_closed_episode_does_not_admit_work():
    env=SynthesisRouteEnv(task(),expand=backend({}))
    env.dispatch('submit',{'route_ids':[]})
    before=env.inspect()['usage']['actions']
    result=run_best_first_workflow(env)
    assert result['stop_reason']=='episode_closed'
    assert result['episode']['usage']['actions']==before


def test_wall_reserve_stops_new_work_but_inflight_deadline_is_not_a_submission():
    now=[0.0]
    def callback(smiles, top_k):
        now[0]=99.0
        return backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})(smiles,top_k)
    env=SynthesisRouteEnv(task(budget=Budget(max_wall_seconds=100)),expand=callback,
                          clock=lambda:now[0],wall_clock=lambda:now[0])
    result=run_best_first_workflow(env)
    assert result['stop_reason']=='wall_reserve'
    assert accepted(result)==[]
    assert result['episode']['terminated']
    now[0]=0.0
    def late(smiles,top_k):
        now[0]=101.0
        return backend({'CCOC(C)=O':[['CCO','CC(=O)O']]})(smiles,top_k)
    result=run_best_first_workflow(SynthesisRouteEnv(
        task(budget=Budget(max_wall_seconds=100)),expand=late,
        clock=lambda:now[0],wall_clock=lambda:now[0]))
    assert result['episode']['truncated']
    assert not result['episode']['submitted_route_ids']
    assert not result['episode']['routes']
    assert result['stop_reason']=='episode_closed'
    assert result['metrics']['generated_states']==0
    assert 'admission' in result['finalization_policy']


@pytest.mark.parametrize('reserve',[True,-1,float('inf'),1800])
def test_invalid_wall_reserve_rejected(reserve):
    with pytest.raises(ValueError,match='reserve'):
        run_best_first_workflow(SynthesisRouteEnv(task()),finalization_reserve_seconds=reserve)


@pytest.mark.parametrize('mutate',[
    lambda c: c.update({'backend_calls':-1}),
    lambda c: c.update({'elapsed_seconds':float('nan')}),
    lambda c: c.update({'entries':[]}),
    lambda c: c.update({'unexpected':1}),
])
def test_malformed_cache_rejected(mutate):
    cache={'schema_version':'srg-expansion-cache-v1','entries':{},'backend_calls':0,'elapsed_seconds':0.0}
    mutate(cache)
    with pytest.raises(ValueError,match='cache'):
        run_best_first_workflow(SynthesisRouteEnv(task()),expansion_cache=cache,cache_mode='shared_precomputed')


def test_wide_search_bounds_dedup_tracking_as_well_as_frontier():
    choices={'C'*10:[[('C'*n)] for n in range(2,10)]}
    choices.update({'C'*n:[['C'*m] for m in range(2,10) if m!=n] for n in range(2,10)})
    result=run_best_first_workflow(SynthesisRouteEnv(
        task(target='C'*10,stock=('C',),constraints=Constraints(max_steps=8)),expand=backend(choices)),
        max_frontier_states=5)
    assert result['search_states']<=5
    assert result['metrics']['peak_frontier_states']<=5
    assert result['metrics']['peak_dedup_signatures']<=10
    assert result['metrics']['frontier_capacity_prunes']>0
