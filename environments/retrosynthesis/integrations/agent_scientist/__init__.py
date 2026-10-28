"""Optional normal-workflow plugin; existing Agent Scientist tools stay enabled.

Only stdlib is imported here. Chemistry can live in a different interpreter.
Bound benchmark dispatch remains separate and never permits normal-only actions.
"""
import atexit
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from threading import RLock

MAX_FRAME_BYTES = 4_000_000
MAX_REPLY_BYTES = 16_000_000
NORMAL_ACTIONS = frozenset({
    'reset', 'inspect', 'propose_route', 'validate', 'submit', 'rank_routes',
    'review_routes', 'capabilities', 'expand', 'predict_conditions', 'retrieve_sources',
    'forward_check', 'observe_condition', 'predict_impurities', 'compare_process',
    'retrieve_biocatalysis', 'score_cn_conditions', 'predict_reaction_yield',
    'application_report', 'condition_options', 'observe_route_condition',
    'predict_route_impurities', 'retrieve_application_sources',
    'generate_routes', 'import_routes', 'close'})
_clients = []
RUNTIME_KEYS = frozenset({'SRG_PACKAGE_ROOT', 'SRG_CHEMISTRY_PYTHON',
    'REBOLT_ROOT', 'REBOLT_PYTHON', 'SRG_BACKEND_TIMEOUT_SECONDS'})


def _installed_runtime():
    """Read setup-owned settings beside the profile plugin, never tool arguments."""
    path = Path(__file__).with_name('runtime.json')
    if not path.exists():
        return {}
    try:
        if path.is_symlink() or path.stat().st_size > 4096:
            raise ValueError('Invalid runtime file')
        settings = json.loads(path.read_text(encoding='utf-8'))
        if (not isinstance(settings, dict) or set(settings) != RUNTIME_KEYS or
                any(not isinstance(value, str) or not value for value in settings.values()) or
                any(not Path(settings[key]).is_absolute() for key in RUNTIME_KEYS - {'SRG_BACKEND_TIMEOUT_SECONDS'})):
            raise ValueError('Invalid runtime settings')
        return settings
    except (OSError, ValueError, UnicodeError) as exc:
        raise RuntimeError('Invalid retrosynthesis runtime configuration') from exc


def _close_clients():
    for client in _clients:
        client.close()


atexit.register(_close_clients)


class _ChemistryClient:
    def __init__(self):
        self.process = None
        self.lock = RLock()

    def _start(self):
        installed = _installed_runtime()
        python = Path(os.environ.get('SRG_CHEMISTRY_PYTHON') or
                      installed.get('SRG_CHEMISTRY_PYTHON') or sys.executable).expanduser()
        if not python.is_absolute() or not python.is_file() or not os.access(python, os.X_OK):
            raise RuntimeError('Chemistry runtime unavailable; configure SRG_CHEMISTRY_PYTHON')
        root = os.environ.get('SRG_PACKAGE_ROOT') or installed.get('SRG_PACKAGE_ROOT')
        source = Path(root).expanduser().resolve() / 'src' if root else Path(__file__).resolve().parents[2] / 'src'
        if root and not (source / 'synthesis_route_gym').is_dir():
            raise RuntimeError('Chemistry package source unavailable; check SRG_PACKAGE_ROOT')
        source_arg = str(source) if (source / 'synthesis_route_gym').is_dir() else ''
        bootstrap = ('import runpy,sys; '
                     'sys.path.insert(0,sys.argv[1]) if sys.argv[1] else None; '
                     'runpy.run_module("synthesis_route_gym.interactive_session",run_name="__main__")')
        allowed = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'LD_LIBRARY_PATH', 'OMP_NUM_THREADS',
                   'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'CUDA_VISIBLE_DEVICES',
                   'REBOLT_ROOT', 'REBOLT_PYTHON', 'SRG_BACKEND_TIMEOUT_SECONDS')
        environment = {key: os.environ[key] for key in allowed if key in os.environ}
        environment = {**{key: value for key, value in installed.items() if key in allowed},
                       **environment}
        self.process = subprocess.Popen([str(python), '-I', '-c', bootstrap, source_arg],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            env=environment, start_new_session=True)

    def request(self, request):
        payload = json.dumps(request, allow_nan=False).encode() + b'\n'
        if len(payload) > MAX_FRAME_BYTES:
            raise ValueError('Tool request exceeds protocol capacity')
        with self.lock:
            if self.process is None:
                self._start()
            if self.process.poll() is not None:
                raise RuntimeError('Chemistry runtime stopped; existing sessions are unavailable')
            try:
                self.process.stdin.write(payload)
                self.process.stdin.flush()
                line = self.process.stdout.readline(MAX_REPLY_BYTES + 1)
                if not line or len(line) > MAX_REPLY_BYTES or not line.endswith(b'\n'):
                    self.close()
                    raise RuntimeError('Chemistry runtime failed or exceeded protocol capacity')
                result = json.loads(line)
                if not isinstance(result, dict):
                    raise ValueError('Invalid chemistry response')
                return result
            except (OSError, ValueError) as exc:
                self.close()
                raise RuntimeError('Chemistry runtime communication failed') from exc

    def close(self):
        process = self.process
        if process is None:
            return
        if process.poll() is None:
            try:
                process.stdin.close()
                process.wait(timeout=1)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    process.wait(timeout=1)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    process.wait()
        for stream in (process.stdin, process.stdout):
            if stream is not None and not stream.closed:
                stream.close()


def register(ctx):
    global _clients
    client = _ChemistryClient()
    _clients = [*_clients, client]
    if callable(getattr(ctx, 'on_unload', None)):
        ctx.on_unload(client.close)

    def handle(args, **kwargs):
        try:
            if (not isinstance(args, dict) or set(args) - {'action', 'arguments', 'session_id'}
                    or args.get('action') not in NORMAL_ACTIONS
                    or not isinstance(args.get('arguments', {}), dict)
                    or ('session_id' in args and not isinstance(args['session_id'], str))):
                raise ValueError('Action and arguments do not match the environment contract')
            action, arguments = args['action'], args.get('arguments', {})
            bound = sys.modules.get('synthesis_route_gym.agent_runner')
            if bound is not None and bound.has_bound_executor():
                result = bound.dispatch_bound_action(action, arguments)
            else:
                from sci_constants import sci_home_key
                result = client.request({'profile': str(sci_home_key()), 'action': action,
                                         'arguments': arguments, 'session_id': args.get('session_id')})
            return json.dumps(result, allow_nan=False)
        except (ValueError, RuntimeError, KeyError, TypeError, OSError) as exc:
            return json.dumps({'success': False, 'error': str(exc)})

    ctx.register_tool(
        name='srg_action', toolset='synthesis_route_gym',
        schema={'name': 'srg_action', 'description':
            'Optional synthesis workspace alongside existing retrosynthesis tools. Reset a task; import_routes '
            '(format, payload, optional provenance) records existing outputs; generate_routes '
            '(search_policy: breadth_first/best_first/synthchem_astar/synthchem_mcts/synthchem_portfolio, '
            'optional expansion_top_k) generates drafts without submitting. Inspect, validate, rank and '
            'submit route IDs. Close releases a session. All chemistry remains predicted until supported.',
            'parameters': {'type': 'object', 'properties': {
                'action': {'type': 'string', 'enum': sorted(NORMAL_ACTIONS)},
                'arguments': {'type': 'object', 'description':
                    'reset: task (target, inventory, constraints, budget) and optional seed. '
                    'import_routes: format=srg-route-candidates-v1 with a list of RouteCandidate objects, '
                    'or format=rebolt-scored-paths-v1 with parsed downloaded topN/path/idx JSON; '
                    'optional provenance uses job_name, doc_id, artifact_id, source_version. '
                    'generate_routes: optional search_policy and expansion_top_k. '
                    'propose_route: route. validate: route_id. rank_routes/submit: route_ids. '
                    'inspect/close: empty object.'},
                'session_id': {'type': 'string', 'description': 'Returned by reset; required for subsequent normal-session actions.'}},
                'required': ['action'], 'additionalProperties': False}}, handler=handle)
