"""Descriptive development aggregation; route matching is not feasibility proof."""
from collections import defaultdict
import math
from pathlib import Path
from . import development_runner as runner
from .development_runner import FIXED_ARMS


def _sum_known(rows,key):
    values=[row.get(key) for row in rows]
    return None if any(value is None for value in values) else sum(values)


def summarize_stage(rows):
    if not isinstance(rows,list) or not rows:
        raise ValueError('Expected nonempty matched development results')
    arms, identities=defaultdict(list), defaultdict(set)
    for row in rows:
        for key in ('arm','task_id','group_id','attempt_status'):
            if not isinstance(row.get(key),str) or not row[key]:
                raise ValueError('Missing development identity')
        for key in ('accepted_routes','expansions'):
            if key=='expansions' and row.get(key) is None:
                continue
            if type(row.get(key)) is not int or row[key] < 0:
                raise ValueError('Invalid development count')
        for key in ('inventory_compliant_reference_recovered','reference_recovered','submitted'):
            if type(row.get(key)) is not bool:
                raise ValueError('Invalid development outcome flag')
        for key in ('model_calls','actual_tokens','unsettled_requests','elapsed_seconds'):
            value=row.get(key)
            if value is not None and (type(value) not in (int,float) or not math.isfinite(value) or value<0):
                raise ValueError('Invalid development telemetry')
        identity=(row['task_id'],row.get('regime','budgeted'),row.get('repeat_id',0))
        if identity in identities[row['arm']]:
            raise ValueError('Duplicate development trial')
        identities[row['arm']].add(identity)
        arms[row['arm']].append(row)
    if len({frozenset(value) for value in identities.values()}) != 1:
        raise ValueError('Development arms have unmatched trial sets')
    summaries={arm:{'attempted':len(values),
        'submitted':sum(r['submitted'] for r in values),
        'failed_or_incomplete':sum(r['attempt_status']!='completed' for r in values),
        'reference_recovered':sum(r['reference_recovered'] for r in values),
        'inventory_compliant_reference_recovered':sum(r['inventory_compliant_reference_recovered'] for r in values),
        'inventory_closed_tasks':sum(r['accepted_routes']>0 for r in values),
        **{key:_sum_known(values,key) for key in ('expansions','elapsed_seconds','model_calls','actual_tokens','unsettled_requests')}}
        for arm,values in arms.items()}
    fixed=[arm for arm in summaries if arm in FIXED_ARMS]
    selected=min(fixed,key=lambda arm:(-summaries[arm]['inventory_compliant_reference_recovered'],
        -summaries[arm]['inventory_closed_tasks'],
        math.inf if summaries[arm]['expansions'] is None else summaries[arm]['expansions'],arm)) if fixed else None
    return {'arms':summaries,'selected_fixed':selected,
        'fixed_selection_rule':'qualified reference recovery, inventory-closed tasks, fewer expansions, algorithm ID',
        'target_groups':len({r['group_id'] for r in rows}),
        'group_independence_scope':'input target groups; source-family independence not established',
        'all_zero_reference_recovery':not any(r['inventory_compliant_reference_recovered'] for r in rows),
        'scientific_improvement_established':False,'final_labels_opened':False,
        'scope':'descriptive development; inventory closure and reference recovery are separate from chemical feasibility'}


def _receipt(folder,row,freeze_sha):
    receipt=runner.read(folder/'receipt.json')
    if (runner.read(folder/'receipt.sha256.json') != {'sha256':runner.digest(folder/'receipt.json')}
            or receipt.get('run')!=row or receipt.get('freeze_sha256')!=freeze_sha):
        raise ValueError('Attempt commitment integrity mismatch')
    for name,expected in receipt['artifact_sha256'].items():
        if name not in {'result.json','decision.json','started.json'} or runner.digest(folder/name)!=expected:
            raise ValueError('Committed result/decision integrity mismatch')
    if receipt['status']=='completed' and not {'result.json','decision.json'}<=set(receipt['artifact_sha256']):
        raise ValueError('Completed attempt lacks a committed submission')
    return receipt


def _analysis_row(row,group,receipt,result,score):
    episode=(result or {}).get('episode') or {}
    usage=episode.get('usage') or receipt.get('resources') or {}
    ledger=((result or {}).get('agent') or {}).get('ledger') or receipt.get('agent_resources') or {}
    fixed=row['arm'] in FIXED_ARMS
    checks=(score or {}).get('route_checks',[])
    accepted=sum(r['graph_valid'] and r['inventory_complete'] and r['constraint_compliant']
        and not r['acquisition_only'] and r['quantity_status'] in {'complete','not_requested'} for r in checks)
    label=(row['arm']+'_model_'+('on' if row['model_enabled'] else 'off')) if 'model_enabled' in row else row['arm']
    return {**row,'arm':label,'executed_arm':row['arm'],'group_id':group,'attempt_status':receipt['status'],'accepted_routes':accepted,
        'submitted':score is not None,'reference_recovered':bool((score or {}).get('reference_match_at_k')),
        'inventory_compliant_reference_recovered':bool((score or {}).get('inventory_compliant_reference_recovery',{}).get('at_k')),
        'expansions':usage.get('expansions'),'elapsed_seconds':receipt.get('elapsed_seconds'),
        'model_calls':0 if fixed else ledger.get('model_calls'),
        'actual_tokens':0 if fixed else None if ledger.get('unsettled_requests',1) else ledger.get('actual_tokens'),
        'confirmed_tokens':0 if fixed else ledger.get('actual_tokens'),
        'reserved_tokens':0 if fixed else ledger.get('reserved_tokens'),
        'unsettled_requests':0 if fixed else ledger.get('unsettled_requests'),
        'model_ablation':(result or {}).get('model_ablation'),
        'independent_chemical_review':'not_performed'}


def _verified_result(folder,row,receipt,task):
    result=runner.read(folder/'result.json') if 'result.json' in receipt['artifact_sha256'] else None
    if result is None:
        if 'decision.json' in receipt['artifact_sha256']:
            raise ValueError('A committed decision requires a verified result')
        return None
    expected=(task.model_copy(update={'budget':runner.Budget.unbudgeted(top_k=task.budget.top_k)})
              if row['regime']=='unbudgeted' else task)
    if result.get('episode',{}).get('task')!=expected.model_dump(mode='json'):
        raise ValueError('Committed task integrity mismatch')
    if ('decision.json' in receipt['artifact_sha256']
            and runner.read(folder/'decision.json')!=runner._decision(expected,result)):
        raise ValueError('Committed submission integrity mismatch')
    return result


def _grouping(plan,selection,tasks,freeze_path,selection_path):
    expected=plan.get('selection_sha256')
    if expected is not None:
        pinned=runner.read(freeze_path)['files']
        if (selection_path is None or str(Path(selection_path).resolve()) not in pinned
                or runner.digest(selection_path)!=expected or runner.read(selection_path)!=selection):
            raise ValueError('Public selection integrity mismatch')
    groups={}
    targets,group_targets={},{}
    for group in selection['groups']:
        for key in group['task_ids']:
            if key in groups:
                raise ValueError('Duplicate task membership in target grouping')
            groups[key]=group['group_id']
            if key not in tasks:
                continue
            target=tasks[key].target
            if (targets.get(target,group['group_id'])!=group['group_id']
                    or group_targets.get(group['group_id'],target)!=target):
                raise ValueError('Target grouping splits inventory siblings or merges distinct targets')
            targets[target]=group['group_id']
            group_targets[group['group_id']]=target
    if not set(tasks)<=set(groups):
        raise ValueError('Task grouping is incomplete')
    return groups


def score_stage(plan_path,freeze_path,output,*,expected_freeze_sha256,public_dir,private_dir,
                expected_public,expected_private,selection,selection_path=None,scorer=None):
    """Score selected development answers only after every planned attempt commits."""
    from .strategist_benchmark import score_selected_development
    scorer=score_selected_development if scorer is None else scorer
    runner.verify_freeze(plan_path,freeze_path,expected_freeze_sha256)
    plan=runner.read(plan_path)
    tasks=runner._load_plan_tasks(plan)
    output=Path(output)
    planned={r['run_id'] for r in plan['runs']}
    if not output.is_dir() or {p.name for p in output.iterdir() if p.is_dir()}!=planned:
        raise ValueError('All planned attempt commitments are required before scoring')
    groups=_grouping(plan,selection,tasks,freeze_path,selection_path)
    receipts=[_receipt(output/r['run_id'],r,expected_freeze_sha256) for r in plan['runs']]
    results=[_verified_result(output/r['run_id'],r,receipt,tasks[r['task_id']])
             for r,receipt in zip(plan['runs'],receipts)]
    start={'freeze_sha256':expected_freeze_sha256,'plan_sha256':runner.digest(plan_path),
        'commitments':{r['run']['run_id']:r['artifact_sha256'] for r in receipts},
        'scope':'selected development answers only; label access may now begin','final_labels_opened':False}
    access=output/'evaluation-start.json'
    if access.exists():
        if runner.read(access)!=start:
            raise ValueError('Prior evaluation commitment differs')
    else:
        runner.write_once(access,start)
    scores,rows=[],[]
    for row,receipt,result in zip(plan['runs'],receipts,results):
        folder=output/row['run_id']
        score=None
        if 'decision.json' in receipt['artifact_sha256']:
            if result is None:
                raise ValueError('A committed decision requires a verified result')
            score=scorer(public_dir,private_dir,folder/'decision.json',receipt['artifact_sha256']['decision.json'],
                expected_manifest_sha256=expected_public,expected_private_manifest_sha256=expected_private)
            if (score.get('task_id')!=row['task_id'] or score.get('partition')!='development'
                    or score.get('decision_sha256')!=receipt['artifact_sha256']['decision.json']):
                raise ValueError('Scoring returned the wrong development identity')
            scores.append(score)
        rows.append(_analysis_row(row,groups[row['task_id']],receipt,result,score))
    runner.verify_freeze(plan_path,freeze_path,expected_freeze_sha256)
    return {'rows':rows,'scores':scores,
        'by_regime':{regime:summarize_stage([r for r in rows if r['regime']==regime]) for regime in sorted({r['regime'] for r in rows})},
        'all_planned_attempts_committed_before_evaluation':True,'final_labels_opened':False,
        'evaluation_start_sha256':runner.digest(access),'freeze_sha256':expected_freeze_sha256}
