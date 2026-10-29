"""Public-only condition policies and evaluator-only decision scoring."""
from copy import deepcopy
import hashlib
import json
import math

import pytest

from synthesis_route_gym import condition_benchmark as benchmark


def observation(key, value):
    source_id='study:'+('1'*64)+':'+hashlib.sha256(json.dumps(key).encode()).hexdigest()[:20]
    return {'candidate_id':key, 'value':value, 'source_record_id':source_id,
            'evidence_kind':'measured_dataset_replay'}


def prediction(key, value, status='scored'):
    return {'candidate_id':key, 'prediction_id':'prediction:'+key, 'status':status,
            'value':value, 'unit':'percent', 'domain':'transfer_unknown',
            'uncertainty':'not_calibrated', 'model_version':'fixture-v1'}


def view():
    return {'schema_version':'srg-condition-view-v1','study_id':'study-one',
            'revision':1,'substrate':'CCBr','target':'CCN',
            'domain_status':'registered_measured_study',
            'measurement':{'name':'yield','unit':'percent','evidence_kind':'measured_dataset_replay'},
            'candidates':[{'candidate_id':key,'conditions':conditions}for key,conditions in [
                ('a',{'ligand':'L1','base':'B1'}),('b',{'ligand':'L2','base':'B1'}),
                ('c',{'ligand':'L1','base':'B2'}),('d',{'ligand':'L2','base':'B2'})]],
            'observations':[observation('a',20.0)],
            'predictions':[prediction('b',60.0),prediction('c',80.0),prediction('d',None,'abstained')],
            'resources':{'initial_observations':1,'new_observations_used':0,
                         'remaining_observations':2,'remaining_actions':30,'remaining_seconds':100.0},
            'submission':{'status':'not_submitted','candidate_id':None}}


@pytest.mark.parametrize('policy',['fixed_order','random','public_model_rank','gp_expected_improvement'])
def test_policies_only_select_unobserved_candidates_and_do_not_mutate(policy):
    state=view();before=deepcopy(state)
    assert benchmark.select_condition_candidate(state,policy,seed=7) in {'b','c','d'}
    assert state==before


def test_fixed_order_and_model_rank_have_deterministic_ties_and_abstention_fallback():
    state=view()
    assert benchmark.select_condition_candidate(state,'fixed_order')=='b'
    assert benchmark.select_condition_candidate(state,'public_model_rank')=='c'
    state['predictions']=[prediction('c',60.0),prediction('b',60.0)]
    assert benchmark.select_condition_candidate(state,'public_model_rank')=='b'
    state['predictions']=[prediction('d',None,'abstained')]
    assert benchmark.select_condition_candidate(state,'public_model_rank')=='b'


def test_random_reproducible_and_does_not_depend_on_observed_yield_or_predictions():
    state=view();changed=deepcopy(state)
    changed['observations'][0]['value']=99.0
    changed['predictions']=[]
    assert benchmark.select_condition_candidate(state,'random',seed=12)==benchmark.select_condition_candidate(changed,'random',seed=12)
    assert len({benchmark.select_condition_candidate(state,'random',seed=seed)for seed in range(40)})>1


@pytest.mark.parametrize('change',[lambda s:s['resources'].update(remaining_observations=0),
    lambda s:s.update(observations=[observation(c['candidate_id'],10.0)for c in s['candidates']]),
    lambda s:s.update(submission={'status':'selected','candidate_id':'a'})])
def test_stop_when_allowance_exhausted_or_pool_observed_or_submitted(change):
    state=view();change(state)
    assert benchmark.select_condition_candidate(state,'fixed_order') is None


def test_gp_acquisition_is_finite_positive_and_uses_only_observations():
    state=view();state['observations'].append(observation('b',80.0))
    scores=benchmark.gp_expected_improvement(state)
    assert {r['candidate_id']for r in scores}=={'c','d'}
    assert all(math.isfinite(r[k])for r in scores for k in ('posterior_mean','posterior_std','expected_improvement'))
    assert all(r['posterior_std']>=0 and r['expected_improvement']>=0 for r in scores)
    assert next(r for r in scores if r['candidate_id']=='d')['posterior_mean']>next(r for r in scores if r['candidate_id']=='c')['posterior_mean']
    other=deepcopy(state);other['predictions']=[prediction('c',100.0)]
    assert benchmark.gp_expected_improvement(other)==scores
    other['observations'][1]['value']=0.0
    assert benchmark.gp_expected_improvement(other)!=scores


def test_gp_empty_and_constant_observations_are_supported():
    state=view();state['observations']=[]
    assert len(benchmark.gp_expected_improvement(state))==4
    state['observations']=[observation('a',20.0),observation('b',20.0)]
    assert len(benchmark.gp_expected_improvement(state))==2


@pytest.mark.parametrize('policy',benchmark.POLICIES)
def test_interrupted_unreturned_observations_are_not_selected_again(policy):
    state=view();state['unavailable_candidate_ids']=['b','c']
    assert benchmark.select_condition_candidate(state,policy)=='d'
    state['unavailable_candidate_ids']=['b','c','d']
    assert benchmark.select_condition_candidate(state,policy)is None
    assert benchmark.gp_expected_improvement(state)==[]


def test_ambiguous_duplicate_settings_and_invalid_unavailable_ids_rejected():
    state=view();state['candidates'][1]['conditions']=dict(state['candidates'][0]['conditions'])
    with pytest.raises(ValueError):benchmark.select_condition_candidate(state,'fixed_order')
    for unavailable in (['unknown'],['a'],['b','b'],'b'):
        state=view();state['unavailable_candidate_ids']=unavailable
        with pytest.raises(ValueError):benchmark.select_condition_candidate(state,'fixed_order')


@pytest.mark.parametrize('change',[
    lambda s:s.update(private_optimum=99),
    lambda s:s['candidates'][1].update(yield_percent=99),
    lambda s:s['observations'].append(observation('unknown',10)),
    lambda s:s['observations'].append(observation('a',10)),
    lambda s:s['observations'][0].update(value=float('nan')),
    lambda s:s['observations'][0].update(value=True),
    lambda s:s['predictions'][0].update(value=101),
    lambda s:s['predictions'][0].update(candidate_id='unknown'),
    lambda s:s['candidates'][1]['conditions'].update({'yield':'90'}),
    lambda s:s['candidates'][1].update(conditions={'base':'B1'}),
    lambda s:s['resources'].update(remaining_observations=-1),
])
def test_policy_rejects_invalid_or_label_leaking_views(change):
    state=view();change(state)
    with pytest.raises(ValueError):benchmark.select_condition_candidate(state,'fixed_order')


def test_unknown_domain_policy_seed_and_policy_name_rejected():
    state=view();state['domain_status']='unrelated_chemistry'
    with pytest.raises(ValueError):benchmark.select_condition_candidate(state,'fixed_order')
    for policy,seed in [('unknown',0),('random',True),('random',1.5)]:
        with pytest.raises(ValueError):benchmark.select_condition_candidate(view(),policy,seed=seed)


class PublicOnlyEpisode:
    def __init__(self,fail=False):
        self.state=view();self.events=[];self.fail=fail
    def public_view(self):return deepcopy(self.state)
    def export(self):return {**deepcopy(self.state),'events':deepcopy(self.events),'stop_reason':None}
    def dispatch(self,name,args):
        self.events.append({'action':name,'arguments':deepcopy(args)})
        if name=='inspect':return {'status':'ok','result':self.public_view()}
        if name=='observe_condition':
            if self.fail:return {'status':'error','result':{'error_type':'FixtureFailure'}}
            key=args['candidate_id'];self.state['observations'].append(observation(key,{'b':80,'c':50,'d':90}[key]))
            self.state['resources']['new_observations_used']+=1
            self.state['resources']['remaining_observations']-=1
        elif name=='submit':
            self.state['submission']={'status':'selected'if args['candidate_id']is not None else'abstained',**args}
        return {'status':'ok','result':{'view':self.public_view()}}


def test_fixed_runner_executes_environment_queries_and_submits_best_observed():
    env=PublicOnlyEpisode();result=benchmark.run_fixed_condition_episode(env,'fixed_order',seed=3)
    assert [e['action']for e in env.events]==['inspect','observe_condition','observe_condition','submit']
    assert result['episode']['submission']['candidate_id']=='b'
    assert result['completed'] and result['error_type'] is None
    assert result['method']=='fixed_order'


def test_fixed_runner_retains_query_failure_without_repeating_forever():
    env=PublicOnlyEpisode(fail=True);result=benchmark.run_fixed_condition_episode(env,'random')
    assert not result['completed']
    assert len(env.events)==2
    assert result['episode']['submission']['status']=='not_submitted'


@pytest.mark.parametrize('policy',benchmark.POLICIES)
def test_real_condition_episode_end_to_end(policy,tmp_path):
    from synthesis_route_gym.condition_episode import ConditionEpisode
    from synthesis_route_gym.portfolio_conditions import ConditionRecord,FiniteConditionStudy
    state=view();outcomes={'a':20.0,'b':80.0,'c':50.0,'d':95.0}
    records=tuple(ConditionRecord(row['candidate_id'],tuple(sorted(row['conditions'].items())),
                                  outcomes[row['candidate_id']])for row in state['candidates'])
    study=FiniteConditionStudy(records,('a',),3,'https://example.org/data','fixture','1'*64,'CCBr')
    env=ConditionEpisode(study,study_id='study-one',target='CCN',
                         predictions=tuple(state['predictions']),store=tmp_path/'episode')
    result=benchmark.run_fixed_condition_episode(env,policy,seed=19)
    assert result['completed'],result
    assert result['episode']['resources']['new_observations_used']==2
    selected=result['episode']['submission']['candidate_id']
    assert selected in {row['candidate_id']for row in result['episode']['observations']}
    score=benchmark.score_condition_decision(spec(),outcomes,
        {key:result['episode'][key]for key in ('study_id','observations','submission')})
    summary=benchmark.summarize_condition_run(result,score,arm=policy,
        product_group='product1',scaffold_group='scaffold1',source_family='publication1')
    assert summary['submitted'] and summary['actual_tokens']==0 and summary['model_calls']==0
    assert summary['observation_reservations_used']==2


def spec():
    return {'schema_version':'srg-condition-study-v1','data_role':'development',
            'study_id':'study-one','substrate':'CCBr','target':'CCN','source_url':'https://example.org/data',
            'source_locator':'fixture','dataset_sha256':'1'*64,'observation_budget':3,
            'initial_ids':['a'],'candidates':view()['candidates'],'outcomes_sha256':'2'*64}


def decision(selected='b'):
    return {'study_id':'study-one','observations':[observation('a',20),observation('b',80),observation('c',50)],
            'submission':{'status':'selected','candidate_id':selected}}


def test_evaluator_does_not_replace_poor_submitted_choice_with_best_observed():
    result=benchmark.score_condition_decision(spec(),{'a':20,'b':80,'c':50,'d':95},decision('c'))
    assert result['best_observed_yield_percent']==80
    assert result['submitted_yield_percent']==50
    assert result['best_observed_regret_percent']==15
    assert result['submitted_regret_percent']==45
    assert result['penalized_submitted_regret_percent']==45
    assert result['trajectory_best_observed_yield_percent']==[20,80,80]
    assert result['new_observations_used']==2


@pytest.mark.parametrize('submission',[{'status':'not_submitted','candidate_id':None},
    {'status':'abstained','candidate_id':None},{'status':'selected','candidate_id':'d'},
    {'status':'selected','candidate_id':'unknown'}])
def test_missing_abstained_and_unobserved_choices_remain_explicit_failures(submission):
    choice={**decision(),'submission':submission}
    result=benchmark.score_condition_decision(spec(),{'a':20,'b':80,'c':50,'d':95},choice)
    assert result['submitted_yield_percent']is None and result['submitted_regret_percent']is None
    assert result['penalized_submitted_yield_percent']==0
    assert result['penalized_submitted_regret_percent']==95
    assert result['selection_failed']
    assert result['best_observed_regret_percent']==15


@pytest.mark.parametrize('change',[
    lambda s,d,o:s.update(data_role='sealed_final'),
    lambda s,d,o:d.update(study_id='wrong'),
    lambda s,d,o:d['observations'][1].update(value=90),
    lambda s,d,o:d['observations'][1].update(source_record_id='forged-source'),
    lambda s,d,o:s.update(dataset_sha256='2'*64),
    lambda s,d,o:d['observations'].append(observation('d',95)),
    lambda s,d,o:d.update(observations=[observation('b',80)]),
    lambda s,d,o:o.update(a=float('nan')),
    lambda s,d,o:o.pop('d'),
    lambda s,d,o:d['observations'].append(observation('a',20)),
])
def test_evaluation_rejects_tampered_identity_measurement_or_budget(change):
    public=spec();choice=decision();outcomes={'a':20,'b':80,'c':50,'d':95};change(public,choice,outcomes)
    with pytest.raises(ValueError):benchmark.score_condition_decision(public,outcomes,choice)


def score_fixture(selected='b'):
    return benchmark.score_condition_decision(spec(),{'a':20,'b':80,'c':50,'d':95},decision(selected))


def run_fixture(arm='main',tokens=100,complete=True):
    episode={**view(),'observations':decision()['observations'],'submission':decision()['submission'],
             'usage':{'actions':5,'wall_seconds':10},'events':[],'stop_reason':None}
    episode['resources'].update(new_observations_used=2,remaining_observations=0)
    return {'method':arm,'episode':episode,'agent':{'completed':complete,'conversation_completed':complete,
        'submission_status':'submitted','model':'main-model','provider':'provider',
        'ledger':{'model_calls':6,'actual_tokens':tokens,'charged_tokens':tokens,'reserved_tokens':0,
                  'unsettled_requests':0},'condition_scientist_runs':[{}]if arm!='main'else[]}}


def row(arm='main',selected='b',study_id='study-one',repeat_id=0):
    run=run_fixture(arm);run['episode']['submission']['candidate_id']=selected
    result=benchmark.summarize_condition_run(run,score_fixture(selected),arm=arm,
        product_group='product1',scaffold_group='scaffold1',source_family='publication1',repeat_id=repeat_id)
    return {**result,'study_id':study_id}


def test_summary_preserves_incomplete_conversation_and_settled_resources():
    summary=benchmark.summarize_condition_run(run_fixture(complete=False),score_fixture(),arm='main',
        product_group='p1',scaffold_group='g1',source_family='source1')
    assert summary['submitted'] and not summary['conversation_completed']
    assert summary['actual_tokens']==100 and summary['charged_tokens']==100
    assert summary['initial_observations']==1 and summary['new_observations_used']==2


def test_summary_rejects_changed_observation_values_after_scoring():
    run=run_fixture();run['episode']['observations'][1]['value']=99
    with pytest.raises(ValueError,match='observation'):
        benchmark.summarize_condition_run(run,score_fixture(),arm='main',
            product_group='p1',scaffold_group='g1',source_family='source1')


@pytest.mark.parametrize('field',['target','substrate'])
def test_summary_rejects_changed_reaction_identity(field):
    run=run_fixture();run['episode'][field]='CCO'
    with pytest.raises(ValueError,match='reaction'):
        benchmark.summarize_condition_run(run,score_fixture(),arm='main',
            product_group='p1',scaffold_group='g1',source_family='source1')


def test_comparison_matches_pools_and_counts_groups_without_promotion():
    rows=[row('main',selected='c'),row('main_condition_scientist',selected='b')]
    summary=benchmark.summarize_condition_comparison(rows)
    assert summary['paired_submitted_regret']['wins']==1
    assert summary['paired_submitted_regret']['mean_gain_percent']==30
    assert summary['source_family_count']==1 and summary['product_group_count']==1
    assert summary['promotion_eligible']is False and summary['default_changed']is False


@pytest.mark.parametrize('field',['candidate_pool_sha256','initial_ids_sha256','observation_budget',
                                'prediction_table_sha256','model','provider'])
def test_comparison_rejects_mismatched_resources_inputs_and_models(field):
    rows=[row('main'),row('main_condition_scientist')]
    rows[1][field]='changed'if field!='observation_budget'else 10
    with pytest.raises(ValueError):benchmark.summarize_condition_comparison(rows)


def test_comparison_retains_failures_repeats_and_rejects_missing_pairs():
    rows=[row('main'),row('main_condition_scientist')]
    rows += [row('main',repeat_id=1),row('main_condition_scientist',repeat_id=1)]
    result=benchmark.summarize_condition_comparison(rows)
    assert result['paired_run_count']==2 and result['study_count']==1
    with pytest.raises(ValueError):benchmark.summarize_condition_comparison(rows[:1])
    with pytest.raises(ValueError):benchmark.summarize_condition_comparison(rows+[rows[0]])
