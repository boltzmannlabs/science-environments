"""Selected development evaluation never opens reserved final answers."""
import json
from pathlib import Path

import pytest

from synthesis_route_gym.dataset_bundle import build_bundle, commit_decision
from synthesis_route_gym import strategist_benchmark as benchmark


def route():
    return {'route_id':'r1','target':'CCO','steps':[{'step_id':'s1','product':'CCO',
        'reactants':[{'smiles':'CCBr'},{'smiles':'O'}],
        'source_tool':'fixture','source_version':'1'}]}


@pytest.fixture
def bundle(tmp_path):
    tasks=[{'task_id':name,'track':'reference_route','partition':part,'target':'CCO'}
           for name,part in [('dev','development'),('other','development'),('final','sealed_final')]]
    receipt=build_bundle(tmp_path/'public',tmp_path/'private',tasks=tasks,
        labels=[{'task_id':r['task_id'],'reference_route':route()}for r in tasks],
        provenance={'sources':[{'source_id':'fixture','url':'https://example.org/data',
                    'sha256':'1'*64,'license':'CC0'}],'baseline_protocol_sha256':'2'*64},
        inventory=['CCBr','O'],assignments=[])
    return tmp_path,receipt


def score(bundle, task='dev', routes=None, **changes):
    root,receipt=bundle
    path=root/f'{task}-decision.json'
    digest=commit_decision(path,{'task_id':task,'routes':[route()]if routes is None else routes})
    args={'expected_manifest_sha256':receipt['public_manifest_sha256'],
          'expected_private_manifest_sha256':receipt['private_manifest_sha256'],**changes}
    return benchmark.score_selected_development(root/'public',root/'private',path,digest,**args)


def test_only_selected_private_label_is_opened(bundle,monkeypatch):
    original=benchmark._read
    seen=[]
    def tracked(path):
        seen.append(Path(path))
        return original(path)
    monkeypatch.setattr(benchmark,'_read',tracked)
    result=score(bundle)
    private=[p.relative_to(bundle[0]/'private').as_posix()for p in seen if bundle[0]/'private' in p.parents]
    assert private==['manifest.json','labels/dev.json']
    assert result['reference_match_at_k'] is True
    assert result['inventory_compliant_reference_recovery']['at_k'] is True
    assert result['scope']=='retrospective_reference_comparison_not_new_experimental_validation'
    assert result['private_access_scope']=='selected_development_label_only'
    assert result['independent_chemical_review']=='not_performed'


def test_final_is_rejected_before_any_private_open(bundle,monkeypatch):
    original=benchmark._read
    def tracked(path):
        assert bundle[0]/'private' not in Path(path).parents
        return original(path)
    monkeypatch.setattr(benchmark,'_read',tracked)
    with pytest.raises(ValueError,match='development'):
        score(bundle,task='final')


def test_empty_submission_remains_zero_quality(bundle):
    result=score(bundle,routes=[])
    assert result['submitted_routes']==0
    assert result['reference_match_at_k'] is False


@pytest.mark.parametrize('kind',['public_anchor','private_anchor','private_label','private_manifest','decision','missing_label'])
def test_tampering_rejected(bundle,kind):
    root,receipt=bundle
    decision=root/'decision.json'
    digest=commit_decision(decision,{'task_id':'dev','routes':[route()]})
    public_sha=receipt['public_manifest_sha256'];private_sha=receipt['private_manifest_sha256']
    if kind=='public_anchor':public_sha='0'*64
    if kind=='private_anchor':private_sha='0'*64
    target={'private_label':root/'private/labels/dev.json','private_manifest':root/'private/manifest.json','decision':decision}.get(kind)
    if target:target.write_bytes(target.read_bytes()+b' ')
    if kind=='missing_label':(root/'private/labels/dev.json').unlink()
    with pytest.raises(ValueError):
        benchmark.score_selected_development(root/'public',root/'private',decision,digest,
            expected_manifest_sha256=public_sha,expected_private_manifest_sha256=private_sha)


def test_unselected_final_mutation_is_not_read_or_silently_claimed_verified(bundle):
    (bundle[0]/'private/labels/final.json').write_text('not opened')
    result=score(bundle)
    assert result['private_bundle_fully_verified'] is False
    assert result['reference_match_at_k'] is True


def test_symlink_selected_label_rejected(bundle):
    root,_=bundle
    target=root/'private/labels/dev.json'
    target.unlink();target.symlink_to(root/'private/labels/other.json')
    with pytest.raises(ValueError,match='[Ss]ymlink'):
        score(bundle)


def run(arm='main',calls=4,charged=100,actual=80,advice=0):
    return {'method':arm,'episode':{'task':{'task_id':'dev','target':'CCO'},
        'submitted_route_ids':['r1'],'terminated':True,'truncated':False,
        'usage':{'actions':5,'expansions':2,'wall_seconds':20}},
        'agent':{'completed':True,'model':'configured','provider':'configured',
            'ledger':{'model_calls':calls,'charged_tokens':charged,'actual_tokens':actual,
                'reserved_tokens':charged-actual,'unsettled_requests':int(charged>actual)},
            'strategist_runs':[{'completed':True}for _ in range(advice)]}}


def score_fixture(hit=True):
    return {'task_id':'dev','reference_match_at_k':hit,
        'inventory_compliant_reference_recovery':{'at_k':hit},
        'route_checks':[{'graph_valid':True,'inventory_complete':True,'constraint_compliant':True,
            'quantity_status':'not_requested','acquisition_only':False,'solved':False}],
        'submitted_routes':1,'scope':'retrospective_reference_comparison_not_new_experimental_validation'}


def test_summary_uses_authoritative_ledger_once_including_advisor():
    result=benchmark.summarize_run(run('main_strategist',calls=5,advice=1),score_fixture(),arm='main_strategist',task_id='dev')
    assert result['model_calls']==5 and result['charged_tokens']==100
    assert result['strategist_invocations']==1
    assert result['deterministically_accepted_routes']==1
    assert result['scientifically_solved_routes']==0
    assert result['actual_tokens']==80 and result['reserved_tokens']==20


def test_fixed_resources_zero_llm_and_failure_missing_agent_usage_stays_unknown():
    fixed=run('fixed');fixed.pop('agent')
    assert benchmark.summarize_run(fixed,score_fixture(),arm='fixed',task_id='dev')['model_calls']==0
    failed=run();failed['agent']={'completed':False,'error_type':'BridgeError'}
    result=benchmark.summarize_run(failed,score_fixture(),arm='main',task_id='dev')
    assert result['model_calls'] is None and result['charged_tokens'] is None
    assert result['completed'] is False


@pytest.mark.parametrize('change',[{'task_id':'wrong'},{'scope':'experimental_validation'}])
def test_score_identity_or_scope_mismatch_rejected(change):
    with pytest.raises(ValueError):
        benchmark.summarize_run(run(),{**score_fixture(),**change},arm='main',task_id='dev')


def paired_rows(hit=True,advice=1):
    return [benchmark.summarize_run(run(arm,calls=4+(arm=='main_strategist'),advice=advice if arm=='main_strategist'else 0),
        score_fixture(hit),arm=arm,task_id='dev')for arm in ('main','main_strategist')]


def test_small_pilot_never_promoted_and_zero_quality_tie_not_resource_win():
    result=benchmark.summarize_comparison(paired_rows(False,0))
    assert result['promotion_eligible'] is False
    assert result['paired']['ties']==1
    assert result['independent_target_count']==1
    assert {'small_development_cohort','no_positive_quality','strategist_not_invoked'}<=set(result['promotion_blockers'])


def test_paired_wins_losses_and_resource_differences_kept():
    rows=paired_rows()
    rows[0]={**rows[0],'inventory_compliant_reference_recovered':False}
    result=benchmark.summarize_comparison(rows)
    assert result['paired']['wins']==1
    assert result['paired']['model_call_delta']==1
    assert result['promotion_eligible'] is False


def test_unpaired_and_duplicate_observations_rejected():
    rows=paired_rows()
    for bad in (rows[:1],rows+[rows[0]],[]):
        with pytest.raises(ValueError):benchmark.summarize_comparison(bad)


def test_missing_usage_does_not_become_zero_in_aggregate():
    rows=paired_rows()
    rows[0]={**rows[0],'model_calls':None,'charged_tokens':None}
    result=benchmark.summarize_comparison(rows)
    assert result['paired']['model_call_delta'] is None
    assert 'incomplete_resource_accounting' in result['promotion_blockers']


@pytest.mark.parametrize('change',[{'bundle_kind':'public'}, {'public_manifest_sha256':'0'*64}, {'files':{}}, {'extra':'field'}])
def test_invalid_reanchored_private_manifest_rejected(bundle,change):
    import hashlib
    root,receipt=bundle
    path=root/'private/manifest.json'
    path.write_text(json.dumps({**json.loads(path.read_text()),**change}))
    with pytest.raises(ValueError):
        score(bundle,expected_private_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest())


@pytest.mark.parametrize('name',['private','private/labels','private/labels/dev.json'])
def test_private_permissions_remain_restrictive(bundle,name):
    (bundle[0]/name).chmod(0o755)
    with pytest.raises(ValueError,match='permissions'):
        score(bundle)


@pytest.mark.parametrize('value',[-1,True,float('inf')])
def test_invalid_resource_telemetry_rejected(value):
    raw=run();raw['agent']['ledger']['model_calls']=value
    with pytest.raises(ValueError):
        benchmark.summarize_run(raw,score_fixture(),arm='main',task_id='dev')


def test_known_profile_mismatch_rejected_but_failed_unknown_profile_is_reported():
    rows=paired_rows()
    changed=[rows[0],{**rows[1],'model':'other'}]
    with pytest.raises(ValueError,match='model/provider'):
        benchmark.summarize_comparison(changed)
    unknown=[{**rows[0],'model':None,'provider':None,'completed':False},rows[1]]
    assert 'unverified_model_profile' in benchmark.summarize_comparison(unknown)['promotion_blockers']


def test_failed_bridge_recovers_durable_counts_without_losing_pending_advice():
    raw=run();raw['agent']={'completed':False,'error_type':'BridgeError'}
    raw['runtime_checkpoint']={'ledger':{'counts':{'model_calls':3,'actual_tokens':100,'reserved_tokens':20},
        'requests':{'1':{'actual':100},'2':{'actual':0},'3':{'actual':None}}},
        'strategist':{'consultation':{'status':'pending'},'runs':[]}}
    result=benchmark.summarize_run(raw,score_fixture(),arm='main',task_id='dev')
    assert result['model_calls']==3 and result['charged_tokens']==120
    assert result['unsettled_requests']==1 and result['strategist_invocations']==1
    assert result['resource_source']=='durable_checkpoint'


def test_skipped_advice_is_not_counted_as_invocation():
    raw=run('main_strategist');raw['agent']['strategist_state']={'consultation':{'status':'skipped_budget'},'runs':[]}
    result=benchmark.summarize_run(raw,score_fixture(),arm='main_strategist',task_id='dev')
    assert result['strategist_invocations']==0


def test_selected_public_loader_reads_only_manifest_task_inventory(bundle,monkeypatch):
    root,receipt=bundle
    (root/'public/tasks/final.json').write_text('must not be opened')
    original=benchmark._read;seen=[]
    def tracked(path):
        seen.append(Path(path).relative_to(root/'public').as_posix())
        return original(path)
    monkeypatch.setattr(benchmark,'_read',tracked)
    task=benchmark.load_public_selected_development(root/'public','dev',
        expected_manifest_sha256=receipt['public_manifest_sha256'])
    assert task['partition']=='development'and task['target']=='CCO'
    assert seen==['manifest.json','tasks/dev.json','inventory.json']


@pytest.mark.parametrize('name',['tasks/dev.json','inventory.json'])
def test_selected_public_loader_checks_every_used_file_hash(bundle,name):
    root,receipt=bundle
    file=root/'public'/name;file.write_bytes(file.read_bytes()+b' ')
    with pytest.raises(ValueError,match='hash'):
        benchmark.load_public_selected_development(root/'public','dev',
            expected_manifest_sha256=receipt['public_manifest_sha256'])


def runner_module():
    import importlib.util
    path=Path(__file__).parents[1]/'artifacts/steps/srg-07/run-development.py'
    if not path.is_file():
        pytest.skip('Optional archived Step 7 runner is not bundled in the source-only release')
    spec=importlib.util.spec_from_file_location('strategist_pilot_runner',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def runner_plan(tmp_path):
    import hashlib
    from synthesis_route_gym.schemas import Task, Budget
    tasks=[]
    for ident in ('task-a','task-b'):
        path=tmp_path/f'{ident}.json'
        path.write_text(Task(task_id=ident,target='CCO',inventory=()).model_dump_json())
        tasks.append({'task_id':ident,'task_path':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (tmp_path/'config.yaml').write_text('model:\n  default: configured\n  provider: configured\n')
    plan={'tasks':tasks,'arms':['best_first','main','main_strategist'],
          'budget':Budget().model_dump(mode='json'),'model':'configured','provider':'configured',
          'runtime':{'repo_root':str(tmp_path),'chemistry_python':'python','adapter_timeout_seconds':10,
            'model_calls':8,'scientist_python':'python','scientist_source':str(tmp_path),'profile_home':str(tmp_path)}}
    path=tmp_path/'plan.json';path.write_text(json.dumps(plan))
    return path,plan


class NoInferenceAdapter:
    def __init__(self,**kwargs):pass
    def expand(self,*args):raise AssertionError('No inference authorized in test')


def test_runner_preserves_failures_and_commits_all_arms_before_labels(tmp_path):
    module=runner_module();path,_=runner_plan(tmp_path);seen=[]
    def fixed(env,**kwargs):
        seen.append((env.task.task_id,'best_first'))
        env.dispatch('submit',{'route_ids':[]})
        return {'episode':env.export()}
    def agent(args,env,runtime_path,**kwargs):
        seen.append((env.task.task_id,args.method))
        env.dispatch('inspect',{})
        if args.method=='main_strategist':raise RuntimeError('synthetic failure')
        env.dispatch('submit',{'route_ids':[]})
        return {'episode':env.export(),'agent':{'completed':True}}
    rows=module.run_experiment(path,tmp_path/'out',agent_runner=agent,
        fixed_runner=fixed,adapter_factory=NoInferenceAdapter)
    assert len(rows)==6 and seen==[(a,b)for a,arms in [('task-a',['best_first','main','main_strategist']),
        ('task-b',['best_first','main_strategist','main'])]for b in arms]
    assert all(r['submitted_routes']==0 for r in rows)
    failed=json.loads((tmp_path/'out/task-a/main_strategist/run.json').read_text())
    assert failed['episode']['terminated'] is False
    assert failed['episode']['usage']['actions']==1
    assert failed['agent']['error_type']=='RuntimeError'
    receipts=json.loads((tmp_path/'out/commitments.json').read_text())
    assert receipts['labels_opened'] is False
    assert receipts['all_decisions_committed_before_evaluation'] is True
    with pytest.raises(FileExistsError):
        module.run_experiment(path,tmp_path/'out',agent_runner=agent,fixed_runner=fixed,adapter_factory=NoInferenceAdapter)


@pytest.mark.parametrize('mutation',['identity','hash','budget','profile'])
def test_runner_checks_every_task_budget_hash_profile_before_external_run(tmp_path,mutation):
    module=runner_module();path,plan=runner_plan(tmp_path)
    if mutation=='identity':plan['tasks'][1]['task_id']='wrong'
    if mutation=='hash':plan['tasks'][1]['sha256']='0'*64
    if mutation=='budget':plan['budget']['max_actions']=1
    if mutation=='profile':plan['model']='wrong'
    path.write_text(json.dumps(plan))
    def forbidden(*args,**kwargs):raise AssertionError('Must validate all tasks before running')
    with pytest.raises(ValueError):
        module.run_experiment(path,tmp_path/'out',agent_runner=forbidden,
            fixed_runner=forbidden,adapter_factory=NoInferenceAdapter)
    assert not (tmp_path/'out').exists()


def test_runner_freeze_refuses_changed_assets_before_calls(tmp_path):
    module=runner_module();path,_=runner_plan(tmp_path)
    freeze=tmp_path/'freeze.json';freeze.write_text(json.dumps({'source_hashes':{str(path):'0'*64},'asset_hashes':{}}))
    def forbidden(*args,**kwargs):raise AssertionError('Changed assets must block execution')
    with pytest.raises(ValueError,match='[Ff]reeze'):
        module.run_experiment(path,tmp_path/'out',freeze_path=freeze,
            agent_runner=forbidden,fixed_runner=forbidden,adapter_factory=NoInferenceAdapter)


def test_runner_parses_the_same_task_bytes_that_were_hashed(tmp_path,monkeypatch):
    module=runner_module();path,plan=runner_plan(tmp_path)
    def forbidden(path):raise AssertionError('Task must not be reopened through read() after hashing')
    monkeypatch.setattr(module,'read',forbidden)
    tasks=module.preflight(path,plan)
    assert [t.task_id for t in tasks]==['task-a','task-b']


def test_summary_reports_effective_pilot_k_and_rejects_excess_submissions():
    raw=run();raw['episode']['task']['budget']={'top_k':3}
    scored={**score_fixture(),'top_k':5}
    result=benchmark.summarize_run(raw,scored,arm='main',task_id='dev')
    assert result['task_top_k']==3 and result['reference_evaluator_top_k']==5
    with pytest.raises(ValueError,match='top-k'):
        benchmark.summarize_run(raw,{**scored,'submitted_routes':4},arm='main',task_id='dev')
