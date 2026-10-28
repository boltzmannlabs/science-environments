"""Frozen main-profile identity and host-controlled comparison prompts."""
from types import SimpleNamespace
import pytest
from synthesis_route_gym import agent_session as module
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.planning import environment_tool_schemas
from test_core import make_task


def options(tmp_path):
    home=tmp_path/'main-profile';home.mkdir()
    (home/'config.yaml').write_text('model:\n  default: fixture-model\n  provider: fixture-provider\n')
    return SimpleNamespace(profile_home=str(home),method='main_route_critic',model_calls=24,
        scientist_python='/trusted/python',scientist_source='/trusted/source')


def test_bridge_failure_keeps_resolved_identity_and_unknown_usage(tmp_path,monkeypatch):
    args=options(tmp_path)
    def fail(*a,**kw):raise module.BridgeError('sensitive runtime diagnostic')
    monkeypatch.setattr(module,'run_agent_scientist_bridge',fail)
    run=module.run_persistent_agent(args,SynthesisRouteEnv(make_task()),tmp_path/'runtime')
    assert run['agent']['model']=='fixture-model' and run['agent']['provider']=='fixture-provider'
    assert run['agent']['resource_accounting']=='unknown_after_bridge_interruption'
    assert 'ledger'not in run['agent'] and 'sensitive'not in str(run)


def test_closed_episode_and_changed_main_model_are_bound(tmp_path,monkeypatch):
    from pathlib import Path
    args=options(tmp_path);env=SynthesisRouteEnv(make_task());env.cancel('fixture')
    monkeypatch.setattr(module,'run_agent_scientist_bridge',lambda *a,**kw:pytest.fail('closed provider call'))
    run=module.run_persistent_agent(args,env,tmp_path/'runtime')
    assert run['agent']['model']=='fixture-model'
    assert run['agent']['resource_accounting']=='no_new_provider_request'
    (Path(args.profile_home)/'config.yaml').write_text('model:\n  default: other\n  provider: fixture-provider\n')
    with pytest.raises(ValueError,match='binding'):
        module.run_persistent_agent(args,env,tmp_path/'runtime',resume=True)


def test_prompt_and_tool_overrides_are_passed_and_bound_on_resume(tmp_path,monkeypatch):
    args=options(tmp_path);env=SynthesisRouteEnv(make_task());seen=[]
    schemas=[s for s in environment_tool_schemas()if s['name']in {'inspect','submit'}]
    def bridge(prompt,executor,**kw):
        seen.append((prompt,kw['tool_schemas']))
        return {'completed':False}
    monkeypatch.setattr(module,'run_agent_scientist_bridge',bridge)
    module.run_persistent_agent(args,env,tmp_path/'runtime',prompt='Fixed comparison task',tool_schemas=schemas)
    assert seen==[('Fixed comparison task',schemas)]
    with pytest.raises(ValueError,match='binding'):
        module.run_persistent_agent(args,env,tmp_path/'runtime',resume=True,prompt='Changed task',tool_schemas=schemas)
    with pytest.raises(ValueError,match='binding'):
        module.run_persistent_agent(args,env,tmp_path/'runtime',resume=True,prompt='Fixed comparison task',tool_schemas=schemas[:1])
    assert len(seen)==1


@pytest.mark.parametrize('prompt',['', '   ', 123])
def test_invalid_prompt_override_fails_before_provider_or_checkpoint(tmp_path,monkeypatch,prompt):
    args=options(tmp_path)
    monkeypatch.setattr(module,'run_agent_scientist_bridge',lambda *a,**kw:pytest.fail('invalid provider call'))
    with pytest.raises(ValueError):
        module.run_persistent_agent(args,SynthesisRouteEnv(make_task()),tmp_path/'runtime',prompt=prompt)
    assert not(tmp_path/'runtime').exists()


def test_forbidden_override_tools_fail_before_provider(tmp_path,monkeypatch):
    args=options(tmp_path)
    monkeypatch.setattr(module,'run_agent_scientist_bridge',lambda *a,**kw:pytest.fail('forbidden provider call'))
    with pytest.raises(ValueError):
        module.run_persistent_agent(args,SynthesisRouteEnv(make_task()),tmp_path/'runtime',
            tool_schemas=[{'name':'read_private_labels','parameters':{'type':'object'}}])
    assert not(tmp_path/'runtime').exists()
