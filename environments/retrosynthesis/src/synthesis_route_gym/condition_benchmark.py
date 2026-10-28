"""Public-view condition policies and separate measured-replay evaluation.

Policies never receive the private outcome map. Gaussian-process acquisition
uses only revealed observations and frozen categorical features/hyperparameters;
it is an episode optimization policy, not a new transferable chemistry model.
"""
import hashlib
import json
import math
import random
import re
from collections import defaultdict

POLICIES = ('fixed_order', 'random', 'public_model_rank', 'gp_expected_improvement')
ARMS = (*POLICIES, 'main', 'main_condition_scientist')
SCOPE = 'measured_development_replay_not_new_experimental_validation'
GP_CONFIGURATION = {
    'version':'srg-condition-categorical-gp-ei-v1',
    'features':'one_hot_condition_categories_from_public_candidate_pool',
    'kernel':'fixed_unit_variance_rbf', 'length_scale':1.0,
    'alpha':1e-6, 'optimizer':None, 'prior_mean_percent':50.0,
    'prior_std_percent':25.0, 'expected_improvement_xi_percent':0.01,
    'uses_pretrained_prediction_values':False,
    'uncertainty_scope':'episode_surrogate_not_calibrated_chemical_uncertainty',
}
_VIEW_KEYS = frozenset({'schema_version','study_id','revision','substrate','target',
    'domain_status','measurement','candidates','observations','predictions','resources','submission',
    'unavailable_candidate_ids','terminated','truncated','usage'})
_OUTCOME_KEYS = frozenset({'yield','yield_percent','outcome','outcomes','label','labels',
    'score','best','optimum','dataset_optimum_yield_percent','simple_regret_percent'})


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    allow_nan=False).encode()).hexdigest()


def _number(value, name, *, maximum=None, integer=False):
    allowed = (int,) if integer else (int, float)
    _require(type(value) in allowed and math.isfinite(value) and value >= 0,
             f'{name} must be finite and nonnegative')
    _require(maximum is None or value <= maximum, f'{name} exceeds its bound')
    return value


def _text(value, name):
    _require(isinstance(value, str) and 0 < len(value.strip()) <= 2000,
             f'{name} must be bounded nonblank text')
    return value


def _candidates(rows, *, recipes_allowed=False):
    _require(isinstance(rows, list) and 1 <= len(rows) <= 100, 'Expected 1..100 candidates')
    result = {}
    keys = {'candidate_id','conditions'} | ({'recipe'} if recipes_allowed else set())
    for row in rows:
        _require(isinstance(row, dict) and {'candidate_id','conditions'} <= set(row)
                 and not set(row)-keys, 'Candidate rows must not contain outcome fields')
        ident = _text(row['candidate_id'], 'candidate_id')
        _require(ident not in result, 'Duplicate candidate identity')
        conditions = row['conditions']
        _require(isinstance(conditions, dict) and 1 <= len(conditions) <= 100,
                 'Expected bounded condition factors')
        for key, value in conditions.items():
            _text(key, 'condition role'); _text(value, 'condition value')
            _require(key.strip().casefold() not in _OUTCOME_KEYS,
                     'Outcome labels cannot be condition factors')
        result = {**result, ident:{'candidate_id':ident,'conditions':dict(conditions)}}
    factors = set(next(iter(result.values()))['conditions'])
    _require(all(set(row['conditions']) == factors for row in result.values()),
             'All candidates must have the same condition factors')
    _require(len({_hash(row['conditions']) for row in result.values()}) == len(result),
             'Duplicate condition settings require explicit replicate aggregation')
    return result


def _observations(rows, candidates):
    _require(isinstance(rows, list) and len(rows) <= len(candidates), 'Invalid observations')
    result = {}
    for row in rows:
        _require(isinstance(row, dict) and set(row) ==
                 {'candidate_id','value','source_record_id','evidence_kind'},
                 'Invalid observation projection')
        ident = row['candidate_id']
        _require(isinstance(ident,str) and ident in candidates and ident not in result,
                 'Unknown or repeated observed candidate')
        _require(row['evidence_kind'] == 'measured_dataset_replay', 'Expected measured replay evidence')
        _text(row['source_record_id'],'source_record_id')
        _number(row['value'],'Observed yield',maximum=100)
        result = {**result, ident:dict(row)}
    return result


def _predictions(rows, candidates):
    _require(isinstance(rows,list) and len(rows) <= len(candidates), 'Invalid prediction table')
    result = {}
    prediction_ids = set()
    fields = {'candidate_id','prediction_id','status','value','unit','domain','uncertainty','model_version'}
    for row in rows:
        _require(isinstance(row,dict) and set(row) == fields, 'Invalid prediction projection')
        ident = row['candidate_id']
        _require(isinstance(ident,str) and ident in candidates and ident not in result,
                 'Unknown or repeated prediction candidate')
        for key in ('prediction_id','domain','uncertainty','model_version'):
            _text(row[key],key)
        _require(row['prediction_id'] not in prediction_ids, 'Duplicate prediction identity')
        prediction_ids.add(row['prediction_id'])
        _require(row['unit'] == 'percent' and row['status'] in {'scored','abstained'},
                 'Expected yield prediction or explicit abstention')
        if row['status'] == 'scored':
            _number(row['value'],'Predicted yield',maximum=100)
        else:
            _require(row['value'] is None, 'Abstention cannot have an accepted prediction value')
        result = {**result, ident:dict(row)}
    return result


def _public_parts(view):
    _require(isinstance(view,dict) and set(view) <= _VIEW_KEYS,
             'Policy accepts only the public condition view')
    _require(view.get('schema_version') == 'srg-condition-view-v1'
             and view.get('domain_status') == 'registered_measured_study', 'Unsupported condition study domain')
    _text(view.get('study_id'),'study_id')
    _require(view.get('measurement') == {'name':'yield','unit':'percent',
             'evidence_kind':'measured_dataset_replay'}, 'Unsupported measurement endpoint')
    candidates = _candidates(view.get('candidates'))
    observed = _observations(view.get('observations'),candidates)
    predictions = _predictions(view.get('predictions'),candidates)
    unavailable = view.get('unavailable_candidate_ids',[])
    _require(isinstance(unavailable,list) and all(isinstance(key,str) for key in unavailable)
             and len(set(unavailable)) == len(unavailable) and set(unavailable) <= set(candidates)
             and not set(unavailable) & set(observed), 'Invalid unavailable candidate identities')
    resources = view.get('resources')
    _require(isinstance(resources,dict),'Missing public resources')
    if resources.get('regime') == 'unbudgeted':
        _require(resources.get('remaining_observations') is None, 'Unbudgeted observation quota must be null')
        _number(resources.get('remaining_candidates'),'Remaining candidates',integer=True)
    else:
        _number(resources.get('remaining_observations'),'Remaining observations',integer=True)
    submission = view.get('submission')
    _require(isinstance(submission,dict) and set(submission) == {'status','candidate_id'}
             and submission['status'] in {'not_submitted','selected','abstained'}, 'Invalid submission state')
    return candidates, observed, predictions


def _one_hot(candidates):
    import numpy as np
    factors = sorted(next(iter(candidates.values()))['conditions'])
    vocabulary = [(factor,value) for factor in factors
                  for value in sorted({row['conditions'][factor] for row in candidates.values()})]
    identities = sorted(candidates)
    encoded = np.array([[float(candidates[key]['conditions'][factor] == value)
                         for factor,value in vocabulary] for key in identities])
    return identities, encoded


def gp_expected_improvement(view):
    """Return finite GP acquisition diagnostics for unobserved candidates only."""
    import numpy as np
    from scipy.special import ndtr
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import RBF
    candidates, observed, _ = _public_parts(view)
    identities, encoded = _one_hot(candidates)
    unavailable = set(view.get('unavailable_candidate_ids',[]))
    query = [index for index,key in enumerate(identities) if key not in observed and key not in unavailable]
    if not query:
        return []
    config = GP_CONFIGURATION
    center, scale = config['prior_mean_percent'], config['prior_std_percent']
    if observed:
        train = [index for index,key in enumerate(identities) if key in observed]
        values = np.array([(observed[identities[index]]['value']-center)/scale for index in train])
        model = GaussianProcessRegressor(kernel=RBF(config['length_scale'],length_scale_bounds='fixed'),
            alpha=config['alpha'],optimizer=None,normalize_y=False)
        model.fit(encoded[train],values)
        mean, std = model.predict(encoded[query],return_std=True)
        mean, std = center+scale*mean, scale*std
    else:
        mean, std = np.full(len(query),center),np.full(len(query),scale)
    best = max((row['value'] for row in observed.values()),default=0.0)
    difference = mean-best-config['expected_improvement_xi_percent']
    safe_std = np.maximum(std,1e-12)
    z = difference/safe_std
    acquisition = np.where(std > 1e-12,
        difference*ndtr(z)+std*np.exp(-0.5*z*z)/math.sqrt(2*math.pi),np.maximum(difference,0))
    _require(np.isfinite(mean).all() and np.isfinite(std).all()
             and np.isfinite(acquisition).all(), 'Nonfinite acquisition from fixed GP policy')
    return [{'candidate_id':identities[index],'posterior_mean':float(mu),
             'posterior_std':max(0.0,float(sigma)), 'expected_improvement':max(0.0,float(ei)),
             'scope':config['uncertainty_scope']}
            for index,mu,sigma,ei in zip(query,mean,std,acquisition)]


def select_condition_candidate(view, policy, *, seed=0):
    """Ask a fixed policy using only allowed public chemistry and past measurements."""
    _require(policy in POLICIES,'Unknown fixed condition policy')
    _require(type(seed) is int,'Seed must be an integer')
    candidates, observed, predictions = _public_parts(view)
    remaining = sorted(set(candidates)-set(observed)-set(view.get('unavailable_candidate_ids',[])))
    if (not remaining or view['resources']['remaining_observations'] == 0
            or view['submission']['status'] != 'not_submitted' or view.get('terminated') or view.get('truncated')):
        return None
    if policy == 'fixed_order':
        return remaining[0]
    if policy == 'random':
        state_seed = int(_hash([seed,view['study_id'],sorted(observed)]),16)
        return random.Random(state_seed).choice(remaining)
    if policy == 'public_model_rank':
        scored = [key for key in remaining if key in predictions and predictions[key]['status'] == 'scored']
        return min(scored,key=lambda key:(-predictions[key]['value'],key)) if scored else remaining[0]
    rows = gp_expected_improvement(view)
    return min(rows,key=lambda row:(-row['expected_improvement'],row['candidate_id']))['candidate_id']


def _successful(response):
    if not isinstance(response,dict) or response.get('status') != 'ok':
        raise RuntimeError('Condition environment action did not complete')
    return response['result']


def run_fixed_condition_episode(episode, policy, *, seed=0):
    """Execute the same metered action interface used by the LLM arms."""
    _require(policy in POLICIES,'Unknown fixed condition policy')
    trace, error = [],None
    try:
        view = _successful(episode.dispatch('inspect',{}))
        for _ in range(len(view['candidates'])+1):
            ident = select_condition_candidate(view,policy,seed=seed)
            if ident is None:
                break
            response = episode.dispatch('observe_condition',{'candidate_id':ident})
            trace.append({'candidate_id':ident,'status':response.get('status')})
            updated = _successful(response)['view']
            _require(ident in {row['candidate_id'] for row in updated['observations']},
                     'Observation response did not reveal the requested candidate')
            view = updated
        observed = view['observations']
        selected = min(observed,key=lambda row:(-row['value'],row['candidate_id']))['candidate_id'] if observed else None
        if view['submission']['status'] == 'not_submitted':
            _successful(episode.dispatch('submit',{'candidate_id':selected}))
    except Exception as exc:
        # Types only: a backend exception can contain private source/runtime paths.
        error = type(exc).__name__
    exported = episode.export()
    completed = error is None and exported['submission']['status'] in {'selected','abstained'}
    return {'method':policy,'seed':seed,'policy_version':'srg-condition-fixed-v1',
            'policy_configuration':dict(GP_CONFIGURATION) if policy == 'gp_expected_improvement' else
                {'abstention_fallback':'lexicographic_unobserved_id' if policy == 'public_model_rank' else None},
            'episode':exported,'policy_trace':trace,'completed':completed,'error_type':error}


def _score_inputs(public, outcomes, decision):
    _require(isinstance(public,dict) and public.get('schema_version') == 'srg-condition-study-v1'
             and public.get('data_role') in {'smoke','development'}, 'Only smoke/development replay may be scored here')
    _require(isinstance(decision,dict) and set(decision) == {'study_id','observations','submission'}
             and decision['study_id'] == public.get('study_id'), 'Decision and study identity differ')
    candidates = _candidates(public.get('candidates'),recipes_allowed=True)
    dataset_sha = public.get('dataset_sha256')
    _require(isinstance(dataset_sha,str) and re.fullmatch('[a-f0-9]{64}',dataset_sha),
             'Invalid source dataset digest')
    _require(isinstance(outcomes,dict) and set(outcomes) == set(candidates), 'Outcome map differs from frozen pool')
    for value in outcomes.values():
        _number(value,'Private measured yield',maximum=100)
    initial = public.get('initial_ids')
    _require(isinstance(initial,list) and all(isinstance(key,str) for key in initial)
             and len(set(initial)) == len(initial) and set(initial) <= set(candidates), 'Invalid initial identities')
    budget = _number(public.get('observation_budget'),'Observation budget',integer=True)
    _require(0 < budget <= len(candidates) and len(initial) <= budget, 'Invalid observation allowance')
    observed = _observations(decision['observations'],candidates)
    _require(list(observed)[:len(initial)] == initial and len(observed) >= len(initial)
             and len(observed) <= budget, 'Observed records violate initial state or budget')
    _require(all(row['value'] == outcomes[key] for key,row in observed.items()),
             'Recorded observations differ from private source measurements')
    _require(all(row['source_record_id'] == f'study:{dataset_sha}:{_hash(key)[:20]}'
                 for key,row in observed.items()), 'Observed source identity differs from registered measurement')
    submission = decision['submission']
    _require(isinstance(submission,dict) and set(submission) == {'status','candidate_id'}
             and submission['status'] in {'selected','abstained','not_submitted'}, 'Invalid decision submission')
    ident = submission['candidate_id']
    _require(ident is None or isinstance(ident,str),'Invalid submitted identity')
    _require((submission['status'] == 'selected') == (ident is not None),'Inconsistent submitted identity/status')
    return candidates,observed,initial,budget,submission


def score_condition_decision(public_spec, outcomes, decision):
    """Evaluator-only scoring; caller must verify commitments and source-file hashes.

    Invalid, missing and abstained choices retain null measured outcome/regret.
    A separate explicit failure penalty uses zero yield, never a synthetic
    observation. No policy-facing API invokes this function.
    """
    candidates,observed,initial,budget,submission = _score_inputs(public_spec,outcomes,decision)
    optimum = max(outcomes.values())
    selected = submission['candidate_id']
    valid = submission['status'] == 'selected' and selected in observed
    best = max((row['value'] for row in observed.values()),default=None)
    chosen = outcomes[selected] if valid else None
    trajectory = []
    for row in observed.values():
        trajectory.append(max(row['value'],trajectory[-1]) if trajectory else row['value'])
    pool = sorted(candidates.values(),key=lambda row:row['candidate_id'])
    return {'scope':SCOPE,'study_id':public_spec['study_id'],'source_data_role':public_spec['data_role'],
        'target':public_spec.get('target'),'substrate':public_spec.get('substrate'),
        'dataset_sha256':public_spec['dataset_sha256'],
        'candidate_pool_sha256':_hash(pool),'initial_ids_sha256':_hash(initial),
        'observations_sha256':_hash(decision['observations']),
        'observation_budget':budget,'initial_observations':len(initial),'observations_revealed':len(observed),
        'new_observations_used':len(observed)-len(initial),'submitted_candidate_id':selected,
        'submission_status':submission['status'],'selection_failed':not valid,
        'invalid_selection':submission['status'] == 'selected' and not valid,
        'dataset_optimum_yield_percent':optimum,'best_observed_yield_percent':best,
        'best_observed_regret_percent':None if best is None else optimum-best,
        'submitted_yield_percent':chosen,'submitted_regret_percent':None if chosen is None else optimum-chosen,
        'penalized_submitted_yield_percent':chosen if chosen is not None else 0.0,
        'penalized_submitted_regret_percent':optimum-(chosen if chosen is not None else 0.0),
        'failure_penalty_scope':'zero-yield scoring penalty; not a measured or simulated outcome',
        'trajectory_best_observed_yield_percent':trajectory,
        'trajectory_regret_percent':[optimum-value for value in trajectory],
        'observation_evidence_kind':'measured_dataset_replay','new_experiment_performed':False}


def _resource(value, name, *, integer=False):
    return None if value is None else _number(value,name,integer=integer)


def summarize_condition_run(run, score, *, arm, product_group, scaffold_group, source_family, repeat_id=0):
    """Keep episode submission and model-conversation completion separate."""
    _require(arm in ARMS and run.get('method') == arm,'Comparison arm differs from run')
    _require(type(repeat_id) is int and repeat_id >= 0,'Invalid repeat identifier')
    for value in (product_group,scaffold_group,source_family):
        _text(value,'Source group')
    episode = run['episode']; agent = run.get('agent') or {}; fixed = arm in POLICIES
    _require(score['scope'] == SCOPE and episode['study_id'] == score['study_id'], 'Run and score identities differ')
    _require(episode.get('target') == score['target'] and episode.get('substrate') == score['substrate'],
             'Run and scored reaction identities differ')
    _require(episode['submission']['candidate_id'] == score['submitted_candidate_id']
             and episode['submission']['status'] == score['submission_status'], 'Run and scored submission differ')
    candidates = _candidates(episode['candidates'])
    _require(_hash(sorted(candidates.values(),key=lambda row:row['candidate_id'])) == score['candidate_pool_sha256'],
             'Run and scored candidate pools differ')
    predictions = _predictions(episode['predictions'],candidates)
    initial_count = episode['resources']['initial_observations']
    _require(initial_count == score['initial_observations']
             and _hash([row['candidate_id'] for row in episode['observations'][:initial_count]]) == score['initial_ids_sha256'],
             'Run and score initial observations differ')
    _require(len(episode['observations']) == score['observations_revealed'], 'Run and score observation counts differ')
    _require(_hash(episode['observations']) == score['observations_sha256'],
             'Run and scored observation records differ')
    ledger = agent.get('ledger') or {}
    usage = episode.get('usage') or {}
    counts = {key:_resource(0 if fixed else ledger.get(key),key,integer=True) for key in
              ('model_calls','actual_tokens','reserved_tokens','charged_tokens','unsettled_requests')}
    state = agent.get('condition_scientist_state') or {}
    consultation = state.get('consultation') or {}
    invocations = max(len(agent.get('condition_scientist_runs') or state.get('runs') or []),
                      int(consultation.get('status') in {'pending','interrupted'}))
    return {**score,'arm':arm,'repeat_id':repeat_id,'product_group':product_group,
        'scaffold_group':scaffold_group,'source_family':source_family,
        'prediction_table_sha256':_hash(sorted(predictions.values(),key=lambda row:row['candidate_id'])),
        'submitted':episode['submission']['status'] in {'selected','abstained'},
        'conversation_completed':None if fixed else bool(agent.get('conversation_completed',agent.get('completed',False))),
        'run_completed':bool(run.get('completed',False)) if fixed else bool(agent.get('completed',False)),
        'model':None if fixed else agent.get('model'),'provider':None if fixed else agent.get('provider'),
        'condition_scientist_invocations':invocations,'condition_scientist_status':consultation.get('status'),
        'actions':_resource(usage.get('actions'),'actions',integer=True),
        'elapsed_seconds':_resource(usage.get('wall_seconds'),'elapsed_seconds'),
        'observation_reservations_used':_resource(episode['resources'].get('new_observations_used'),
                                                 'observation_reservations_used',integer=True),
        'stop_reason':episode.get('stop_reason'),'error_type':agent.get('error_type') or run.get('error_type'),
        **counts}


def _sum_known(rows, key):
    values = [row.get(key) for row in rows]
    return sum(values) if all(value is not None for value in values) else None


def _average_known(rows, key):
    values = [row[key] for row in rows if row.get(key) is not None]
    return sum(values)/len(values) if values else None


def _paired(rows,metric):
    differences = [main[metric]-assisted[metric] for main,assisted in rows
                   if main.get(metric) is not None and assisted.get(metric) is not None]
    return {'paired_observations':len(differences),'wins':sum(value>1e-9 for value in differences),
        'ties':sum(abs(value)<=1e-9 for value in differences),'losses':sum(value < -1e-9 for value in differences),
        'mean_gain_percent':sum(differences)/len(differences) if differences else None,
        'gain_interpretation':'Main regret minus assisted regret; positive favors assisted.'}


def summarize_condition_comparison(rows):
    """Descriptive paired development comparison; no automatic promotion decision."""
    _require(isinstance(rows,list) and rows,'Provide nonempty comparison rows')
    indexed,blocks = {},defaultdict(list)
    for row in rows:
        _require(row.get('arm') in ARMS and row.get('scope') == SCOPE,'Unknown comparison arm or scope')
        key = (row['study_id'],row['repeat_id'],row['arm'])
        _require(key not in indexed,'Duplicate study/arm/repeat')
        indexed[key] = row
        blocks[(row['study_id'],row['repeat_id'])].append(row)
    pairs = []
    invariants = ('candidate_pool_sha256','initial_ids_sha256','observation_budget','prediction_table_sha256',
                  'product_group','scaffold_group','source_family','target','substrate','dataset_sha256')
    for (study,repeat),block in blocks.items():
        _require(all((study,repeat,arm) in indexed for arm in ('main','main_condition_scientist')),
                 'Every study/repeat requires both agent arms, including failures')
        _require(all(len({_hash(row[key]) for row in block}) == 1 for key in invariants),
                 'Paired arms have different candidate pools, observations, predictions or group identities')
        main,assisted = (indexed[(study,repeat,arm)] for arm in ('main','main_condition_scientist'))
        _require((main.get('model'),main.get('provider')) == (assisted.get('model'),assisted.get('provider')),
                 'Paired agent model/provider differs')
        pairs.append((main,assisted))
    resource_keys = ('model_calls','actual_tokens','charged_tokens','reserved_tokens','actions','elapsed_seconds',
                     'observation_reservations_used')
    aggregate = {}
    for arm in sorted({row['arm'] for row in rows}):
        selected = [row for row in rows if row['arm'] == arm]
        aggregate[arm] = {'runs':len(selected),'selection_failures':sum(row['selection_failed'] for row in selected),
            'missing_submissions':sum(not row['submitted'] for row in selected),
            'incomplete_model_conversations':sum(row['conversation_completed'] is False for row in selected),
            'mean_best_observed_regret_percent':_average_known(selected,'best_observed_regret_percent'),
            'mean_submitted_regret_percent_successful_only':_average_known(selected,'submitted_regret_percent'),
            'mean_penalized_submitted_regret_percent':_average_known(selected,'penalized_submitted_regret_percent'),
            'mean_best_observed_yield_percent':_average_known(selected,'best_observed_yield_percent'),
            'mean_penalized_submitted_yield_percent':_average_known(selected,'penalized_submitted_yield_percent'),
            'condition_scientist_invocations':sum(row['condition_scientist_invocations'] for row in selected),
            **{key:_sum_known(selected,key) for key in resource_keys}}
    return {'scope':'paired_condition_development_diagnostic_not_final_benchmark',
        'paired_run_count':len(pairs),'study_count':len({row['study_id'] for row in rows}),
        'product_group_count':len({row['product_group'] for row in rows}),
        'scaffold_group_count':len({row['scaffold_group'] for row in rows}),
        'source_family_count':len({row['source_family'] for row in rows}),
        'aggregate':aggregate,'paired_submitted_regret':_paired(pairs,'penalized_submitted_regret_percent'),
        'paired_best_observed_regret':_paired(pairs,'best_observed_regret_percent'),
        'promotion_eligible':False,'default_changed':False,
        'promotion_blockers':['descriptive_development_comparison','source_group_generalization_not_established'],
        'independence_limit':'Substrates and repeats sharing product/scaffold/publication are correlated; not independent new chemistry.',
        'failure_policy':'Missing, invalid or abstained choice: null measured outcome plus explicit zero-yield scoring penalty.',
        'experimental_validation':False}
