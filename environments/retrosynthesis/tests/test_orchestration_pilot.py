"""Synthetic frozen-runner checks; no provider calls or private chemistry labels."""
import importlib.util
import json
from pathlib import Path

import pytest
from synthesis_route_gym.critic_benchmark import run_direct_critic_policy
from test_core import make_task,make_route

ROOT=Path(__file__).resolve().parents[1]
STEP=ROOT/'artifacts/steps/srg-11'

if any(not (STEP / name).is_file() for name in ('prepare-pilot.py', 'run-pilot.py')):
    pytest.skip('Optional archived Step 11 pilot runners are not bundled in the source-only release',
                allow_module_level=True)

def module(name):
    spec=importlib.util.spec_from_file_location(name,STEP/(name+'.py'))
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

PREP=module('prepare-pilot');RUN=module('run-pilot')

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2)+'\n');return path

@pytest.fixture
def prepared(tmp_path):
    rows=[]
    for ident in ('case-z','case-b','case-a'):
        task=make_task().model_dump(mode='json')
        task={**task,'task_id':ident,'budget':{'max_actions':80,'max_expansions':6,'max_wall_seconds':600.0,'max_llm_tokens':350000,'top_k':3}}
        route=make_route().model_dump(mode='json');routes=[{**route,'route_id':f'r{i}'}for i in range(3)]
        source={'record_id':'source-1','document_id':'synthetic','source_url':'https://example.org/fixture','locator':'synthetic test only',
            'reactants':[u['smiles']for u in route['steps'][0]['reactants']],'product':route['target'],'claim_kind':'proxy',
            'retrieved_at':'2026-01-01T00:00:00Z','source_content_sha256':'a'*64}
        routes=[{**r,'steps':[{**s,'evidence_ids':['source-1']}for s in r['steps']]}for r in routes]
        path=write(tmp_path/'original'/f'{ident}.json',{'case_id':ident,'data_role':'previously_used_development',
            'task':task,'routes':routes,'sources':[source],'source_family':'synthetic','source_case_id':ident,'label_sha256':'f'*64})
        rows.append({'case_id':ident,'public_path':str(path),'public_sha256':RUN.sha(path),'labels_path':'/never/open/private.json'})
    manifest=write(tmp_path/'original/manifest.json',{'schema_version':'srg09-development-manifest-v1','cases':rows,'final_labels_opened':False})
    profile=tmp_path/'profile';profile.mkdir();(profile/'config.yaml').write_text('model:\n  default: test-main\n  provider: openai-codex\n')
    pilot=tmp_path/'pilot'
    PREP.prepare_pilot(manifest,pilot,profile_home=profile,scientist_python=Path(__import__('sys').executable),scientist_source=tmp_path/'scientist')
    return pilot


def freeze(pilot):
    plan=RUN.read(pilot/'plan.json');cases=RUN.load_cases(plan)
    files={str(p):RUN.sha(p)for p in RUN.required_anchors(pilot/'plan.json',plan,cases)}
    return write(pilot/'freeze.json',{'schema_version':'srg11-execution-freeze-v1','files':files})


def fake_agent(args,env,path,*,resume=False,prompt=None,tool_schemas=None):
    assert not resume and 'closed shortlist' in prompt
    assert {s['name']for s in tool_schemas}=={'inspect','validate','review_routes','submit'}
    value=run_direct_critic_policy(env,[r['route_id']for r in env.export()['routes']])
    return {**value,'method':args.method,'agent':{'completed':True,'conversation_completed':True,'model':'test-main','provider':'openai-codex',
        'ledger':{'model_calls':2,'tool_calls':2,'actual_tokens':10,'reserved_tokens':0,'charged_tokens':10,'unsettled_requests':0}}}


def test_preparation_uses_first_two_public_cases_and_no_label_paths(prepared):
    plan=RUN.read(prepared/'plan.json');cases=RUN.load_cases(plan)
    assert [c['case_id']for c in cases]==['case-a','case-b']
    assert plan['arms']==list(RUN.ARMS) and plan['repeat_ids']==[0]
    assert plan['policies']['main_adaptive']['enabled_roles']==[]
    for case in cases:
        assert 'label' not in json.dumps(case)
        assert case['handoff']['candidate_id'].endswith(case['case_id'])
        assert len(case['handoff']['upstream_payload_sha256'])==64


def test_preparation_and_output_refuse_overwrite(prepared):
    with pytest.raises(FileExistsError):
        PREP.prepare_pilot(prepared/'plan.json',prepared,profile_home=prepared.parent/'profile',scientist_python='/bin/python',scientist_source='/tmp/sci')


def test_frozen_ten_episode_end_to_end_retains_handoff_and_feedback(prepared):
    frozen=freeze(prepared)
    result=RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,agent_runner=fake_agent)
    assert len(result['runs'])==10 and result['final_labels_opened']is False
    assert result['claims_scientific_improvement']is False
    for row in result['runs']:
        run=RUN.read(row['result_path']);assert run['handoff_manifest']['handoff']['candidate_id']==row['candidate_id']
        assert run['feedback']['candidate_id']==row['candidate_id']
        assert run['feedback']['source_job_id']=='srg11-public-candidate-pool'
        assert row['submission_status']=='submitted_routes'
        assert run['run']['bootstrap']['actions']==4
    assert all(not row['selection_changed']for row in result['feedback_comparison'])
    with pytest.raises(FileExistsError):
        RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,agent_runner=fake_agent)


def test_agent_failure_is_retained_without_retry(prepared):
    frozen=freeze(prepared);calls=[]
    def failed(args,env,path,**kwargs):
        calls.append((args.method,env.task.task_id));raise RuntimeError('synthetic bridge failure')
    result=RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,agent_runner=failed)
    assert len(calls)==8 and len(set(calls))==8
    assert sum(row['submission_status']=='not_submitted'for row in result['runs'])==8
    for row in result['runs']:
        if row['arm']=='direct_tool':continue
        value=RUN.read(row['result_path']);assert value['feedback']['resources']['actual_tokens']is None


@pytest.mark.parametrize('tamper',['case','plan','profile','source','missing_anchor'])
def test_frozen_input_changes_fail_before_provider(prepared,tamper):
    frozen=freeze(prepared);plan=RUN.read(prepared/'plan.json')
    if tamper=='case':path=Path(plan['cases'][0]['path'])
    elif tamper=='plan':path=prepared/'plan.json'
    elif tamper=='profile':path=prepared.parent/'profile/config.yaml'
    elif tamper=='source':path=Path(RUN.read(plan['cases'][0]['path'])['source_public_path'])
    else:
        value=RUN.read(frozen);value['files'].pop(str(STEP/'run-pilot.py'));write(frozen,value);path=None
    if path:path.write_text(path.read_text()+' ')
    with pytest.raises(ValueError):
        RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,agent_runner=lambda *a,**k:pytest.fail('Provider reached'))


def test_same_pool_feedback_rule_changes_only_when_gate_changes():
    pool=[{'candidate_id':'a','upstream_priority':0},{'candidate_id':'b','upstream_priority':1}]
    feedback=[{'candidate_id':'a','deterministically_eligible_route_ids':[]},
              {'candidate_id':'b','deterministically_eligible_route_ids':['r']}]
    result=RUN.feedback_selection(pool,feedback)
    assert result['without_feedback']=='a' and result['with_feedback']=='b'
    assert result['selection_changed'] and result['claims_downstream_gain']is False
    with pytest.raises(ValueError):RUN.feedback_selection(pool,feedback[:1])


def test_missing_handoff_result_is_explicit_failure(prepared):
    frozen=freeze(prepared)
    def failed(*args,**kwargs):raise RuntimeError('synthetic handoff setup failure')
    result=RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,handoff_runner=failed,agent_runner=fake_agent)
    assert len(result['runs'])==10 and all(r['submission_status']=='not_submitted'for r in result['runs'])
    assert all(r['runner_failure']for r in result['runs'])
    committed=RUN.read(prepared/'runs/commitments.json')
    assert committed['all_attempts_recorded'] is True
    assert committed['all_decisions_committed'] is False


def test_invalid_return_retains_raw_artifacts_and_never_retries(prepared):
    from synthesis_route_gym.handoff_runner import run_handoff
    frozen=freeze(prepared);calls=[]
    def damaged(*args,**kwargs):
        result=run_handoff(*args,**kwargs);calls.append(args[0].method)
        return {**result,'feedback':{**result['feedback'],'candidate_id':'wrong'}}
    result=RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,handoff_runner=damaged,agent_runner=fake_agent)
    assert len(calls)==10
    for row in result['runs']:
        value=RUN.read(row['result_path'])
        assert value['runner_failure'] and value['unverified_result']['run']['episode']['terminated']
        assert value['unverified_result']['artifact_paths']['run']
        assert value['failure_stage']=='result_verification'
        assert row['resources'] is None
        assert row['unverified_resources'] is not None
    assert RUN.read(prepared/'runs/commitments.json')['all_decisions_committed'] is False


@pytest.mark.parametrize('tamper',['route','inventory','source','candidate','extra'])
def test_refrozen_derived_fixture_cannot_change_original_inputs(prepared,tamper):
    plan=RUN.read(prepared/'plan.json');path=Path(plan['cases'][0]['path']);case=RUN.read(path)
    if tamper=='route':case['routes'][0]['route_id']='different'
    elif tamper=='inventory':case['handoff']['inventory']=[]
    elif tamper=='source':case['sources'][0]['source_url']='https://example.org/different'
    elif tamper=='candidate':case['handoff']['candidate_id']='different'
    else:case['private_labels']={'do_not_allow':True}
    write(path,case);plan['cases'][0]['sha256']=RUN.sha(path);write(prepared/'plan.json',plan)
    with pytest.raises(ValueError):RUN.load_cases(plan)


def test_feedback_requires_bound_selected_route_subset():
    case={'handoff':{'candidate_id':'a'},'case_id':'case-a'}
    pool=[{'candidate_id':'a','upstream_priority':0},{'candidate_id':'b','upstream_priority':1}]
    with pytest.raises(ValueError):
        RUN.feedback_selection(pool,[{'candidate_id':'a','deterministically_eligible_route_ids':'r'},
                                     {'candidate_id':'b','deterministically_eligible_route_ids':[]}])


def test_nonobject_return_is_retained_as_unverified_without_crashing_campaign(prepared):
    frozen=freeze(prepared)
    result=RUN.run_pilot(prepared/'plan.json',prepared/'runs',freeze_path=frozen,
        handoff_runner=lambda *args,**kwargs:[1],agent_runner=fake_agent)
    assert len(result['runs'])==10 and all(row['runner_failure']for row in result['runs'])
    assert RUN.read(result['runs'][0]['result_path'])['unverified_result']==[1]
