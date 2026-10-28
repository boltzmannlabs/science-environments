"""Prospective condition plans freeze public choices before measured replay."""
import json
from pathlib import Path
import pytest
from synthesis_route_gym import condition_development_execution as module
from test_condition_io import files


def fixture(tmp_path):
    rows = []
    for index in range(3):
        folder = tmp_path / str(index); folder.mkdir()
        public, _, _ = files(folder)
        # Different authorized groups may share a synthetic study ID in this fixture.
        for name in ('study.json', 'labels.json', 'predictions.json'):
            value = json.loads((folder/name).read_text())
            value['study_id'] = f'study-{index}'
            if name == 'study.json':
                value.update(product_group_id=f'product-{index}', group_id=f'scaffold-{index}')
            (folder/name).write_text(json.dumps(value))
        from synthesis_route_gym.condition_identity import condition_input_digest
        public = module.read(folder/'study.json')
        for name in ('labels.json', 'predictions.json'):
            value = module.read(folder/name)
            value['candidate_inputs_sha256'] = condition_input_digest(public)
            (folder/name).write_text(json.dumps(value))
        public['outcomes_sha256'] = module.digest(folder/'labels.json')
        (folder/'study.json').write_text(json.dumps(public))
        rows.append({'study_id':f'study-{index}', 'product_group_id':f'product-{index}',
                     'group_id':f'scaffold-{index}', **{kind+'_path':str(folder/name) for kind,name in
                     [('public','study.json'),('outcomes','labels.json'),('predictions','predictions.json')]},
                     **{kind+'_sha256':module.digest(folder/name) for kind,name in
                     [('public','study.json'),('outcomes','labels.json'),('predictions','predictions.json')]}})
    manifest = tmp_path/'manifest.json'
    module.write_once(manifest, {'data_role':'previously_used_development','final_labels_accessed':False,
                               'studies':rows,'model_metadata':{'version':'test-model'},'source_family_count':1})
    prior = tmp_path/'prior.json'
    runs = [{'arm':arm,'product_group':group,'penalized_submitted_regret_percent':value}
            for arm,group,value in [('fixed_order','g1',10),('fixed_order','g2',0),
                                    ('public_model_rank','g1',6),('public_model_rank','g2',6)]]
    module.write_once(prior, {'runs':runs, 'promotion_eligible':False})
    profile = tmp_path/'profile'; profile.mkdir()
    (profile/'config.yaml').write_text('model:\n  default: gpt-6-sol\n  provider: openai-codex\n')
    runtime = {'profile_home':str(profile),'model':'gpt-6-sol','provider':'openai-codex',
               'scientist_python':'/trusted/python','scientist_source':'/trusted/scientist',
               'hardware':module.capture_runtime_hardware(),
               'provider_hardware':'unknown_remote_provider_allocation'}
    return manifest, prior, runtime


def prepare(tmp_path):
    manifest, prior, runtime = fixture(tmp_path)
    plan = module.prepare_condition_plan(manifest, prior, tmp_path/'prepared', runtime=runtime)
    return plan, tmp_path/'prepared'/'plan.json'


def test_prepare_is_public_only_and_deterministic(tmp_path, monkeypatch):
    manifest, prior, runtime = fixture(tmp_path)
    original = Path.open
    def guarded(path, *args, **kwargs):
        if path.name == 'labels.json':
            pytest.fail('Outcome accessed before public plan freeze')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'open', guarded)
    plan = module.prepare_condition_plan(manifest, prior, tmp_path/'prepared', runtime=runtime)
    assert len(plan['runs']) == 12 and len(plan['studies']) == 2
    assert plan['fixed_selection']['policy'] == 'fixed_order'
    assert plan['execution_approved'] is False
    assert {r['regime'] for r in plan['runs']} == {'budgeted','unbudgeted'}
    assert plan['fixed_selection']['promotion_eligible'] is False
    assert len(plan['ranking_decisions']) == 4
    assert not list((tmp_path/'prepared').rglob('labels.json'))


def test_policy_group_weighting_and_ties():
    rows = [{'arm':'random','product_group':'a','penalized_submitted_regret_percent':0}]*10
    rows += [{'arm':'random','product_group':'b','penalized_submitted_regret_percent':10},
             {'arm':'fixed_order','product_group':'a','penalized_submitted_regret_percent':4},
             {'arm':'fixed_order','product_group':'b','penalized_submitted_regret_percent':4}]
    assert module.select_fixed_policy({'runs':rows})['policy'] == 'fixed_order'
    with pytest.raises(ValueError): module.select_fixed_policy({'runs':[]})


def test_rank_abstentions_deterministic_ties():
    public = {'candidates':[{'candidate_id':k} for k in ('c','b','a')]}
    predictions = [{'candidate_id':'a','status':'scored','value':20},
                   {'candidate_id':'b','status':'scored','value':20},
                   {'candidate_id':'c','status':'abstained','value':None}]
    ranked = module.ranking_decisions(public,predictions)
    assert ranked['model_off']['order'] == ['c','b','a']
    assert ranked['model_on']['order'] == ['a','b','c']
    assert ranked['model_on']['abstained_candidate_ids'] == ['c']
    assert ranked['model_on']['fallback_policy'] == 'append_abstentions_in_frozen_base_order'


def test_all_abstained_ranking_keeps_pool_without_prediction_exposure():
    public={'candidates':[{'candidate_id':key} for key in ('c','a','b')]}
    predictions=[{'candidate_id':key,'status':'abstained','value':None} for key in ('a','b','c')]
    ranked=module.ranking_decisions(public,predictions)
    assert ranked['model_on']['order']==ranked['model_off']['order']==['c','a','b']
    score=module._rank_score(ranked['model_on'],{'a':10,'b':80,'c':30})
    assert score['coverage']==0 and score['ranking_pool_coverage']==1
    assert score['top_1_regret_percent']==50
    with pytest.raises(ValueError,match='same candidate pool'):
        module.ranking_decisions(public,predictions[:-1])


def test_revised_plan_retains_prior_hash_and_rejects_mismatched_model_metadata(tmp_path):
    manifest,prior,runtime=fixture(tmp_path)
    module.prepare_condition_plan(manifest,prior,tmp_path/'v1',runtime=runtime)
    previous=tmp_path/'v1/plan.json'; previous_hash=module.digest(previous)
    revised=module.prepare_condition_plan(manifest,prior,tmp_path/'v2',runtime=runtime,previous_plan_path=previous)
    assert revised['previous_plan']['plan_sha256']==previous_hash
    assert module.digest(previous)==previous_hash
    source=module.read(manifest)
    source['model_metadata']={'version':'other-model'}
    manifest.write_text(json.dumps(source))
    with pytest.raises(ValueError,match='model metadata'):
        module.prepare_condition_plan(manifest,prior,tmp_path/'v3',runtime=runtime)


def test_requires_freeze_and_explicit_execution_approval(tmp_path):
    plan, path = prepare(tmp_path)
    with pytest.raises(ValueError, match='approval'):
        module.run_condition_plan(path,tmp_path/'missing',tmp_path/'runs',expected_freeze_sha256='x')
    with pytest.raises(ValueError, match='commit'):
        module.score_condition_plan(path,tmp_path/'missing',tmp_path/'runs',expected_freeze_sha256='x')


def test_freeze_execute_commit_then_score_no_llm(tmp_path):
    plan, path = prepare(tmp_path)
    frozen = path.parent/'freeze.json'
    module.freeze_condition_plan(path,frozen)
    frozen_sha = module.digest(frozen)
    calls=[]
    def execute(inputs,row,runtime,folder):
        from synthesis_route_gym.condition_episode import ConditionEpisode
        from synthesis_route_gym.condition_benchmark import run_fixed_condition_episode
        from dataclasses import replace
        calls.append(row['run_id'])
        unlimited=row['regime']=='unbudgeted'
        study=replace(inputs['study'],budget=None) if unlimited else inputs['study']
        env=ConditionEpisode(study,study_id=inputs['study_id'],target=inputs['target'],
            predictions=inputs['predictions'],regime=row['regime'],max_actions=None if unlimited else 80,
            wall_seconds=None if unlimited else 600)
        result=run_fixed_condition_episode(env,'fixed_order')
        return {**result,'method':row['arm']}
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=frozen_sha,
                                     execution_approved=True,executor=execute)
    assert len(calls)==12 and result['all_decisions_committed']
    scored=module.score_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=frozen_sha)
    assert len(scored['runs'])==12 and len(scored['ranking_ablation'])==4
    assert scored['promotion_eligible'] is False
    assert all(r['top_1_regret_percent'] is not None for r in scored['ranking_ablation'])
    with pytest.raises(ValueError,match='attempt'):
        module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=frozen_sha,
                                  execution_approved=True,executor=execute)


def test_failure_is_committed_and_not_retried(tmp_path):
    _,path=prepare(tmp_path); frozen=path.parent/'freeze.json'
    module.freeze_condition_plan(path,frozen)
    def fail(*args):raise RuntimeError('SECRET')
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                     execution_approved=True,executor=fail)
    assert result['all_decisions_committed'] and result['failed']==12
    assert 'SECRET' not in json.dumps(result)
    score=module.score_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen))
    assert all(r['submission_status']=='not_submitted' for r in score['runs'])


@pytest.mark.parametrize('regime',['budgeted','unbudgeted'])
def test_execute_native_receives_main_profile_and_matching_limits(tmp_path,monkeypatch,regime):
    manifest,_,runtime=fixture(tmp_path)
    source=module.read(manifest)['studies'][0]
    inputs=module.load_condition_inputs(source['public_path'],source['outcomes_path'],source['predictions_path'])
    def fake(args,episode,path):
        assert args.model_calls==(None if regime=='unbudgeted' else 24)
        assert args.max_tokens==(None if regime=='unbudgeted' else 200000)
        assert episode.public_view()['resources']['remaining_seconds'] is None if regime=='unbudgeted' else True
        episode.dispatch('submit',{'candidate_id':'a'})
        return {'method':args.method,'episode':episode.export(),'agent':{'completed':True}}
    monkeypatch.setattr('synthesis_route_gym.condition_session.run_condition_agent',fake)
    row={'arm':'main','regime':regime,'seed':0}
    result=module.execute_condition(inputs,row,runtime,tmp_path/'run')
    assert result['episode']['submission']['status']=='selected'


def test_execute_fixed_and_interrupted_native_preserves_observations(tmp_path,monkeypatch):
    manifest,_,runtime=fixture(tmp_path);source=module.read(manifest)['studies'][0]
    inputs=module.load_condition_inputs(source['public_path'],source['outcomes_path'],source['predictions_path'])
    result=module.execute_condition(inputs,{'arm':'strong_fixed','regime':'unbudgeted','seed':0},
                                    runtime|{'fixed_policy':'fixed_order'},tmp_path/'fixed')
    assert result['completed']
    def cancel(args,episode,path):
        episode.dispatch('observe_condition',{'candidate_id':'b'})
        raise KeyboardInterrupt
    monkeypatch.setattr('synthesis_route_gym.condition_session.run_condition_agent',cancel)
    result=module.execute_condition(inputs,{'arm':'main','regime':'unbudgeted','seed':0},runtime,tmp_path/'interrupted')
    assert result['interrupted'] and len(result['episode']['observations'])==2
    assert result['agent']['resource_accounting']=='unknown_after_interruption'


def test_cancelled_panel_cannot_be_scored_and_artifact_tampering_rejected(tmp_path):
    _,path=prepare(tmp_path); frozen=path.parent/'freeze.json';module.freeze_condition_plan(path,frozen)
    def interrupt(*args):raise KeyboardInterrupt
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                    execution_approved=True,executor=interrupt)
    assert not result['all_decisions_committed'] and len(result['receipts'])==1
    with pytest.raises(ValueError,match='commit'):
        module.score_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen))


def test_snapshot_excludes_profile_and_private_outcomes(tmp_path):
    plan,path=prepare(tmp_path);frozen=path.parent/'freeze.json'
    with pytest.raises(ValueError,match='Private'):
        module.freeze_condition_plan(path,frozen,assets=[next(iter(plan['studies'].values()))['outcomes_path']])
    value=module.freeze_condition_plan(path,frozen)
    assert all(not p.endswith('config.yaml') and not p.endswith('labels.json') for p in value['snapshot_files'])


def test_commit_integrity_and_balanced_frozen_matrix(tmp_path):
    plan,path=prepare(tmp_path)
    changed={**plan,'runs':[dict(row,arm='main') for row in plan['runs']]}
    path.write_text(json.dumps(changed)); frozen=path.parent/'freeze.json'
    module.freeze_condition_plan(path,frozen)
    with pytest.raises(ValueError,match='matrix'):
        module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),execution_approved=True)


def test_rank_metrics_all_abstained_and_paired_aggregate():
    result=module._rank_score({'order':['a','b'],'abstained_candidate_ids':['a','b']},{'a':10,'b':90})
    assert result['coverage']==0 and result['ranking_pool_coverage']==1
    assert result['top_1_regret_percent']==80
    rows=[{'arm':arm,'regime':regime,'product_group_id':group,
           'penalized_submitted_regret_percent':value,'submission_status':'selected','attempt_status':'completed'}
          for regime in ('budgeted','unbudgeted') for group in ('a','b')
          for arm,value in [('strong_fixed',4),('main',3),('main_condition_scientist',5)]]
    aggregate=module.aggregate_scores(rows)
    assert aggregate['budgeted']['paired_main_minus_assisted_regret']['mean']==-2
    assert aggregate['budgeted']['paired_main_minus_assisted_regret']['losses']==2


@pytest.mark.parametrize('regime',['budgeted','unbudgeted'])
@pytest.mark.parametrize('truncated,reason',[(True,'bridge_interrupted'),(False,'bridge_interrupted'),(True,None)])
def test_returned_bridge_interruption_stops_panel_before_next_run(tmp_path,regime,truncated,reason):
    plan,path=prepare(tmp_path)
    runs=sorted(plan['runs'],key=lambda row:row['regime']!=regime)
    path.write_text(json.dumps({**plan,'runs':runs}))
    frozen=path.parent/'freeze.json';module.freeze_condition_plan(path,frozen)
    calls=[]
    def returned_failure(inputs,row,runtime,folder):
        calls.append(row['run_id'])
        return {'method':row['arm'],'episode':{'study_id':inputs['study_id'],'observations':[],
                'submission':{'status':'not_submitted','candidate_id':None},'truncated':truncated},
                'agent':{'completed':False,'stop_reason':reason,'error_type':'BridgeError',
                         'resource_accounting':'unknown_after_bridge_interruption'}}
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                    execution_approved=True,executor=returned_failure)
    assert len(calls)==1 and result['receipts'][0]['status']=='interrupted'
    assert not result['all_decisions_committed']
    committed=module.read(tmp_path/'runs'/calls[0]/'result.json')
    assert committed['agent']['resource_accounting']=='unknown_after_bridge_interruption'


def test_hardware_change_before_run_blocks_private_loading(tmp_path,monkeypatch):
    _,path=prepare(tmp_path);frozen=path.parent/'freeze.json';module.freeze_condition_plan(path,frozen)
    monkeypatch.setenv('OMP_NUM_THREADS','999999')
    def forbidden(*args):pytest.fail('Hardware mismatch must precede private data access')
    monkeypatch.setattr(module,'load_condition_inputs',forbidden)
    with pytest.raises(ValueError,match='Runtime|hardware|thread|environment'):
        module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                  execution_approved=True,executor=forbidden)
    assert not (tmp_path/'runs').exists()


def test_hardware_change_after_run_retains_artifacts_and_stops_panel(tmp_path,monkeypatch):
    _,path=prepare(tmp_path);frozen=path.parent/'freeze.json';module.freeze_condition_plan(path,frozen)
    calls=[]
    def execution(inputs,row,runtime,folder):
        calls.append(row['run_id'])
        monkeypatch.setenv('OMP_NUM_THREADS','999999')
        return {'method':row['arm'],'episode':None,'agent':{'completed':True}}
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                    execution_approved=True,executor=execution)
    assert len(calls)==1 and result['receipts'][0]['status']=='interrupted'
    assert result['receipts'][0]['hardware_verification']['after']=='mismatch'
    assert (tmp_path/'runs'/calls[0]/'result.json').is_file()
    assert not result['all_decisions_committed']


@pytest.mark.parametrize('external',[False,True])
def test_finite_budget_exhaustion_continues_but_explicit_cancel_wins(tmp_path,external):
    plan,path=prepare(tmp_path)
    path.write_text(json.dumps({**plan,'runs':sorted(plan['runs'],key=lambda row:row['regime']!='budgeted')}))
    frozen=path.parent/'freeze.json';module.freeze_condition_plan(path,frozen)
    calls=[]
    def returned(inputs,row,runtime,folder):
        first=not calls;calls.append(row['run_id'])
        return {'method':row['arm'],'episode':{'study_id':inputs['study_id'],'observations':[],
            'submission':{'status':'not_submitted','candidate_id':None},'truncated':first,
            'stop_reason':('host_cancelled' if external else 'episode_deadline_expired') if first else None,
            'usage':{'actions':1,'wall_seconds':600 if first else 1}},
            'agent':{'completed':False,'stop_reason':'bridge_interrupted' if first else None}}
    result=module.run_condition_plan(path,frozen,tmp_path/'runs',expected_freeze_sha256=module.digest(frozen),
                                    execution_approved=True,executor=returned)
    assert len(calls)==(1 if external else 12)
    assert result['receipts'][0]['status']==('interrupted' if external else 'budget_exhausted')
