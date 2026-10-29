"""Matched search comparisons use only public inputs and committed decisions."""
import hashlib
import json
from pathlib import Path

import pytest
from synthesis_route_gym.schemas import Task, InventoryItem, Budget
from synthesis_route_gym.planning import run_fixed_workflow
from synthesis_route_gym.search_benchmark import (
    run_comparison, summarize_run, select_development_tasks, pin_localretro_assets,
)


def fixture_task():
    return Task(task_id='fixture', target='CCO', inventory=tuple(
        InventoryItem(smiles=s) for s in ('C=C', 'O')), budget=Budget(top_k=1))


def success(smiles, top_k):
    return {'status':'ok', 'version':'fixture-v1', 'predictions':[
        {'product':smiles, 'reactants':['C=C','O'], 'score':0.8,
         'source':{'tool':'fixture','version':'v1'}}]}


def run(tmp_path, factory=lambda: success, **kwargs):
    return run_comparison(tmp_path/'run', [fixture_task()], backend_factory=factory,
        backend_identity={'kind':'synthetic_fixture','sha256':'a'*64},
        cohort={'data_role':'smoke'}, policies={'legacy_bfs':run_fixed_workflow,
        'best_first':run_fixed_workflow}, **kwargs)


def test_comparison_freezes_plan_commits_decisions_and_replays_without_calls(tmp_path):
    calls=[]
    def factory():
        def backend(s,k):
            assert (tmp_path/'run'/'plan.json').is_file()
            calls.append((s,k))
            return success(s,k)
        return backend
    report=run(tmp_path,factory)
    assert len(calls)==2
    assert len(report['runs'])==4
    assert report['precomputation']['backend_invocations']==2
    assert report['precomputation']['unique_successful_keys']==1
    assert report['private_labels_read'] is False
    assert report['scientific_feasibility'] == 'not_evaluated'
    for row in report['runs']:
        assert row['accepted_submitted_routes']==1
        path=tmp_path/'run'/row['decision_path']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==row['decision_sha256']
        if row['mode']=='shared_precomputed':
            assert row['backend_invocations']==0 and row['pool_hits']==1
    with pytest.raises(FileExistsError):
        run(tmp_path)
    assert len(calls)==2


def test_failures_are_retained_and_not_cached(tmp_path):
    report=run(tmp_path,lambda:lambda s,k:{'status':'unavailable','diagnostic':'host path secret'})
    assert report['precomputation']['unique_successful_keys']==0
    assert all(row['accepted_submitted_routes']==0 for row in report['runs'])
    assert all(row['pool_misses']==1 for row in report['runs'] if row['mode']=='shared_precomputed')
    assert 'host path secret' not in (tmp_path/'run'/'expansion-pool.json').read_text()


def test_conflicting_prediction_results_are_excluded_from_shared_pool(tmp_path):
    calls=[]
    def factory():
        def backend(s,k):
            calls.append(s)
            result=success(s,k)
            result['predictions'][0]['score']=len(calls)/10
            return result
        return backend
    report=run(tmp_path,factory)
    assert report['precomputation']['conflicting_keys']==1
    assert report['precomputation']['unique_successful_keys']==0
    assert all(row['pool_misses']==1 for row in report['runs'] if row['mode']=='shared_precomputed')


def test_backend_exception_recorded_without_secret_message(tmp_path):
    def factory():
        def backend(s,k):
            raise RuntimeError('confidential-file-value')
        return backend
    report=run(tmp_path,factory)
    assert report['precomputation']['backend_failures']==2
    assert 'confidential-file-value' not in (tmp_path/'run'/'summary.json').read_text()


def test_metrics_reject_unknown_quantity_acquisition_and_invalid_routes():
    assessments=[{'route_id':'valid','graph_valid':True,'inventory_complete':True,
        'constraint_compliant':True,'quantity_status':'not_requested','acquisition_only':False}]
    for key,value in [('graph_valid',False),('inventory_complete',False),
        ('constraint_compliant',False),('quantity_status','unknown'),('acquisition_only',True)]:
        assessments.append({**assessments[0],key:value,'route_id':key})
    result={'search_states':7,'episode':{'routes':[], 'assessments':assessments,
        'submitted_route_ids':[a['route_id'] for a in assessments],
        'terminated':True,'truncated':False,'events':[],
        'usage':{'expansions':2,'actions':3,'wall_seconds':0.1}}}
    metrics=summarize_run(result)
    assert metrics['accepted_submitted_routes']==1
    assert metrics['rejected_submitted_routes']==5
    assert metrics['submitted_routes']==6


@pytest.mark.parametrize('bad', [True,0,101])
def test_invalid_group_count_fails_before_loading(bad,tmp_path):
    with pytest.raises(ValueError):
        select_development_tasks(tmp_path,'a'*64,group_count=bad)


def test_asset_pin_requires_complete_existing_assets(tmp_path):
    with pytest.raises(ValueError):
        pin_localretro_assets(tmp_path,Path('/missing/python'))


def test_empty_duplicate_or_invalid_cohort_rejected_before_output(tmp_path):
    for tasks in ([],[fixture_task(),fixture_task()]):
        with pytest.raises(ValueError):
            run_comparison(tmp_path/'bad',tasks,backend_factory=lambda:success,
                backend_identity={'kind':'fixture'},cohort={'data_role':'smoke'})
    with pytest.raises(ValueError):
        run_comparison(tmp_path/'bad',[fixture_task()],backend_factory=lambda:success,
            backend_identity={'kind':'fixture'},cohort={'data_role':'sealed_final'})
    assert not (tmp_path/'bad').exists()


def test_late_callback_settlement_records_started_call_before_next_arm(tmp_path):
    import time
    active=[]
    def factory():
        assert not active
        def callback(s,k):
            active.append(s)
            time.sleep(0.15)
            active.clear()
            return success(s,k)
        return callback
    task=fixture_task().model_copy(update={'budget':Budget(max_wall_seconds=0.1,top_k=1)})
    report=run_comparison(tmp_path/'late',[task],backend_factory=factory,
        backend_identity={'kind':'fixture'},cohort={'data_role':'smoke'},
        policies={'legacy_bfs':run_fixed_workflow,'best_first':run_fixed_workflow})
    assert report['precomputation']['backend_invocations']==2
    assert report['precomputation']['settlement_overhead_seconds']>0
    assert report['precomputation']['unique_successful_keys']==0
    assert not active


def test_changed_assets_invalidate_comparison_and_retain_report(tmp_path):
    asset=tmp_path/'asset'; asset.write_text('before')
    initial=hashlib.sha256(asset.read_bytes()).hexdigest()
    def factory():
        def callback(s,k):
            asset.write_text('after')
            return success(s,k)
        return callback
    with pytest.raises(RuntimeError,match='changed'):
        run_comparison(tmp_path/'changed',[fixture_task()],backend_factory=factory,
            backend_identity={'kind':'fixture','assets':{str(asset):initial}},
            cohort={'data_role':'smoke'},policies={'legacy_bfs':run_fixed_workflow,'best_first':run_fixed_workflow})
    assert json.loads((tmp_path/'changed'/'summary.json').read_text())['integrity']['unchanged'] is False


def test_real_policies_handle_invalid_first_proposal_end_to_end(tmp_path):
    def callback(s,k):
        valid=success(s,k)
        invalid={**valid['predictions'][0],'reactants':['C=C']}
        return {**valid,'predictions':[invalid,*valid['predictions']]}
    report=run_comparison(tmp_path/'actual',[fixture_task()],backend_factory=lambda:callback,
        backend_identity={'kind':'fixture'},cohort={'data_role':'smoke'})
    for mode in ('cold','shared_precomputed'):
        rows={r['arm']:r for r in report['runs'] if r['mode']==mode}
        assert rows['legacy_bfs']['rejected_submitted_routes']==1
        assert rows['best_first']['accepted_submitted_routes']==1
        assert rows['best_first']['accepted_top1']
    assert report['integrity']['unchanged']


def test_selection_uses_public_development_target_groups_and_all_variants(tmp_path):
    from synthesis_route_gym.dataset_bundle import build_bundle
    tasks=[{'task_id':f'task-{i}-{j}','target':target,'track':'reference_route',
        'partition':partition,'inventory_exclusions':[] if j==0 else ['O']}
        for i,(target,partition) in enumerate([('CCO','development'),('CCC','development'),('CCN','sealed_final')])
        for j in (0,1)]
    labels=[{'task_id':t['task_id'],'reference_route':{
        'route_id':t['task_id'],'target':t['target'],'steps':[]}} for t in tasks]
    receipt=build_bundle(tmp_path/'public',tmp_path/'private',tasks=tasks,labels=labels,
        inventory=['C=C','O'],assignments=[],provenance={'sources':[{
        'source_id':'fixture','url':'https://example.org/data','sha256':'a'*64,'license':'CC0'}]})
    selected,cohort=select_development_tasks(tmp_path/'public',receipt['public_manifest_sha256'],group_count=1)
    expected=min(('CCO','CCC'),key=lambda s:hashlib.sha256(s.encode()).hexdigest())
    assert len(selected)==2 and {t.target for t in selected}=={expected}
    assert all(t.budget.max_expansions==6 and t.budget.max_wall_seconds==120 for t in selected)
    assert cohort['data_role']=='development'
    with pytest.raises(ValueError,match='Insufficient'):
        select_development_tasks(tmp_path/'public',receipt['public_manifest_sha256'],group_count=3)
    with pytest.raises(ValueError):
        select_development_tasks(tmp_path/'public','0'*64,group_count=1)


def test_asset_pin_includes_sources_and_scientific_interpreter_metadata(tmp_path):
    import sys
    paths=['req_data/LocalRetro_boltz_USPTO_MIT.pth',
        'req_data/USPTO_MIT/atom_templates.csv','req_data/USPTO_MIT/bond_templates.csv',
        'req_data/USPTO_MIT/template_infos.csv','rebolt_update_opt/localretro/LocalRetro/default_config.json',
        'rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py',
        'rebolt_update_opt/localretro/LocalRetro/scripts/utils.py']
    for name in paths:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
    identity=pin_localretro_assets(tmp_path,Path(sys.executable))
    assert len(identity['assets'])==8
    assert identity['worker_runtime']['status']=='metadata_read'
    assert 'torch' in identity['worker_runtime']['versions']
    assert identity['adapter_timeout_seconds']==40


def test_worker_metadata_failure_remains_unknown(monkeypatch):
    import subprocess
    from synthesis_route_gym.search_benchmark import _worker_runtime
    def fail(*args,**kwargs):
        assert kwargs['timeout']==15 and 'API_KEY' not in kwargs['env']
        raise subprocess.TimeoutExpired('python',15)
    monkeypatch.setattr(subprocess,'run',fail)
    assert _worker_runtime('/missing')['status']=='unknown'


def test_unresolved_worker_aborts_before_another_arm():
    import threading
    from synthesis_route_gym.search_benchmark import _RecordedBackend
    started,release=threading.Event(),threading.Event()
    def callback(s,k):
        started.set();release.wait(2)
        return success(s,k)
    backend=_RecordedBackend(callback,'fixture')
    thread=threading.Thread(target=backend.expand,args=('CCO',10),daemon=True);thread.start()
    assert started.wait(1)
    with pytest.raises(RuntimeError,match='quiesce'):
        backend.settle(set(),timeout=0)
    release.set();thread.join(1);backend.settle(set())
    assert backend.expand('CCO',10)['status']=='error'


@pytest.mark.parametrize('raw',[None,{'status':'not-a-status'}, {'status':'ok','predictions':None},
    {'status':'ok','predictions':[{'product':'CCC','reactants':['C=C'],'score':0.5}]}])
def test_bad_backend_contracts_fail_closed(tmp_path,raw):
    report=run(tmp_path,lambda:lambda s,k:raw)
    assert report['precomputation']['backend_failures']==2
    assert report['precomputation']['unique_successful_keys']==0


def test_unresolved_settlement_preserves_current_episode_and_failure(tmp_path,monkeypatch):
    from synthesis_route_gym.search_benchmark import _RecordedBackend
    calls=[]
    def factory():
        calls.append('started')
        return success
    def fail(self,*args,**kwargs):
        raise RuntimeError('worker did not quiesce')
    monkeypatch.setattr(_RecordedBackend,'settle',fail)
    with pytest.raises(RuntimeError,match='quiesce'):
        run(tmp_path,factory)
    folder=tmp_path/'run'/'cold'/'fixture'/'legacy_bfs'
    assert (folder/'episode.json').is_file()
    assert (folder/'decision.json').is_file()
    failure=json.loads((folder/'failure.json').read_text())
    assert failure['status']=='worker_settlement_failed'
    assert len(failure['backend_calls'])==1
    assert len(calls)==1
