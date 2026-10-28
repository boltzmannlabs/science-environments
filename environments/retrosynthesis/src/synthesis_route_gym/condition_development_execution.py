"""Frozen condition development comparisons with scoring after all commitments.

Preparation reads public candidates and cached predictions only. Private replay
stays host-side; snapshots and model contexts exclude unqueried outcomes.
"""
from collections import defaultdict
from dataclasses import replace
import hashlib
import math
from pathlib import Path
import re
from types import SimpleNamespace
from .development_runner import digest, read, write_once, freeze_plan, verify_freeze
from .development_runner import capture_runtime_hardware, verify_runtime_hardware, classify_episode_stop
from .condition_benchmark import POLICIES, run_fixed_condition_episode, score_condition_decision
from .condition_io import ConditionStudySpec, _load_predictions, load_condition_inputs
from .condition_identity import condition_input_digest

SALT = 'srg12-condition-v1:'
ARMS = ('strong_fixed', 'main', 'main_condition_scientist')
FINITE = {'max_actions':80, 'wall_seconds':600, 'max_tokens':200000, 'model_calls':24}


def _require(test, message):
    if not test:
        raise ValueError(message)


def _ident(value):
    _require(isinstance(value,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}',value), 'Invalid study identifier')
    return value


def _hardware_declared(runtime):
    snapshot = runtime.get('hardware')
    required = {'platform','logical_cpus','affinity','gpu_inventory','gpu_inventory_status','environment'}
    _require(isinstance(snapshot,dict) and required <= set(snapshot), 'Actual local hardware snapshot required')
    _require(isinstance(snapshot['environment'],dict) and
             {'CUDA_VISIBLE_DEVICES','OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS'} <= set(snapshot['environment']),
             'Device and thread environment snapshot required')


def select_fixed_policy(summary):
    """Equal product weighting after within-product averaging; retain failures."""
    groups = defaultdict(lambda: defaultdict(list))
    for row in summary.get('runs',[]):
        if row.get('arm') not in POLICIES:
            continue
        value = row.get('penalized_submitted_regret_percent')
        _require(type(value) in (int,float) and math.isfinite(value) and value >= 0,
                 'Prior fixed policy lacks a finite failure-inclusive regret')
        groups[row['arm']][row['product_group']].append(value)
    _require(bool(groups), 'No prior fixed-policy development evidence')
    _require(len({tuple(sorted(rows)) for rows in groups.values()}) == 1, 'Prior policies have unmatched product groups')
    scores = {arm:sum(sum(values)/len(values) for values in rows.values())/len(rows)
              for arm,rows in groups.items()}
    return {'policy':min(scores,key=lambda arm:(scores[arm],arm)),
            'group_weighted_penalized_submitted_regret':scores,
            'selection_rule':'equal_product_group_mean_then_policy_id',
            'promotion_eligible':False,
            'prior_specialist_finding':'Step8 did not establish benefit attributable to accepted condition advice'}


def ranking_decisions(public, predictions):
    """Label-free base order and cached-model ranking, with explicit abstentions."""
    base = [row['candidate_id'] for row in public['candidates']]
    indexed = {row['candidate_id']:row for row in predictions}
    _require(len(indexed)==len(predictions) and set(indexed)==set(base), 'Predictions must match the same candidate pool')
    scored = [key for key in base if indexed[key]['status']=='scored']
    for key in scored:
        value = indexed[key]['value']
        _require(type(value) in (int,float) and math.isfinite(value) and 0 <= value <= 100, 'Invalid prediction value')
    abstained = [key for key in base if indexed[key]['status']=='abstained' and indexed[key]['value'] is None]
    _require(len(scored)+len(abstained)==len(base), 'Invalid prediction status')
    return {'model_off':{'order':base,'abstained_candidate_ids':[],'fallback_policy':None},
            'model_on':{'order':sorted(scored,key=lambda key:(-indexed[key]['value'],key))+abstained,
                        'abstained_candidate_ids':abstained,
                        'fallback_policy':'append_abstentions_in_frozen_base_order'}}


def _public_studies(manifest):
    _require(manifest.get('data_role')=='previously_used_development'
             and manifest.get('final_labels_accessed') is False, 'Only authorized development manifest permitted')
    groups = defaultdict(list)
    seen = set()
    for row in manifest['studies']:
        _ident(row['study_id']); _ident(row['product_group_id'])
        _require(row['study_id'] not in seen, 'Duplicate study identity')
        seen.add(row['study_id']); groups[row['product_group_id']].append(row)
    ordered = sorted(groups,key=lambda key:(hashlib.sha256((SALT+key).encode()).hexdigest(),key))
    _require(len(ordered)>=2, 'Two distinct development product groups required')
    return [min(groups[key],key=lambda row:row['study_id']) for key in ordered[:2]]


def _copy_public(row, output, model_metadata):
    paths = {}
    for kind in ('public','predictions'):
        source = Path(row[kind+'_path'])
        _require(digest(source)==row[kind+'_sha256'], 'Public input integrity mismatch')
        destination = output/'inputs'/(row['study_id']+'-'+kind+'.json')
        destination.parent.mkdir(parents=True,exist_ok=True)
        with destination.open('xb') as handle:
            handle.write(source.read_bytes())
        _require(digest(destination)==row[kind+'_sha256'], 'Public input changed during copy')
        paths[kind+'_path'] = str(destination.resolve())
    public = read(paths['public_path'])
    validated = ConditionStudySpec.model_validate(public)
    _require(validated.data_role=='development' and validated.study_id==row['study_id']
             and validated.product_group_id==row['product_group_id']
             and validated.group_id==row['group_id']
             and validated.outcomes_sha256==row['outcomes_sha256'], 'Manifest/public study binding differs')
    predictions = _load_predictions(paths['predictions_path'],validated.study_id,
        {c.candidate_id for c in validated.candidates},condition_input_digest(public))
    cached_metadata = read(paths['predictions_path'])['model_metadata']
    version = cached_metadata.get('model_version',cached_metadata.get('version'))
    _require(cached_metadata==model_metadata and isinstance(version,str)
             and all(prediction['model_version']==version for prediction in predictions),
             'Cached model metadata differs from frozen public manifest')
    return {**row, **paths, 'cached_model_metadata':cached_metadata}, ranking_decisions(public,predictions)


def prepare_condition_plan(manifest_path, prior_summary_path, output, *, runtime, previous_plan_path=None,
                           previous_plan_reason='keep identical candidate pools with explicit abstention fallback'):
    """Write a reviewable twelve-run plan without opening private outcomes."""
    _require((runtime.get('model'),runtime.get('provider'))==('gpt-6-sol','openai-codex'), 'Main-profile identity required')
    _hardware_declared(runtime)
    verify_runtime_hardware(runtime)
    manifest, summary = read(manifest_path), read(prior_summary_path)
    previous = None
    if previous_plan_path is not None:
        previous_path = Path(previous_plan_path)
        _require(not (previous_path.parent/'freeze.json').exists()
                 and not (previous_path.parent/'commitment.json').exists(), 'Previous plan must remain unexecuted')
        previous = {'plan_path':str(previous_path.resolve()),'plan_sha256':digest(previous_path),
                    'status':'superseded_before_freeze_or_execution',
                    'reason':previous_plan_reason}
    selected, fixed = _public_studies(manifest), select_fixed_policy(summary)
    output = Path(output); output.mkdir(parents=True,exist_ok=False)
    studies, rankings = {}, {}
    for row in selected:
        copied, ordering = _copy_public(row,output,manifest.get('model_metadata'))
        studies[row['study_id']] = copied
        for mode, decision in ordering.items():
            rankings[row['study_id']+'-'+mode] = {'study_id':row['study_id'],'mode':mode,**decision}
    runs = [{'run_id':f'D-{key}-{arm}-{regime}-r0','study_id':key,'arm':arm,'regime':regime,'seed':0}
            for key in studies for regime in ('budgeted','unbudgeted')
            for arm in sorted(ARMS,key=lambda value:hashlib.sha256(f'{SALT}{key}:{regime}:{value}'.encode()).hexdigest())]
    tasks = {key+'-'+kind:{'path':row[kind+'_path'],'sha256':row[kind+'_sha256']}
             for key,row in studies.items() for kind in ('public','predictions')}
    plan = {'schema_version':'srg12-condition-development-plan-v1','stage':'D_and_F_condition_pool',
            'partition':'development','studies':studies,'tasks':tasks,'runs':runs,
            'runtime':dict(runtime),'finite_limits':FINITE,'fixed_selection':fixed,
            'ranking_decisions':rankings,'ranking_top_k':[1,5],
            'ranking_policy_version':'srg12-condition-identical-pool-v2','previous_plan':previous,
            'selection_rule':SALT+'SHA256 product ordering; minimum study ID within product',
            'manifest_path':str(Path(manifest_path).resolve()),'manifest_sha256':digest(manifest_path),
            'prior_summary_path':str(Path(prior_summary_path).resolve()),'prior_summary_sha256':digest(prior_summary_path),
            'model_metadata':manifest.get('model_metadata'),
            'execution_approved':False,'final_labels_opened':False,
            'source_scope':'two previously used development products; one publication; no new experiments',
            'retry_policy':'one attempt per frozen run; retain failure/cancellation/unknown usage',
            'score_policy':'all twelve decisions and results committed before any scoring',
            'unbudgeted_policy':'null aggregate ceilings; finite authorized pool; explicit agent submission',
            'failure_policy':'null measured submission with explicit zero-yield scoring penalty'}
    write_once(output/'plan.json',plan)
    return plan


def freeze_condition_plan(plan_path, freeze_path, *, assets=()):
    plan = read(plan_path)
    profile = Path(plan['runtime']['profile_home'])/'config.yaml'
    _require(not any(Path(row['outcomes_path']).resolve() in [Path(p).resolve() for p in assets]
                     for row in plan['studies'].values()), 'Private outcomes cannot enter source snapshots')
    return freeze_plan(plan_path,freeze_path,
        assets=[*assets,profile,plan['manifest_path'],plan['prior_summary_path']],private_hash_only=[profile])


def _verify(plan_path, freeze_path, expected):
    verify_freeze(plan_path,freeze_path,expected)
    plan = read(plan_path)
    _hardware_declared(plan['runtime'])
    _require(plan.get('schema_version')=='srg12-condition-development-plan-v1'
             and plan.get('partition')=='development' and len(plan['runs'])==12,
             'Invalid condition development plan')
    _require(len({row['run_id'] for row in plan['runs']})==12, 'Duplicate run identities')
    expected_matrix = {(key,arm,regime) for key in plan['studies'] for arm in ARMS
                       for regime in ('budgeted','unbudgeted')}
    actual_matrix = {(row['study_id'],row['arm'],row['regime']) for row in plan['runs']}
    _require(len(plan['studies'])==2 and len(expected_matrix)==12 and actual_matrix==expected_matrix,
             'Condition run matrix must contain all twelve matched comparisons')
    _require(plan['finite_limits']==FINITE and
             (plan['runtime']['model'],plan['runtime']['provider'])==('gpt-6-sol','openai-codex'),
             'Runtime configuration differs from prospective design')
    for row in plan['runs']:
        _ident(row['run_id'])
        _require(row['arm'] in ARMS and row['regime'] in {'budgeted','unbudgeted'}
                 and row['study_id'] in plan['studies'], 'Invalid run configuration')
    return plan


def execute_condition(inputs, row, runtime, folder):
    """Existing metered fixed/native interfaces receive identical public data."""
    from .condition_episode import ConditionEpisode
    from .condition_session import run_condition_agent
    from .agent_runner import resolve_main_profile
    unlimited = row['regime']=='unbudgeted'
    limits = {key:None if unlimited else value for key,value in FINITE.items()}
    study = replace(inputs['study'],budget=None) if unlimited else inputs['study']
    episode = ConditionEpisode(study,**{key:inputs[key] for key in ('study_id','target','predictions')},
        regime=row['regime'],max_actions=limits['max_actions'],wall_seconds=limits['wall_seconds'],store=folder/'environment')
    try:
        if row['arm']=='strong_fixed':
            return run_fixed_condition_episode(episode,runtime['fixed_policy'],seed=row['seed'])
        profile = resolve_main_profile(runtime['profile_home'])
        _require((profile.model,profile.provider)==(runtime['model'],runtime['provider']), 'Main profile identity changed')
        args = SimpleNamespace(**{key:runtime[key] for key in ('profile_home','scientist_python','scientist_source')},
            **limits,method=row['arm'],budget_regime=row['regime'])
        return run_condition_agent(args,episode,folder/'runtime')
    except (Exception, KeyboardInterrupt) as error:
        interrupted = isinstance(error,KeyboardInterrupt)
        if interrupted:
            episode.cancel('external_operator_interruption')
        return {'method':row['arm'],'episode':episode.export(),'interrupted':interrupted,
                'error_type':type(error).__name__,'agent':{'completed':False,
                'resource_accounting':'unknown_after_interruption',
                'checkpoint_policy':'preserved runtime/environment are authoritative'}}


def run_condition_plan(plan_path, freeze_path, output, *, expected_freeze_sha256,
                       execution_approved=False, executor=None):
    _require(execution_approved is True, 'Explicit coordinator execution approval required')
    plan = _verify(plan_path,freeze_path,expected_freeze_sha256)
    verify_runtime_hardware(plan['runtime'])
    output = Path(output)
    _require(not output.exists(), 'Existing attempt must not be silently retried')
    output.mkdir(parents=True)
    receipts = []
    for row in plan['runs']:
        _verify(plan_path,freeze_path,expected_freeze_sha256)
        verify_runtime_hardware(plan['runtime'])
        folder = output/row['run_id']; folder.mkdir()
        write_once(folder/'started.json',{'run':row,'freeze_sha256':expected_freeze_sha256})
        error = None
        try:
            source = plan['studies'][row['study_id']]
            _require(digest(source['outcomes_path'])==source['outcomes_sha256'], 'Private development commitment differs')
            inputs = load_condition_inputs(source['public_path'],source['outcomes_path'],source['predictions_path'])
            runtime = {**plan['runtime'],'fixed_policy':plan['fixed_selection']['policy']}
            result = (executor or execute_condition)(inputs,row,runtime,folder)
        except (Exception,KeyboardInterrupt) as caught:
            error = caught
            result = {'method':row['arm'],'episode':None,'error_type':type(caught).__name__,
                      'resource_accounting':'unknown; inspect preserved environment/runtime checkpoints'}
        episode = result.get('episode')
        decision = ({key:episode[key] for key in ('study_id','observations','submission')} if episode else None)
        ceiling = {'max_actions':FINITE['max_actions'],'max_wall_seconds':FINITE['wall_seconds'],
                   'max_llm_tokens':FINITE['max_tokens'],'max_model_calls':FINITE['model_calls'],
                   'max_tool_calls':FINITE['max_actions']}
        reason = (episode or {}).get('stop_reason')
        cancellation = reason if reason in {'external_operator_interruption','host_cancelled','cancelled'} else None
        stop = classify_episode_stop(result,row['regime'],ceilings=ceiling,
                                     agent_expected=row['arm']!='strong_fixed',cancel_reason=cancellation)
        status = 'failed' if error is not None else stop['status']
        if isinstance(error,KeyboardInterrupt) or result.get('interrupted') is True:
            status = 'interrupted'
        hardware = {'before':'matched','after':'matched'}
        try:
            verify_runtime_hardware(plan['runtime'])
        except (ValueError,OSError) as mismatch:
            hardware = {'before':'matched','after':'mismatch','error_type':type(mismatch).__name__}
            status = 'interrupted'
        receipt = {'run':row,'freeze_sha256':expected_freeze_sha256,
            'status':status,'hardware_verification':hardware,
            'result_sha256':write_once(folder/'result.json',result),
            'decision_sha256':write_once(folder/'decision.json',decision)}
        _verify(plan_path,freeze_path,expected_freeze_sha256)
        receipts.append(receipt)
        write_once(folder/'receipt.json',receipt)
        if status=='interrupted':
            break
    commitment = {'schema_version':'srg12-condition-decisions-v1','freeze_sha256':expected_freeze_sha256,
                  'receipts':receipts,'all_decisions_committed':len(receipts)==len(plan['runs']),
                  'failed':sum(row['status']=='failed' for row in receipts)}
    write_once(output/'commitment.json',commitment)
    write_once(output/'commitment.sha256.json',{'sha256':digest(output/'commitment.json')})
    return commitment


def _committed(output, plan, freeze_sha):
    _require((output/'commitment.json').is_file(), 'All decisions must be committed before scoring')
    commitment = read(output/'commitment.json')
    _require(read(output/'commitment.sha256.json')=={'sha256':digest(output/'commitment.json')}
             and commitment['freeze_sha256']==freeze_sha and commitment['all_decisions_committed'] is True
             and [row['run'] for row in commitment['receipts']]==plan['runs'], 'Decision commitment differs')
    for receipt in commitment['receipts']:
        folder = output/receipt['run']['run_id']
        _require(read(folder/'receipt.json')==receipt, 'Run receipt differs')
        for kind in ('result','decision'):
            _require(digest(folder/(kind+'.json'))==receipt[kind+'_sha256'], 'Committed artifact differs')
        result, decision = read(folder/'result.json'),read(folder/'decision.json')
        episode = result.get('episode')
        expected = {key:episode[key] for key in ('study_id','observations','submission')} if episode else None
        _require(decision==expected, 'Committed decision differs from actual episode')
    return commitment


def _rank_score(decision,outcomes):
    order = decision['order']; optimum = max(outcomes.values())
    comparable = [(a,b) for i,a in enumerate(order) for b in order[i+1:] if outcomes[a]!=outcomes[b]]
    return {**decision,'coverage':(len(order)-len(decision['abstained_candidate_ids']))/len(outcomes),
            'coverage_scope':('baseline_pool_coverage' if decision.get('mode')=='model_off'
                              else 'accepted_model_predictions; fallback does not imply prediction exposure'),
            'ranking_pool_coverage':len(order)/len(outcomes),
            'top_1_regret_percent':None if not order else optimum-outcomes[order[0]],
            'top_5_regret_percent':None if not order else optimum-max(outcomes[key] for key in order[:5]),
            'pairwise_accuracy':None if not comparable else sum(outcomes[a]>outcomes[b] for a,b in comparable)/len(comparable),
            'scope':'same authorized finite pool; cached model ranking only; no route generation claim'}


def aggregate_scores(rows):
    """Product-group means and paired directions; no independence/power claim."""
    result = {}
    for regime in ('budgeted','unbudgeted'):
        selected = [row for row in rows if row['regime']==regime]
        groups = defaultdict(lambda: defaultdict(list))
        for row in selected:
            groups[row['arm']][row['product_group_id']].append(row['penalized_submitted_regret_percent'])
        means = {arm:{group:sum(values)/len(values) for group,values in records.items()}
                 for arm,records in groups.items()}
        gains = [means['main'][group]-means['main_condition_scientist'][group]
                 for group in means.get('main',{}) if group in means.get('main_condition_scientist',{})]
        result[regime] = {'group_weighted_penalized_submitted_regret':{
            arm:sum(records.values())/len(records) for arm,records in means.items()},
            'failed_or_missing_submissions':sum(row['submission_status']!='selected' for row in selected),
            'incomplete_attempts':sum(row['attempt_status']!='completed' for row in selected),
            'paired_main_minus_assisted_regret':{'mean':sum(gains)/len(gains) if gains else None,
                'wins':sum(value>0 for value in gains),'ties':sum(value==0 for value in gains),
                'losses':sum(value<0 for value in gains),'product_groups':len(gains)}}
    return result


def score_condition_plan(plan_path, freeze_path, output, *, expected_freeze_sha256):
    output = Path(output)
    _require((output/'commitment.json').is_file(), 'All decisions must be committed before scoring')
    plan = _verify(plan_path,freeze_path,expected_freeze_sha256)
    commitment = _committed(output,plan,expected_freeze_sha256)
    scores, ranking = [], []
    for key,source in plan['studies'].items():
        _require(digest(source['outcomes_path'])==source['outcomes_sha256'], 'Private development commitment differs')
        inputs = load_condition_inputs(source['public_path'],source['outcomes_path'],source['predictions_path'])
        outcomes = {row.candidate_id:row.yield_percent for row in inputs['study']._records}
        for receipt in commitment['receipts']:
            row = receipt['run']
            if row['study_id']!=key: continue
            decision = read(output/row['run_id']/'decision.json')
            public = inputs['public_metadata']
            # Existing evaluator uses a finite validation allowance. Pool size
            # bounds authorized observations without imposing a research quota.
            if row['regime']=='unbudgeted':
                public = {**public,'observation_budget':len(outcomes)}
            score = (score_condition_decision(public,outcomes,decision) if decision is not None else
                     {'submission_status':'not_submitted','submitted_yield_percent':None,
                      'submitted_regret_percent':None,'penalized_submitted_regret_percent':max(outcomes.values()),
                      'failure_penalty_scope':'zero-yield scoring penalty, not a measured outcome'})
            result = read(output/row['run_id']/'result.json')
            scores.append({**score,**row,'product_group_id':source['product_group_id'],
                           'observation_ceiling':None if row['regime']=='unbudgeted' else inputs['study'].budget,
                           'episode_usage':(result.get('episode') or {}).get('usage'),
                           'agent_resources':(result.get('agent') or {}).get('ledger'),
                           'attempt_status':receipt['status']})
        ranking.extend({**_rank_score(value,outcomes),'product_group_id':source['product_group_id']}
                       for value in plan['ranking_decisions'].values() if value['study_id']==key)
    return {'scope':'previously used development; two product groups in one publication',
            'runs':scores,'aggregate':aggregate_scores(scores),'ranking_ablation':ranking,
            'ranking_group_mean_top_1_regret':{mode:sum(values)/len(values) if values else None
                for mode in ('model_off','model_on')
                for values in [[row['top_1_regret_percent'] for row in ranking
                                if row['mode']==mode and row['top_1_regret_percent'] is not None]]},
            'all_decisions_committed_before_scoring':True,
            'promotion_eligible':False,'final_labels_opened':False,'new_experiments':False,
            'commitment_sha256':digest(output/'commitment.json'),'freeze_sha256':expected_freeze_sha256}
