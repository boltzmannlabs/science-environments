"""Public-input-only fixed-search comparison; deterministic gates are not feasibility."""
import hashlib
import importlib.metadata
import json
import os
import subprocess
import threading
from pathlib import Path
import platform
import time

from .adapters.common import normalise_prediction
from .chemistry import canonical_smiles
from .dataset_bundle import commit_decision, load_public_task, verify_bundle
from .environment import SynthesisRouteEnv
from .schemas import Budget, Task

VERSION = 'srg-search-comparison-v1'
BUDGET = Budget(max_actions=80, max_expansions=6, max_wall_seconds=120, top_k=5)


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _hash(value):
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _json(value) + '\n'
    with path.open('x') as stream:
        stream.write(data)
    return hashlib.sha256(data.encode()).hexdigest()


def select_development_tasks(public_dir, expected_digest, *, group_count=4):
    """Hash-select complete target groups without reading reference routes."""
    if type(group_count) is not int or not 1 <= group_count <= 100:
        raise ValueError('group_count must be an integer in [1,100]')
    public_dir = Path(public_dir)
    verify_bundle(public_dir, expected_manifest_sha256=expected_digest)
    manifest = json.loads((public_dir/'manifest.json').read_text())
    records = [json.loads((public_dir/'tasks'/f"{r['task_id']}.json").read_text())
               for r in manifest['tasks']
               if r['partition'] == 'development' and r['track'] == 'reference_route']
    targets = sorted({r['target'] for r in records}, key=lambda s: hashlib.sha256(s.encode()).hexdigest())
    if len(targets) < group_count:
        raise ValueError('Insufficient development target groups')
    selected = sorted((r for r in records if r['target'] in targets[:group_count]),
                      key=lambda r: (targets.index(r['target']), r['task_id']))
    tasks = []
    for row in selected:
        public = load_public_task(public_dir, row['task_id'], expected_manifest_sha256=expected_digest)
        task = Task.model_validate({k: public[k] for k in Task.model_fields if k in public})
        tasks = [*tasks, task.model_copy(update={'budget': BUDGET})]
    return tasks, {'data_role':'development', 'public_manifest_sha256':expected_digest,
        'public_bundle_path':str(public_dir.resolve()),
        'group_count':group_count, 'selection':'first canonical-target SHA256 groups; all inventory variants',
        'selected_task_ids':[t.task_id for t in tasks], 'private_labels_read':False}


def pin_localretro_assets(repo_root, python_executable):
    """Hash actual local files, without asserting complete training provenance."""
    root, python = Path(repo_root).resolve(), Path(python_executable).absolute()
    source = root/'rebolt_update_opt/localretro/LocalRetro'
    required = [root/'req_data/LocalRetro_boltz_USPTO_MIT.pth',
                *(root/'req_data/USPTO_MIT'/name for name in
                  ('atom_templates.csv','bond_templates.csv','template_infos.csv')),
                source/'default_config.json', source/'Retrosynthesis.py', python]
    if any(not path.is_file() for path in required):
        raise ValueError('Required LocalRetro asset or interpreter is missing')
    paths = sorted(set(required + list(source.rglob('*.py'))), key=str)
    return {'kind':'localretro_cpu', 'assets':{str(p):_file_hash(p) for p in paths},
        'checkpoint_sha256':_file_hash(required[0]), 'python_executable':str(python),
        'thread_limit':1, 'device':'cpu', 'worker_runtime':_worker_runtime(python),
        'adapter_timeout_seconds':40, 'contract_timeout_seconds':45,
        'training_provenance':'not_independently_verified'}


def _worker_runtime(python):
    script = """import importlib.metadata,json,platform
names=('torch','dgl','dgllife','rdkit','pandas','numpy','scikit-learn')
versions={}
for name in names:
 try: versions[name]=importlib.metadata.version(name)
 except importlib.metadata.PackageNotFoundError: versions[name]=None
print(json.dumps({'python':platform.python_version(),'versions':versions}))
"""
    env = {k:v for k,v in os.environ.items() if k in {'PATH','HOME','LANG','LC_ALL','LD_LIBRARY_PATH'}}
    try:
        result = subprocess.run([str(python),'-c',script],env=env,capture_output=True,
                                text=True,timeout=15,check=True)
        record = json.loads(result.stdout)
        return {**record,'status':'metadata_read','scope':'installed distribution versions; runtime imports not verified'}
    except (OSError,subprocess.SubprocessError,ValueError,TypeError):
        return {'status':'unknown','scope':'bounded interpreter metadata query failed'}


def _source_hashes():
    root = Path(__file__).resolve().parents[2]
    paths = sorted((root/'src/synthesis_route_gym').rglob('*.py'))
    script = root/'scripts/run_search_comparison.py'
    return {str(p.relative_to(root)):_file_hash(p) for p in paths + ([script] if script.is_file() else [])}


def _runtime():
    return {'python':platform.python_version(), 'platform':platform.platform(),
        'versions':{name:importlib.metadata.version(name) for name in ('rdkit','pydantic','numpy')}}


def _clean(raw, molecule, top_k):
    if not isinstance(raw, dict) or raw.get('status') not in {'ok','error','unavailable'}:
        raise ValueError('Invalid backend result')
    if raw['status'] != 'ok':
        return {'status':raw['status'], 'predictions':[], 'diagnostic':'Recorded backend failure'}
    rows = raw.get('predictions')
    if not isinstance(rows, list) or len(rows) > 10000:
        raise ValueError('Invalid prediction collection')
    predictions = [normalise_prediction(row, 'pinned-expansion', str(raw.get('version','unknown')))
                   for row in rows[:top_k]]
    if any(row['product'] != molecule for row in predictions):
        raise ValueError('Prediction product differs from query')
    return {'status':'ok', 'predictions':predictions, 'version':str(raw.get('version','unknown'))}


class _RecordedBackend:
    def __init__(self, callback, context):
        self.callback, self.context, self.records = callback, context, ()
        self._condition, self._closed = threading.Condition(), False

    def expand(self, smiles, top_k):
        molecule, started = canonical_smiles(smiles), time.monotonic()
        with self._condition:
            if self._closed:
                return {'status':'error','predictions':[], 'diagnostic':'Recorder already settled'}
            index = len(self.records)
            record = {'key':_hash([self.context,molecule,top_k]),'molecule':molecule,
                'top_k':top_k,'result':{'status':'pending','predictions':[]},'elapsed_seconds':0.0}
            self.records = (*self.records,record)
        try:
            result = _clean(self.callback(molecule,top_k),molecule,top_k)
        except Exception as error:
            result = {'status':'error','predictions':[], 'diagnostic':f'Backend {type(error).__name__}'}
        with self._condition:
            if not self._closed:
                completed = {**record,'result':result,'elapsed_seconds':time.monotonic()-started}
                self.records = (*self.records[:index],completed,*self.records[index+1:])
                self._condition.notify_all()
        return json.loads(_json(result))

    def settle(self, observed_keys, timeout=45):
        """Wait outside episode allowance; never pool late/unobserved predictions."""
        started = time.monotonic()
        with self._condition:
            while any(r['result']['status']=='pending' for r in self.records):
                remaining = timeout-(time.monotonic()-started)
                if remaining <= 0:
                    raise RuntimeError('Worker did not quiesce; comparison stopped before next arm')
                self._condition.wait(remaining)
            self.records = tuple({**r,'observed_by_policy':r['key'] in observed_keys} for r in self.records)
            self._closed = True
        return time.monotonic()-started


class _ReplayBackend:
    def __init__(self, entries, context):
        self.entries, self.context, self.hits, self.misses = entries, context, 0, 0

    def expand(self, smiles, top_k):
        key = _hash([self.context,canonical_smiles(smiles),top_k])
        if key not in self.entries:
            self.misses += 1
            return {'status':'unavailable','predictions':[], 'diagnostic':'Frozen pool miss; no model fallback'}
        self.hits += 1
        return json.loads(_json(self.entries[key]))


def _pool(records):
    entries, conflicts = {}, set()
    for row in records:
        key, result = row['key'], row['result']
        if result['status'] != 'ok' or not row.get('observed_by_policy',False) or key in conflicts:
            continue
        if key in entries and _hash(entries[key]) != _hash(result):
            conflicts = conflicts | {key}
            entries = {k:v for k,v in entries.items() if k != key}
        else:
            entries = {**entries, key:result}
    return entries, conflicts


def summarize_run(result):
    episode = result['episode']
    submitted = episode['submitted_route_ids']
    assessments = {a['route_id']:a for a in episode['assessments']}
    accepted = [a for key in submitted if (a := assessments.get(key)) is not None
        and a['graph_valid'] and a['inventory_complete'] and a['constraint_compliant']
        and a['quantity_status'] in {'complete','not_requested'} and not a['acquisition_only']]
    events = episode.get('events', [])
    requests = [e.get('arguments',{}).get('smiles') for e in events if e.get('action') == 'expand']
    return {'submitted_routes':len(submitted), 'accepted_submitted_routes':len(accepted),
        'rejected_submitted_routes':len(submitted)-len(accepted),
        'has_accepted_route':bool(accepted),
        'accepted_top1':bool(submitted and submitted[0] in {a['route_id'] for a in accepted}),
        'invalid_reasons':{code:sum(code in {f['code'] for f in a.get('findings',[]) if f['severity']=='error'}
            for a in assessments.values() if a['route_id'] in submitted)
            for code in sorted({f['code'] for a in assessments.values() if a['route_id'] in submitted
                for f in a.get('findings',[]) if f['severity']=='error'})}, 'inventory_closed_submitted_routes':sum(
            assessments[key]['inventory_complete'] for key in submitted if key in assessments),
        'search_states':result.get('search_states'), 'search_metrics':result.get('metrics',{}),
        'stop_reason':result.get('stop_reason'), 'usage':episode['usage'],
        'duplicate_expansion_requests':len(requests)-len(set(requests)),
        'terminated':episode['terminated'], 'truncated':episode['truncated'],
        'acceptance_scope':'deterministic_gates_only', 'scientific_feasibility':'not_evaluated'}


def _one_run(folder, task, mode, arm, policy, backend, identity, limits):
    version = {'version':'srg05-pinned-expansion-v1', 'configuration_version':_hash(identity),
        'model_version':identity.get('checkpoint_sha256','fixture'),
        'artifact_sha256':identity.get('checkpoint_sha256'), 'timeout_seconds':45}
    env = SynthesisRouteEnv(task, expand=backend.expand, backend_versions={'expand':version})
    started = time.monotonic()
    result = policy(env, **limits)
    elapsed = time.monotonic()-started
    relative = Path(mode)/task.task_id/arm
    result_sha = _write(folder/relative/'episode.json',result)
    episode = result['episode']
    routes = {r['route_id']:r for r in episode['routes']}
    decision = {'task_id':task.task_id,'routes':[routes[key] for key in episode['submitted_route_ids']]}
    decision_path = relative/'decision.json'
    decision_sha = commit_decision(folder/decision_path,decision)
    settlement = 0.0
    if isinstance(backend,_RecordedBackend):
        observed = {_hash([backend.context,e['arguments']['smiles'],e['arguments'].get('top_k',10)])
            for e in result['episode']['events'] if e['action']=='expand' and e['status']=='ok'
            and e.get('result',{}).get('tool_result',{}).get('status')=='ok'}
        try:
            settlement = backend.settle(observed)
        except RuntimeError:
            _write(folder/relative/'failure.json',{'status':'worker_settlement_failed',
                'next_arm_started':False,'backend_calls':list(backend.records)})
            raise
    metrics = {**summarize_run(result), 'task_id':task.task_id, 'mode':mode, 'arm':arm,
        'task_sha256':_hash(task.model_dump(mode='json')), 'elapsed_seconds':elapsed,
        'settlement_overhead_seconds':settlement,
        'episode_path':str(relative/'episode.json'), 'episode_sha256':result_sha,
        'decision_path':str(decision_path), 'decision_sha256':decision_sha,
        'backend_invocations':len(backend.records) if isinstance(backend,_RecordedBackend) else 0,
        'pool_hits':getattr(backend,'hits',0), 'pool_misses':getattr(backend,'misses',0)}
    _write(folder/relative/'metrics.json',metrics)
    return metrics


def _validate(tasks, cohort, limits, policies):
    if not tasks or any(not isinstance(t,Task) for t in tasks):
        raise ValueError('A nonempty list of validated tasks is required')
    if len({t.task_id for t in tasks}) != len(tasks):
        raise ValueError('Duplicate task IDs')
    if cohort.get('data_role') not in {'smoke','development'}:
        raise ValueError('Only smoke/development comparisons are allowed')
    if set(policies) != {'legacy_bfs','best_first'} or not all(callable(p) for p in policies.values()):
        raise ValueError('Exactly two fixed search policies are required')
    for name, maximum in [('expansion_top_k',100),('max_frontier_states',100000)]:
        if type(limits[name]) is not int or not 1 <= limits[name] <= maximum:
            raise ValueError('Invalid search limits')


def _aggregate(runs):
    return {mode:{arm:{'tasks':len(rows),
        'tasks_with_accepted_routes':sum(r['has_accepted_route'] for r in rows),
        'accepted_submitted_routes':sum(r['accepted_submitted_routes'] for r in rows),
        'rejected_submitted_routes':sum(r['rejected_submitted_routes'] for r in rows),
        'expansions':sum(r['usage']['expansions'] for r in rows),
        'search_states':sum(r['search_states'] or 0 for r in rows),
        'duplicate_expansion_requests':sum(r['duplicate_expansion_requests'] for r in rows),
        'elapsed_seconds':sum(r['elapsed_seconds'] for r in rows),
        'pool_misses':sum(r['pool_misses'] for r in rows)}
        for arm in ('legacy_bfs','best_first')
        for rows in [[r for r in runs if r['mode']==mode and r['arm']==arm]]}
        for mode in ('cold','shared_precomputed')}


def run_comparison(output_dir, tasks, *, backend_factory, backend_identity, cohort,
                   expansion_top_k=10, max_frontier_states=10000, policies=None):
    """Write-once paired comparison. Exceptions leave completed artifacts intact."""
    if policies is None:
        from .planning import run_fixed_workflow
        from .fixed_search import run_best_first_workflow
        policies = {'legacy_bfs':run_fixed_workflow, 'best_first':run_best_first_workflow}
    limits = {'expansion_top_k':expansion_top_k,'max_frontier_states':max_frontier_states}
    _validate(tasks,cohort,limits,policies)
    folder = Path(output_dir)
    folder.mkdir(parents=True,exist_ok=False)
    plan = {'schema_version':VERSION,'cohort':cohort,'backend_identity':backend_identity,
        'tasks':[t.model_dump(mode='json') for t in tasks], 'search_limits':limits,
        'arm_order':'alternating by selected task index; identical order in both modes',
        'promotion_rule':'keep legacy default unless new has zero rejected submissions, tasks with accepted routes >= legacy in both modes and strictly greater in at least one; report per-target losses',
        'modes':['cold','shared_precomputed'],'precomputation':'successful union of cold requests; no fallback',
        'source_hashes':_source_hashes(),'runtime':_runtime(), 'private_labels_read':False}
    plan_sha = _write(folder/'plan.json',plan)
    records, runs = (), ()
    for index,task in enumerate(tasks):
        context = _hash([backend_identity,task.model_dump(mode='json')])
        for arm in (('legacy_bfs','best_first') if index%2==0 else ('best_first','legacy_bfs')):
            backend = _RecordedBackend(backend_factory(),context)
            row = _one_run(folder,task,'cold',arm,policies[arm],backend,backend_identity,limits)
            records, runs = (*records,*backend.records), (*runs,row)
            _write(folder/'cold'/task.task_id/arm/'backend-calls.json',list(backend.records))
    entries, conflicts = _pool(records)
    pool_sha = _write(folder/'expansion-pool.json',{'entries':entries,'conflicting_keys':sorted(conflicts)})
    for index,task in enumerate(tasks):
        context = _hash([backend_identity,task.model_dump(mode='json')])
        for arm in (('legacy_bfs','best_first') if index%2==0 else ('best_first','legacy_bfs')):
            backend = _ReplayBackend(entries,context)
            row = _one_run(folder,task,'shared_precomputed',arm,policies[arm],backend,backend_identity,limits)
            runs = (*runs,row)
    report = {'schema_version':VERSION,'plan_sha256':plan_sha,'pool_sha256':pool_sha,
        'runs':list(runs),'aggregate':_aggregate(runs), 'private_labels_read':False,
        'scientific_feasibility':'not_evaluated','precomputation':{
        'backend_invocations':len(records),'backend_failures':sum(r['result']['status']!='ok' for r in records),
        'elapsed_seconds':sum(r['elapsed_seconds'] for r in records),
        'late_or_unobserved_calls':sum(not r.get('observed_by_policy',False) for r in records),
        'settlement_overhead_seconds':sum(r['settlement_overhead_seconds'] for r in runs),
        'unique_successful_keys':len(entries),'conflicting_keys':len(conflicts)},
        'limitations':['Small development pilot; no independent chemical review or final outcome scoring.',
            'Cold times include model startup; shared-precomputed excludes inference but records its cost.',
            'Faster replay may visit uncached nodes; pool misses are explicit and never trigger inference.',
            'Inventory variants of one target are correlated observations; accepted routes are predictions.']}
    source_end = _source_hashes()
    changed_sources = sorted(k for k in set(source_end)|set(plan['source_hashes'])
        if source_end.get(k) != plan['source_hashes'].get(k))
    changed_assets = [p for p,h in backend_identity.get('assets',{}).items()
        if not Path(p).is_file() or _file_hash(p) != h]
    public_integrity = None
    if cohort.get('public_bundle_path'):
        try:
            public_integrity = verify_bundle(cohort['public_bundle_path'],
                expected_manifest_sha256=cohort['public_manifest_sha256'])['verified']
        except (ValueError,OSError):
            public_integrity = False
    report = {**report,'integrity':{'public_bundle_verified':public_integrity,'source_changes':changed_sources,
        'asset_changes':changed_assets,'unchanged':not changed_sources and not changed_assets and public_integrity is not False}}
    _write(folder/'summary.json',report)
    if changed_sources or changed_assets or public_integrity is False:
        raise RuntimeError('Source/assets changed during comparison; retained report is invalid for acceptance')
    return report
