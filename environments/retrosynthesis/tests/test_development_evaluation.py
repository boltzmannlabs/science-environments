"""Development ranking retains failures and matched inventory siblings."""
import pytest
from synthesis_route_gym.development_evaluation import summarize_stage


def row(arm,task,*,recovered=False,accepted=0,expansions=2,status='completed'):
    return {'arm':arm,'task_id':task,'group_id':task.split('-')[0],
        'inventory_compliant_reference_recovered':recovered,
        'accepted_routes':accepted,'expansions':expansions,'attempt_status':status,
        'submitted':True,'reference_recovered':recovered,'elapsed_seconds':1.,
        'actual_tokens':0,'unsettled_requests':0}


def test_fixed_choice_uses_recovery_then_inventory_acceptance_then_work():
    data=[row(a,t) for a in ('best_first','breadth_first','synthchem_portfolio') for t in ('g-full','g-limited')]
    data[0]={**data[0],'inventory_compliant_reference_recovered':True,'reference_recovered':True}
    result=summarize_stage(data)
    assert result['selected_fixed']=='best_first'
    assert result['scientific_improvement_established'] is False
    assert result['target_groups']==1
    data=[{**item,'inventory_compliant_reference_recovered':False} for item in data]
    data[2]={**data[2],'accepted_routes':1}
    assert summarize_stage(data)['selected_fixed']=='breadth_first'


def test_all_zero_and_failed_trials_stay_in_denominator():
    data=[row(a,'g-full',expansions=2,status='failed') for a in ('best_first','breadth_first')]
    result=summarize_stage(data)
    assert result['selected_fixed']=='best_first'
    assert result['all_zero_reference_recovery']
    assert result['arms']['best_first']['attempted']==1
    assert result['arms']['best_first']['failed_or_incomplete']==1


def test_unmatched_trials_and_duplicate_runs_are_rejected():
    with pytest.raises(ValueError):
        summarize_stage([row('best_first','a'),row('breadth_first','b')])
    with pytest.raises(ValueError):
        summarize_stage([row('best_first','a'),row('best_first','a')])


def test_scoring_requires_full_matrix_before_private_access(tmp_path):
    from synthesis_route_gym.development_evaluation import score_stage
    from synthesis_route_gym.development_runner import digest
    from test_development_runner import fixture_plan
    plan,freeze,_=fixture_plan(tmp_path)
    with pytest.raises(ValueError,match='commit'):
        score_stage(plan,freeze,tmp_path/'missing',expected_freeze_sha256=digest(freeze),
            public_dir=tmp_path,private_dir=tmp_path,expected_public='a'*64,expected_private='b'*64,
            selection={'groups':[]},scorer=lambda *a,**k:pytest.fail('private scoring started'))


def test_scoring_checks_receipts_and_reports_empty_submission(tmp_path):
    from synthesis_route_gym.development_evaluation import score_stage
    from synthesis_route_gym import development_runner as runner
    from test_development_runner import fixture_plan,executor
    plan,freeze,_=fixture_plan(tmp_path)
    out=tmp_path/'runs'
    runner.run_plan(plan,freeze,out,executor=executor)
    calls=[]
    def scorer(*args,**kwargs):
        calls.append(args)
        return {'task_id':'fixture','partition':'development','decision_sha256':args[3],
            'reference_match_at_k':False,'inventory_compliant_reference_recovery':{'at_k':False},
            'route_checks':[]}
    arguments={'expected_freeze_sha256':runner.digest(freeze),'public_dir':tmp_path,
        'private_dir':tmp_path,'expected_public':'a'*64,'expected_private':'b'*64,
        'selection':{'groups':[{'group_id':'g','task_ids':['fixture']}]},'scorer':scorer}
    report=score_stage(plan,freeze,out,**arguments)
    assert len(calls)==1
    assert report['by_regime']['budgeted']['selected_fixed']=='breadth_first'
    assert report['rows'][0]['submitted']
    assert not report['rows'][0]['reference_recovered']
    decision=next(out.glob('*/decision.json'))
    decision.write_text('{}')
    with pytest.raises(ValueError,match='integrity'):
        score_stage(plan,freeze,out,**arguments)


def test_missing_submission_keeps_unknown_usage_and_reads_no_answer(tmp_path):
    from synthesis_route_gym.development_evaluation import score_stage
    from synthesis_route_gym import development_runner as runner
    from synthesis_route_gym.environment import SynthesisRouteEnv
    from test_development_runner import fixture_plan
    plan,freeze,_=fixture_plan(tmp_path,arms=('main',))
    def incomplete(task,*args):
        return {'episode':SynthesisRouteEnv(task).export(),'agent':{'completed':False}}
    out=tmp_path/'runs'
    runner.run_plan(plan,freeze,out,executor=incomplete)
    report=score_stage(plan,freeze,out,expected_freeze_sha256=runner.digest(freeze),
        public_dir=tmp_path,private_dir=tmp_path,expected_public='a'*64,expected_private='b'*64,
        selection={'groups':[{'group_id':'g','task_ids':['fixture']}]},
        scorer=lambda *a,**k:pytest.fail('unsubmitted candidate was scored'))
    assert report['scores']==[]
    assert report['rows'][0]['actual_tokens'] is None
    assert not report['rows'][0]['submitted']
    assert report['by_regime']['budgeted']['arms']['main']['failed_or_incomplete']==1


def test_all_task_bindings_are_checked_before_any_answer(tmp_path):
    from synthesis_route_gym.development_evaluation import score_stage
    from synthesis_route_gym import development_runner as runner
    from test_development_runner import fixture_plan,executor
    from synthesis_route_gym.environment import SynthesisRouteEnv
    plan,freeze,_=fixture_plan(tmp_path,arms=('breadth_first','best_first'))
    calls=[]
    def run(task,row,runtime,folder):
        calls.append(row)
        if len(calls)==1:
            return executor(task,row,runtime,folder)
        wrong=task.model_copy(update={'target':'CCN'})
        env=SynthesisRouteEnv(wrong)
        env.dispatch('submit',{'route_ids':[]})
        return {'episode':env.export()}
    out=tmp_path/'runs'
    runner.run_plan(plan,freeze,out,executor=run)
    with pytest.raises(ValueError,match='task integrity'):
        score_stage(plan,freeze,out,expected_freeze_sha256=runner.digest(freeze),
            public_dir=tmp_path,private_dir=tmp_path,expected_public='a'*64,expected_private='b'*64,
            selection={'groups':[{'group_id':'g','task_ids':['fixture']}]},
            scorer=lambda *a,**k:pytest.fail('answers opened before all task bindings verified'))


def test_grouping_uses_pinned_selection_and_preserves_target_relations(tmp_path):
    from synthesis_route_gym.development_evaluation import _grouping
    from synthesis_route_gym import development_runner as runner
    from test_core import make_task
    selection={'groups':[{'group_id':'g','task_ids':['one','two']}]}
    path=tmp_path/'selection.json'
    runner.write_once(path,selection)
    freeze=tmp_path/'freeze.json'
    runner.write_once(freeze,{'files':{str(path):runner.digest(path)}})
    tasks={name:make_task(task_id=name) for name in ('one','two')}
    plan={'selection_sha256':runner.digest(path)}
    assert _grouping(plan,selection,tasks,freeze,path)=={'one':'g','two':'g'}
    with pytest.raises(ValueError,match='selection integrity'):
        _grouping(plan,{'groups':[{'group_id':'edited','task_ids':['one','two']}]},tasks,freeze,path)
    split={'groups':[{'group_id':name,'task_ids':[name]} for name in ('one','two')]}
    with pytest.raises(ValueError,match='splits'):
        _grouping({},split,tasks,freeze,None)
    with pytest.raises(ValueError,match='Duplicate'):
        _grouping({}, {'groups':selection['groups']*2},tasks,freeze,None)
