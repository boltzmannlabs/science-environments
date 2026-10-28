"""Private IPC integration tests using a local fake child, never a model."""
import os
from pathlib import Path
import sys
import pytest
from synthesis_route_gym.agent_runner import AgentBudget
from synthesis_route_gym.agent_bridge import run_agent_scientist_bridge, BridgeError


def _fake_command(source):
    def command(executable, scientist_source, read_fd, write_fd):
        return [sys.executable, '-c', source, str(read_fd), str(write_fd)]
    return command


FAKE = '''import os,sys,json
r=os.fdopen(int(sys.argv[1]));w=os.fdopen(int(sys.argv[2]),'w')
config=json.loads(r.readline())
w.write(json.dumps({'type':'tool','name':'inspect','arguments':{}})+'\\n');w.flush()
reply=json.loads(r.readline())
w.write(json.dumps({'type':'result','result':{'completed':True,'observed':reply['result']}})+'\\n');w.flush()
'''


def test_parent_executes_tools_and_returns_child_result(monkeypatch):
    monkeypatch.setattr('synthesis_route_gym.agent_bridge._child_command', _fake_command(FAKE))
    result = run_agent_scientist_bridge('test', lambda name, args: {'name': name},
        tool_schemas=[{'name':'inspect','parameters':{'type':'object'}}],
        scientist_python=sys.executable, scientist_source=Path.cwd())
    assert result == {'completed': True, 'observed': {'name': 'inspect'}}


def test_child_timeout_kills_process_group(monkeypatch):
    monkeypatch.setattr('synthesis_route_gym.agent_bridge._child_command', _fake_command('import time;time.sleep(30)'))
    with pytest.raises(BridgeError, match='deadline'):
        run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            budget=AgentBudget(wall_seconds=0.1), startup_grace_seconds=0)


def test_invalid_or_oversize_ipc_is_rejected(monkeypatch):
    script = "import os,sys;os.write(int(sys.argv[2]),b'x'*9000000)"
    monkeypatch.setattr('synthesis_route_gym.agent_bridge._child_command', _fake_command(script))
    with pytest.raises(BridgeError, match='size'):
        run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd())


def test_child_bootstraps_installed_dependencies_and_uses_native_runner(monkeypatch, tmp_path):
    from types import SimpleNamespace
    import synthesis_route_gym.agent_bridge as bridge
    monkeypatch.setenv('SCI_HOME', str(tmp_path))
    monkeypatch.setattr(sys, 'path', list(sys.path))
    monkeypatch.setitem(sys.modules, 'pm.environments', SimpleNamespace(
        committed_venv=lambda source: tmp_path, site_packages=lambda runtime: tmp_path))
    monkeypatch.setattr('site.addsitedir', lambda value: None)
    monkeypatch.setitem(sys.modules, 'run_agent', SimpleNamespace())
    received = []
    class Channel:
        def __init__(self, *args):
            self.replies = iter([{'budget': {}, 'prompt': 'test', 'tool_schemas': [],
                                  'mode': 'main', 'profile_home': None},
                                 {'type': 'result', 'result': {'ok': True}}])
        def receive(self):
            return next(self.replies)
        def send(self, value):
            received.append(value)
    monkeypatch.setattr(bridge, '_Channel', Channel)
    def run(prompt, executor, **kwargs):
        assert executor('inspect', {}) == {'ok': True}
        return {'completed': True}
    monkeypatch.setattr('synthesis_route_gym.agent_runner.run_agent_scientist', run)
    bridge._child(1, 2, tmp_path)
    assert received[0]['type'] == 'tool'
    assert received[1] == {'type': 'result', 'result': {'completed': True}}


@pytest.mark.parametrize('message,match', [
    ({'type':'tool','name':'terminal','arguments':{}}, 'capability'),
    ({'type':'error','error':'ExampleError'}, 'ExampleError')])
def test_parent_rejects_unapproved_tools_and_reports_sanitized_child_errors(monkeypatch, message, match):
    import json
    script = 'import os,sys;os.write(int(sys.argv[2]),' + repr((json.dumps(message)+'\n').encode()) + ')'
    monkeypatch.setattr('synthesis_route_gym.agent_bridge._child_command', _fake_command(script))
    with pytest.raises(BridgeError, match=match):
        run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd())


def test_environment_exception_is_sanitized():
    from synthesis_route_gym.agent_bridge import _execute_bounded
    def fail(*args):
        raise RuntimeError('secret provider detail')
    result = _execute_bounded(fail, 'inspect', {}, 1)
    assert result == {'type': 'error', 'error': 'Environment operation failed'}


def test_checkpoint_is_acknowledged_only_after_host_persistence(monkeypatch):
    import json
    import synthesis_route_gym.agent_bridge as bridge
    script = '''import os,sys,json
r=os.fdopen(int(sys.argv[1]));w=os.fdopen(int(sys.argv[2]),'w')
config=json.loads(r.readline())
w.write(json.dumps({'type':'checkpoint','state':{'ledger':{'model_calls':1}}})+'\\n');w.flush()
ack=json.loads(r.readline())
w.write(json.dumps({'type':'result','result':{'ack':ack,'resume':config.get('resume_state')}})+'\\n');w.flush()
'''
    monkeypatch.setattr(bridge, '_child_command', _fake_command(script))
    stored = []
    result = bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
        scientist_python=sys.executable, scientist_source=Path.cwd(),
        resume_state={'previous': True}, checkpoint=lambda state: stored.append(state))
    assert stored == [{'ledger': {'model_calls': 1}}]
    assert result['ack'] == {'type': 'checkpoint_ack'}
    assert result['resume'] == {'previous': True}


def test_checkpoint_failure_cancels_executor_and_never_acknowledges(monkeypatch):
    import synthesis_route_gym.agent_bridge as bridge
    script = '''import os,sys,json,time
r=os.fdopen(int(sys.argv[1]));w=os.fdopen(int(sys.argv[2]),'w')
r.readline();w.write(json.dumps({'type':'checkpoint','state':{}})+'\\n');w.flush();time.sleep(30)
'''
    monkeypatch.setattr(bridge, '_child_command', _fake_command(script))
    cancelled = []
    def fail(state):
        raise OSError('disk full')
    with pytest.raises(OSError):
        bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            checkpoint=fail, cancel=lambda reason: cancelled.append(reason))
    assert cancelled == ['bridge_interrupted']


def test_tool_action_ids_and_timeout_cancellation(monkeypatch):
    import synthesis_route_gym.agent_bridge as bridge
    fake = FAKE.replace("'arguments':{}", "'arguments':{},'action_id':'action-1'")
    monkeypatch.setattr(bridge, '_child_command', _fake_command(fake))
    seen = []
    def action(name, args, *, action_id):
        seen.append(action_id)
        return {'ok': True}
    bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[{'name':'inspect'}],
        scientist_python=sys.executable, scientist_source=Path.cwd(), action_executor=action)
    assert seen == ['action-1']


def test_timeout_notifies_cancellation_callback(monkeypatch):
    import synthesis_route_gym.agent_bridge as bridge
    monkeypatch.setattr(bridge, '_child_command', _fake_command('import time;time.sleep(30)'))
    cancelled = []
    with pytest.raises(BridgeError):
        bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            budget=AgentBudget(wall_seconds=.05), startup_grace_seconds=0,
            cancel=lambda reason: cancelled.append(reason))
    assert cancelled == ['bridge_interrupted']


def test_remaining_episode_time_includes_startup_and_bounds_bridge(monkeypatch):
    import time
    import synthesis_route_gym.agent_bridge as bridge
    monkeypatch.setattr(bridge, '_child_command', _fake_command('import time;time.sleep(30)'))
    started = time.monotonic()
    with pytest.raises(BridgeError, match='deadline'):
        bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            remaining_seconds=.05, startup_grace_seconds=30)
    assert time.monotonic() - started < 2


@pytest.mark.parametrize('remaining', [0, -1, True, float('nan'), float('inf')])
def test_invalid_remaining_episode_time_rejects_before_spawn(remaining):
    with pytest.raises(ValueError, match='Remaining'):
        run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(), remaining_seconds=remaining)


@pytest.mark.parametrize('ack,expected', [({'type':'checkpoint_ack'}, 'result'), ({'type':'wrong'}, 'error')])
def test_child_requires_host_checkpoint_ack_before_proceeding(monkeypatch, tmp_path, ack, expected):
    from types import SimpleNamespace
    import synthesis_route_gym.agent_bridge as bridge
    monkeypatch.setattr(sys, 'path', list(sys.path))
    monkeypatch.setitem(sys.modules, 'pm.environments', SimpleNamespace(
        committed_venv=lambda source: tmp_path, site_packages=lambda runtime: tmp_path))
    monkeypatch.setattr('site.addsitedir', lambda value: None)
    monkeypatch.setitem(sys.modules, 'run_agent', SimpleNamespace())
    sent = []
    class Channel:
        def __init__(self, *args):
            self.replies = iter([{'budget': {}, 'prompt': 'test', 'tool_schemas': [],
                                 'mode': 'main', 'profile_home': None, 'resume_state': {'known': True}}, ack])
        def receive(self): return next(self.replies)
        def send(self, value): sent.append(value)
    monkeypatch.setattr(bridge, '_Channel', Channel)
    def run(prompt, executor, **kw):
        assert kw['resume_state'] == {'known': True}
        kw['checkpoint']({'reserved_tokens': 42})
        return {'completed': True}
    monkeypatch.setattr('synthesis_route_gym.agent_runner.run_agent_scientist', run)
    bridge._child(1, 2, tmp_path)
    assert sent[0] == {'type':'checkpoint','state':{'reserved_tokens':42}}
    assert sent[1]['type'] == expected


def test_persistent_bridge_rejects_missing_action_identity(monkeypatch):
    import synthesis_route_gym.agent_bridge as bridge
    monkeypatch.setattr(bridge, '_child_command', _fake_command(FAKE))
    with pytest.raises(BridgeError, match='identity'):
        bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[{'name':'inspect'}],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            action_executor=lambda *a, **kw: pytest.fail('invalid identity executed'))
