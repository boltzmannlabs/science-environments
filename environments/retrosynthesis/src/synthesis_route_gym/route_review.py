"""Bounded host review facts, without retrieval, hidden labels or model calls."""
from collections import Counter
import hashlib
import json
from rdkit import Chem
from .chemistry import reaction_identity
from .evidence_contracts import SourceProjection, SourceRecord, public_projection
from .schemas import Task, RouteCandidate, RouteAssessment
from .tool_contracts import INPUT_MODELS, OUTPUT_MODELS, ToolEnvelope
from .validation import assess_route

MAX_PACKET_BYTES = 100000
CATEGORIES = frozenset({'route_structure','constraint_violation','unsupported_transformation',
    'missing_materials','stereochemistry','quantity_conflict','incomplete_conditions','model_domain_mismatch'})
_CONSTRAINT_CODES = frozenset({'step_limit','excluded_material','equipment_unavailable','excluded_operation'})
_MODEL_ACTIONS = frozenset({'predict_conditions','score_cn_conditions','predict_reaction_yield','forward_check'})


def _hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _data(value):
    return value.model_dump(mode='json') if hasattr(value,'model_dump') else value


def _bounded_rows(value, maximum, name, minimum=0):
    if not isinstance(value,(tuple,list)) or not minimum<=len(value)<=maximum:
        raise ValueError(f'Invalid bounded {name}')
    return value


def _models(task,routes,assessments):
    task=Task.model_validate(_data(task))
    _bounded_rows(routes,3,'route shortlist',1)
    for row in routes:_bounded_rows(_data(row).get('steps',()),12,'route steps')
    routes=tuple(RouteCandidate.model_validate(_data(row)) for row in routes)
    if any(len({s.step_id for s in r.steps})!=len(r.steps)for r in routes):
        raise ValueError('Duplicate step identities make critic citations ambiguous')
    _bounded_rows(assessments,3,'assessments',1)
    checks=tuple(RouteAssessment.model_validate(_data(row)) for row in assessments)
    if len({r.route_id for r in routes})!=len(routes) or len(checks)!=len(routes):
        raise ValueError('Duplicate routes or incomplete assessments')
    if len({r.route_id for r in checks})!=len(checks):raise ValueError('Duplicate assessments')
    indexed={row.route_id:row for row in checks}
    for route in routes:
        actual=indexed.get(route.route_id); expected=assess_route(task,route).model_dump(mode='json')
        ignored={'evidence_status','conditions_evidence','weak_steps'}
        if actual is None or any(actual.model_dump(mode='json')[key]!=value for key,value in expected.items()if key not in ignored):
            raise ValueError('Assessment is not bound to the supplied route/task')
        ids={step.step_id for step in route.steps}
        if set(actual.evidence_status)!=ids or set(actual.conditions_evidence)!=ids or not set(actual.weak_steps)<=ids:
            raise ValueError('Assessment step identities differ')
    return task,routes,tuple(indexed[route.route_id]for route in routes)


def _sources(rows,routes):
    _bounded_rows(rows,100000,'public source history'); projected=[]
    cited={value for route in routes for step in route.steps for value in step.evidence_ids}
    identities={reaction_identity([u.smiles for u in step.reactants],step.product)
                for route in routes for step in route.steps}
    seen=set()
    for value in rows:
        row=SourceProjection.model_validate(_data(value));raw=row.model_dump(mode='json')
        base=SourceRecord.model_validate({key:raw[key]for key in SourceRecord.model_fields})
        if raw!=public_projection(base):raise ValueError('Source projection identity or authority changed')
        if raw['record_id']in seen:raise ValueError('Duplicate source identities')
        seen.add(raw['record_id'])
        if raw['record_id']in cited or reaction_identity(raw['reactants'],raw['product'])in identities:
            projected.append(raw)
    _bounded_rows(projected,60,'relevant public sources')
    return sorted(projected,key=lambda row:row['record_id'])


def _component_matches(row,step):
    supplied=step.condition_inputs or {}
    return all((step.product if key=='product'else supplied.get(key))==value
               for key,value in row.items()if key!='id')


def _request_matches(name,args,step):
    expected=reaction_identity([u.smiles for u in step.reactants],step.product)
    if name=='forward_check':
        return reaction_identity(args['reactants'],args['product'])==expected
    if name=='predict_reaction_yield':
        return any(reaction_identity(row['reactants'],row['product'])==expected
            and Counter(row['reagents'])==Counter(u.smiles for u in step.reagents)
            for row in args['candidates'])
    return any(_component_matches(row,step)for row in args['candidates'])


def _check_prediction_binding(name,args,result):
    if result['status']!='ok':return
    binding=result['provenance']['binding']
    if binding is not None and binding['authority']!='prediction':
        raise ValueError('Scientific model result has incompatible authority')
    predictions=result['data']['predictions']
    if name=='forward_check':
        actual=any(row['product']==args['product']for row in predictions)
        if result['data']['target_in_predictions']!=actual:
            raise ValueError('Forward prediction membership flag differs')
        return
    ids=[row['id']for row in predictions]
    if len(ids)!=len(set(ids))or set(ids)!={row['id']for row in args['candidates']}:
        raise ValueError('Prediction IDs differ from recorded request')
    if binding is not None and any(row['model_version']!=binding['model_version']for row in predictions):
        raise ValueError('Prediction model version differs from host binding')


def _tool_results(rows,routes):
    _bounded_rows(rows,100000,'scientific history');result={}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'action','arguments','result'}:
            raise ValueError('Scientific records require exact request/result binding')
        name=row['action']
        if name not in _MODEL_ACTIONS:raise ValueError('Unsupported route-review scientific capability')
        args=INPUT_MODELS[name].model_validate(row['arguments']).model_dump(mode='json',by_alias=True)
        raw=row['result']
        if isinstance(raw,dict)and 'tool_result'in raw:
            if {k:v for k,v in raw.items()if k!='tool_result'}!=(raw['tool_result'].get('data')or{}):
                raise ValueError('Scientific legacy projection differs')
            raw=raw['tool_result']
        envelope=ToolEnvelope.model_validate(raw)
        if envelope.capability!=name:raise ValueError('Scientific capability binding differs')
        projected=envelope.model_dump(mode='json')
        if envelope.status=='ok':
            projected={**projected,'data':OUTPUT_MODELS[name].model_validate(envelope.data).model_dump(mode='json')}
        _check_prediction_binding(name,args,projected)
        if not any(_request_matches(name,args,step)for route in routes for step in route.steps):continue
        item={'action':name,'arguments':args,'result':projected}
        identity='tool-'+_hash(item)[:32]
        result={**result,identity:{'tool_result_id':identity,**item}}
    _bounded_rows(list(result),12,'relevant scientific records')
    return list(result.values())


def _fact(route,step_id,category,code,message,*,severity='review',authority='uncertainty',source_ids=()):
    body={'route_id':route.route_id,'step_id':step_id,'category':category,'severity':severity,
        'authority':authority,'source_record_ids':sorted(set(source_ids)),'code':code,'message':message}
    return {'fact_id':'fact-'+_hash(body)[:32],**body}


def _category(code):
    if code in _CONSTRAINT_CODES:return 'constraint_violation'
    return {'conditions_incomplete':'incomplete_conditions','material_unavailable':'missing_materials',
        'element_amount_deficit':'quantity_conflict','stoichiometry_unverified':'unsupported_transformation'}.get(code,'route_structure')


def _no_stereo(smiles):
    molecule=Chem.MolFromSmiles(smiles);Chem.RemoveStereochemistry(molecule)
    # Stereo has already been removed. Isomeric output preserves isotope labels.
    return Chem.MolToSmiles(molecule,canonical=True,isomericSmiles=True)


def _nonstereo_identity(reactants,product):
    return tuple(sorted(Counter(_no_stereo(v)for v in reactants).items())),_no_stereo(product)


def _deterministic_facts(task,route,assessment):
    rows=[_fact(route,f.step_id,_category(f.code),f.code,f.message,
        severity={'unknown':'review'}.get(f.severity,f.severity),
        authority='deterministic'if f.severity=='error'else'uncertainty')for f in assessment.findings]
    if assessment.quantity_status in {'insufficient','unknown'}:
        insufficient=assessment.quantity_status=='insufficient'
        rows.append(_fact(route,None,'quantity_conflict','quantity_insufficient'if insufficient else'quantity_unknown',
            'Declared material amounts are insufficient for the requested target.'if insufficient else'Required material amounts are not fully specified.',
            severity='error'if insufficient else'review',authority='deterministic'if insufficient else'uncertainty'))
    if route.target!=task.target and _no_stereo(route.target)==_no_stereo(task.target):
        rows.append(_fact(route,None,'stereochemistry','target_stereochemistry_mismatch',
            'Route and requested target have different encoded stereochemistry.',severity='error',authority='deterministic'))
    if assessment.acquisition_only:
        rows.append(_fact(route,None,'route_structure','acquisition_only',
            'Acquiring the stocked target is not a preparative synthesis route.',severity='error',authority='deterministic'))
    return rows


def _source_facts(route,sources):
    indexed={r['record_id']:r for r in sources};rows=[]
    for step in route.steps:
        reactants=[u.smiles for u in step.reactants]
        identity=reaction_identity(reactants,step.product)
        for source in sources:
            if source['record_id'] not in step.evidence_ids and identity==reaction_identity(source['reactants'],source['product']):
                rows.append(_fact(route,step.step_id,'unsupported_transformation','accessible_source_reaction_match',
                    'An accessible uncited source has matching encoded reaction participants; citing it would not establish experimental feasibility.',
                    severity='info',authority='source_consistency',source_ids=[source['record_id']]))
        if not step.evidence_ids:
            rows.append(_fact(route,step.step_id,'unsupported_transformation','step_support_unresolved',
                'No accessible source record is cited for this step; feasibility is unresolved.'))
        for identity in dict.fromkeys(step.evidence_ids):
            source=indexed.get(identity)
            if source is None:
                rows.append(_fact(route,step.step_id,'unsupported_transformation','source_record_unavailable',
                    'A cited source record is not available in the supplied public evidence.'))
                continue
            exact=reaction_identity(reactants,step.product)==reaction_identity(source['reactants'],source['product'])
            stereo=not exact and _nonstereo_identity(reactants,step.product)==_nonstereo_identity(source['reactants'],source['product'])
            code='source_reaction_match'if exact else'source_stereochemistry_mismatch'if stereo else'source_reaction_mismatch'
            message=('Encoded participants match the accessible source claim; this does not establish experimental feasibility.'if exact else
                'Encoded stereochemistry differs from the cited reaction; source support requires review.'if stereo else
                'Reaction participants differ from the cited source; this is a source mismatch, not proof of chemical impossibility.')
            rows.append(_fact(route,step.step_id,'stereochemistry'if stereo else'unsupported_transformation',code,message,
                severity='info'if exact else'review',authority='source_consistency',source_ids=[identity]))
            if source['stereochemistry_scope']=='not_reported':
                rows.append(_fact(route,step.step_id,'stereochemistry','source_stereochemistry_unreported',
                    'The source does not report stereochemical scope.',authority='source_consistency',source_ids=[identity]))
            if step.conditions_complete and (not step.conditions or not source['conditions']
                    or tuple(step.conditions)!=tuple(source['conditions'])or source['conditions_scope']!='same'):
                rows.append(_fact(route,step.step_id,'incomplete_conditions','condition_completeness_unverified',
                    'The completeness assertion is not established by matching accessible source conditions.',
                    authority='source_consistency',source_ids=[identity]))
    return rows


def _bound_predictions(step,tool):
    name,args,result=tool['action'],tool['arguments'],tool['result']
    if result['status']!='ok'or result['provenance']['binding']is None:return []
    if name=='forward_check':
        matches=reaction_identity(args['reactants'],args['product'])==reaction_identity([u.smiles for u in step.reactants],step.product)
        return [{'kind':'forward','data':result['data']}]if matches else[]
    if name=='predict_reaction_yield':
        requested=[row for row in args['candidates']if reaction_identity(row['reactants'],row['product'])==
            reaction_identity([u.smiles for u in step.reactants],step.product)and Counter(row['reagents'])==Counter(u.smiles for u in step.reagents)]
        ids={row['id']for row in requested}
        return [{'kind':'yield','data':row}for row in result['data']['predictions']if row['id']in ids]
    ids={row['id']for row in args['candidates']if _component_matches(row,step)}
    return [{'kind':name,'data':row}for row in result['data']['predictions']if row['id']in ids]


def _model_facts(route,tools):
    rows=[]
    for step in route.steps:
        bound=[row for tool in tools for row in _bound_predictions(step,tool)]
        if step.predicted_yield is not None:
            matches=[r for r in bound if r['kind']=='yield'and r['data']['status']=='scored'
                and abs(r['data']['predicted_yield_percent']/100-step.predicted_yield)<1e-9]
            if not matches:rows.append(_fact(route,step.step_id,'model_domain_mismatch','unverified_yield_claim',
                'Route-authored yield is not backed by an exactly bound recorded prediction; no measured yield is established.'))
        for row in bound:
            value=row['data']
            if row['kind']=='forward':
                rows.append(_fact(route,step.step_id,'unsupported_transformation',
                    'forward_model_agreement'if value['target_in_predictions']else'forward_model_disagreement',
                    'Bound forward-model output checks model consistency, not experimental feasibility.',
                    severity='info'if value['target_in_predictions']else'review'))
            elif row['kind']=='predict_conditions':
                rows.append(_fact(route,step.step_id,'model_domain_mismatch','component_yield_scope_unverified',
                    'The matching component-model yield estimate retains its declared dataset domain; it does not validate a complete reaction recipe, model transfer or experimental outcome.'))
            elif row['kind']=='score_cn_conditions':
                abstained=value['status']=='abstained'
                rows.append(_fact(route,step.step_id,'model_domain_mismatch',
                    'screening_model_abstained'if abstained else'screening_hit_not_yield',
                    'The matching C-N screening model abstained; no route yield or reaction feasibility is established.'if abstained else
                    'The matching C-N model estimates a source-screen hit, not synthesis yield or reaction feasibility; calibration does not establish transfer.'))
            else:
                rows.append(_fact(route,step.step_id,'model_domain_mismatch',
                    'yield_model_abstained'if value['status']=='abstained'else'yield_model_scope_unverified',
                    'A bound model abstained.'if value['status']=='abstained'else
                    'Bound yield remains an uncalibrated prediction; route feasibility and model transfer are unverified.'))
    return rows


def _inventory(task,routes):
    relevant={u.smiles for r in routes for s in r.steps for u in s.reactants+s.reagents}
    relevant|={v for r in routes for s in r.steps for v in (s.condition_inputs or{}).values()}
    relevant|={r.target for r in routes if not r.steps}
    stock={i.smiles:i.model_dump(mode='json')for i in task.inventory if i.smiles in relevant}
    return [{'smiles':smiles,'item':stock.get(smiles)}for smiles in sorted(relevant)]


def build_route_review(task,routes,assessments,*,sources=(),scientific_results=()):
    """Build a detached public shortlist packet from explicit host inputs only."""
    task,routes,assessments=_models(task,routes,assessments)
    sources,tools=_sources(sources,routes),_tool_results(scientific_results,routes);facts=[]
    for route,assessment in zip(routes,assessments):
        facts.extend(_deterministic_facts(task,route,assessment));facts.extend(_source_facts(route,sources));facts.extend(_model_facts(route,tools))
    summary=task.model_dump(mode='json',include={'task_id','target','target_amount_mmol','constraints'})
    packet={'schema_version':'srg-route-review-v1','task_sha256':hashlib.sha256(task.model_dump_json().encode()).hexdigest(),'task':summary,
        'routes':[r.model_dump(mode='json')for r in routes],'assessments':[r.model_dump(mode='json')for r in assessments],
        'inventory':_inventory(task,routes),'sources':sources,'tool_results':tools,
        'facts':list({r['fact_id']:r for r in facts}.values()),
        'recheck_menu':[{'recheck_id':'recheck-'+_hash(r.model_dump(mode='json'))[:32],
            'action':'validate','arguments':{'route_id':r.route_id}}for r in routes]}
    encoded=json.dumps(packet,allow_nan=False)
    if len(encoded.encode())>MAX_PACKET_BYTES:raise ValueError('Route review packet exceeds bounded public context')
    from .route_critic import ReviewPacket
    return ReviewPacket.model_validate(json.loads(encoded)).model_dump(mode='json')
