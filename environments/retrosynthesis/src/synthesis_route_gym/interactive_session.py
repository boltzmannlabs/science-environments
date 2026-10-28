"""Optional normal-workflow sessions; no LLM, global registry or evaluator access.

The scientific host can run in a separate chemistry interpreter. Its inputs are
bounded tool requests, never executable paths or commands supplied by a model.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import math
import os
import sys
import time
from threading import RLock
from pathlib import Path
from uuid import uuid4

MAX_FRAME_BYTES = 4_000_000
MAX_REPLY_BYTES = 16_000_000
SEARCH_POLICIES = frozenset({'breadth_first', 'best_first', 'synthchem_astar',
                             'synthchem_mcts', 'synthchem_portfolio'})


class _DraftWorkflow:
    """Reuse search while leaving final submission to the normal main agent."""
    def __init__(self, env):
        self.env = env
        self.route_ids = []

    def __getattr__(self, name):
        return getattr(self.env, name)

    def dispatch(self, action, arguments, **kwargs):
        if action != 'submit':
            return self.env.dispatch(action, arguments, **kwargs)
        self.route_ids = list(arguments['route_ids'])
        accepted = []
        for ident in self.route_ids:
            response = self.env.dispatch('validate', {'route_id': ident})
            result = response.get('result', {})
            if (response['status'] == 'ok' and result.get('graph_valid')
                    and result.get('inventory_complete') and result.get('constraint_compliant')
                    and result.get('quantity_status') in {'complete', 'not_requested'}
                    and not result.get('acquisition_only')):
                accepted.append(ident)
        return {'status': 'ok', 'result': {'accepted_route_ids': accepted,
                'submitted_route_ids': [], 'draft_only': True}}


class InteractiveSessions:
    """Profile-owned sessions with explicit capacity, and no unbudgeted TTL."""
    def __init__(self, *, expand=None, clock=time.monotonic, capacity=32, backend_versions=None,
                 backend_assets=None):
        if type(capacity) is not int or not 1 <= capacity <= 1000:
            raise ValueError('Invalid host session capacity')
        self.sessions = {}
        self.expand, self.clock, self.capacity = expand, clock, capacity
        self.backend_versions = backend_versions
        self.backend_assets = backend_assets
        self.lock = RLock()

    def handle(self, request):
        from .agent_runner import ACTIONS
        allowed = ACTIONS | {'generate_routes', 'import_routes', 'close'}
        if (not isinstance(request, dict) or set(request) - {'profile', 'action', 'arguments', 'session_id'}
                or not isinstance(request.get('profile'), str) or not request['profile']
                or len(request['profile']) > 4096 or request.get('action') not in allowed
                or not isinstance(request.get('arguments', {}), dict)):
            raise ValueError('Invalid session request')
        with self.lock:
            now = self.clock()
            self.sessions = {k: v for k, v in self.sessions.items() if v[1] is None or v[1] > now}
            profile, action, args = request['profile'], request['action'], request.get('arguments', {})
            if action == 'reset':
                return self._reset(profile, args, now)
            sid = request.get('session_id')
            if not isinstance(sid, str) or (profile, sid) not in self.sessions:
                raise ValueError('Unknown or expired environment session')
            if action == 'close':
                if args:
                    raise ValueError('Close accepts no arguments')
                self.sessions = {k: v for k, v in self.sessions.items() if k != (profile, sid)}
                return {'session_id': sid, 'closed': True}
            env = self.sessions[(profile, sid)][0]
            if action in {'generate_routes', 'import_routes'}:
                state = env.inspect()
                if state['terminated'] or state['truncated']:
                    raise ValueError('Episode is closed; create a new task session')
                result = self._search(env, args) if action == 'generate_routes' else self._import(env, args)
                return {'session_id': sid, **result}
            return {'session_id': sid, 'observation': env.dispatch(action, args)}

    def _reset(self, profile, args, now):
        from .environment import SynthesisRouteEnv
        from .schemas import Task
        if (set(args) - {'task', 'seed'} or 'task' not in args
                or type(args.get('seed', 0)) is not int):
            raise ValueError('Reset requires task and optional integer seed')
        if len(self.sessions) >= self.capacity:
            raise ValueError('Host session capacity reached; close an existing session')
        task = Task.model_validate(args['task'])
        env = SynthesisRouteEnv(task, seed=args.get('seed', 0), expand=self.expand,
                                backend_versions=self.backend_versions)
        sid = uuid4().hex
        expiry = None if task.budget.max_wall_seconds is None else now + task.budget.max_wall_seconds
        self.sessions = {**self.sessions, (profile, sid): (env, expiry)}
        return {'session_id': sid, 'observation': env.dispatch('inspect', {}),
                **({'backend_assets': self.backend_assets} if self.backend_assets is not None else {})}

    @staticmethod
    def _search(env, args):
        if set(args) - {'search_policy', 'expansion_top_k', 'max_frontier_states'}:
            raise ValueError('Unsupported search arguments')
        policy, width = args.get('search_policy', 'breadth_first'), args.get('expansion_top_k', 10)
        nodes = args.get('max_frontier_states', 10000)
        if (policy not in SEARCH_POLICIES or type(width) is not int or not 1 <= width <= 100
                or type(nodes) is not int or not 1 <= nodes <= 100000):
            raise ValueError('Invalid search policy or bounds')
        if env.task.budget.regime == 'unbudgeted':
            if 'max_frontier_states' in args:
                raise ValueError('Unbudgeted search cannot impose a frontier ceiling')
            nodes = None
        view = _DraftWorkflow(env)
        event_start = len(env.export()['events'])
        if policy.startswith('synthchem_'):
            from .synthchem_search import run_synthchem_workflow
            result = run_synthchem_workflow(view, algorithm=policy.removeprefix('synthchem_'),
                                           expansion_top_k=width, max_graph_nodes=nodes)
        else:
            from .fixed_search import run_best_first_workflow
            from .planning import run_fixed_workflow
            fn = run_fixed_workflow if policy == 'breadth_first' else run_best_first_workflow
            result = fn(view, expansion_top_k=width, max_frontier_states=nodes)
        failures = [{'status': e['status'], 'code':
                    (e['result'].get('tool_result', e['result']).get('error') or {}).get('code')}
                    for e in env.export()['events'][event_start:]
                    if e['action'] == 'expand' and e['status'] in {'error', 'unavailable', 'cancelled'}]
        stop = 'backend_failure' if failures and not view.route_ids else result.get('stop_reason')
        return {'search_policy': policy, 'route_ids': view.route_ids, 'submitted': False,
                'stop_reason': stop, 'search_stop_reason': result.get('stop_reason'),
                'backend_failures': failures, 'observation': env.dispatch('inspect', {}),
                'scope': 'Predicted draft routes; main agent owns revision and final submission'}

    @staticmethod
    def _import(env, args):
        from .route_import import import_routes
        if set(args) - {'payload', 'format', 'provenance'} or not {'payload', 'format'} <= set(args):
            raise ValueError('Import requires payload, format and optional provenance')
        report = import_routes(args['payload'], target=env.task.target, format=args['format'],
                               provenance=args.get('provenance'))
        ids = [r['route_id'] for r in report['routes']]
        existing = {r['route_id'] for r in env.export()['routes']}
        if any(ident in existing for ident in ids):
            raise ValueError('Imported route IDs already exist')
        stored, observations = [], []
        for route in report['routes']:
            response = env.dispatch('propose_route', {'route': route})
            observations.append(response)
            if response['status'] != 'ok':
                break
            stored.append(route['route_id'])
        return {'route_ids': stored, 'import_report': report, 'observations': observations,
                'complete': len(stored) == len(ids), 'submitted': False}


def localretro_asset_attestation(root):
    """Inventory trusted local assets; never load or redistribute model weights."""
    root = Path(root)
    checkpoint = 'req_data/LocalRetro_boltz_USPTO_MIT.pth'
    required = (checkpoint, 'req_data/USPTO_MIT/atom_templates.csv',
        'req_data/USPTO_MIT/bond_templates.csv', 'req_data/USPTO_MIT/template_infos.csv',
        'rebolt_update_opt/localretro/LocalRetro/default_config.json',
        'rebolt_update_opt/localretro/LocalRetro/Retrosynthesis.py')
    names = set(required) | {str(p.relative_to(root)) for p in
        (root / 'rebolt_update_opt/localretro/LocalRetro').rglob('*.py')}
    files = {}
    for name in sorted(names):
        path = root / name
        if not path.is_file():
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(chunk)
        files = {**files, name: digest.hexdigest()}
    missing = sorted(set(required) - set(files))
    return {'schema_version': 'srg-localretro-assets-v1', 'status': 'incomplete' if missing else 'complete',
            'files': files, 'missing': missing, 'checkpoint_sha256': files.get(checkpoint),
            'scope': 'Checkpoint, required templates/configuration and LocalRetro Python sources; transitive runtime libraries are not attested'}


def _verified_localretro_expand(adapter, checkpoint_sha256):
    def expand(target_smiles, top_k=10):
        result = adapter.expand(target_smiles=target_smiles, top_k=top_k)
        if result.get('status') == 'ok' and result.get('checkpoint_sha256') != checkpoint_sha256:
            return {'status': 'error', 'predictions': [],
                    'diagnostic': 'LocalRetro checkpoint identity differs from host binding'}
        return result
    return expand


def _configured_host():
    """Backend paths come only from operator environment, never tool input."""
    root = os.environ.get('REBOLT_ROOT')
    expand = None
    versions = None
    assets = None
    if root:
        from .adapters import LocalRetroAdapter
        timeout = float(os.environ.get('SRG_BACKEND_TIMEOUT_SECONDS', '120'))
        if not math.isfinite(timeout) or not 0 < timeout <= 3595:
            raise ValueError('Backend timeout must be positive and at most 3595 seconds')
        python = os.environ.get('REBOLT_PYTHON') or sys.executable
        adapter = LocalRetroAdapter(repo_root=root, python_executable=python, timeout_seconds=timeout)
        assets = localretro_asset_attestation(root)
        expand = adapter.expand
        # Allow the subprocess timeout to kill/drain its own group first.
        versions = {'expand': {'timeout_seconds': timeout + 5}}
        if assets['status'] == 'complete':
            digest = assets['checkpoint_sha256']
            expand = _verified_localretro_expand(adapter, digest)
            versions = {'expand': {**versions['expand'], 'version': 'LocalRetro:sha256:' + digest,
                'model_version': 'sha256:' + digest, 'artifact_sha256': digest,
                'configuration_version': hashlib.sha256(json.dumps(assets['files'], sort_keys=True).encode()).hexdigest()}}
    return InteractiveSessions(expand=expand, backend_versions=versions, backend_assets=assets)


def main():
    host = _configured_host()
    while True:
        line = sys.stdin.buffer.readline(MAX_FRAME_BYTES + 1)
        if not line:
            return
        if len(line) > MAX_FRAME_BYTES or not line.endswith(b'\n'):
            return
        try:
            request = json.loads(line, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
            with contextlib.redirect_stdout(sys.stderr):
                result = host.handle(request)
            reply = json.dumps(result, allow_nan=False).encode() + b'\n'
            if len(reply) > MAX_REPLY_BYTES:
                raise ValueError('Response exceeds protocol capacity')
        except (ValueError, RuntimeError, TypeError, KeyError, ImportError, OSError, RecursionError) as exc:
            reply = json.dumps({'success': False, 'error': 'Chemistry host rejected request',
                                'error_type': type(exc).__name__}).encode() + b'\n'
        sys.stdout.buffer.write(reply)
        sys.stdout.buffer.flush()


if __name__ == '__main__':
    main()
