"""Serial, frozen development execution; never reads chemistry outcome labels."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

from .schemas import Budget, InventoryItem, Task

FIXED_ARMS = ('breadth_first', 'best_first', 'synthchem_portfolio')
AGENT_ARMS = ('main', 'main_strategist', 'main_condition_scientist',
              'main_route_critic', 'main_all_advisors', 'main_adaptive', 'main_role_prompt')


def capture_runtime_hardware():
    """Capture local allocation metadata, not provider hardware or exclusivity."""
    try:
        result = subprocess.run(['nvidia-smi','--query-gpu=index,name,uuid,memory.total',
            '--format=csv,noheader'],capture_output=True,text=True,check=False,timeout=30)
        inventory = result.stdout.strip().splitlines() if result.returncode == 0 else None
    except (OSError,subprocess.TimeoutExpired):
        inventory = None
    return {'platform':platform.platform(),'logical_cpus':os.cpu_count(),
        'affinity':sorted(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None,
        'gpu_inventory':inventory,
        'gpu_inventory_status':'recorded' if inventory is not None else 'unavailable',
        'environment':{key:os.environ.get(key) for key in
            ('CUDA_VISIBLE_DEVICES','OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS')}}


def verify_runtime_hardware(runtime):
    expected = runtime.get('hardware')
    if expected is None:
        return {'status':'not_declared'}
    actual = capture_runtime_hardware()
    if any(actual.get(key) != value for key,value in expected.items()):
        raise ValueError('Runtime hardware/device/thread allocation differs from frozen plan')
    return {'status':'verified','local_allocation':actual,'provider_hardware':'unknown'}


def _finite_budget_reached(episode,agent,ceilings):
    usage,ledger = episode.get('usage',{}), agent.get('ledger') or {}
    limits = ledger.get('limits') or {}
    pairs = [(usage.get('actions'),ceilings.get('max_actions')),
             (usage.get('wall_seconds'),ceilings.get('max_wall_seconds')),
             (ledger.get('model_calls'),limits.get('max_model_calls',ceilings.get('max_model_calls'))),
             (ledger.get('tool_calls'),limits.get('max_tool_calls',ceilings.get('max_tool_calls'))),
             (ledger.get('charged_tokens'),limits.get('max_total_tokens',ceilings.get('max_llm_tokens'))),
             (ledger.get('elapsed_seconds'),limits.get('wall_seconds',ceilings.get('max_wall_seconds')))]
    return any(type(used) in (int,float) and type(limit) in (int,float) and used >= limit
               for used,limit in pairs)


def classify_episode_stop(result, regime, ceilings=None, *, agent_expected=False, cancel_reason=None):
    """Separate a measured finite budget stop from an external interruption."""
    episode,agent = result.get('episode') or {}, result.get('agent') or {}
    reason = result.get('stop_reason') or agent.get('stop_reason') or episode.get('stop_reason')
    condition_submitted = episode.get('submission',{}).get('status') in {'selected','abstained'}
    submitted = bool(episode.get('terminated') or condition_submitted or
                     episode.get('submission',{}).get('status') == 'submitted')
    explicit_cancel = cancel_reason or episode.get('cancel_reason')
    external = (result.get('interrupted') is True or
                explicit_cancel not in {None,'bridge_interrupted','episode_deadline_expired'})
    if external:
        return {'status':'interrupted','natural_completion':False}
    interrupted = episode.get('truncated') or reason in {'bridge_interrupted','external_operator_interruption'}
    if interrupted:
        finite = regime == 'budgeted' and _finite_budget_reached(episode,agent,ceilings or {})
        return {'status':'budget_exhausted' if finite else 'interrupted','natural_completion':False}
    if reason in {'backend_failure','search_capacity_failure','capacity_interrupted'}:
        return {'status':'failed','natural_completion':False}
    complete = submitted and (not agent_expected or agent.get('completed') is True)
    natural = complete and (agent_expected or condition_submitted or
                           reason in {'frontier_exhausted','route_quota','pool_exhausted'})
    if agent_expected and not complete:
        exhausted = regime == 'budgeted' and _finite_budget_reached(episode,agent,ceilings or {})
        return {'status':'budget_exhausted' if exhausted else 'incomplete','natural_completion':False}
    status = 'completed' if complete else 'incomplete'
    if regime == 'unbudgeted' and not natural:
        status = 'failed'
    return {'status':status,'natural_completion':natural}


def digest(path):
    hashed = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hashed.update(block)
    return hashed.hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def model_runtime_metadata(artifact):
    """Inspect installed version metadata only; never import scientific models."""
    expected = artifact['runtime_versions']
    if not expected:
        return {}
    code = '''import importlib.metadata as m,json,sys
names=json.loads(sys.argv[1])
def record(name):
    dist=m.distribution(name)
    path=next((str(dist.locate_file(p)) for p in (dist.files or []) if str(p).endswith(".dist-info/METADATA")),None)
    return {"version":dist.version,"metadata_file":path}
print(json.dumps({name:record(name) for name in names}))
'''
    try:
        result = subprocess.run([artifact['python_executable'],'-c',code,json.dumps(list(expected))],
                                capture_output=True,text=True,check=True,timeout=60)
        metadata = json.loads(result.stdout)
    except (OSError,subprocess.SubprocessError,ValueError) as exc:
        raise ValueError('Cannot verify public yield runtime metadata') from exc
    if set(metadata) != set(expected) or any(not isinstance(value,dict) or
            value.get('version') != expected[name] or not value.get('metadata_file') or
            not Path(value['metadata_file']).is_file() for name,value in metadata.items()):
        raise ValueError('Public yield runtime version metadata mismatch')
    return metadata


def _model_binding(plan):
    runtime = plan['runtime']
    declared = runtime.get('reaction_yield_model_manifest')
    if declared is None:
        if plan.get('model_manifest_sha256') is not None:
            raise ValueError('Model manifest digest has no runtime manifest')
        return set(), None
    if not isinstance(declared,str) or not declared:
        raise ValueError('Invalid runtime public yield manifest path')
    path = Path(declared).expanduser().absolute()
    if not path.is_file():
        raise ValueError('Public yield manifest file is unavailable')
    actual = digest(path)
    expected = plan.get('model_manifest_sha256')
    if not isinstance(expected,str) or not re.fullmatch('[a-f0-9]{64}',expected) or actual != expected:
        raise ValueError('Public yield manifest digest differs from recorded plan')
    if runtime.get('model_manifest_sha256',expected) != expected:
        raise ValueError('Runtime public yield manifest digest differs from plan')
    from . import public_yield
    try:
        predictor = public_yield.ReactionT5YieldPredictor.from_manifest(path)
    except OSError as exc:
        raise ValueError('Public yield model asset integrity cannot be verified') from exc
    artifact = predictor.artifact
    metadata = model_runtime_metadata(artifact)
    files = {path,path.resolve(),Path(artifact['python_executable']),Path(artifact['python_executable']).resolve(),
             Path(public_yield.__file__),public_yield.WORKER,
             *(Path(artifact['model_dir'])/name for name in artifact['files']),
             *(Path(item['metadata_file']) for item in metadata.values())}
    return files, {'manifest_sha256':expected,'configuration':predictor.configuration,
                   'runtime_metadata':metadata}


def write_once(path, value):
    path = Path(path)
    payload = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream:
        stream.write(payload)
    return digest(path)


def _identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise ValueError('Invalid development identifier')
    return value


def materialize_inputs(public_dir, selection, output):
    """Validate public stock once, then project selected development tasks only."""
    from .dataset_bundle import verify_bundle
    public_dir, output = Path(public_dir).resolve(), Path(output).resolve()
    verify_bundle(public_dir, expected_manifest_sha256=selection['manifest_sha256'])
    manifest = read(public_dir / 'manifest.json')
    # verify_bundle already validated each stock SMILES canonically. Reusing
    # those identities avoids repeating RDKit work for every inventory variant.
    stock = tuple(InventoryItem.model_construct(smiles=s) for s in read(public_dir / 'inventory.json'))
    records = {row['task_id']: row for row in manifest['tasks']}
    result = {}
    for group in selection['groups']:
        for task_id in group['task_ids']:
            _identifier(task_id)
            if records[task_id]['partition'] != 'development' or records[task_id]['track'] != 'reference_route':
                raise ValueError('Only public development route tasks are permitted')
            path = public_dir / 'tasks' / (task_id + '.json')
            if digest(path) != selection['task_hashes'][task_id]:
                raise ValueError('Selected task integrity mismatch')
            raw = read(path)
            excluded = set(raw.get('inventory_exclusions', ()))
            task = Task(task_id=task_id, target=raw['target'],
                        inventory=tuple(item for item in stock if item.smiles not in excluded),
                        constraints=raw['constraints'], budget=raw['budget'])
            dest = output / (task_id + '.json')
            result = {**result, task_id: {'path':str(dest),
                      'sha256':write_once(dest, task.model_dump(mode='json'))}}
    return result


def make_plan(selection, inputs, *, stage, arms, regimes, runtime):
    if stage not in {'B', 'B_unbudgeted_smoke', 'C', 'E'}:
        raise ValueError('Unsupported development stage')
    if not arms or len(set(arms)) != len(arms) or any(a not in FIXED_ARMS + AGENT_ARMS for a in arms):
        raise ValueError('Invalid development arms')
    if not regimes or len(set(regimes)) != len(regimes) or any(r not in {'budgeted','unbudgeted'} for r in regimes):
        raise ValueError('Invalid resource regimes')
    group_ids = (selection['screen_group_ids'] if stage == 'C' else
                 selection['confirmation_group_ids'] if stage == 'E' else None)
    groups = [g for g in selection['groups'] if group_ids is None or g['group_id'] in group_ids]
    task_ids = [t for g in groups for t in g['task_ids']]
    if stage == 'B_unbudgeted_smoke':
        smallest = min(groups,key=lambda g:(g.get('heavy_atoms',float('inf')),g.get('selection_key','')))
        candidates = [_identifier(t) for t in smallest['task_ids']]
        task_ids = [min(candidates,key=lambda t:(-len(read(Path(inputs)/(t+'.json')).get('inventory',[])),t))]
    if not task_ids or len(set(task_ids)) != len(task_ids):
        raise ValueError('Missing or duplicate selected tasks')
    tasks = {t:{'path':str((Path(inputs)/(_identifier(t)+'.json')).resolve()),
                'sha256':digest(Path(inputs)/(t+'.json'))} for t in task_ids}
    rows = [{'run_id':f'{stage}-{t}-{arm}-{regime}-r0', 'task_id':t,
             'arm':arm, 'regime':regime, 'seed':0, 'repeat_id':0}
            for t in task_ids for regime in regimes for arm in sorted(arms,
                key=lambda a:hashlib.sha256(f'srg12-order-v1:{t}:{regime}:{a}'.encode()).hexdigest())]
    return {'schema_version':'srg12-development-plan-v1', 'stage':stage,
            'tasks':tasks, 'runs':rows, 'runtime':dict(runtime),
            'partition':'development', 'final_labels_opened':False,
            'smoke_selection_rule':('smallest public target heavy-atom count; salted selection key tie-break; largest supplied stock; task ID tie-break'
                                    if stage=='B_unbudgeted_smoke' else None),
            'cache_policy':'cold_episode_local', 'retry_policy':'no_automatic_episode_retry'}


def freeze_plan(plan_path, freeze_path, *, assets, private_hash_only=()):
    plan = read(plan_path)
    model_files, model_binding = _model_binding(plan)
    paths = {Path(plan_path).resolve(), *(Path(t['path']).resolve() for t in plan['tasks'].values()),
             *(Path(p).absolute() for p in assets), *model_files}
    # Bind the live package, not a historical snapshot. Executed adapters and
    # algorithms are included even when the caller forgets individual modules.
    paths.update(Path(__file__).parent.rglob('*.py'))
    hashes = {str(p):digest(p) for p in sorted(paths)}
    snapshot = Path(freeze_path).parent/(Path(freeze_path).stem+'-snapshot')
    snapshot.mkdir(exist_ok=False)
    excluded = {Path(p).absolute() for p in private_hash_only}
    copies = {}
    for path in sorted(paths):
        if path in excluded or path.suffix not in {'.py','.json','.yaml','.yml','.toml','.txt'}:
            continue
        dest = snapshot/path.as_posix().lstrip('/')
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,dest)
        if digest(dest) != hashes[str(path)]:
            raise ValueError('Source changed during snapshot')
        copies = {**copies,str(dest):hashes[str(path)]}
    freeze = {'schema_version':'srg12-development-freeze-v1',
              'plan_sha256':hashes[str(Path(plan_path).resolve())], 'files':hashes,
              'snapshot_files':copies,
              'public_yield_model_binding':model_binding,
              'snapshot_scope':'source/input/config copies; model binaries and interpreters hashed in place',
              'local_only':True, 'final_labels_opened':False}
    write_once(freeze_path, freeze)
    verify_freeze(plan_path, freeze_path, digest(freeze_path))
    return freeze


def verify_freeze(plan_path, freeze_path, expected):
    if digest(freeze_path) != expected:
        raise ValueError('Freeze integrity mismatch')
    frozen = read(freeze_path)
    if frozen.get('schema_version') != 'srg12-development-freeze-v1' or frozen['plan_sha256'] != digest(plan_path):
        raise ValueError('Plan integrity mismatch')
    plan = read(plan_path)
    model_files, model_binding = _model_binding(plan)
    if frozen.get('public_yield_model_binding') != model_binding:
        raise ValueError('Frozen public yield model binding integrity mismatch')
    required = {str(Path(plan_path).resolve()), *(str(Path(t['path']).resolve())
                 for t in plan['tasks'].values()), *(str(p) for p in model_files)}
    if not required <= set(frozen['files']):
        raise ValueError('Required input absent from integrity freeze')
    for name, expected_hash in {**frozen['files'],**frozen.get('snapshot_files',{})}.items():
        if not Path(name).is_file() or digest(name) != expected_hash:
            raise ValueError('Frozen source/input integrity mismatch')
    return {'freeze_sha256':expected, 'verified_files':len(frozen['files'])}


def arm_configuration(arm):
    from .orchestration import normalize_policy
    if arm == 'main_condition_scientist':
        return 'main_adaptive', normalize_policy('main_adaptive', {
            'policy_id':'srg12-condition-only-v1', 'experimental':True,
            'enabled_roles':['condition_scientist'], 'max_consultations':1})
    if arm == 'main_adaptive':
        return arm, normalize_policy(arm, {'experimental':True,
            'enabled_roles':['strategist','condition_scientist','route_critic'], 'max_consultations':1})
    if arm in {'main_all_advisors','main_role_prompt'}:
        return arm, normalize_policy(arm)
    if arm not in FIXED_ARMS + AGENT_ARMS:
        raise ValueError('Unknown arm')
    return arm, None


def execute_episode(task, row, runtime, folder, *, expand=None):
    from .environment import SynthesisRouteEnv
    if expand is None:
        from .adapters import LocalRetroAdapter
        expand = LocalRetroAdapter(repo_root=runtime['repo_root'],
            python_executable=runtime['chemistry_python'],
            timeout_seconds=runtime['tool_timeout_seconds']).expand
    width = runtime['expansion_top_k']
    actual_expand = expand
    def checked_expand(target_smiles, top_k=10):
        if top_k != width:
            return {'status':'error','message':f'Frozen experiment requires top_k={width}', 'predictions':[]}
        return actual_expand(target_smiles=target_smiles,top_k=top_k)
    env = SynthesisRouteEnv(task, seed=row['seed'], expand=checked_expand, store=Path(folder)/'environment')
    nodes = None if task.budget.regime == 'unbudgeted' else runtime['max_frontier_states']
    try:
        return _execute_policy(task,row,runtime,folder,env,width,nodes)
    except KeyboardInterrupt:
        env.cancel('external_operator_interruption')
        raise


def _execute_policy(task,row,runtime,folder,env,width,nodes):
    if row['arm'] == 'synthchem_portfolio':
        from .synthchem_search import run_synthchem_workflow
        return run_synthchem_workflow(env, algorithm='portfolio', expansion_top_k=width, max_graph_nodes=nodes)
    if row['arm'] in FIXED_ARMS:
        from .planning import run_fixed_workflow
        from .fixed_search import run_best_first_workflow
        fn = run_fixed_workflow if row['arm'] == 'breadth_first' else run_best_first_workflow
        return fn(env, expansion_top_k=width, max_frontier_states=nodes)
    return _execute_agent(task, row, runtime, folder, env)


def _execute_agent(task, row, runtime, folder, env):
    from .agent_session import run_persistent_agent
    from .agent_runner import resolve_main_profile
    from .planning import environment_tool_schemas
    profile = resolve_main_profile(runtime['profile_home'])
    if (profile.model,profile.provider) != (runtime['model'],runtime['provider']):
        raise ValueError('Main profile identity differs from frozen configuration')
    mode, policy = arm_configuration(row['arm'])
    policy_path = Path(folder)/'orchestration-policy.json' if policy else None
    if policy_path:
        write_once(policy_path, policy)
    args = SimpleNamespace(**{key:runtime[key] for key in
        ('profile_home','scientist_python','scientist_source','repo_root','chemistry_python')},
        method=mode, model_calls=None if task.budget.regime=='unbudgeted' else runtime['model_calls'],
        timeout=runtime['tool_timeout_seconds'], seed=row['seed'],
        condition_model=None, orchestration_policy=policy_path)
    schemas = environment_tool_schemas()
    width = runtime['expansion_top_k']
    narrowed = [{**item,'parameters':{**item['parameters'],'properties':{
        **item['parameters']['properties'],'top_k':{'type':'integer','enum':[width],'default':width}}}}
        if item['name']=='expand' else item for item in schemas]
    return run_persistent_agent(args, env, Path(folder)/'runtime',tool_schemas=narrowed)


def _load_plan_tasks(plan):
    if plan.get('schema_version') != 'srg12-development-plan-v1' or plan.get('partition') != 'development':
        raise ValueError('Invalid development plan')
    tasks, raw_inputs = {}, {}
    for key, item in plan['tasks'].items():
        _identifier(key)
        if digest(item['path']) != item['sha256']:
            raise ValueError('Materialized task integrity mismatch')
        raw_inputs = {**raw_inputs,key:read(item['path'])}
    def inventory_key(item):
        return json.dumps(item,sort_keys=True,allow_nan=False)
    unique_items = {inventory_key(item):item for raw in raw_inputs.values() for item in raw['inventory']}
    inventory = {key:InventoryItem.model_validate(item) for key,item in unique_items.items()}
    for key, raw in raw_inputs.items():
        task = Task.model_validate({**raw,'inventory':tuple(inventory[inventory_key(i)] for i in raw['inventory'])})
        if task.task_id != key:
            raise ValueError('Task identity mismatch')
        if task.budget.regime != 'budgeted':
            raise ValueError('Base development inputs must retain their finite public budget')
        tasks = {**tasks, key:task}
    ids = [row['run_id'] for row in plan['runs']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate run IDs')
    for row in plan['runs']:
        _identifier(row['run_id'])
        if row['arm'] not in FIXED_ARMS + AGENT_ARMS or row['regime'] not in {'budgeted','unbudgeted'} or row['task_id'] not in tasks:
            raise ValueError('Invalid run specification')
        if type(row.get('seed')) is not int or type(row.get('repeat_id')) is not int or row['repeat_id'] < 0:
            raise ValueError('Invalid seed or repeat identifier')
    return tasks


def _verified_existing(folder, row, freeze_sha, task):
    path = folder/'receipt.json'
    if not path.is_file():
        raise ValueError('Incomplete existing attempt is not resumable')
    receipt = read(path)
    anchor = folder/'receipt.sha256.json'
    if not anchor.is_file() or read(anchor) != {'sha256':digest(path)}:
        raise ValueError('Existing receipt integrity mismatch')
    if receipt.get('status') != 'completed':
        raise ValueError('Failed/interrupted attempt is not resumable')
    if receipt.get('run') != row or receipt.get('freeze_sha256') != freeze_sha:
        raise ValueError('Existing receipt integrity mismatch')
    for name in ('started.json','result.json','decision.json'):
        if not (folder/name).is_file() or digest(folder/name) != receipt['artifact_sha256'][name]:
            raise ValueError('Existing artifact integrity mismatch')
    result = read(folder/'result.json')
    if result['episode']['task'] != task.model_dump(mode='json'):
        raise ValueError('Existing episode input integrity mismatch')
    if read(folder/'decision.json') != _decision(task,result):
        raise ValueError('Existing committed decision integrity mismatch')
    return receipt


def _decision(task, result):
    episode = result['episode']
    if not episode.get('terminated'):
        return None
    by_id = {r['route_id']:r for r in episode.get('routes',[])}
    return {'task_id':task.task_id, 'routes':[by_id[key] for key in episode['submitted_route_ids']]}


def _attempt(task, row, runtime, folder, freeze_sha, executor):
    start = time.monotonic()
    hashes = {'started.json':write_once(folder/'started.json', {'run':row, 'freeze_sha256':freeze_sha})}
    try:
        result = executor(task, row, runtime, folder)
        hashes = {**hashes,'result.json':write_once(folder/'result.json',result)}
        decision = _decision(task,result)
        agent = result.get('agent',{})
        reason = result.get('stop_reason',agent.get('stop_reason'))
        cancel_reason = None
        if result['episode'].get('truncated') and (folder/'environment').is_dir():
            from .episode_store import EpisodeStore
            state,_ = EpisodeStore(folder/'environment').load()
            cancel_reason = state.get('cancel_reason')
        classification = classify_episode_stop(result,task.budget.regime,task.budget.model_dump(),
            agent_expected=row['arm'] in AGENT_ARMS,cancel_reason=cancel_reason)
        if decision is not None:
            from .dataset_bundle import commit_decision
            hashes = {**hashes,'decision.json':commit_decision(folder/'decision.json', decision)}
        return {'run':row,'freeze_sha256':freeze_sha,**classification,
                'artifact_sha256':hashes,'elapsed_seconds':time.monotonic()-start,
                'resources':result['episode'].get('usage',{}),
                'agent_resources':agent.get('ledger'), 'stop_reason':reason}
    except (Exception, KeyboardInterrupt) as exc:
        from .episode_store import EpisodeStore
        resources = None
        if (folder/'environment').is_dir():
            try:
                state,_ = EpisodeStore(folder/'environment').load()
                resources = state.get('usage')
            except (OSError,ValueError,RuntimeError):
                pass  # Failure remains explicit; never fabricate checkpoint usage.
        return {'run':row,'freeze_sha256':freeze_sha,
                'status':'interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed',
                'error_type':type(exc).__name__, 'elapsed_seconds':time.monotonic()-start,
                'resources':resources, 'resource_accounting':'inspect_preserved_environment_and_runtime_checkpoints',
                'natural_completion':False, 'artifact_sha256':hashes}


def run_plan(plan_path, freeze_path, output, *, executor=execute_episode):
    """Run serially; resume skips only intact completed outputs, never failures."""
    freeze_sha = digest(freeze_path)
    verify_freeze(plan_path,freeze_path,freeze_sha)
    plan = read(plan_path)
    tasks = _load_plan_tasks(plan)
    output = Path(output)
    receipts = []
    for row in plan['runs']:
        verify_freeze(plan_path,freeze_path,freeze_sha)
        hardware_before = verify_runtime_hardware(plan['runtime'])
        folder = output/row['run_id']
        base = tasks[row['task_id']]
        task = (base.model_copy(update={'budget':Budget.unbudgeted(top_k=base.budget.top_k)})
                if row['regime']=='unbudgeted' else base)
        if folder.exists():
            receipts.append(_verified_existing(folder,row,freeze_sha,task))
            continue
        receipt = _attempt(task,row,plan['runtime'],folder,freeze_sha,executor)
        try:
            verify_freeze(plan_path,freeze_path,freeze_sha)
        except ValueError:
            write_once(folder/'receipt.json',{**receipt,'status':'integrity_failure','natural_completion':False})
            raise
        try:
            hardware_after = verify_runtime_hardware(plan['runtime'])
            receipt = {**receipt,'hardware_verification':{'before':hardware_before,'after':hardware_after}}
        except ValueError:
            receipt = {**receipt,'status':'interrupted','natural_completion':False,
                       'hardware_verification':{'before':hardware_before,'after':{'status':'mismatch'}}}
        receipt_sha = write_once(folder/'receipt.json',receipt)
        write_once(folder/'receipt.sha256.json',{'sha256':receipt_sha})
        receipts.append(receipt)
        if receipt['status']=='interrupted':
            break
    return {'freeze_sha256':freeze_sha, 'completed':sum(r['status']=='completed' for r in receipts),
            'attempts':len(receipts), 'receipts':receipts, 'final_labels_opened':False}
