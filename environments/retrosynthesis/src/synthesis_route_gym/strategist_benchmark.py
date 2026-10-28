"""Development-only source scoring and descriptive Strategist comparisons.

Only the selected private answer is read. This is deliberately narrower than
full private-bundle verification and never claims the other labels were checked.
"""
import math

from .dataset_bundle import (_read, _path, _hash, _digest, _identifier, _json_load, _decision,
    _labels, _PublicTask, _score_reference, SCHEMA_VERSION, SCORE_SCOPE)
from .schemas import Task, InventoryItem


def _pinned_file(folder, manifest, name):
    if name not in manifest['files']:
        raise ValueError('Required file absent from pinned manifest')
    raw = _read(folder/name)
    if _hash(raw) != _digest(manifest['files'][name]):
        raise ValueError('Selected bundle file hash mismatch')
    return _json_load(raw)


def load_public_selected_development(public_dir, task_id, *, expected_manifest_sha256):
    """Read pinned manifest, selected development task and shared stock only."""
    _identifier(task_id)
    folder = _path(public_dir)
    raw = _read(folder/'manifest.json')
    if _hash(raw) != _digest(expected_manifest_sha256):
        raise ValueError('Public manifest hash mismatch')
    manifest = _json_load(raw)
    if (not isinstance(manifest,dict)
            or set(manifest) != {'schema_version','bundle_kind','files','tasks'}
            or manifest['schema_version'] != SCHEMA_VERSION or manifest['bundle_kind'] != 'public'
            or not isinstance(manifest['tasks'],list) or not isinstance(manifest['files'],dict)):
        raise ValueError('Invalid pinned public manifest')
    matches = [row for row in manifest['tasks']if row.get('task_id') == task_id]
    if len(matches) != 1 or matches[0].get('partition') != 'development' or matches[0].get('track') != 'reference_route':
        raise ValueError('Only development reference-route decisions may be scored')
    task = _PublicTask.model_validate(_pinned_file(folder,manifest,f'tasks/{task_id}.json'))
    if any(getattr(task,key) != matches[0].get(key)for key in ('task_id','partition','track')):
        raise ValueError('Selected task differs from public manifest')
    stock = _pinned_file(folder,manifest,'inventory.json')
    if (not isinstance(stock,list) or any(not isinstance(s,str)for s in stock)
            or len(stock) != len(set(stock)) or not set(task.inventory_exclusions) <= set(stock)):
        raise ValueError('Invalid pinned shared stock')
    inventory = tuple(InventoryItem(smiles=s)for s in stock if s not in task.inventory_exclusions)
    materialized = Task(task_id=task.task_id,target=task.target,inventory=inventory,
                        constraints=task.constraints,budget=task.budget)
    return {**task.model_dump(mode='json',exclude_none=True),**materialized.model_dump(mode='json')}


def _selected_manifest(private_dir, expected_private, expected_public):
    folder = _path(private_dir)
    raw = _read(folder / 'manifest.json')
    if _hash(raw) != _digest(expected_private):
        raise ValueError('Private manifest hash mismatch')
    manifest = _json_load(raw)
    fields = {'schema_version','bundle_kind','public_manifest_sha256','files'}
    if (not isinstance(manifest,dict) or set(manifest) != fields
            or manifest['schema_version'] != SCHEMA_VERSION
            or manifest['bundle_kind'] != 'private'
            or manifest['public_manifest_sha256'] != expected_public
            or not isinstance(manifest['files'],dict)):
        raise ValueError('Private manifest differs from pinned public bundle')
    if folder.stat().st_mode & 0o777 != 0o700:
        raise ValueError('Private directory permissions must be 0700')
    return folder, manifest


def score_selected_development(public_dir, private_dir, decision_path, expected_sha256,
                               *, expected_manifest_sha256, expected_private_manifest_sha256):
    """Verify a commitment and open exactly one pinned development route label."""
    expected_public = _digest(expected_manifest_sha256)
    _digest(expected_private_manifest_sha256)
    raw = _read(decision_path)
    if _hash(raw) != _digest(expected_sha256):
        raise ValueError('Decision hash mismatch before private evaluation')
    decision = _decision(_json_load(raw))
    public = load_public_selected_development(public_dir,decision['task_id'],expected_manifest_sha256=expected_public)
    if public['partition'] != 'development' or public['track'] != 'reference_route':
        raise ValueError('Only development reference-route decisions may be scored')
    if 'routes' not in decision:
        raise ValueError('Reference task requires committed routes')
    folder, manifest = _selected_manifest(private_dir,expected_private_manifest_sha256,expected_public)
    name = f"labels/{decision['task_id']}.json"
    if name not in manifest['files']:
        raise ValueError('Selected label is absent from pinned manifest')
    label_path = _path(folder / name)
    if label_path.parent.stat().st_mode & 0o777 != 0o700:
        raise ValueError('Private label directory permissions must be 0700')
    label_raw = _read(label_path)
    if label_path.stat().st_mode & 0o777 != 0o600:
        raise ValueError('Private label permissions must be 0600')
    if _hash(label_raw) != _digest(manifest['files'][name]):
        raise ValueError('Selected label hash mismatch')
    label = _json_load(label_raw)
    task = _PublicTask.model_validate({k:public[k] for k in _PublicTask.model_fields if k in public})
    _labels((task,),[label])
    return {'task_id':decision['task_id'],'track':'reference_route','partition':'development',
        'decision_sha256':expected_sha256,'scope':SCORE_SCOPE,
        'private_access_scope':'selected_development_label_only','private_bundle_fully_verified':False,
        **_score_reference(public,label,decision)}


def _number(value, *, integer=False):
    if value is None:
        return None
    allowed = (int,) if integer else (int,float)
    if type(value) not in allowed or not math.isfinite(value) or value < 0:
        raise ValueError('Resource telemetry must be finite and nonnegative')
    return value


def _resources(run, agent, fixed):
    ledger = agent.get('ledger') or {}
    source = 'agent_ledger' if ledger else 'unknown'
    checkpoint = run.get('runtime_checkpoint') or {}
    if not ledger and checkpoint.get('ledger'):
        saved = checkpoint['ledger']
        counts = saved['counts']
        ledger = {**counts,'charged_tokens':counts['actual_tokens']+counts['reserved_tokens'],
                  'unsettled_requests':sum(r['actual'] is None for r in saved['requests'].values())}
        source = 'durable_checkpoint'
    counts = {key:_number(0 if fixed else ledger.get(key),integer=True)
              for key in ('model_calls','actual_tokens','reserved_tokens','charged_tokens','unsettled_requests')}
    state = agent.get('strategist_state') or checkpoint.get('strategist') or {}
    status = (state.get('consultation') or {}).get('status')
    attempts = len(agent.get('strategist_runs') or state.get('runs') or [])
    attempts = max(attempts,int(status in {'pending','interrupted'}))
    return {**counts,'resource_source':'fixed_no_llm' if fixed else source,
            'strategist_invocations':attempts,'strategist_status':status,
            'strategist_invocation_scope':'recorded role attempts; ledger retains actual request admissions'}


def summarize_run(run, score, *, arm, task_id):
    """Preserve failures and unsettled reservations; do not count nested usage twice."""
    if arm not in {'fixed','best_first','main','main_strategist'}:
        raise ValueError('Unknown comparison arm')
    episode = run['episode']
    if (episode['task']['task_id'] != task_id or score['task_id'] != task_id
            or score['scope'] != SCORE_SCOPE):
        raise ValueError('Run and development score identities or scope differ')
    fixed = arm in {'fixed','best_first'}
    agent = run.get('agent') or {}
    usage = episode['usage']
    pilot_k = episode['task'].get('budget',{}).get('top_k')
    if pilot_k is not None and score['submitted_routes'] > _number(pilot_k,integer=True):
        raise ValueError('Submission exceeds effective pilot top-k')
    checks = score['route_checks']
    accepted = [r for r in checks if r['graph_valid'] and r['inventory_complete']
        and r['constraint_compliant'] and not r['acquisition_only']
        and r['quantity_status'] in {'not_requested','complete'}]
    return {'arm':arm,'task_id':task_id,'target':episode['task']['target'],
        'completed':bool(episode['terminated']) if fixed else bool(agent.get('completed',False)),
        'submitted':bool(episode['terminated']),'submitted_routes':score['submitted_routes'],
        'task_top_k':pilot_k,'reference_evaluator_top_k':score.get('top_k'),
        'truncated':bool(episode['truncated']),
        'reference_recovered':bool(score['reference_match_at_k']),
        'inventory_compliant_reference_recovered':bool(score['inventory_compliant_reference_recovery']['at_k']),
        'deterministically_accepted_routes':len(accepted),
        'scientifically_solved_routes':sum(r.get('solved') is True for r in checks),
        'model':agent.get('model'),'provider':agent.get('provider'),**_resources(run,agent,fixed),
        'actions':_number(usage.get('actions'),integer=True),
        'expansions':_number(usage.get('expansions'),integer=True),
        'elapsed_seconds':_number(usage.get('wall_seconds')),
        'evaluation_scope':SCORE_SCOPE,'error_type':agent.get('error_type')}


def _sum_known(rows, key):
    values = [_number(row.get(key)) for row in rows]
    return sum(values) if all(v is not None for v in values) else None


def summarize_comparison(rows):
    """A small development diagnostic never automatically promotes a specialist."""
    if not isinstance(rows,list) or not rows:
        raise ValueError('Provide nonempty paired run summaries')
    indexed = {}
    for row in rows:
        if row['arm'] not in {'fixed','best_first','main','main_strategist'}:
            raise ValueError('Unknown comparison arm')
        key = (row['task_id'],row['arm'])
        if key in indexed:
            raise ValueError('Duplicate comparison observation')
        indexed = {**indexed,key:row}
    task_ids = sorted({row['task_id']for row in rows})
    pairs = []
    for ident in task_ids:
        if any((ident,arm) not in indexed for arm in ('main','main_strategist')):
            raise ValueError('Every task requires both agent arms, including failures')
        main, strategy = (indexed[(ident,arm)]for arm in ('main','main_strategist'))
        if main['target'] != strategy['target']:
            raise ValueError('Paired targets differ')
        identities = [(r.get('model'),r.get('provider'))for r in (main,strategy)]
        if all(all(value for value in identity)for identity in identities) and identities[0] != identities[1]:
            raise ValueError('Paired model/provider differs; compare failures explicitly before aggregation')
        pairs.append((main,strategy))
    return _comparison_result(rows,pairs,task_ids)


def _comparison_result(rows, pairs, task_ids):
    main = [p[0] for p in pairs]
    strategy = [p[1] for p in pairs]
    quality = lambda row:int(row['inventory_compliant_reference_recovered'])
    differences = [quality(s)-quality(m) for m,s in pairs]
    targets = {row['target'] for row in main}
    resource_keys = ('model_calls','charged_tokens','actual_tokens','reserved_tokens','actions','expansions','elapsed_seconds')
    aggregate = {arm:{'tasks':len(selected),
        'reference_recovered_tasks':sum(bool(r['reference_recovered'])for r in selected),
        'inventory_compliant_reference_recovered_tasks':sum(quality(r)for r in selected),
        'deterministically_accepted_routes':sum(r['deterministically_accepted_routes']for r in selected),
        'failed_runs':sum(not r['completed']for r in selected),
        'strategist_invocations':sum(r['strategist_invocations']for r in selected),
        **{key:_sum_known(selected,key)for key in resource_keys}}
        for arm in sorted({r['arm']for r in rows})
        for selected in [[r for r in rows if r['arm']==arm]]}
    deltas = {key:(_sum_known(strategy,key)-_sum_known(main,key)
        if _sum_known(strategy,key) is not None and _sum_known(main,key) is not None else None)
        for key in resource_keys}
    blockers = ['descriptive_development_pilot_not_promotion_test']
    if len(targets)<20: blockers.append('small_development_cohort')
    if not any(quality(r)for r in main+strategy): blockers.append('no_positive_quality')
    if not any(r['strategist_invocations']for r in strategy): blockers.append('strategist_not_invoked')
    if any(deltas[k] is None for k in resource_keys): blockers.append('incomplete_resource_accounting')
    if any(not r.get('model') or not r.get('provider')for r in main+strategy):
        blockers.append('unverified_model_profile')
    return {'scope':'paired_development_diagnostic_not_final_benchmark',
        'paired_task_count':len(task_ids),'independent_target_count':len(targets),
        'independence_limit':'Distinct targets are not proof of independent source or scaffold groups.',
        'aggregate':aggregate,'paired':{'wins':sum(d>0 for d in differences),
            'ties':sum(d==0 for d in differences),'losses':sum(d<0 for d in differences),
            'model_call_delta':deltas['model_calls'],'resource_deltas_strategy_minus_main':deltas},
        'promotion_eligible':False,'promotion_blockers':blockers,
        'default_changed':False,'independent_chemical_review':'not_performed'}
