from synthesis_route_gym.handoff import build_handoff_feedback
from test_handoff import episode


def test_none_runtime_checkpoint_does_not_hide_bridge_failure():
    manifest,export=episode(submit=False)
    result=build_handoff_feedback(manifest,export,agent_run={'runtime_checkpoint':None,
        'agent':{'completed':False,'error_type':'BridgeError','stop_reason':'bridge_interrupted'}})
    assert result['execution_status']=='interrupted'
    assert result['resources']['actual_tokens'] is None


def test_nested_provider_failure_is_not_in_progress():
    manifest,export=episode(submit=False)
    result=build_handoff_feedback(manifest,export,agent_run={'agent':{'completed':True,
        'runs':[{'error_type':'TimeoutError','completed':False}]}})
    assert result['execution_status']=='failed'
