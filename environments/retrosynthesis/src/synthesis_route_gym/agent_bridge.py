"""Private-pipe bridge between the chemistry environment and installed Sci Python.

The child receives schemas and observations, never an evaluator path or a shell
capability. Its model/provider resolution remains in agent_runner.
"""
from __future__ import annotations

from contextvars import copy_context
from dataclasses import asdict
import json
import os
from pathlib import Path
import queue
import select
import signal
import subprocess
import threading
import time
from uuid import uuid4

import sys
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from synthesis_route_gym.agent_runner import AgentBudget

MAX_MESSAGE_BYTES = 8 * 1024 * 1024


class BridgeError(RuntimeError):
    """The isolated runtime could not complete within its IPC contract."""


class _Channel:
    def __init__(self, read_fd, write_fd, deadline, *, alive=None, cancelled=None):
        self.read_fd, self.write_fd, self.deadline = read_fd, write_fd, deadline
        self.alive, self.cancelled = alive, cancelled
        self.buffer = b''

    def remaining(self):
        if self.cancelled is not None and self.cancelled():
            raise BridgeError('Agent bridge cancelled')
        if self.deadline is None:
            return None
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise BridgeError('Agent bridge deadline exceeded')
        return remaining

    def _wait(self, *, writing=False):
        while True:
            remaining = self.remaining()
            interval = .1 if remaining is None else min(.1, remaining)
            ready = select.select([] if writing else [self.read_fd],
                                  [self.write_fd] if writing else [], [], interval)
            if ready[1 if writing else 0]:
                return
            if self.alive is not None and not self.alive():
                raise BridgeError('Agent runtime exited while awaiting IPC')

    def send(self, value):
        data = json.dumps(value, allow_nan=False).encode() + b'\n'
        if len(data) > MAX_MESSAGE_BYTES:
            raise BridgeError('IPC message exceeds size limit')
        offset = 0
        while offset < len(data):
            self._wait(writing=True)
            offset += os.write(self.write_fd, data[offset:offset + 4096])

    def receive(self):
        while b'\n' not in self.buffer:
            if len(self.buffer) >= MAX_MESSAGE_BYTES:
                raise BridgeError('IPC message exceeds size limit')
            self._wait()
            chunk = os.read(self.read_fd, 65536)
            if not chunk:
                raise BridgeError('Agent runtime closed its private channel')
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b'\n', 1)
        if len(line) > MAX_MESSAGE_BYTES:
            raise BridgeError('IPC message exceeds size limit')
        try:
            value = json.loads(line)
        except (ValueError, UnicodeError) as exc:
            raise BridgeError('Invalid IPC JSON') from exc
        if not isinstance(value, dict):
            raise BridgeError('IPC payload must be an object')
        return value


def _child_command(executable, scientist_source, read_fd, write_fd):
    return [str(executable), str(Path(__file__).resolve()), '--child',
            str(read_fd), str(write_fd), str(scientist_source)]


def _execute_bounded(executor, name, arguments, timeout, *, check=None):
    replies = queue.Queue(maxsize=1)
    def execute():
        try:
            replies.put(('result', executor(name, arguments)))
        except Exception:
            replies.put(('error', 'Environment operation failed'))
    thread = threading.Thread(target=copy_context().run, args=(execute,), daemon=True)
    thread.start()
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        if check is not None:
            check()
        remaining = None if deadline is None else deadline - time.monotonic()
        if remaining is not None and remaining <= 0:
            raise BridgeError('Environment operation exceeded bridge deadline')
        try:
            kind, result = replies.get(timeout=.1 if remaining is None else min(.1, remaining))
            break
        except queue.Empty:
            continue
    return {'type': kind, kind: result}


def run_agent_scientist_bridge(prompt, executor, *, tool_schemas, scientist_python,
                               scientist_source, budget=None, mode='main',
                               profile_home=None, startup_grace_seconds=30, resume_state=None,
                               checkpoint=None, cancel=None, action_executor=None, remaining_seconds=None,
                               orchestration_policy=None, cancelled=None):
    """Launch the trusted local Sci runtime; hold the scientific executor here.

    ``scientist_python`` and ``scientist_source`` are operator configuration,
    never model-supplied arguments. Callback implementations must enforce their
    own backend cancellation: timed-out local daemon threads cannot be killed.
    """
    limits = budget or AgentBudget()
    if not callable(executor) or not 0 <= startup_grace_seconds <= 120:
        raise ValueError('Invalid executor or startup allowance')
    if remaining_seconds is not None and (isinstance(remaining_seconds, bool) or not isinstance(remaining_seconds, (int, float))
                                          or not 0 < remaining_seconds < float('inf')):
        raise ValueError('Remaining episode allowance must be positive and finite')
    if limits.regime == 'unbudgeted' and remaining_seconds is not None:
        raise ValueError('Unbudgeted episodes cannot have a remaining wall allowance')
    started = time.monotonic()
    episode_seconds = (remaining_seconds if remaining_seconds is not None else
                       None if limits.wall_seconds is None else startup_grace_seconds + limits.wall_seconds)
    parent_deadline = None if episode_seconds is None else started + episode_seconds
    startup_seconds = startup_grace_seconds or limits.wall_seconds or .001
    startup_deadline = started + startup_seconds
    if parent_deadline is not None:
        startup_deadline = min(startup_deadline, parent_deadline)
    executable, source = Path(scientist_python).expanduser().resolve(), Path(scientist_source).expanduser().resolve()
    if not executable.is_file() or not source.is_dir():
        raise ValueError('Trusted Sci executable and source directory must exist')
    to_child_r, to_child_w = os.pipe()
    from_child_r, from_child_w = os.pipe()
    proc, finished = None, False
    try:
        env = {**os.environ, 'PYTHONPATH': str(Path(__file__).resolve().parents[1])}
        proc = subprocess.Popen(_child_command(executable, source, to_child_r, from_child_w),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            pass_fds=(to_child_r, from_child_w), close_fds=True, start_new_session=True, env=env)
        os.close(to_child_r)
        os.close(from_child_w)
        to_child_r = from_child_w = -1
        channel = _Channel(from_child_r, to_child_w, startup_deadline,
                           alive=lambda: proc.poll() is None, cancelled=cancelled)
        channel.send({'prompt': prompt, 'tool_schemas': tool_schemas, 'budget': asdict(limits),
                      'protocol_version': 2, 'startup_seconds': startup_seconds,
                      'mode': mode, 'profile_home': str(profile_home) if profile_home else None,
                      'orchestration_policy': orchestration_policy,
                      'resume_state': resume_state})
        allowed = {schema['name'] for schema in tool_schemas}
        ready = False
        while True:
            request = channel.receive()
            if not ready:
                if limits.regime == 'unbudgeted' and request.get('type') != 'ready':
                    raise BridgeError('Unbudgeted runtime requires an explicit startup handshake')
                ready = True
                channel.deadline = parent_deadline
                if request.get('type') == 'ready':
                    continue
            if request.get('type') == 'result':
                finished = True
                return request['result']
            if request.get('type') == 'checkpoint':
                if not isinstance(request.get('state'), dict):
                    raise BridgeError('Invalid runtime checkpoint')
                if checkpoint is not None:
                    checkpoint(request['state'])
                channel.send({'type': 'checkpoint_ack'})
                continue
            if request.get('type') == 'error':
                raise BridgeError('Agent runtime failed: ' + request.get('error', 'unknown'))
            if request.get('type') != 'tool' or request.get('name') not in allowed or not isinstance(request.get('arguments'), dict):
                raise BridgeError('Child requested a capability outside the environment contract')
            action_id = request.get('action_id')
            if action_executor is not None:
                if not isinstance(action_id, str) or not 1 <= len(action_id) <= 128:
                    raise BridgeError('Missing or invalid action identity')
                callback = lambda name, args: action_executor(name, args, action_id=action_id)
            else:
                callback = executor
            def check_operation():
                channel.remaining()
                if proc.poll() is not None:
                    raise BridgeError('Agent runtime exited during environment operation')
            channel.send(_execute_bounded(callback, request['name'], request['arguments'],
                                         channel.remaining(), check=check_operation))
    finally:
        if not finished and cancel is not None:
            try:
                cancel('bridge_interrupted')
            except Exception:
                import logging
                logging.getLogger(__name__).error('Episode cancellation callback failed')
        for fd in (to_child_r, to_child_w, from_child_r, from_child_w):
            if fd >= 0:
                os.close(fd)
        if proc is not None:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
            proc.wait(timeout=5)


def _child(read_fd, write_fd, source):
    import site
    import sys
    os.environ['SCI_HOME'] = str(Path.home() / '.sci')
    sys.path.insert(0, str(source))
    from pm.environments import committed_venv, site_packages
    runtime = committed_venv(Path(source))
    if runtime is None:
        raise BridgeError('No committed Agent Scientist dependency environment')
    site.addsitedir(str(site_packages(runtime)))
    # Host bootstrap may re-exec into its committed interpreter. Do this before
    # consuming any non-replayable pipe request.
    import run_agent  # noqa: F401
    channel = _Channel(read_fd, write_fd, time.monotonic() + 120)
    request = channel.receive()
    limits = AgentBudget(**request['budget'])
    channel.deadline = None if limits.wall_seconds is None else time.monotonic() + limits.wall_seconds
    if request.get('protocol_version') == 2:
        channel.send({'type': 'ready'})
    def executor(name, arguments):
        channel.send({'type': 'tool', 'name': name, 'arguments': arguments, 'action_id': uuid4().hex})
        response = channel.receive()
        if response.get('type') != 'result':
            raise BridgeError('Environment operation failed')
        return response['result']
    def checkpoint(state):
        channel.send({'type': 'checkpoint', 'state': state})
        if channel.receive().get('type') != 'checkpoint_ack':
            raise BridgeError('Host did not persist the runtime checkpoint')
    from synthesis_route_gym.agent_runner import run_agent_scientist
    try:
        result = run_agent_scientist(request['prompt'], executor, tool_schemas=request['tool_schemas'],
            budget=limits, mode=request['mode'], profile_home=request['profile_home'],
            orchestration_policy=request.get('orchestration_policy'),
            resume_state=request.get('resume_state'), checkpoint=checkpoint)
        channel.send({'type': 'result', 'result': result})
    except Exception as exc:
        # Provider exceptions may include credential-bearing URLs; expose type only.
        channel.send({'type': 'error', 'error': type(exc).__name__})


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 5 or sys.argv[1] != '--child':
        raise SystemExit('Internal child entrypoint requires private pipe descriptors')
    _child(int(sys.argv[2]), int(sys.argv[3]), Path(sys.argv[4]))
