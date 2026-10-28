"""Frozen serial development runs cannot silently retry or change their inputs."""
import json
from pathlib import Path
import pytest
from synthesis_route_gym import development_runner as runner
from synthesis_route_gym.schemas import Task, Budget


def fixture_plan(tmp_path, arms=('breadth_first',), regimes=('budgeted',)):
    task = Task(task_id='fixture', target='CCO', inventory=())
    inputs = tmp_path / 'inputs'
    inputs.mkdir(parents=True)
    runner.write_once(inputs / 'fixture.json', task.model_dump(mode='json'))
    source = tmp_path / 'source.py'
    source.write_text('# pinned source\n')
    plan = runner.make_plan({'groups':[{'group_id':'g', 'task_ids':['fixture']}],
        'screen_group_ids':['g'], 'confirmation_group_ids':['g']}, inputs,
        stage='B', arms=arms, regimes=regimes, runtime={'expansion_top_k':10,
        'tool_timeout_seconds':120, 'max_frontier_states':10000})
    plan_path = tmp_path / 'plan.json'
    runner.write_once(plan_path, plan)
    freeze_path = tmp_path / 'freeze.json'
    runner.freeze_plan(plan_path, freeze_path, assets=[source])
    return plan_path, freeze_path, source


def executor(task, row, runtime, folder):
    from synthesis_route_gym.environment import SynthesisRouteEnv
    env = SynthesisRouteEnv(task)
    env.dispatch('submit', {'route_ids':[]})
    return {'episode':env.export(), 'stop_reason':'frontier_exhausted'}


def test_serial_e2e_decision_commit_and_verified_resume(tmp_path):
    plan, freeze, _ = fixture_plan(tmp_path, arms=('breadth_first','best_first'),
                                    regimes=('budgeted','unbudgeted'))
    calls = []
    def run(task, row, runtime, folder):
        calls.append((row['arm'],task.budget.regime))
        return executor(task,row,runtime,folder)
    out = tmp_path / 'runs'
    report = runner.run_plan(plan, freeze, out, executor=run)
    assert len(calls) == 4
    assert report['completed'] == 4
    runner.run_plan(plan, freeze, out, executor=run)
    assert len(calls) == 4
    record = next(out.glob('*/receipt.json'))
    decision = record.parent / 'decision.json'
    decision.write_text('{}')
    with pytest.raises(ValueError, match='integrity'):
        runner.run_plan(plan, freeze, out, executor=run)


@pytest.mark.parametrize('error,status', [(RuntimeError('secret'), 'failed'),
                                           (KeyboardInterrupt(), 'interrupted')])
def test_failed_attempt_is_retained_and_never_silently_retried(tmp_path,error,status):
    plan, freeze, _ = fixture_plan(tmp_path)
    def broken(*args):
        raise error
    out=tmp_path/'runs'
    runner.run_plan(plan,freeze,out,executor=broken)
    receipt=json.loads(next(out.glob('*/receipt.json')).read_text())
    assert receipt['status']==status
    assert 'secret' not in json.dumps(receipt)
    with pytest.raises(ValueError,match='not resumable'):
        runner.run_plan(plan,freeze,out,executor=executor)


def test_source_drift_prevents_execution_and_postrun_acceptance(tmp_path):
    plan, freeze, source = fixture_plan(tmp_path)
    def changing(*args):
        source.write_text('# changed')
        return executor(*args)
    with pytest.raises(ValueError,match='integrity'):
        runner.run_plan(plan,freeze,tmp_path/'runs',executor=changing)
    receipt=json.loads(next((tmp_path/'runs').glob('*/receipt.json')).read_text())
    assert receipt['status']=='integrity_failure'
    with pytest.raises(ValueError,match='integrity'):
        runner.run_plan(plan,freeze,tmp_path/'other',executor=executor)


def test_plan_validation_duplicates_unknown_modes_and_unsafe_ids(tmp_path):
    for arm in ('unknown','../main'):
        with pytest.raises(ValueError):
            fixture_plan(tmp_path/arm.replace('/','_'),arms=(arm,))


def test_condition_route_role_maps_to_adaptive_policy():
    mode, policy=runner.arm_configuration('main_condition_scientist')
    assert mode=='main_adaptive'
    assert policy['enabled_roles']==['condition_scientist']
    assert policy['max_consultations']==1
    assert runner.arm_configuration('main')[1] is None


def test_fixed_dispatch_real_empty_search_both_regimes(tmp_path):
    for regime in ('budgeted','unbudgeted'):
        task=Task(task_id='fixture',target='CCO',inventory=(),
                  budget=Budget.unbudgeted(top_k=5) if regime=='unbudgeted' else Budget())
        for arm in ('breadth_first','best_first','synthchem_portfolio'):
            result=runner.execute_episode(task, {'arm':arm,'seed':0},
                {'expansion_top_k':10,'max_frontier_states':10000,
                 'tool_timeout_seconds':120},tmp_path/f'{regime}-{arm}',
                expand=lambda **kwargs:{'status':'ok','predictions':[]})
            assert result['episode']['terminated']
            assert result['episode']['submitted_route_ids']==[]


def test_public_materialization_verifies_once_and_excludes_stock(tmp_path,monkeypatch):
    from synthesis_route_gym import dataset_bundle
    public=tmp_path/'public'
    public.mkdir()
    tasks=[{'task_id':f't{i}','partition':'development','track':'reference_route'} for i in range(2)]
    runner.write_once(public/'manifest.json',{'tasks':tasks})
    runner.write_once(public/'inventory.json',['CC','O'])
    hashes={}
    for t in tasks:
        raw={**t,'target':'CCO','inventory_exclusions':['O'],
             'constraints':{},'budget':{}}
        hashes[t['task_id']]=runner.write_once(public/'tasks'/(t['task_id']+'.json'),raw)
    calls=[]
    monkeypatch.setattr(dataset_bundle,'verify_bundle',lambda *a,**kw:calls.append(a))
    selection={'manifest_sha256':runner.digest(public/'manifest.json'),
               'groups':[{'task_ids':['t0','t1']}],'task_hashes':hashes}
    result=runner.materialize_inputs(public,selection,tmp_path/'inputs')
    assert len(calls)==1
    assert len(result)==2
    assert [i['smiles'] for i in runner.read(result['t0']['path'])['inventory']]==['CC']
    (public/'tasks/t0.json').write_text('{}')
    with pytest.raises(ValueError,match='integrity'):
        runner.materialize_inputs(public,selection,tmp_path/'again')


@pytest.mark.parametrize('arm',runner.AGENT_ARMS)
def test_all_agent_arms_bind_main_profile_and_nullable_budget(tmp_path,monkeypatch,arm):
    from types import SimpleNamespace
    from synthesis_route_gym import agent_runner,agent_session
    monkeypatch.setattr(agent_runner,'resolve_main_profile',lambda p:SimpleNamespace(model='test',provider='test'))
    captured=[]
    monkeypatch.setattr(agent_session,'run_persistent_agent',lambda args,env,path,**kw:captured.append(args) or {'ok':True})
    runtime={k:'test' for k in ('profile_home','scientist_python','scientist_source','repo_root','chemistry_python','model','provider')}
    runtime={**runtime,'model_calls':20,'tool_timeout_seconds':120,'expansion_top_k':10,'max_frontier_states':10000}
    task=Task(task_id='fixture',target='CCO',inventory=(),budget=Budget.unbudgeted())
    assert runner.execute_episode(task,{'arm':arm,'seed':0},runtime,tmp_path,
                                  expand=lambda **kw:{})=={'ok':True}
    assert captured[0].model_calls is None
    if arm=='main_condition_scientist':
        assert captured[0].method=='main_adaptive'
        assert runner.read(captured[0].orchestration_policy)['enabled_roles']==['condition_scientist']


def test_plan_group_selection_and_smoke_are_separate(tmp_path):
    for task_id in ('one','two'):
        runner.write_once(tmp_path/(task_id+'.json'),{})
    selection={'groups':[{'group_id':'a','task_ids':['one']},{'group_id':'b','task_ids':['two']}],
               'screen_group_ids':['a'],'confirmation_group_ids':['b']}
    for stage,expected in [('B',['one','two']),('C',['one']),('E',['two']),('B_unbudgeted_smoke',['one'])]:
        plan=runner.make_plan(selection,tmp_path,stage=stage,arms=('main',),regimes=('budgeted',),runtime={})
        assert list(plan['tasks'])==expected
    for change in ({'stage':'invalid'},{'regimes':('budgeted','budgeted')},{'arms':('main','main')}):
        args={'stage':'B','arms':('main',),'regimes':('budgeted',),'runtime':{},**change}
        with pytest.raises(ValueError):
            runner.make_plan(selection,tmp_path,**args)


@pytest.mark.parametrize('regime',['budgeted','unbudgeted'])
@pytest.mark.parametrize('reason',['backend_failure','search_capacity_failure'])
def test_backend_failure_with_submission_not_natural(tmp_path,regime,reason):
    plan,freeze,_=fixture_plan(tmp_path,regimes=(regime,))
    def failed_backend(*args):
        return {**executor(*args),'stop_reason':reason}
    report=runner.run_plan(plan,freeze,tmp_path/'runs',executor=failed_backend)
    assert report['receipts'][0]['status']=='failed'
    assert not report['receipts'][0]['natural_completion']
    assert (next((tmp_path/'runs').iterdir())/'decision.json').exists()


def test_incomplete_attempt_and_missing_receipt_cannot_resume(tmp_path):
    plan,freeze,_=fixture_plan(tmp_path)
    def incomplete(task,*args):
        return {'episode':{'terminated':False,'truncated':False,'usage':{}}}
    out=tmp_path/'runs'
    report=runner.run_plan(plan,freeze,out,executor=incomplete)
    assert report['receipts'][0]['status']=='incomplete'
    next(out.glob('*/receipt.json')).unlink()
    with pytest.raises(ValueError,match='not resumable'):
        runner.run_plan(plan,freeze,out,executor=executor)


def test_fixed_adapter_is_constructed_with_declared_runtime(tmp_path,monkeypatch):
    from synthesis_route_gym import adapters
    from types import SimpleNamespace
    captured=[]
    monkeypatch.setattr(adapters,'LocalRetroAdapter',lambda **kw:captured.append(kw) or
        SimpleNamespace(expand=lambda **kwargs:{'status':'ok','predictions':[]}))
    task=Task(task_id='fixture',target='CCO',inventory=())
    runner.execute_episode(task,{'arm':'breadth_first','seed':0},
        {'repo_root':'root','chemistry_python':'python','tool_timeout_seconds':120,
         'expansion_top_k':10,'max_frontier_states':10000},tmp_path)
    assert captured==[{'repo_root':'root','python_executable':'python','timeout_seconds':120}]


def test_frozen_expand_schema_and_host_reject_different_width(tmp_path,monkeypatch):
    from types import SimpleNamespace
    from synthesis_route_gym import agent_runner,agent_session
    monkeypatch.setattr(agent_runner,'resolve_main_profile',lambda p:SimpleNamespace(model='test',provider='test'))
    calls=[]
    def native(args,env,path,*,tool_schemas):
        schema=next(s for s in tool_schemas if s['name']=='expand')
        assert schema['parameters']['properties']['top_k']['enum']==[10]
        result=env.dispatch('expand',{'smiles':'CCO','top_k':20})
        assert result['status']=='error'
        assert env.export()['usage']['expansions']==1
        return {'ok':True}
    monkeypatch.setattr(agent_session,'run_persistent_agent',native)
    runtime={k:'test' for k in ('profile_home','scientist_python','scientist_source','repo_root','chemistry_python','model','provider')}
    runtime={**runtime,'model_calls':20,'tool_timeout_seconds':120,'expansion_top_k':10,'max_frontier_states':10000}
    runner.execute_episode(Task(task_id='fixture',target='CCO',inventory=()),
        {'arm':'main','seed':0},runtime,tmp_path,expand=lambda **kw:calls.append(kw))
    assert calls==[]


def test_keyboard_interrupt_cancels_persistent_environment(tmp_path,monkeypatch):
    from synthesis_route_gym import planning
    from synthesis_route_gym.episode_store import EpisodeStore
    def interrupt(*a,**kw):
        raise KeyboardInterrupt()
    monkeypatch.setattr(planning,'run_fixed_workflow',interrupt)
    with pytest.raises(KeyboardInterrupt):
        runner.execute_episode(Task(task_id='fixture',target='CCO',inventory=()),
            {'arm':'breadth_first','seed':0},{'expansion_top_k':10,'max_frontier_states':10000},
            tmp_path,expand=lambda **kw:{})
    state,_=EpisodeStore(tmp_path/'environment').load()
    assert state['truncated']
    assert state['cancel_reason']=='external_operator_interruption'


def test_freeze_snapshots_public_sources_but_only_hashes_profile(tmp_path):
    plan,_,source=fixture_plan(tmp_path)
    profile=tmp_path/'profile.yaml'
    profile.write_text('secret: must-not-be-copied\n')
    freeze=runner.freeze_plan(plan,tmp_path/'separate-freeze.json',assets=[source,profile],
                             private_hash_only=[profile])
    copied=[Path(p) for p in freeze['snapshot_files']]
    assert any(p.name=='source.py' for p in copied)
    assert not any(p.name=='profile.yaml' for p in copied)
    assert str(profile) in freeze['files']
    copied[0].write_text('changed')
    with pytest.raises(ValueError,match='integrity'):
        runner.verify_freeze(plan,tmp_path/'separate-freeze.json',runner.digest(tmp_path/'separate-freeze.json'))


def test_receipt_tampering_cannot_skip_execution(tmp_path):
    plan,freeze,_=fixture_plan(tmp_path)
    runner.run_plan(plan,freeze,tmp_path/'runs',executor=executor)
    receipt=next((tmp_path/'runs').glob('*/receipt.json'))
    receipt.write_text(receipt.read_text()+' ')
    with pytest.raises(ValueError,match='integrity'):
        runner.run_plan(plan,freeze,tmp_path/'runs',executor=executor)


def test_unbudgeted_smoke_selection_uses_public_size_and_stock_only(tmp_path):
    selection={'groups':[{'group_id':'large','heavy_atoms':35,'task_ids':['large']},
                         {'group_id':'small','heavy_atoms':9,'task_ids':['restricted','full']}],
               'screen_group_ids':['large'],'confirmation_group_ids':['small']}
    for task_id,stock in [('large',['CC']),('restricted',['O']),('full',['CC','O'])]:
        runner.write_once(tmp_path/(task_id+'.json'),{'inventory':stock})
    plan=runner.make_plan(selection,tmp_path,stage='B_unbudgeted_smoke',
                          arms=runner.FIXED_ARMS,regimes=('unbudgeted',),runtime={})
    assert len(plan['runs'])==3
    assert {row['task_id'] for row in plan['runs']}=={'full'}


@pytest.mark.parametrize('regime',['budgeted','unbudgeted'])
def test_bridge_interruption_keeps_precedence_and_stops_campaign(tmp_path,regime):
    plan,freeze,_=fixture_plan(tmp_path,arms=('main','main_strategist'),regimes=(regime,))
    calls=[]
    def cancelled(*args):
        calls.append(args[1]['run_id'])
        base=executor(*args)
        return {**base,'stop_reason':'bridge_interrupted',
                'episode':{**base['episode'],'terminated':False,'truncated':True},
                'agent':{'completed':False,'stop_reason':'bridge_interrupted'}}
    result=runner.run_plan(plan,freeze,tmp_path/'runs',executor=cancelled)
    assert len(calls)==1
    assert result['attempts']==1
    assert result['receipts'][0]['status']=='interrupted'
    assert result['receipts'][0]['natural_completion'] is False
    assert not list((tmp_path/'runs').glob('*/decision.json'))


def yield_model_plan(tmp_path):
    import sys
    plan,_,_=fixture_plan(tmp_path)
    model=tmp_path/'yield-model'
    model.mkdir()
    files=('config.json','tokenizer.json','tokenizer_config.json',
           'special_tokens_map.json','model.safetensors')
    hashes={name:runner.write_once(model/name,{}) for name in files}
    manifest=tmp_path/'yield-manifest.json'
    runner.write_once(manifest,{'schema_version':'srg-public-yield-model-v1',
        'model_dir':'yield-model','python_executable':sys.executable,'files':hashes,
        'model_version':'fixture-v1','model_revision':'a'*40,
        'source_url':'https://example.org/public-yield','license':'MIT'})
    raw=runner.read(plan)
    path=tmp_path/'model-plan.json'
    runner.write_once(path,{**raw,'stage':'F_search','model_manifest_sha256':runner.digest(manifest),
        'runtime':{**raw['runtime'],'reaction_yield_model_manifest':str(manifest)},
        'runs':[{**row,'model_enabled':False} for row in raw['runs']]})
    return path,manifest,model


@pytest.mark.parametrize('changed',['manifest','model.safetensors','config.json','missing'])
def test_model_off_freeze_automatically_binds_manifest_and_assets(tmp_path,changed):
    plan,manifest,model=yield_model_plan(tmp_path)
    freeze=tmp_path/'model-freeze.json'
    record=runner.freeze_plan(plan,freeze,assets=[])
    assert str(manifest) in record['files']
    assert str(model/'model.safetensors') in record['files']
    target=manifest if changed=='manifest' else model/('model.safetensors' if changed=='missing' else changed)
    if changed=='missing':
        target.unlink()
    else:
        target.write_text(target.read_text()+' ')
    with pytest.raises(ValueError,match='integrity|manifest|digest'):
        runner.verify_freeze(plan,freeze,runner.digest(freeze))


def test_model_manifest_digest_mismatch_rejected_before_freeze(tmp_path):
    plan,manifest,_=yield_model_plan(tmp_path)
    manifest.write_text(manifest.read_text()+' ')
    with pytest.raises(ValueError,match='manifest.*(digest|integrity)|digest.*manifest'):
        runner.freeze_plan(plan,tmp_path/'bad-freeze.json',assets=[])
    assert not (tmp_path/'bad-freeze.json').exists()


def test_yield_manifest_paths_are_strictly_validated_without_inference(tmp_path):
    plan,manifest,_=yield_model_plan(tmp_path)
    raw=runner.read(manifest)
    manifest.write_text(json.dumps({**raw,'files':{'../escape':'a'*64}}))
    raw_plan=runner.read(plan)
    alternate=tmp_path/'invalid-model-plan.json'
    runner.write_once(alternate,{**raw_plan,'model_manifest_sha256':runner.digest(manifest)})
    with pytest.raises(ValueError,match='asset'):
        runner.freeze_plan(alternate,tmp_path/'bad-freeze.json',assets=[])


def test_finite_budget_truncation_is_accounted_and_campaign_continues(tmp_path):
    plan,freeze,_=fixture_plan(tmp_path,arms=('main','main_strategist'))
    calls=[]
    def exhausted(task,*args):
        calls.append(task.task_id)
        base=executor(task,*args)
        return {**base,'stop_reason':'bridge_interrupted',
                'episode':{**base['episode'],'terminated':False,'truncated':True,
                           'usage':{'actions':task.budget.max_actions,'wall_seconds':0}},
                'agent':{'completed':False,'stop_reason':'bridge_interrupted'}}
    report=runner.run_plan(plan,freeze,tmp_path/'runs',executor=exhausted)
    assert len(calls)==2
    assert {r['status'] for r in report['receipts']}=={'budget_exhausted'}


def test_explicit_external_cancel_overrides_finite_budget():
    result={'episode':{'truncated':True,'usage':{'actions':80}},'agent':{'completed':False}}
    status=runner.classify_episode_stop(result,'budgeted',{'max_actions':80},
        agent_expected=True,cancel_reason='external_operator_interruption')
    assert status=={'status':'interrupted','natural_completion':False}


def test_hardware_capture_and_pre_post_drift(tmp_path,monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess,'run',lambda *a,**kw: (_ for _ in ()).throw(FileNotFoundError()))
    hardware=runner.capture_runtime_hardware()
    assert hardware['gpu_inventory'] is None
    runner.verify_runtime_hardware({'hardware':hardware})
    monkeypatch.setenv('OMP_NUM_THREADS','srg-test-drift')
    with pytest.raises(ValueError,match='hardware|device|thread'):
        runner.verify_runtime_hardware({'hardware':hardware})


def test_model_runtime_metadata_is_pinned_even_when_tool_disabled(tmp_path,monkeypatch):
    from types import SimpleNamespace
    plan,manifest,_=yield_model_plan(tmp_path)
    raw=runner.read(manifest)
    manifest.write_text(json.dumps({**raw,'runtime_versions':{'torch':'fixture'}}))
    selected=runner.read(plan)
    model_plan=tmp_path/'versioned-model-plan.json'
    runner.write_once(model_plan,{**selected,'model_manifest_sha256':runner.digest(manifest)})
    metadata=tmp_path/'torch-METADATA'
    metadata.write_text('Version: fixture\n')
    response={'torch':{'version':'fixture','metadata_file':str(metadata)}}
    monkeypatch.setattr(runner.subprocess,'run',lambda *a,**kw:SimpleNamespace(stdout=json.dumps(response)))
    freeze=tmp_path/'versioned-freeze.json'
    record=runner.freeze_plan(model_plan,freeze,assets=[])
    assert str(metadata) in record['files']
    metadata.write_text('Version: drifted\n')
    with pytest.raises(ValueError,match='integrity'):
        runner.verify_freeze(model_plan,freeze,runner.digest(freeze))
    monkeypatch.setattr(runner.subprocess,'run',lambda *a,**kw:SimpleNamespace(stdout=json.dumps(
        {'torch':{'version':'different','metadata_file':str(metadata)}})))
    with pytest.raises(ValueError,match='version metadata'):
        runner.freeze_plan(model_plan,tmp_path/'mismatch-freeze.json',assets=[])


def test_post_run_hardware_change_is_interrupted_and_stops(tmp_path,monkeypatch):
    plan,freeze,_=fixture_plan(tmp_path,arms=('main','main_strategist'))
    checks=[]
    def hardware(runtime):
        checks.append(True)
        if len(checks)>1:
            raise ValueError('hardware changed')
        return {'status':'verified'}
    monkeypatch.setattr(runner,'verify_runtime_hardware',hardware)
    report=runner.run_plan(plan,freeze,tmp_path/'runs',executor=executor)
    assert report['attempts']==1
    assert report['receipts'][0]['status']=='interrupted'
    assert report['receipts'][0]['hardware_verification']['after']['status']=='mismatch'
