"""Bounded public observations; exact inventory access remains available on request."""
from .chemistry import canonical_smiles


def _validate(arguments):
    if not isinstance(arguments, dict) or set(arguments) - {
        'inventory_offset', 'inventory_limit', 'inventory_smiles', 'route_ids', 'evidence_ids',
        'evidence_offset', 'evidence_limit', 'condition_offset', 'condition_limit'
    }:
        raise ValueError('Unsupported observation query')
    for key, default, low, high in [('inventory_offset', 0, 0, 100000),
                                     ('inventory_limit', 50, 1, 200),
                                     ('evidence_offset', 0, 0, 100000), ('evidence_limit', 10, 1, 20),
                                     ('condition_offset', 0, 0, 100000), ('condition_limit', 20, 1, 100)]:
        value = arguments.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f'Invalid {key}')
    for key, maximum in [('inventory_smiles', 100), ('route_ids', 20), ('evidence_ids', 20)]:
        values = arguments.get(key, [])
        if not isinstance(values, list) or len(values) > maximum or any(not isinstance(v, str) for v in values):
            raise ValueError(f'Invalid {key}')


def compact_observation(env, arguments=None):
    """Read one consistent projection without serializing all stock or route steps."""
    args = {} if arguments is None else arguments
    _validate(args)
    with env._lock:
        task = env.task
        study = env._science_options.get('condition_study')
        summary = task.model_dump(mode='json', exclude={'inventory', 'evidence'})
        result = {
            'task': summary,
            'task_sha256': env._task_sha256,
            'scientific_usage': dict(env._scientific_usage),
            'source_access_mode':env._source_access_mode,
            'observation_allowance':env._scientific_limits.observation_calls,
            'retrieval_allowance':env._scientific_limits.retrieval_calls,
            'capability_fingerprint': env._scientific_tools.fingerprint,
            'inventory_count': len(task.inventory), 'evidence_count': len(task.evidence),
            'condition_candidate_count': len(study._records) if study is not None else 0,
            'route_ids': [r.route_id for r in env._routes],
            'submitted_route_ids': list(env._submitted), 'usage': env._usage_dict(),
            'terminated': env._terminated, 'truncated': env._truncated,
            'inspection': 'Use inventory_smiles for exact identities, inventory_offset/limit for pages, condition_offset/limit to discover replay candidates; route_ids for details; evidence_offset/limit to discover evidence and evidence_ids to retrieve it.',
        }
        if 'condition_offset' in args or 'condition_limit' in args:
            offset, limit = args.get('condition_offset',0), args.get('condition_limit',20)
            rows = study._records if study is not None else ()
            result['condition_candidates'] = [{'candidate_id':r.candidate_id,'conditions':dict(r.conditions)} for r in rows[offset:offset+limit]]
            result['next_condition_offset'] = offset+limit if offset+limit < len(rows) else None
        if 'inventory_offset' in args or 'inventory_limit' in args:
            offset, limit = args.get('inventory_offset', 0), args.get('inventory_limit', 50)
            result['inventory_page'] = [i.model_dump(mode='json') for i in task.inventory[offset:offset + limit]]
            result['next_inventory_offset'] = offset + limit if offset + limit < len(task.inventory) else None
        if 'evidence_offset' in args or 'evidence_limit' in args:
            offset, limit = args.get('evidence_offset', 0), args.get('evidence_limit', 10)
            result['evidence_page'] = [e.model_dump(mode='json') for e in task.evidence[offset:offset + limit]]
            result['next_evidence_offset'] = offset + limit if offset + limit < len(task.evidence) else None
        if 'inventory_smiles' in args:
            stock = {i.smiles: i for i in task.inventory}
            identities = [canonical_smiles(s) for s in args['inventory_smiles']]
            result['inventory_matches'] = [{'smiles': s, 'item': stock[s].model_dump(mode='json') if s in stock else None}
                                           for s in identities]
        for key, records in [('route_ids', env._routes), ('evidence_ids', task.evidence)]:
            if key in args:
                field = 'route_id' if key == 'route_ids' else 'evidence_id'
                indexed = {getattr(record, field): record for record in records}
                if any(value not in indexed for value in args[key]):
                    raise ValueError(f'Unknown {key}')
                result['routes' if key == 'route_ids' else 'evidence'] = [indexed[value].model_dump(mode='json') for value in args[key]]
        return result


def task_prompt(env):
    import json
    summary = compact_observation(env)
    # Prompt binding is stable across resume; usage/routes are obtained through inspect.
    initial = {key: summary[key] for key in ('task', 'task_sha256', 'inventory_count', 'evidence_count', 'inspection', 'source_access_mode', 'condition_candidate_count', 'observation_allowance', 'retrieval_allowance')}
    return (
        'Plan synthesis from the declared inventory. Query exact inventory identities or pages with inspect; '
        'expand unresolved precursors, propose routes, review deterministic checks and submit a ranked shortlist. '
        'Use application_report for route-bound inventory, condition, impurity, process or biocatalysis reports when relevant. '
        'condition_options and observe_route_condition expose only registered alternatives and admitted observations; '
        'predict_route_impurities predicts hypotheses, and retrieve_application_sources retrieves source claims under shared limits. '
        'Before submitting, use review_routes on up to three shortlisted candidates to check stored routes '
        'against deterministic findings and already accessible sources. '
        'All atom-contributing branches must terminate in inventory. Predictions and toolkit checks do not '
        'establish experimental success. Do not invent evidence, yields, costs or conditions. '
        'Submit an empty list when no route is suitable. The evaluator is separate and unavailable. '
        'Inspect current routes and resources before resuming interrupted work.\nTask summary:\n'
        + json.dumps(initial, sort_keys=True, allow_nan=False)
    )
