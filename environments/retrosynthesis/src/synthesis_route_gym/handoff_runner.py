"""Durable local handoff execution with immutable attempt receipts."""
import fcntl
import hashlib
import json
import os
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
from .agent_session import run_persistent_agent, _orchestration_policy
from .agent_runner import resolve_main_profile
from .environment import SynthesisRouteEnv
from .episode_store import EpisodeStore
from .handoff import (SmallMoleculeHandoff, build_handoff_task, build_handoff_manifest,
                      build_handoff_feedback, digest, plain, require)


def _write(path, value):
    data = json.dumps(plain(value), sort_keys=True, indent=2).encode() + b'\n'
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return hashlib.sha256(data).hexdigest()


def _read(path):
    require(not path.is_symlink() and path.is_file() and path.stat().st_size <= 20_000_000, 'Invalid handoff artifact')
    return json.loads(path.read_text())


def _file_hash(path):
    _read(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _arguments(args, seed, regime='budgeted'):
    values = dict(vars(args))
    require(all(k in values for k in ('method','model_calls','scientist_python','scientist_source','profile_home')), 'Missing agent host arguments')
    require(values.get('seed', seed) == seed, 'Host seed differs from candidate handoff')
    valid = values['model_calls'] is None if regime == 'unbudgeted' else type(values['model_calls']) is int and values['model_calls'] > 0
    require(valid, 'Invalid model-call allowance for resource regime')
    return SimpleNamespace(**{**values, 'seed':seed})


def _binding(args, env, manifest):
    arguments = {k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()
                 if k not in {'resume','output','output_dir','input','command','func'}}
    package = Path(__file__).parent
    paths = sorted(package.glob('*.py')) + sorted((package/'adapters').glob('*.py'))
    profile = None if args.method == 'direct_tool' else resolve_main_profile(args.profile_home)
    policy = _orchestration_policy(args)
    return {'profile':None if profile is None else {'home':str(profile.home),'model':profile.model,'provider':profile.provider},
            'orchestration_policy':policy, 'schema_version':'srg-handoff-binding-v1','handoff_sha256':digest(manifest),
            'host_arguments_sha256':digest(arguments), 'scientific_registry':env._scientific_tools.fingerprint,
            'application_configuration':env._application_fingerprint,
            'source_access_mode':env._source_access_mode,'scientific_limits':asdict(env._scientific_limits),
            'implementation_sha256':digest({str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})}


def _core(episode):
    return {k:v for k,v in episode.items() if k != 'usage'} | {
        'usage':{k:v for k,v in episode['usage'].items() if k != 'wall_seconds'}}


def _head(path):
    if not path.exists():
        return None
    EpisodeStore(path).load()
    return _read(path/'HEAD.json')['sha256']


def _verified_previous(root, state):
    entry = state.get('last_attempt')
    if entry is None:
        return None
    number = entry['number']
    require(type(number) is int and 1 <= number <= 100, 'Invalid attempt number')
    directory = root/'attempts'/f'{number:04d}'
    receipt = _read(directory/'receipt.json')
    require(digest(receipt) == entry['receipt_sha256'], 'Attempt receipt mismatch')
    for name in ('run','feedback'):
        require(_file_hash(directory/f'{name}.json') == receipt[f'{name}_file_sha256'], 'Attempt artifact hash mismatch')
    return {'schema_version':'srg-handoff-run-v1','handoff_manifest':_read(root/'handoff.json'),
            'run':_read(directory/'run.json'),'feedback':_read(directory/'feedback.json'),
            'artifact_paths':{k:str(directory/f'{k}.json') for k in ('run','feedback','receipt')}}


def _invoke(args, env, root, callback):
    try:
        result = plain(callback(args, env, root/'agent', resume=(root/'agent').exists()))
        require(isinstance(result,dict) and isinstance(result.get('agent'),dict), 'Invalid agent result')
        require(_core(result.get('episode',{})) == _core(env.export()), 'Agent callback episode differs from host state')
        return result
    except (Exception, KeyboardInterrupt) as exc:
        interrupted = isinstance(exc, KeyboardInterrupt)
        if interrupted:
            env.cancel('external interruption')
        runtime = None
        if (root/'agent').exists():
            runtime = EpisodeStore(root/'agent').load()[0].get('runtime')
        return {'method':args.method, 'agent':{'completed':False,'error_type':type(exc).__name__,
                'stop_reason':'external_interruption' if interrupted else 'handoff_runner_exception','resource_accounting':'unknown_after_runner_failure'},
                'episode':env.export(), 'runtime_checkpoint':runtime}


def _save_attempt(root, manifest, result, number):
    episode = result['episode']
    commitment = {'durability':'durable_local_store','episode_sha256':digest(episode),
                  'environment_head_sha256':_head(root/'environment'), 'agent_head_sha256':_head(root/'agent')}
    feedback = build_handoff_feedback(manifest,episode,agent_run=result,commitment=commitment)
    directory = root/'attempts'/f'{number:04d}'
    directory.mkdir(mode=0o700)
    run_hash = _write(directory/'run.json',result)
    feedback_hash = _write(directory/'feedback.json',feedback)
    receipt = {'schema_version':'srg-handoff-attempt-v1','number':number,
               'handoff_sha256':digest(manifest),'run_file_sha256':run_hash,'feedback_file_sha256':feedback_hash,
               'commitment':commitment}
    _write(directory/'receipt.json',receipt)
    return {'number':number,'receipt_sha256':digest(receipt),'closed':episode['terminated'] or episode['truncated']}


def run_handoff(args, handoff, output_dir, *, resume=False, environment_options=None, agent_runner=None):
    """Execute host-only callbacks/configuration; candidate JSON cannot set them."""
    request = SmallMoleculeHandoff.model_validate(plain(handoff))
    manifest, task = build_handoff_manifest(request), build_handoff_task(request)
    args = _arguments(args,request.seed,task.budget.regime)
    options = dict(environment_options or {})
    require(not {'task','seed','store'} & set(options), 'Environment options cannot override handoff identity or store')
    probe = SynthesisRouteEnv(task,seed=request.seed,**options)
    binding = _binding(args,probe,manifest)
    root = EpisodeStore(output_dir).path
    if not resume:
        root.mkdir(parents=True,exist_ok=False,mode=0o700)
    require(root.is_dir(), 'Missing handoff output directory')
    fd = os.open(root/'.execution.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError('Handoff execution already active') from exc
        return _execute(args,manifest,task,options,binding,root,resume,agent_runner)
    finally:
        os.close(fd)


def _execute(args,manifest,task,options,binding,root,resume,agent_runner):
    store = EpisodeStore(root/'handoff-state')
    if resume:
        state, revision = store.load()
        require(state.get('binding') == binding and _read(root/'handoff.json') == manifest, 'Handoff resume binding mismatch')
        previous = _verified_previous(root,state)
        if (state.get('last_attempt') or {}).get('closed'):
            require(_head(root/'environment') == previous['feedback']['commitment']['environment_head_sha256'], 'Environment changed after closed attempt')
            require(_head(root/'agent') == previous['feedback']['commitment']['agent_head_sha256'], 'Agent changed after closed attempt')
            return previous
        env = SynthesisRouteEnv.resume(root/'environment',expected_task=task,**options)
    else:
        _write(root/'handoff.json',manifest)
        (root/'attempts').mkdir(mode=0o700)
        env = SynthesisRouteEnv(task,seed=manifest['handoff']['seed'],store=root/'environment',**options)
        state = {'schema_version':'srg-handoff-execution-v1','binding':binding,'attempt_count':0,
                 'pending_attempt':None,'last_attempt':None}
        revision = store.initialize(state)
    number = state['attempt_count'] + 1
    require(number <= 100, 'Handoff attempt limit reached')
    state = {**state,'attempt_count':number,'pending_attempt':number}
    revision = store.commit(state,expected_revision=revision)
    result = _invoke(args,env,root,agent_runner or run_persistent_agent)
    entry = _save_attempt(root,manifest,result,number)
    state = {**state,'pending_attempt':None,'last_attempt':entry}
    store.commit(state,expected_revision=revision)
    return _verified_previous(root,state)
