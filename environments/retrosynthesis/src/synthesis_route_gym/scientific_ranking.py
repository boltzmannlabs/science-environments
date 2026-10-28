"""Batch host ranking predictions through the same metered science contract."""
from .condition_domain import condition_roles_match_step
from .ranking import COMPONENTS, rank_routes
from .scientific_execution import execute_scientific


def _key(roles):
    return tuple((name, roles[name]) for name in COMPONENTS)


def rank_with_contract(env, records):
    rows = {}
    for route in records:
        for step in route['steps']:
            if condition_roles_match_step(step):
                roles = dict(step['condition_inputs'])
                rows = {**rows, _key(roles): roles}
    if not rows or not env._scientific_tools.available('predict_conditions'):
        return rank_routes(records), []
    if len(rows) > 1000:
        raise ValueError('Ranking exceeds condition candidate allowance')
    candidates = [{'id': f'rank-{index}', **roles} for index, roles in enumerate(rows.values())]
    env._scientific_usage = {**env._scientific_usage,
                            'predict_conditions':env._scientific_usage.get('predict_conditions',0)+1}
    env._pending = {**env._pending,'scientific_usage':dict(env._scientific_usage)}
    env._persist()  # The single batch is charged before scientific inference.
    status, response = execute_scientific(env,'predict_conditions',{'candidates':candidates})
    if status != 'ok':
        raise ValueError('Ranking prediction unavailable or invalid')
    predictions = response['predictions']
    by_key = dict(zip(rows, predictions))
    binding = response['tool_result']['provenance']['binding']
    class KnownPredictions:
        metadata = {'model_version':binding['model_version']}
        def predict(self, queries):
            return [by_key[_key(row)] for row in queries]
    return rank_routes(records, KnownPredictions()), [response['tool_result']]
