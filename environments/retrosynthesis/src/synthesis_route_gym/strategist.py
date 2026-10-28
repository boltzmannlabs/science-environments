"""Pure host-observation advice contracts; no chemistry runtime in the LLM child."""
from typing import Annotated, Literal
import hashlib
import json
import math
from pydantic import BaseModel, ConfigDict, Field, model_validator
from .condition_scientist import RuntimeResources
MAX_BYTES=20000
RESOURCE_KEYS=('remaining_model_calls','remaining_tool_calls','remaining_tokens','remaining_seconds')
CONSTRAINT_KEYS=('max_steps','forbidden_smiles','forbidden_smarts','available_equipment','forbidden_operations','require_complete_conditions')
ID=Annotated[str,Field(strict=True,min_length=1,max_length=200)]
Molecule=Annotated[str,Field(strict=True,min_length=1,max_length=600)]
class StrategistPlan(BaseModel):
    model_config=ConfigDict(extra='forbid',frozen=True)
    schema_version: Literal['srg-strategist-plan-v1']
    context_sha256: Annotated[str,Field(strict=True,pattern='^[a-f0-9]{64}$')]
    candidate_route_ids: Annotated[tuple[ID,...],Field(max_length=24)]
    next_expansion_targets: Annotated[tuple[Molecule,...],Field(max_length=2)]
    alternative_disconnection_ids: Annotated[tuple[ID,...],Field(max_length=12)]
    relevant_constraint_keys: Annotated[tuple[ID,...],Field(max_length=10)]
    action_allowance: Annotated[int,Field(strict=True,ge=0,le=2)]
    rationale: Annotated[str,Field(strict=True,min_length=1,max_length=1000)]
    evidence_status: Literal['agent_proposal']='agent_proposal'
    @model_validator(mode='after')
    def unique_and_bounded(self):
        for field in ('candidate_route_ids','next_expansion_targets','alternative_disconnection_ids','relevant_constraint_keys'):
            values=getattr(self,field)
            if len(set(values))!=len(values):raise ValueError('Duplicate plan choices')
        if not self.rationale.strip() or len(self.next_expansion_targets)>self.action_allowance:
            raise ValueError('Plan needs rationale and bounded expansion choices')
        return self

def _copy(value):return json.loads(json.dumps(value,allow_nan=False))
def _hash(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def _unique(values):return list(dict.fromkeys(values))
def observer_state():
    return {'schema_version':'srg-strategist-observer-v1','target':None,'constraints':{},
            'frontier':[],'inventory':{},'alternatives':[],'expanded':[],
            'candidate_route_ids':[],'route_cores':{},'failed_branches':[],
            'evidence_gaps':[],'expansion_count':0,'stalled_count':0,
            'missing_assessment':False,'equivalent_route':False,'closed':False,
            'saturated':False,'truncated':False,'pending_expansions':[],
            'max_expansions':None,'expansions_used':None}
def _molecule(value):
    if not isinstance(value,str) or not 1<=len(value)<=600 or value!=value.strip():
        raise ValueError('Observer requires bounded host molecular identities')
    return value

def _bounded(state):
    result=_copy(state)
    caps={'frontier':24,'alternatives':12,'expanded':32,'candidate_route_ids':24,'failed_branches':12,'evidence_gaps':24}
    for key,limit in caps.items():
        if len(result[key])>limit:
            result={**result,key:result[key][:limit],'truncated':True,'saturated':result['saturated'] or key=='expanded'}
    if len(result['route_cores'])>32:
        result={**result,'route_cores':dict(list(result['route_cores'].items())[:32]),'truncated':True,'saturated':True}
    relevant=set(result['frontier'])|{result['target']}
    entries=list(result['inventory'].items())
    entries=[(k,v)for k,v in entries if k in relevant]+[(k,v)for k,v in entries if k not in relevant]
    result={**result,'inventory':dict(entries[:64]),'truncated':result['truncated'] or len(entries)>64}
    while len(json.dumps(result).encode())>MAX_BYTES:
        removable=[k for k in result['inventory'] if k not in relevant]
        if removable:
            result={**result,'inventory':{k:v for k,v in result['inventory'].items() if k!=removable[-1]},'truncated':True}
            continue
        key=next((k for k in ('alternatives','evidence_gaps','failed_branches','frontier') if result[k]),None)
        if key is None:return {**observer_state(),'closed':True,'saturated':True,'truncated':True}
        result={**result,key:result[key][:-1],'truncated':True}
    return result

def _routes(state,routes):
    cores=dict(state['route_cores']);ids=list(state['candidate_route_ids']);duplicate=state['equivalent_route']
    for route in routes:
        ident=route['route_id']
        if not isinstance(ident,str) or not 1<=len(ident)<=200:raise ValueError('Invalid host route ID')
        core=[[_molecule(s['product']),sorted(_molecule(r['smiles'])for r in s['reactants'])]for s in route['steps']]
        digest=_hash(sorted(core))
        duplicate=duplicate or any(other!=ident and value==digest for other,value in cores.items())
        cores={**cores,ident:digest};ids=_unique([*ids,ident])
    return {**state,'route_cores':cores,'candidate_route_ids':ids,'equivalent_route':duplicate}

def _inspect(state,data):
    task=data.get('task')
    if isinstance(task,dict) and 'target' in task:
        target=_molecule(task['target'])
        if state['target'] is not None and state['target']!=target:raise ValueError('Observed task changed')
        budget=task.get('budget',{})
        maximum=budget.get('max_expansions') if isinstance(budget,dict) else None
        if isinstance(budget,dict) and budget:
            regime=budget.get('regime','budgeted')
            if regime not in {'budgeted','unbudgeted'}:
                raise ValueError('Invalid host budget regime')
            established=state.get('budget_regime','budgeted') if state['max_expansions'] is not None or 'budget_regime' in state else None
            if established is not None and established != regime:
                raise ValueError('Host expansion budget regime changed')
            if regime=='unbudgeted':
                if 'max_expansions' not in budget or maximum is not None:
                    raise ValueError('Unbudgeted host expansion limit must be explicit null')
                state={**state,'budget_regime':regime,'max_expansions':None}
        if maximum is not None and (type(maximum)is not int or not 1<=maximum<=100000):
            raise ValueError('Invalid host expansion budget')
        state={**state,'max_expansions':maximum if maximum is not None else state['max_expansions']}
        constraints=task.get('constraints',{})
        if not isinstance(constraints,dict) or set(constraints)-set(CONSTRAINT_KEYS):raise ValueError('Invalid host constraints')
        state={**state,'target':target,'constraints':_copy(constraints),'frontier':_unique([*state['frontier'],target])}
    inventory=dict(state['inventory'])
    for match in data.get('inventory_matches',[]):
        smiles=_molecule(match['smiles']);item=match.get('item')
        if item is not None and _molecule(item['smiles'])!=smiles:raise ValueError('Inventory lookup identity differs')
        inventory={**inventory,smiles:'unavailable' if item is None or item.get('available_mmol')==0 else 'available'}
    for item in data.get('inventory_page',[]):
        smiles=_molecule(item['smiles'])
        inventory={**inventory,smiles:'unavailable' if item.get('available_mmol')==0 else 'available'}
    ids=[v for v in data.get('route_ids',[]) if isinstance(v,str) and 1<=len(v)<=200]
    state={**state,'inventory':inventory,'candidate_route_ids':_unique([*state['candidate_route_ids'],*ids])}
    return _routes(state,data.get('routes',[]))

def _cycle(product,reactants,alternatives):
    edges={}
    for row in alternatives:edges[row['product']]=edges.get(row['product'],set())|set(row['reactants'])
    for first in reactants:
        todo,seen=[first],set()
        while todo:
            node=todo.pop()
            if node==product:return True
            if node not in seen:seen.add(node);todo.extend(edges.get(node,()))
    return False

def _buffer_expansion(state,args,data,success):
    if len(state['pending_expansions'])>=8:
        return {**state,'truncated':True,'saturated':True}
    raw=data.get('predictions',[]) if success else []
    rows=[{'product':_molecule(r['product']),'reactants':[_molecule(v)for v in r['reactants']]}for r in raw[:12]]
    identity=rows[0]['product'] if rows else args.get('smiles')
    if not isinstance(identity,str) or not 1<=len(identity)<=600:
        return state
    entry={'identity':identity,'success':success,'predictions':rows}
    candidate={**state,'pending_expansions':[*state['pending_expansions'],entry],
               'truncated':state['truncated'] or len(raw)>12}
    if len(json.dumps(candidate).encode())>MAX_BYTES:
        return {**state,'truncated':True,'saturated':True}
    return candidate

def _replay_pending(state):
    pending=state['pending_expansions']
    state={**state,'pending_expansions':[]}
    for entry in pending:
        state=_expand(state,{'smiles':entry['identity']},{'predictions':entry['predictions']},entry['success'])
    return state

def _expand(state,args,data,success):
    rows=data.get('predictions',[]) if success else []
    if not rows and args.get('smiles') not in state['frontier']:
        return state
    molecule=_molecule(rows[0]['product'] if rows else args['smiles'])
    if molecule not in state['frontier']:
        return state  # Invalid or unrelated caller identities are not search evidence.
    digest=_hash(molecule);repeated=digest in state['expanded']
    alternatives=list(state['alternatives']);frontier=list(state['frontier'])
    old_ids={r['id']for r in alternatives}
    rows=rows if molecule in frontier else []
    limited=len(rows)>100
    for row in rows[:100]:
        try:product=_molecule(row['product']);reactants=sorted(_molecule(v)for v in row['reactants'])
        except (ValueError,TypeError,KeyError):limited=True;continue
        if product!=molecule or not 1<=len(reactants)<=12 or _cycle(product,reactants,alternatives):
            limited=True;continue
        ident='alternative-'+_hash([product,reactants])[:24]
        if ident not in {r['id']for r in alternatives}:
            alternatives=[*alternatives,{'id':ident,'product':product,'reactants':reactants}]
        frontier=_unique([*frontier,*reactants])
    progress=bool({r['id']for r in alternatives}-old_ids) and not repeated
    failed=state['failed_branches'] if progress else [*state['failed_branches'],
        {'smiles':molecule,'status':'repeated_expansion' if repeated else 'no_new_alternative' if success else 'failed_expansion'}]
    return {**state,'frontier':frontier,'alternatives':alternatives,'expanded':_unique([*state['expanded'],digest]),
            'expansion_count':state['expansion_count']+1,'stalled_count':0 if progress else state['stalled_count']+1,
            'failed_branches':failed,'truncated':state['truncated'] or limited}

def _assessment(state,assessment):
    ident=assessment.get('route_id')
    if not isinstance(ident,str) or not 1<=len(ident)<=200:return state
    missing=[_molecule(v)for v in assessment.get('unstocked',[])]
    gaps=[f'{ident}:{s}'for s in assessment.get('weak_steps',[]) if isinstance(s,str) and len(s)<=200]
    return {**state,'candidate_route_ids':_unique([*state['candidate_route_ids'],ident]),
            'frontier':_unique([*state['frontier'],*missing]),'inventory':{**state['inventory'],**{v:'unavailable'for v in missing}},
            'evidence_gaps':_unique([*state['evidence_gaps'],*gaps]),'missing_assessment':state['missing_assessment'] or bool(missing)}

def observe(state,action,args,response):
    """Project canonical host results; proposal arguments never supply chemistry."""
    if (not isinstance(state,dict) or set(state)-{'budget_regime'}!=set(observer_state())
            or state.get('schema_version')!='srg-strategist-observer-v1'
            or ('budget_regime' in state and (state['budget_regime']!='unbudgeted' or state['max_expansions'] is not None))):
        raise ValueError('Invalid Strategist observer snapshot')
    state=_copy(state)
    if not isinstance(args,dict) or not isinstance(response,dict):raise ValueError('Host action/response must be objects')
    state={**state,'closed':state['closed'] or bool(response.get('terminated') or response.get('truncated'))}
    usage=response.get('usage',{})
    used=usage.get('expansions') if isinstance(usage,dict) else None
    if used is not None:
        if type(used)is not int or used<0:raise ValueError('Invalid host expansion usage')
        state={**state,'expansions_used':max(state['expansions_used'] or 0,used)}
    data=response.get('result',{})
    if not isinstance(data,dict):return _bounded(state)
    success=response.get('status')=='ok'
    if action=='expand':
        state=_buffer_expansion(state,args,data,success) if state['target']is None else _expand(state,args,data,success)
    elif success and action=='inspect':
        state=_inspect(state,data)
        if state['target']is not None:state=_replay_pending(state)
    elif success and action=='propose_route':state=_assessment(state,data.get('assessment',{}))
    elif success and action=='validate':state=_assessment(state,data)
    return _bounded(state)

def _resources(resources):
    if not isinstance(resources,dict):raise ValueError('Resources must be a host object')
    if resources.get('regime') == 'unbudgeted':
        return RuntimeResources.model_validate(resources).model_dump(mode='json')
    if resources.get('regime', 'budgeted') != 'budgeted':raise ValueError('Invalid resource regime')
    values={key:resources.get(key,0)for key in RESOURCE_KEYS}
    for key,value in values.items():
        if type(value) not in (int,float) or not math.isfinite(value) or value<0:raise ValueError('Resources must be finite nonnegative')
        if key!='remaining_seconds' and type(value) is not int:raise ValueError('Remaining counts must be integers')
    return values

def build_context(state,resources):
    resources=_resources(resources)
    if (state['max_expansions']is None and state.get('budget_regime')!='unbudgeted')or state['expansions_used']is None:return None
    allowance=None if state['max_expansions'] is None else max(0,state['max_expansions']-state['expansions_used'])
    resources={**resources,'remaining_expansions':allowance}
    if state['closed'] or state['saturated'] or state['target'] is None or any(v==0 for v in resources.values()):return None
    frontier=[{'smiles':v,'inventory_status':state['inventory'].get(v,'unknown')}for v in state['frontier']
              if _hash(v) not in state['expanded'] and state['inventory'].get(v)!='available']
    if not frontier:return None
    missing=any(r['inventory_status']=='unavailable'for r in frontier)
    trigger=('equivalent_route' if state['equivalent_route'] and state['expansion_count'] else
             'inventory_obligation' if missing and (state['missing_assessment'] and state['expansion_count'] or state['expansion_count']>=2) else
             'stalled_expansion' if state['stalled_count']>=2 else None)
    if trigger is None:return None
    context={'schema_version':'srg-strategist-context-v1','trigger':trigger,'target':state['target'],
             'constraints':_copy(state['constraints']),'frontier':frontier,'alternatives':_copy(state['alternatives']),
             'candidate_route_ids':list(state['candidate_route_ids']),'failed_branches':_copy(state['failed_branches']),
             'evidence_gaps':list(state['evidence_gaps']),'resources':resources,'truncated':state['truncated']}
    return context if len(json.dumps(context).encode())<=MAX_BYTES else None

def context_fingerprint(context):return _hash(context)
def _json_object(pairs):
    if len({key for key,_ in pairs})!=len(pairs):raise ValueError('Duplicate JSON keys')
    return dict(pairs)
def parse_plan(text,context):
    if not isinstance(text,str) or len(text.encode())>MAX_BYTES:raise ValueError('Plan exceeds bounded JSON input')
    raw=json.loads(text,object_pairs_hook=_json_object,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON')))
    plan=StrategistPlan.model_validate(raw)
    if plan.context_sha256!=context_fingerprint(context):raise ValueError('Plan context identity differs')
    allowed={'candidate_route_ids':set(context['candidate_route_ids']),
             'next_expansion_targets':{v['smiles']for v in context['frontier']},
             'alternative_disconnection_ids':{v['id']for v in context['alternatives']},
             'relevant_constraint_keys':set(context['constraints'])}
    if any(set(getattr(plan,key))-values for key,values in allowed.items()):raise ValueError('Unobserved or disallowed plan choice')
    if any(limit is not None and plan.action_allowance>limit for limit in
           (context['resources']['remaining_tool_calls'],context['resources']['remaining_expansions'])):
        raise ValueError('Plan exceeds remaining tools or expansions')
    return plan.model_dump(mode='json')
