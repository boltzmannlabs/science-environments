"""Condition campaigns reveal only admitted measurements and survive restart."""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor
import json
import pytest
from synthesis_route_gym.condition_episode import ConditionEpisode
from synthesis_route_gym.episode_store import EpisodeStore, StoreConflict
from synthesis_route_gym.portfolio_conditions import ConditionRecord, FiniteConditionStudy


def study(values=(10.,40.,90.), initial=('a',), budget=3):
    rows=tuple(ConditionRecord(k,(('base',b),('ligand','P')),v)
               for k,b,v in zip(('a','b','c'),('N','O','S'),values))
    return FiniteConditionStudy(rows,initial,budget,'https://example.org/study',
                                'private-source-locator','d'*64,'CCO')


def predictions():
    return [{'candidate_id':k,'prediction_id':'pred-'+k,'status':'scored','value':v,
             'unit':'percent','domain':'transfer_unknown','uncertainty':'not_calibrated',
             'model_version':'public-v1'} for k,v in zip(('a','b','c'),(25.,30.,35.))]


def episode(**kwargs):
    return ConditionEpisode(study(),study_id='study-1',predictions=predictions(),
                            clock=lambda:0.,wall_clock=lambda:1000.,**kwargs)


def resume(path, **kwargs):
    return ConditionEpisode.resume(path,study(),study_id='study-1',predictions=predictions(),
                                    clock=lambda:0.,wall_clock=lambda:1000.,**kwargs)


def test_initial_view_is_filtered_detached_and_hidden_outcome_invariant():
    env=episode();view=env.public_view()
    assert view['schema_version']=='srg-condition-view-v1'
    assert view['measurement']=={'name':'yield','unit':'percent','evidence_kind':'measured_dataset_replay'}
    assert len(view['observations'])==1 and view['observations'][0]['value']==10
    assert len(view['candidates'])==3 and view['resources']['remaining_observations']==2
    view['observations'][0]['value']=999;view['candidates'][0]['conditions']['base']='changed'
    assert env.public_view()['observations'][0]['value']==10
    assert env.public_view()['candidates'][0]['conditions']['base']=='N'
    raw=json.dumps(env.export())
    assert 'private-source-locator' not in raw and 'dataset_optimum' not in raw and 'yield_percent' not in raw
    other=ConditionEpisode(study((10.,1.25,99.75)),study_id='study-1',predictions=predictions(),clock=lambda:0.,wall_clock=lambda:1000.)
    assert env.public_view()==other.public_view()


def test_observe_update_and_measured_submit():
    env=episode();r=env.dispatch('observe_condition',{'candidate_id':'b'},action_id='query')
    assert r['status']=='ok' and r['result']['observation']['value']==40
    assert r['result']['view']['resources']['new_observations_used']==1
    assert env.dispatch('submit',{'candidate_id':'b'})['terminated']
    assert env.export()['submission']=={'status':'selected','candidate_id':'b'}
    assert env.dispatch('observe_condition',{'candidate_id':'c'})['status']=='error'


def test_unknown_unobserved_and_extra_submission_fields_fail():
    env=episode()
    for args in ({'candidate_id':'missing'},{'candidate_id':'c'},{'candidate_id':'a','yield_percent':99}):
        assert env.dispatch('submit',args)['status']=='error'
    assert env.public_view()['resources']['remaining_actions']==77
    assert env.dispatch('submit',{'candidate_id':None})['terminated']


def test_prediction_access_is_cached_and_not_observation():
    env=episode();r=env.dispatch('predict_reaction_yield',{'candidate_ids':['c','a']})
    assert [x['candidate_id']for x in r['result']['predictions']]==['c','a']
    assert r['result']['view']['resources']['new_observations_used']==0
    for args in ({'candidate_ids':[]},{'candidate_ids':['a','a']},{'candidate_ids':['unknown']},{'candidate_ids':['a'],'outcome':1}):
        assert env.dispatch('predict_reaction_yield',args)['status']=='error'
    empty=ConditionEpisode(study(),study_id='s')
    assert empty.dispatch('predict_reaction_yield',{'candidate_ids':['a']})['status']=='unavailable'


def test_exact_idempotent_action_and_duplicate_observation():
    env=episode();first=env.dispatch('observe_condition',{'candidate_id':'b'},action_id='same')
    assert env.dispatch('observe_condition',{'candidate_id':'b'},action_id='same')==first
    assert env.public_view()['usage']['actions']==1
    assert env.dispatch('observe_condition',{'candidate_id':'c'},action_id='same')['status']=='error'
    r=env.dispatch('observe_condition',{'candidate_id':'b'},action_id='new')
    assert r['status']=='ok' and r['result']['already_observed'] is True
    assert env.public_view()['resources']['new_observations_used']==1
    assert env.dispatch('observe_condition',{'candidate_id':'a'})['result']['already_observed']


def test_observation_budget_includes_initial():
    env=ConditionEpisode(study(budget=2),study_id='s')
    assert env.dispatch('observe_condition',{'candidate_id':'b'})['status']=='ok'
    assert env.dispatch('observe_condition',{'candidate_id':'c'})['status']=='error'
    assert env.public_view()['resources']['remaining_observations']==0


def test_invalid_actions_consume_actions_not_observations():
    env=episode()
    for name,args in [('reset',{}),('inspect',{'report':True}),('observe_condition',{'candidate_id':'secret'}),('observe_condition',{'candidate_id':'b','yield_percent':99}),('submit',{}),('inspect',[])]:
        assert env.dispatch(name,args)['status']=='error'
    assert env.public_view()['usage']['actions']==6
    assert env.public_view()['resources']['new_observations_used']==0


def test_budgets_deadline_and_cancel():
    env=episode(max_actions=1);assert env.dispatch('inspect',{})['status']=='ok'
    assert env.dispatch('submit',{'candidate_id':'a'})['truncated']
    now=[0.];timed=ConditionEpisode(study(),study_id='s',wall_seconds=2,clock=lambda:now[0],wall_clock=lambda:1000+now[0])
    now[0]=2
    assert timed.dispatch('observe_condition',{'candidate_id':'b'})['truncated']
    assert timed.public_view()['resources']['new_observations_used']==0
    env=episode();env.cancel('host_cancelled');env.cancel('second_reason')
    assert env.dispatch('observe_condition',{'candidate_id':'b'})['truncated']
    assert env.export()['stop_reason']=='host_cancelled'


def test_concurrent_duplicate_only_reveals_once():
    env=episode()
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(lambda _:env.dispatch('observe_condition',{'candidate_id':'b'}),range(4)))
    assert all(r['status']=='ok'for r in rows)
    assert env.public_view()['resources']['new_observations_used']==1
    assert env.public_view()['usage']['actions']==4


def test_persistent_resume_cache_and_submission(tmp_path):
    path=tmp_path/'episode';env=episode(store=path)
    first=env.dispatch('observe_condition',{'candidate_id':'b'},action_id='query');restored=resume(path)
    assert restored.public_view()==env.public_view()
    assert restored.dispatch('observe_condition',{'candidate_id':'b'},action_id='query')==first
    assert restored.dispatch('submit',{'candidate_id':'b'})['terminated']
    assert resume(path).public_view()['submission']['candidate_id']=='b'


def test_resume_binding_and_downtime(tmp_path):
    path=tmp_path/'episode';episode(store=path,wall_seconds=5)
    args=dict(study_id='study-1',predictions=predictions(),wall_seconds=5)
    with pytest.raises(ValueError,match='binding'):ConditionEpisode.resume(path,study((10.,2.,3.)),**args)
    with pytest.raises(ValueError,match='binding'):ConditionEpisode.resume(path,study(),max_actions=81,**args)
    restored=ConditionEpisode.resume(path,study(),clock=lambda:0,wall_clock=lambda:1006,**args)
    assert restored.dispatch('inspect',{})['truncated']


def test_pending_query_is_persisted_consumed_and_not_replayed(tmp_path,monkeypatch):
    path=tmp_path/'episode';env=episode(store=path)
    def interrupted(key):
        saved,_=EpisodeStore(path).load()
        assert saved['pending']['candidate_id']==key and saved['reserved_candidate_ids']==['b']
        raise KeyboardInterrupt()
    monkeypatch.setattr(env,'_reveal',interrupted)
    with pytest.raises(KeyboardInterrupt):env.dispatch('observe_condition',{'candidate_id':'b'},action_id='query')
    restored=resume(path)
    assert restored.public_view()['resources']['new_observations_used']==1
    assert len(restored.public_view()['observations'])==1
    assert restored.dispatch('observe_condition',{'candidate_id':'b'},action_id='query')['status']=='interrupted'
    assert restored.dispatch('observe_condition',{'candidate_id':'b'})['status']=='error'
    assert restored.dispatch('observe_condition',{'candidate_id':'c'})['status']=='ok'


def test_stale_writer_cannot_query_oracle(tmp_path,monkeypatch):
    path=tmp_path/'episode';first=episode(store=path);stale=resume(path);first.dispatch('inspect',{})
    monkeypatch.setattr(stale,'_reveal',lambda _:pytest.fail('Stale writer reached oracle'))
    with pytest.raises(StoreConflict):stale.dispatch('observe_condition',{'candidate_id':'b'})


@pytest.mark.parametrize('mutate',[lambda s:replace(s,budget=True),lambda s:replace(s,budget=0),lambda s:replace(s,observed_ids=('a','a')),lambda s:replace(s,observed_ids=('x',)),lambda s:replace(s,observed_ids=('a','b'),budget=1),lambda s:replace(s,source_url='/private/path'),lambda s:replace(s,dataset_sha256='invalid'),lambda s:replace(s,substrate='not smiles'),lambda s:replace(s,_records=(s._records[0],s._records[0])),lambda s:replace(s,_records=(replace(s._records[0],yield_percent=float('nan')),)),lambda s:replace(s,_records=(replace(s._records[0],yield_percent=101),)),lambda s:replace(s,_records=(replace(s._records[0],conditions=(('yield','10'),)),))])
def test_invalid_study_rejected(mutate):
    with pytest.raises(ValueError):ConditionEpisode(mutate(study()),study_id='s')


@pytest.mark.parametrize('change',[{'value':float('nan')},{'value':101},{'status':'measured'},{'status':'abstained','value':1},{'candidate_id':'unknown'},{'uncertainty':''},{'unit':'CAD'},{'outcome':9}])
def test_invalid_prediction_rejected(change):
    with pytest.raises(ValueError):ConditionEpisode(study(),study_id='s',predictions=[{**predictions()[0],**change}])


def test_abstained_prediction_and_detached_input():
    rows=[{**predictions()[0],'status':'abstained','value':None}]
    env=ConditionEpisode(study(),study_id='s',predictions=rows);rows[0]['domain']='changed'
    assert env.public_view()['predictions'][0]['domain']=='transfer_unknown'
    assert env.public_view()['predictions'][0]['value'] is None


def test_failed_and_late_oracle_results_stay_charged(monkeypatch):
    env=episode()
    def failed(_):raise RuntimeError('private-path-or-secret-outcome')
    monkeypatch.setattr(env,'_reveal',failed)
    result=env.dispatch('observe_condition',{'candidate_id':'b'})
    assert result['status']=='error' and 'private-path' not in json.dumps(result)
    assert env.public_view()['resources']['new_observations_used']==1
    assert env.public_view()['unavailable_candidate_ids']==['b']
    now=[0.];env=ConditionEpisode(study(),study_id='s',wall_seconds=1,clock=lambda:now[0],wall_clock=lambda:1000+now[0])
    original=env._reveal
    def late(key):now[0]=2.;return original(key)
    monkeypatch.setattr(env,'_reveal',late)
    result=env.dispatch('observe_condition',{'candidate_id':'b'})
    assert result['truncated'] and len(result['result']['view']['observations'])==1
    assert result['usage']['observation_calls']==1


def test_pending_action_requires_resume(tmp_path,monkeypatch):
    env=episode(store=tmp_path/'e')
    def stop(_):raise KeyboardInterrupt()
    monkeypatch.setattr(env,'_reveal',stop)
    with pytest.raises(KeyboardInterrupt):env.dispatch('observe_condition',{'candidate_id':'b'})
    assert env.dispatch('inspect',{})['status']=='error'
    assert env.public_view()['usage']['actions']==1


@pytest.mark.parametrize('changes',[{'candidate_id':[]},{'prediction_id':'bad id'},{'value':True}])
def test_malformed_prediction_types_raise_value_error(changes):
    with pytest.raises(ValueError):ConditionEpisode(study(),study_id='s',predictions=[{**predictions()[0],**changes}])


@pytest.mark.parametrize('override',[{'observed_ids':None},{'observed_ids':(['a'],)},
    {'_records':()}, {'_records':(object(),)}, {'source_locator':''}])
def test_malformed_study_types_raise_value_error(override):
    with pytest.raises(ValueError):ConditionEpisode(replace(study(),**override),study_id='s')


def test_binding_changes_with_initials_predictions_and_target():
    a=episode();assert len(a.binding_fingerprint)==64
    assert episode(target='CO').binding_fingerprint!=a.binding_fingerprint
    assert ConditionEpisode(study(initial=()),study_id='study-1',predictions=predictions()).binding_fingerprint!=a.binding_fingerprint
    rows=predictions();rows[0]['value']=21
    assert ConditionEpisode(study(),study_id='study-1',predictions=rows).binding_fingerprint!=a.binding_fingerprint


@pytest.mark.parametrize('mutate',[
    lambda s:{**s,'unexpected':True},lambda s:{**s,'actions':-1},
    lambda s:{**s,'deadline':s['deadline']+1},lambda s:{**s,'reserved_candidate_ids':['b','b']},
    lambda s:{**s,'observations':[]},lambda s:{**s,'terminated':'false'},
    lambda s:{**s,'submission':{'status':'selected','candidate_id':'c'},'terminated':True},
    lambda s:{**s,'pending':{'candidate_id':'c'}},
    lambda s:{**s,'cache':{'fake':{'request':{},'response':{'secret':90}}}},
])
def test_checkpoint_consistency_validated(tmp_path,mutate):
    path=tmp_path/'episode';episode(store=path)
    store=EpisodeStore(path);saved,revision=store.load();store.commit(mutate(saved),expected_revision=revision)
    with pytest.raises(ValueError):resume(path)


def test_duplicate_predictions_and_condition_factors_rejected():
    with pytest.raises(ValueError):ConditionEpisode(study(),study_id='s',predictions=[predictions()[0]]*2)
    row=study()._records[0]
    for bad in [replace(row,conditions=()),replace(row,conditions=(('base','N'),('base','O'))),
                replace(row,conditions=(('base',),)),replace(row,conditions=(('base',''),))]:
        with pytest.raises(ValueError):ConditionEpisode(replace(study(),_records=(bad,)),study_id='s')


def test_persisted_checkpoint_has_only_known_measurements(tmp_path):
    path=tmp_path/'episode';env=episode(store=path)
    env.dispatch('observe_condition',{'candidate_id':'b'})
    saved,_=EpisodeStore(path).load()
    assert 'private-source-locator' not in json.dumps(saved)
    assert [x['value']for x in saved['observations']]==[10.,40.]
    assert len(env.export()['events'])==1


@pytest.mark.parametrize('value',[float('inf'),float('nan'),True,'1000'])
def test_nonfinite_or_nonnumeric_checkpoint_time_rejected(tmp_path,value):
    path=tmp_path/'episode';episode(store=path)
    store=EpisodeStore(path);saved,revision=store.load()
    # JSON rejects NaN/Infinity at the store boundary, independently of resume.
    changed={**saved,'started_wall':value,'deadline':value if not isinstance(value,(int,float)) else value+600}
    if isinstance(value,float) and not __import__('math').isfinite(value):
        with pytest.raises(ValueError):store.commit(changed,expected_revision=revision)
    else:
        store.commit(changed,expected_revision=revision)
        with pytest.raises(ValueError):resume(path)


def test_resume_wall_clock_rollback_never_refunds_elapsed_budget(tmp_path):
    path=tmp_path/'episode';wall=[1000.];mono=[0.]
    env=ConditionEpisode(study(),study_id='s',wall_seconds=10,store=path,
                          clock=lambda:mono[0],wall_clock=lambda:wall[0])
    wall[0]=1009.;mono[0]=9.
    assert env.dispatch('inspect',{})['result']['resources']['remaining_seconds']==1.
    wall[0]=1001.;mono[0]=0.
    restored=ConditionEpisode.resume(path,study(),study_id='s',wall_seconds=10,
                                      clock=lambda:mono[0],wall_clock=lambda:wall[0])
    assert restored.public_view()['resources']['remaining_seconds']==1.
    mono[0]=1.
    result=restored.dispatch('observe_condition',{'candidate_id':'b'})
    assert result['truncated'] and result['usage']['observation_calls']==0


def test_resume_adds_downtime_after_prior_in_process_clock_rollback(tmp_path):
    path=tmp_path/'episode';wall=[1000.];mono=[0.]
    env=ConditionEpisode(study(),study_id='s',wall_seconds=10,store=path,
                          clock=lambda:mono[0],wall_clock=lambda:wall[0])
    wall[0]=1001.;mono[0]=9.
    env.dispatch('inspect',{})
    wall[0]=1002.;mono[0]=0.
    restored=ConditionEpisode.resume(path,study(),study_id='s',wall_seconds=10,
                                      clock=lambda:mono[0],wall_clock=lambda:wall[0])
    assert restored.public_view()['resources']['remaining_seconds']==0.
    assert restored.dispatch('submit',{'candidate_id':'a'})['truncated']


@pytest.mark.parametrize('field,value',[
    ('elapsed_seconds',-1),('elapsed_seconds',True),('saved_at_wall','1000'),
])
def test_resume_rejects_malformed_persisted_elapsed_clock(tmp_path,field,value):
    path=tmp_path/'episode';episode(store=path)
    store=EpisodeStore(path);saved,revision=store.load()
    store.commit({**saved,field:value},expected_revision=revision)
    with pytest.raises(ValueError):resume(path)
