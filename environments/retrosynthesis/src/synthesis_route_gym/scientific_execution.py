"""Host policy and execution for metered scientific capabilities."""
from dataclasses import asdict, dataclass
import time

SCIENTIFIC_ACTIONS = frozenset({'expand','predict_conditions','retrieve_sources','forward_check',
                              'observe_condition','predict_impurities','compare_process','retrieve_biocatalysis',
                              'score_cn_conditions','predict_reaction_yield'})
ACCOUNTED_SCIENTIFIC_ACTIONS = SCIENTIFIC_ACTIONS | frozenset({'retrieve_application_sources'})
RETRIEVAL_ACTIONS = frozenset({'retrieve_sources','retrieve_biocatalysis','retrieve_application_sources'})
APPLICATION_ACTIONS = frozenset({'application_report','condition_options','observe_route_condition',
                                 'predict_route_impurities','retrieve_application_sources'})
ACCOUNTING_ALIASES = {'observe_route_condition':'observe_condition','predict_route_impurities':'predict_impurities'}


@dataclass(frozen=True)
class ScientificLimits:
    retrieval_calls: int | None = 0
    observation_calls: int | None = 0

    def __post_init__(self):
        for value in (self.retrieval_calls, self.observation_calls):
            if value is not None and (isinstance(value,bool) or not isinstance(value,int) or not 0 <= value <= 100000):
                raise ValueError('Scientific limits must be integers between 0 and 100000')


def execute_scientific(env, name, args):
    registry = env._scientific_tools
    limits, usage = env._scientific_limits, env._scientific_usage
    allowed = True
    if name in RETRIEVAL_ACTIONS:
        allowed = limits.retrieval_calls is None or sum(usage.get(n,0) for n in RETRIEVAL_ACTIONS) <= limits.retrieval_calls
    if name == 'observe_condition':
        allowed = limits.observation_calls is None or usage.get(name,0) <= limits.observation_calls
    if name in RETRIEVAL_ACTIONS and env._source_access_mode == 'closed_information':
        try:
            registry.validate_request(name,args)
        except (ValueError,TypeError):
            return 'error', registry.invoke(name,args)
        return 'unavailable', registry.failure(name,'closed_information',status='unavailable')
    descriptor = next(row for row in registry.describe() if row['name'] == name)
    if not allowed and registry.available(name):
        try:
            registry.validate_request(name,args)
        except (ValueError,TypeError):
            result = registry.invoke(name,args)
        else:
            result = registry.failure(name,'access_budget_exhausted')
        return 'error', result
    started = time.monotonic()
    try:
        result = env._call_bounded(registry.invoke,name,args, timeout_seconds=descriptor['timeout_seconds'])
    except TimeoutError:
        result = registry.failure(name,'tool_timeout',backend_calls=1)
        result = {**result, 'usage':{**result['usage'],'elapsed_seconds':time.monotonic()-started}}
    if name == 'retrieve_sources' and result['status']=='ok':
        ids = [r['record_id'] for r in result.get('data',{}).get('records',[])]
        env._retrieved_source_ids = tuple(dict.fromkeys((*env._retrieved_source_ids,*ids)))
    if name in {'expand','predict_conditions'}:
        return result['status'], {**(result.get('data') or {}), 'tool_result':result}
    return result['status'], result


def science_checkpoint(env):
    return {'scientific_usage':dict(env._scientific_usage),
            'scientific_limits':asdict(env._scientific_limits),
            'source_access_mode':env._source_access_mode,
            'capability_fingerprint':env._scientific_tools.fingerprint}
