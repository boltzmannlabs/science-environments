"""Persistent local handoff acceptance uses deterministic callbacks, never providers."""
import json
from types import SimpleNamespace
import pytest
from synthesis_route_gym.handoff_runner import run_handoff
from synthesis_route_gym.episode_store import EpisodeStore
from test_handoff import payload
from test_core import make_route


@pytest.fixture(autouse=True)
def profile_fixture(tmp_path,monkeypatch):
    from synthesis_route_gym.agent_runner import MainProfile
    profile=MainProfile(tmp_path/'profile','fixture-model','fixture-provider')
    monkeypatch.setattr('synthesis_route_gym.handoff_runner.resolve_main_profile',lambda home:profile)
    monkeypatch.setattr('synthesis_route_gym.agent_session.resolve_main_profile',lambda home:profile)


def args(**updates):
    return SimpleNamespace(**{'method':'main','model_calls':3,'scientist_python':'python',
        'scientist_source':'.','profile_home':'.',**updates})


def submit(args,env,path,*,resume=False):
    assert not resume
    env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')})
    env.dispatch('submit',{'route_ids':['r1']})
    return {'method':args.method,'agent':{'completed':True,'conversation_completed':True},'episode':env.export()}


def test_persistent_handoff_and_closed_resume_do_not_repeat_calls(tmp_path):
    root=tmp_path/'run'
    result=run_handoff(args(),payload(),root,agent_runner=submit)
    assert result['feedback']['submission_status']=='submitted_routes'
    assert result['feedback']['commitment']['durability']=='durable_local_store'
    assert (root/'attempts/0001/receipt.json').is_file()
    assert EpisodeStore(root/'environment').load()[0]['submitted_route_ids']==['r1']
    again=run_handoff(args(),payload(),root,resume=True,agent_runner=lambda *a,**kw:pytest.fail('closed replay'))
    assert again==result


def test_failed_attempt_is_preserved_and_can_resume(tmp_path):
    root=tmp_path/'run'
    def fail(args,env,path,*,resume=False):
        env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')})
        raise RuntimeError('SECRET provider detail')
    result=run_handoff(args(),payload(),root,agent_runner=fail)
    assert result['feedback']['submission_status']=='not_submitted'
    assert result['feedback']['execution_status']=='failed'
    assert result['feedback']['resources']['actual_tokens'] is None
    assert 'SECRET' not in json.dumps(result)
    def finish(args,env,path,*,resume=False):
        assert len(env.export()['routes'])==1
        env.dispatch('submit',{'route_ids':['r1']})
        return {'agent':{'completed':True},'episode':env.export()}
    again=run_handoff(args(),payload(),root,resume=True,agent_runner=finish)
    assert again['feedback']['submission_status']=='submitted_routes'
    assert (root/'attempts/0001/feedback.json').exists() and (root/'attempts/0002/feedback.json').exists()


@pytest.mark.parametrize('change',['candidate','source','seed','method','limits','config','artifact','manifest'])
def test_resume_rejects_changed_bindings_and_artifacts(tmp_path,change):
    root=tmp_path/'run';run_handoff(args(),payload(),root,agent_runner=submit)
    request=payload();options={};a=args()
    if change=='candidate':request['candidate_id']='other'
    if change=='source':request['source_job_id']='other'
    if change=='seed':request['seed']=1
    if change=='method':a.method='main_adaptive'
    if change=='limits':a.model_calls=9
    if change=='config':options={'source_access_mode':'evidence_retrieval'}
    if change=='artifact':(root/'attempts/0001/feedback.json').write_text('{}')
    if change=='manifest':(root/'handoff.json').write_text('{}')
    with pytest.raises(ValueError):run_handoff(a,request,root,resume=True,environment_options=options,agent_runner=submit)


def test_invalid_inputs_existing_paths_and_symlinks_fail_before_callback(tmp_path):
    root=tmp_path/'run';root.mkdir()
    with pytest.raises(FileExistsError):run_handoff(args(),payload(),root,agent_runner=submit)
    (tmp_path/'link').symlink_to(root,target_is_directory=True)
    with pytest.raises(ValueError):run_handoff(args(),payload(),tmp_path/'link',agent_runner=submit)
    with pytest.raises(ValueError):run_handoff(args(seed=1),payload(),tmp_path/'seed',agent_runner=submit)
    with pytest.raises(ValueError):run_handoff(args(),payload(),tmp_path/'bad',environment_options={'task':{}},agent_runner=submit)
    assert not (tmp_path/'bad').exists()


def test_forged_callback_episode_preserved_as_runner_failure(tmp_path):
    def forged(args,env,path,*,resume=False):
        return {'agent':{'completed':True},'episode':{**env.export(),'seed':999}}
    result=run_handoff(args(),payload(),tmp_path/'run',agent_runner=forged)
    assert result['feedback']['execution_status']=='failed'
    assert result['run']['agent']['error_type']=='ValueError'


def test_concurrent_resume_cannot_admit_another_execution(tmp_path):
    root=tmp_path/'run'
    def active(a,env,path,*,resume=False):
        with pytest.raises(ValueError,match='active'):
            run_handoff(a,payload(),root,resume=True,agent_runner=submit)
        return {'agent':{'completed':False},'episode':env.export()}
    result=run_handoff(args(),payload(),root,agent_runner=active)
    assert result['feedback']['execution_status']=='incomplete'


@pytest.mark.parametrize('kind',['profile','policy'])
def test_closed_resume_rejects_same_path_profile_or_policy_changes(tmp_path,monkeypatch,kind):
    from synthesis_route_gym.agent_runner import MainProfile
    root=tmp_path/'run';a=args(method='main_adaptive')
    policy=tmp_path/'policy.json';policy.write_text('{}');a.orchestration_policy=str(policy)
    run_handoff(a,payload(),root,agent_runner=submit)
    if kind=='profile':
        monkeypatch.setattr('synthesis_route_gym.handoff_runner.resolve_main_profile',lambda home:MainProfile(tmp_path/'profile','other-model','fixture-provider'))
    else:
        policy.write_text(json.dumps({'enabled_roles':['route_critic'],'experimental':True,'max_consultations':1}))
    with pytest.raises(ValueError,match='binding'):
        run_handoff(a,payload(),root,resume=True,agent_runner=submit)


def test_native_persistent_runner_retains_unsettled_ledger_then_resumes(tmp_path,monkeypatch):
    from synthesis_route_gym.agent_accounting import SharedLedger,AgentBudget
    from synthesis_route_gym.agent_bridge import BridgeError
    import synthesis_route_gym.agent_session as session
    root=tmp_path/'run'
    def first(prompt,executor,**kw):
        ledger=SharedLedger(AgentBudget(max_model_calls=3,max_tool_calls=200,wall_seconds=1800,max_total_tokens=100000))
        ledger.claim_model_call(estimated_input_tokens=20,reserved_output_tokens=30)
        kw['checkpoint']({'ledger':ledger.export_state()})
        raise BridgeError('secret failure detail')
    monkeypatch.setattr(session,'run_agent_scientist_bridge',first)
    result=run_handoff(args(),payload(),root)
    assert result['feedback']['execution_status']=='interrupted'
    assert result['feedback']['resources']['reserved_tokens']==50
    assert result['feedback']['resources']['fully_settled_actual_tokens'] is None
    assert result['feedback']['commitment']['agent_head_sha256']
    def second(prompt,executor,**kw):
        ledger=SharedLedger.from_state(kw['resume_state']['ledger'])
        assert ledger.snapshot()['reserved_tokens']==50
        executor('submit',{'route_ids':[]})
        return {'completed':True,'ledger':ledger.snapshot()}
    monkeypatch.setattr(session,'run_agent_scientist_bridge',second)
    resumed=run_handoff(args(),payload(),root,resume=True)
    assert resumed['feedback']['submission_status']=='submitted_empty'
    assert resumed['feedback']['resources']['reserved_tokens']==50


def test_unknown_pending_attempt_is_retained_without_overwriting(tmp_path):
    root=tmp_path/'run'
    def interrupted(a,env,path,**kwargs):
        raise SystemExit()
    with pytest.raises(SystemExit):
        run_handoff(args(),payload(),root,agent_runner=interrupted)
    state,_=EpisodeStore(root/'handoff-state').load()
    assert state['pending_attempt']==1
    result=run_handoff(args(),payload(),root,resume=True,agent_runner=submit)
    assert result['feedback']['submission_status']=='submitted_routes'
    assert result['artifact_paths']['feedback'].endswith('0002/feedback.json')


def test_keyboard_interrupt_preserves_failure_feedback_and_closes_episode(tmp_path):
    def stop(a,env,path,**kwargs):
        env.dispatch('propose_route',{'route':make_route().model_dump(mode='json')})
        raise KeyboardInterrupt()
    result=run_handoff(args(),payload(),tmp_path/'interrupted',agent_runner=stop)
    assert result['feedback']['execution_status']=='interrupted'
    assert result['feedback']['submission_status']=='not_submitted'
    assert result['run']['episode']['truncated']
