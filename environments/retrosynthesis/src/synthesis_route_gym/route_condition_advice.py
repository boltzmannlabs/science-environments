"""Pure route-bound condition advice using actual host catalogs and query charges.

No chemistry toolkit, private study, evaluator, or invented ConditionEpisode is
loaded into the isolated LLM process. The host owns canonical chemical identity.
"""
from collections import Counter
import hashlib
import json
from typing import Annotated, Literal
from urllib.parse import urlsplit
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from .route_critic import Step
from .condition_scientist import RegimeResources, RuntimeResources

MAX_BYTES = 300000
MAX_STATE_BYTES = 650000
ID = Annotated[str, Field(strict=True, min_length=1, max_length=240)]
Text = Annotated[str, Field(strict=True, min_length=1, max_length=2000)]
Molecule = Annotated[str, Field(strict=True, min_length=1, max_length=10000)]
Count = Annotated[int, Field(strict=True, ge=0, le=1000000)]
Digest = Annotated[str, Field(strict=True, pattern=r'^[a-f0-9]{64}$')]
Flag = Annotated[bool, Field(strict=True)]
Factors = Annotated[dict[ID, Text], Field(min_length=1, max_length=100)]
RECIPE_KEYS = ('reactants', 'reagents', 'product', 'product_amount_mmol', 'conditions',
              'condition_inputs', 'required_equipment', 'operations', 'conditions_complete')
RESOURCE_KEYS = ('remaining_model_calls', 'remaining_tool_calls', 'remaining_tokens', 'remaining_seconds')
DYNAMIC_KEYS = frozenset({'candidates', 'observations', 'observation_count', 'observation_resources', 'offset', 'next_offset'})
QUERY_ACTIONS = frozenset({'observe_route_condition', 'observe_condition', 'condition_observation'})


class _Record(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, validate_default=True)

    @field_validator('*')
    @classmethod
    def nonblank(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError('Text must not be blank')
        return value


class RouteStepReference(_Record):
    route_id: ID
    route_sha256: Digest
    parent_route_id: ID | None
    step_id: ID
    step_sha256: Digest


class Candidate(_Record):
    candidate_id: ID
    conditions: Factors
    recipe: Step
    recipe_sha256: Digest
    recipe_matches_current_step: Flag

    @field_validator('conditions')
    @classmethod
    def input_factors(cls, values):
        forbidden = {'yield','yield_percent','outcome','outcomes','label','labels','score','best','optimum','value',
                     'dataset_optimum_yield_percent','simple_regret_percent'}
        if any(not key.strip() or not value.strip() or key.strip().casefold() in forbidden for key,value in values.items()):
            raise ValueError('Condition factors must be inputs only')
        return values


class Observation(_Record):
    candidate_id: ID
    conditions: Factors
    yield_percent: Annotated[float, Field(strict=True, ge=0, le=100, allow_inf_nan=False)]
    source_record_id: ID
    dataset_sha256: Digest
    evidence_kind: Literal['measured_dataset_replay']
    new_experiment_performed: Literal[False]
    recipe: Step
    recipe_matches_current_step: Flag


class ObservationResources(RegimeResources):
    nullable_keys = ('call_limit', 'remaining_calls')
    schema_version: Literal['srg-route-observation-resources-v1']
    calls_used: Count
    call_limit: Count | None
    remaining_calls: Count | None
    attempted_candidate_ids: Annotated[tuple[ID, ...], Field(max_length=100000)]

    @model_validator(mode='after')
    def real_allowance(self):
        if self.call_limit is not None and self.remaining_calls != max(0,self.call_limit-self.calls_used):
            raise ValueError('Observation allowance differs from actual query charges')
        if len(set(self.attempted_candidate_ids)) != len(self.attempted_candidate_ids):
            raise ValueError('Duplicate attempted observation IDs')
        return self


class Catalog(_Record):
    schema_version: Literal['srg-route-condition-catalog-v1']
    study_id: ID
    dataset_sha256: Digest
    source_url: Text
    source_locator: Text
    reactants: Annotated[tuple[Molecule, ...], Field(min_length=1, max_length=100)]
    product: Molecule
    candidates: Annotated[tuple[Candidate, ...], Field(max_length=100)]
    binding_sha256: Digest
    study_observation_allowance: Count | None
    current_recipe_sha256: Digest
    observations: Annotated[tuple[Observation, ...], Field(max_length=100)]
    observation_count: Count
    claims_experimental_validation: Literal[False]
    evidence_scope: Text
    limitations: Annotated[tuple[Text, ...], Field(max_length=20)]
    route_step_reference: RouteStepReference
    application_configuration_sha256: Digest
    observation_resources: ObservationResources
    candidate_count: Annotated[int, Field(strict=True, ge=1, le=100)]
    offset: Count
    next_offset: Count | None

    @model_validator(mode='after')
    def explicit_study_allowance(self):
        if self.study_observation_allowance is None and self.observation_resources.regime != 'unbudgeted':
            raise ValueError('Unlimited study allowance requires explicit unbudgeted resources')
        return self

    @field_validator('source_url')
    @classmethod
    def source_public(cls, value):
        parsed=urlsplit(value)
        if (any(c.isspace() or ord(c)<32 for c in value) or parsed.scheme not in {'http','https'}
                or not parsed.hostname or parsed.username is not None or parsed.password is not None):
            raise ValueError('Expected public source URL without credentials')
        parsed.port
        return value


class RouteConditionPlan(_Record):
    schema_version: Literal['srg-route-condition-plan-v1']
    context_sha256: Digest
    decision: Literal['observe','abstain']
    next_candidate_id: ID | None
    cited_observation_ids: Annotated[tuple[ID,...],Field(max_length=20)]
    rationale: Annotated[str,Field(strict=True,min_length=1,max_length=1200)]
    evidence_status: Literal['agent_proposal']

    @model_validator(mode='after')
    def choice(self):
        if (self.decision=='observe') != (self.next_candidate_id is not None):
            raise ValueError('Condition decision and candidate differ')
        if len(set(self.cited_observation_ids)) != len(self.cited_observation_ids):
            raise ValueError('Duplicate observed source citations')
        if self.decision=='observe' and not self.cited_observation_ids:
            raise ValueError('Observation advice must cite revealed feedback')
        return self


def _encoded(value, limit=MAX_STATE_BYTES):
    try: raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
    except (ValueError,TypeError,RecursionError) as exc: raise ValueError('Expected finite JSON contract')from exc
    if len(raw)>limit: raise ValueError('Route condition contract exceeds bounded size')
    return raw


def _copy(value):return json.loads(_encoded(value))


def _hash(value):return hashlib.sha256(_encoded(value)).hexdigest()


def _recipe_hash(recipe):
    recipe={key:recipe[key]for key in RECIPE_KEYS}
    for key in ('reactants','reagents'):
        recipe={**recipe,key:sorted(recipe[key],key=lambda row:(row['smiles'],row['amount_mmol']or 0))}
    return _hash(recipe)


def _static(catalog):return {key:value for key,value in catalog.items()if key not in DYNAMIC_KEYS}


def _candidate(row,catalog):
    if (row['recipe']['step_id']!=row['candidate_id'] or row['recipe']['product']!=catalog['product']
            or Counter(v['smiles']for v in row['recipe']['reactants'])!=Counter(catalog['reactants'])
            or row['recipe_sha256']!=_recipe_hash(row['recipe'])
            or row['recipe_matches_current_step']!=(row['recipe_sha256']==catalog['current_recipe_sha256'])):
        raise ValueError('Condition candidate recipe binding differs')


def _page(value):
    page=Catalog.model_validate(_copy(value)).model_dump(mode='json')
    count,offset,length=page['candidate_count'],page['offset'],len(page['candidates'])
    if (offset+length>count and length or (offset<count and length==0)
            or page['next_offset']!=(offset+length if offset+length<count else None)):
        raise ValueError('Invalid condition catalog pagination')
    for row in page['candidates']:_candidate(row,page)
    if len({row['candidate_id']for row in page['candidates']})!=length:
        raise ValueError('Duplicate candidate page identities')
    observed=page['observations'];resources=page['observation_resources']
    if (len(observed)!=page['observation_count'] or len({row['candidate_id']for row in observed})!=len(observed)
            or len({row['source_record_id']for row in observed})!=len(observed)
            or len(observed)>resources['calls_used']
            or (resources['call_limit'] is not None and page['study_observation_allowance'] is not None
                and resources['call_limit']>page['study_observation_allowance'])):
        raise ValueError('Observed records differ from actual query resources')
    for row in observed:
        expected=f"study:{page['dataset_sha256']}:{_hash(row['candidate_id'])[:20]}"
        if (row['dataset_sha256']!=page['dataset_sha256'] or row['source_record_id']!=expected
                or row['candidate_id']not in resources['attempted_candidate_ids']):
            raise ValueError('Observed source record binding differs')
    _encoded(page,MAX_BYTES)
    return page


def _check_slots(catalog,slots):
    if not isinstance(slots,dict)or len(slots)>100:raise ValueError('Invalid catalog slots')
    checked={}
    for key,row in slots.items():
        if not isinstance(key,str)or not key.isdigit()or str(int(key))!=key or not 0<=int(key)<catalog['candidate_count']:
            raise ValueError('Invalid candidate slot index')
        value=Candidate.model_validate(row).model_dump(mode='json');_candidate(value,catalog)
        checked={**checked,key:value}
    ids=[row['candidate_id']for row in checked.values()]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate merged candidate identities')
    indexed={row['candidate_id']:row for row in checked.values()}
    for row in catalog['observations']:
        candidate=indexed.get(row['candidate_id'])
        if candidate is not None and any(row[key]!=candidate[key]for key in ('conditions','recipe','recipe_matches_current_step')):
            raise ValueError('Observed recipe or factor binding differs')
    if len(checked)==catalog['candidate_count']:
        if any(row['candidate_id']not in indexed for row in catalog['observations']):
            raise ValueError('Observation names unknown candidate')
        payload={key:catalog[key]for key in ('study_id','dataset_sha256','source_url','source_locator','reactants','product','study_observation_allowance')}
        payload={**payload,'schema_version':'srg-route-condition-binding-v1',
                 'candidates':[{key:checked[str(i)][key]for key in ('candidate_id','conditions','recipe')}for i in range(len(checked))]}
        if _hash(payload)!=catalog['binding_sha256']:raise ValueError('Complete condition catalog binding hash differs')
    return checked


def initial_state():
    return {'schema_version':'srg-route-condition-observer-v1','catalog':None,'candidate_slots':{},
            'identity_sha256':None,'closed':False,'refresh_required':False}


def validate_state(state):
    state=_copy(state)
    if (not isinstance(state,dict)or set(state)!=set(initial_state())or state['schema_version']!='srg-route-condition-observer-v1'
            or type(state['closed'])is not bool or type(state['refresh_required'])is not bool):
        raise ValueError('Invalid route condition observer state')
    if state['catalog']is None:
        if state['candidate_slots']!={}or state['identity_sha256']is not None:raise ValueError('Unbound observer has stored candidates')
        return state
    page=_page(state['catalog'])
    if state['identity_sha256']!=_hash(_static(page)):raise ValueError('Route condition observer identity differs')
    slots=_check_slots(page,state['candidate_slots'])
    for i,row in enumerate(page['candidates'],page['offset']):
        if slots.get(str(i))!=row:raise ValueError('Last page differs from merged catalog')
    return {**state,'catalog':page,'candidate_slots':slots}


def _advance(previous,current):
    before={row['candidate_id']:row for row in previous['observations']}
    after={row['candidate_id']:row for row in current['observations']}
    if any(after.get(key)!=row for key,row in before.items()):raise ValueError('Observed feedback changed or disappeared')
    old,new=previous['observation_resources'],current['observation_resources']
    if (old.get('regime', 'budgeted') != new.get('regime', 'budgeted')
            or old['call_limit']!=new['call_limit']or new['calls_used']<old['calls_used']
            or (old['remaining_calls'] is not None and new['remaining_calls']>old['remaining_calls'])
            or set(old['attempted_candidate_ids'])-set(new['attempted_candidate_ids'])):
        raise ValueError('Observation query resources were reset')
    if len(after)>len(before)and new['calls_used']==old['calls_used']:
        raise ValueError('New observations require a new charged query')


def observe(state,action,args,response):
    saved=validate_state(state)
    if not isinstance(args,dict)or not isinstance(response,dict):raise ValueError('Expected host arguments and response')
    if any(flag in response and type(response[flag])is not bool for flag in ('terminated','truncated')):
        raise ValueError('Invalid terminal flag')
    saved={**saved,'closed':saved['closed']or action=='submit'or response.get('terminated',False)or response.get('truncated',False)}
    if action not in {'condition_options',*QUERY_ACTIONS}:return saved
    data=response.get('result');data=data if isinstance(data,dict)else{}
    page=data if action=='condition_options'and response.get('status')=='ok'else data.get('condition_catalog')
    if page is None:return {**saved,'refresh_required':saved['refresh_required']or action in QUERY_ACTIONS}
    current=_page(page);ref=current['route_step_reference']
    if args.get('route_id')!=ref['route_id']or args.get('step_id')!=ref['step_id']:
        raise ValueError('Catalog differs from requested stored route step')
    if action=='condition_options':
        if current['offset']!=args.get('offset',0)or len(current['candidates'])>args.get('limit',20):
            raise ValueError('Catalog page differs from requested bounds')
    elif action!='observe_route_condition'or current['offset']!=0:
        raise ValueError('Unexpected attached condition catalog')
    identity=_hash(_static(current))
    if saved['identity_sha256']is not None and saved['identity_sha256']!=identity:
        raise ValueError('Route, recipe, study or application configuration changed')
    if saved['catalog']is not None:_advance(saved['catalog'],current)
    slots=dict(saved['candidate_slots'])
    for i,row in enumerate(current['candidates'],current['offset']):
        if str(i)in slots and slots[str(i)]!=row:raise ValueError('Previously read candidate page changed')
        slots={**slots,str(i):row}
    return validate_state({**saved,'catalog':current,'candidate_slots':slots,'identity_sha256':identity,'refresh_required':False})


def eligibility(state):
    saved=validate_state(state);catalog=saved['catalog']
    if saved['closed']:return {'eligible':False,'reason':'episode_closed'}
    if saved['refresh_required']:return {'eligible':False,'reason':'fresh_query_accounting_required'}
    if catalog is None:return {'eligible':False,'reason':'no_route_condition_catalog'}
    if len(saved['candidate_slots'])!=catalog['candidate_count']:return {'eligible':False,'reason':'complete_catalog_required'}
    if catalog['observation_count']<2:return {'eligible':False,'reason':'two_observed_candidates_required'}
    allowance = catalog['observation_resources']['remaining_calls']
    if allowance is not None and allowance<1:return {'eligible':False,'reason':'observation_allowance_exhausted'}
    blocked=set(catalog['observation_resources']['attempted_candidate_ids'])|{row['candidate_id']for row in catalog['observations']}
    if not any(row['candidate_id']not in blocked for row in saved['candidate_slots'].values()):
        return {'eligible':False,'reason':'no_unqueried_candidate'}
    return {'eligible':True,'reason':'route_feedback_after_two_observations'}


def build_context(state,resources):
    saved=validate_state(state);available=RuntimeResources.model_validate(_copy(resources)).model_dump(mode='json')
    if not eligibility(saved)['eligible']or any(available[key] is not None and available[key]<=0 for key in RESOURCE_KEYS):return None
    catalog={**saved['catalog'],'candidates':[saved['candidate_slots'][str(i)]for i in range(saved['catalog']['candidate_count'])],
             'offset':0,'next_offset':None}
    context={'schema_version':'srg-route-condition-context-v1','trigger':'route_feedback_after_two_observations',
             'catalog':catalog,'resources':available}
    return json.loads(_encoded(context,MAX_BYTES))


def _context(value):
    value=_copy(value)
    if (not isinstance(value,dict)or set(value)!={'schema_version','trigger','catalog','resources'}
            or value['schema_version']!='srg-route-condition-context-v1'or value['trigger']!='route_feedback_after_two_observations'):
        raise ValueError('Invalid route condition advice context')
    catalog=_page(value['catalog']);ref=catalog['route_step_reference']
    saved=observe(initial_state(),'condition_options',{'route_id':ref['route_id'],'step_id':ref['step_id'],'limit':100},
                  {'status':'ok','result':catalog})
    rebuilt=build_context(saved,value['resources'])
    if rebuilt is None:raise ValueError('Route condition context is ineligible')
    return rebuilt


def context_fingerprint(context):return _hash(_context(context))


def _pairs(pairs):
    if len(dict(pairs))!=len(pairs):raise ValueError('Duplicate JSON field')
    return dict(pairs)


def _constant(_):raise ValueError('Nonfinite JSON value')


def parse_plan(text,context):
    if not isinstance(text,str)or len(text.encode())>MAX_BYTES:raise ValueError('Expected bounded JSON advice')
    try:raw=json.loads(text,object_pairs_hook=_pairs,parse_constant=_constant)
    except (ValueError,RecursionError)as exc:raise ValueError('Advice must be strict JSON')from exc
    plan=RouteConditionPlan.model_validate(raw).model_dump(mode='json');current=_context(context)
    if plan['context_sha256']!=context_fingerprint(current):raise ValueError('Advice context hash differs')
    catalog=current['catalog'];known={row['candidate_id']for row in catalog['candidates']}
    blocked=set(catalog['observation_resources']['attempted_candidate_ids'])|{row['candidate_id']for row in catalog['observations']}
    if plan['decision']=='observe'and plan['next_candidate_id']not in known-blocked:
        raise ValueError('Advice must name a known unqueried candidate')
    if set(plan['cited_observation_ids'])-{row['source_record_id']for row in catalog['observations']}:
        raise ValueError('Advice cites unavailable observed evidence')
    return plan


def hydrate_plan(plan,context):
    checked=parse_plan(_encoded(plan).decode(),context);catalog=_context(context)['catalog']
    candidates={row['candidate_id']:row for row in catalog['candidates']};observed={row['source_record_id']:row for row in catalog['observations']}
    ident=checked['next_candidate_id'];ref=catalog['route_step_reference']
    action={'action':'observe_route_condition','arguments':{'route_id':ref['route_id'],'step_id':ref['step_id'],'candidate_id':ident}}if ident is not None else None
    return _copy({**checked,'next_action':action,'selected_candidate':candidates.get(ident),
        'supporting_observations':[observed[key]for key in checked['cited_observation_ids']],
        'route_step_reference':ref,'study_binding_sha256':catalog['binding_sha256'],
        'application_configuration_sha256':catalog['application_configuration_sha256']})
