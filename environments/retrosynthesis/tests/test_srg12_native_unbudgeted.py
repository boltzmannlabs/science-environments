"""Absent native limits, private IPC polling and same-profile accounting."""
import importlib.util
import os
from pathlib import Path
import sys
import threading

import pytest

from synthesis_route_gym import agent_bridge as bridge
from synthesis_route_gym.agent_runner import AgentBudget, run_agent_scientist
from test_agent_runner import main_home, native_host_double, SCHEMAS
from test_agent_bridge import _fake_command

def test_native_iteration_budget_has_no_finite_ceiling():
    source = os.environ.get('SRG_SCIENTIST_SOURCE')
    if not source:
        pytest.skip('Optional native integration: set SRG_SCIENTIST_SOURCE to a compatible Agent Scientist checkout')
    path = Path(source).expanduser()/'agent/iteration_budget.py'
    if not path.is_file():
        pytest.skip('Optional native integration: SRG_SCIENTIST_SOURCE has no agent/iteration_budget.py')
    spec = importlib.util.spec_from_file_location('native_iteration_budget', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    budget = module.IterationBudget(None)
    budget._used = sys.maxsize * 2
    assert budget.consume()
    assert budget.remaining is None
    assert budget.used == sys.maxsize * 2 + 1
    budget.refund()
    assert budget.used == sys.maxsize * 2


def test_native_adapter_passes_absent_ceilings(main_home, native_host_double):
    result = run_agent_scientist('test', lambda *_: {}, tool_schemas=SCHEMAS,
        profile_home=main_home, budget=AgentBudget.unbudgeted())
    constructor = native_host_double['constructor']
    assert constructor['max_iterations'] is None
    assert constructor['max_tokens'] is None
    assert constructor['run_budget_seconds'] is None
    assert constructor['unbudgeted_run'] is True
    assert result['ledger']['model_calls'] == 1


def test_channel_absent_deadline_polls_liveness(monkeypatch):
    calls = []
    channel = bridge._Channel(10, 11, None, alive=lambda: len(calls) < 2)
    def select(*args):
        calls.append(args[-1])
        return [], [], []
    monkeypatch.setattr(bridge.select, 'select', select)
    with pytest.raises(bridge.BridgeError, match='exited'):
        channel.receive()
    assert calls == [0.1, 0.1]


def test_channel_cancel_interrupts_unlimited_wait():
    event = threading.Event()
    event.set()
    channel = bridge._Channel(10, 11, None, cancelled=event.is_set)
    with pytest.raises(bridge.BridgeError, match='cancelled'):
        channel.receive()


def test_unbudgeted_handshake_transitions_to_no_episode_deadline(monkeypatch):
    fake = '''import os,sys,json,time
r=os.fdopen(int(sys.argv[1])); w=os.fdopen(int(sys.argv[2]),'w')
config=json.loads(r.readline())
w.write(json.dumps({'type':'ready'})+'\\n');w.flush()
time.sleep(.15)
w.write(json.dumps({'type':'result','result':{'completed':True}})+'\\n');w.flush()
'''
    monkeypatch.setattr(bridge, '_child_command', _fake_command(fake))
    result = bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
        scientist_python=sys.executable, scientist_source=Path.cwd(),
        budget=AgentBudget.unbudgeted(), startup_grace_seconds=.1)
    assert result['completed']


def test_unbudgeted_startup_is_still_bounded(monkeypatch):
    monkeypatch.setattr(bridge, '_child_command', _fake_command('import time;time.sleep(30)'))
    with pytest.raises(bridge.BridgeError, match='deadline'):
        bridge.run_agent_scientist_bridge('test', lambda *_: {}, tool_schemas=[],
            scientist_python=sys.executable, scientist_source=Path.cwd(),
            budget=AgentBudget.unbudgeted(), startup_grace_seconds=.05)
