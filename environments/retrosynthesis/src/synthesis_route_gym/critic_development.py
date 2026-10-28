"""Source-derived development slates and separately committed mutation labels.

These are record-consistency tasks, not measured route-feasibility labels.
The public loader never opens private mutation/retention annotations.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Literal
from pydantic import Field, StrictBool
from .chemistry import canonical_smiles, reaction_identity
from .evidence_contracts import Digest, SourceRecord, aware_datetime, digest
from .evidence_corpus import FrozenEvidenceCorpus
from .schemas import Record, RouteCandidate, Task
from .validation import assess_route

CATEGORIES=('route_structure','constraint_violation','unsupported_transformation',
 'missing_materials','stereochemistry','quantity_conflict','incomplete_conditions','model_domain_mismatch')
Category=Literal['route_structure','constraint_violation','unsupported_transformation',
 'missing_materials','stereochemistry','quantity_conflict','incomplete_conditions','model_domain_mismatch']
PAROUTES_SHA='b818f2115ce10da51f84bf13f19dc2206863b1b074ef348017de258e9e1bff02'
MUTATIONS=('missing_material','cycle','equipment','target_stereochemistry',
           'quantity_deficit','wrong_target','missing_material','equipment')


class Provenance(Record):
    artifact_path: str=Field(min_length=1,max_length=2000)
    artifact_sha256: Digest
    locator: str=Field(min_length=1,max_length=2000)


class PublicCase(Record):
    schema_version: Literal['srg-critic-development-case-v1']
    data_role: Literal['previously_used_development']
    case_id: str=Field(min_length=1,max_length=128)
    task: Task
    routes: tuple[RouteCandidate,...]=Field(min_length=3,max_length=3)
    sources: tuple[SourceRecord,...]=Field(min_length=1,max_length=20)
    source_family: str=Field(min_length=1,max_length=200)
    source_case_id: str=Field(min_length=1,max_length=200)
    source_provenance: tuple[Provenance,...]=Field(min_length=1,max_length=20)
    limitations: tuple[str,...]=Field(min_length=1,max_length=20)
    case_inputs_sha256: Digest
    label_sha256: Digest


class RouteLabel(Record):
    hard_valid: StrictBool
    source_consistent: StrictBool
    retain: StrictBool
    expected_categories: tuple[Category,...]
    expected_error_categories: tuple[Category,...]
    expected_review_categories: tuple[Category,...]
    mutation_kind: str=Field(min_length=1,max_length=100)


class PrivateLabels(Record):
    schema_version: Literal['srg-critic-labels-v1']
    case_id: str=Field(min_length=1,max_length=128)
    case_inputs_sha256: Digest
    routes: dict[str,RouteLabel]
    label_basis: str=Field(min_length=1,max_length=2000)


def serialized(value):
    return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def case_inputs_digest(public):
    return digest({k:v for k,v in public.items() if k not in {'case_inputs_sha256','label_sha256'}})


def _require(value,message):
    if not value:raise ValueError(message)


def _unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('Duplicate JSON key')
        result={**result,key:value}
    return result


def _read(path,expected_sha256=None):
    path=Path(path)
    _require(path.is_file() and not path.is_symlink(),'Expected regular public case file')
    with path.open('rb')as handle:raw=handle.read(2097153)
    _require(len(raw)<=2097152,'Public case exceeds size limit')
    if expected_sha256 is not None:
        _require(hashlib.sha256(raw).hexdigest()==expected_sha256,'Public case digest mismatch')
    def invalid(value):raise ValueError('Nonfinite JSON number')
    return json.loads(raw,object_pairs_hook=_unique_object,parse_constant=invalid)


def load_critic_case(public_path,expected_sha256=None):
    raw=_read(public_path,expected_sha256);case=PublicCase.model_validate(raw)
    _require(raw['case_inputs_sha256']==case_inputs_digest(raw),'Public scientific inputs changed')
    _require(case.model_dump(mode='json')==raw,'Public inputs must already be canonical and complete')
    ids=[r.route_id for r in case.routes];source_ids=[s.record_id for s in case.sources]
    _require(len(ids)==len(set(ids)) and len(source_ids)==len(set(source_ids)),'Duplicate route/source identity')
    _require(case.task.task_id==case.case_id,'Case/task identity differs')
    return {'task':case.task,'routes':case.routes,
        'evidence_corpus':FrozenEvidenceCorpus(case.sources,mode='evidence_retrieval'),'public':deepcopy(raw)}


load_public_case=load_critic_case


def validate_critic_labels(public,labels):
    case=PublicCase.model_validate(public);private=PrivateLabels.model_validate(labels)
    _require(case.case_inputs_sha256==case_inputs_digest(public),'Public scientific inputs changed')
    _require(private.case_id==case.case_id and private.case_inputs_sha256==case.case_inputs_sha256,
             'Labels belong to different scientific inputs')
    _require(hashlib.sha256(serialized(labels)).hexdigest()==case.label_sha256,'Label commitment differs')
    _require(set(private.routes)=={r.route_id for r in case.routes},'Label route identities differ')
    for row in private.routes.values():
        _require(row.retain==(row.hard_valid and row.source_consistent),'Inconsistent retention label')
        _require(set(row.expected_categories)==set(row.expected_error_categories)|set(row.expected_review_categories),
                 'Category union differs')
        _require(not(row.hard_valid and row.expected_error_categories),'Hard-valid label has error categories')
    return private.model_dump(mode='json')


def _provenance(anchor,locator):
    return Provenance(**{**anchor,'locator':locator}).model_dump(mode='json')


def _paroutes_sources(review,anchor):
    rows=review['sources']
    _require(len(rows)==4 and len({r['task_id']for r in rows})==4,'Require four distinct reviewed PaRoutes cases')
    ordered=sorted(rows,key=lambda r:('@'in r['target'],r['task_id']))
    _require('@'in ordered[3]['target'],'Fourth PaRoutes control must encode stereochemistry')
    return [{'source_family':'paroutes-v2-n1','source_case_id':r['task_id'],
        'target':canonical_smiles(r['target']),
        'edges':[{'product':canonical_smiles(e['product']),
                  'reactants':[canonical_smiles(v)for v in e['reactants']],
                  'reagents':[],'conditions':[]}for e in r['reference_edges']],
        'source_url':'https://zenodo.org/records/7341155/files/ref_routes_n1.json',
        'source_content_sha256':PAROUTES_SHA,'source_locator':r['source_locator'],
        'claim_kind':'proxy','source_provenance':[_provenance(anchor,r['source_locator'])]}for r in ordered]


def _doyle_sources(review,studies,anchor):
    selected=[];seen=set()
    for sid in sorted(studies,key=lambda v:hashlib.sha256(v.encode()).hexdigest()):
        study=studies[sid];_require(study['study_id']==sid,'Study identity differs')
        for candidate in study['candidates']:
            _require(canonical_smiles(candidate['recipe']['product'])==canonical_smiles(study['target']),
                     'Source recipe target differs')
        if study['target']in seen:continue
        cases=[c for c in review['cases']if c['study_id']==sid and c['submission_status']=='selected']
        _require(cases and all(c['source_match']is True for c in cases),'Missing or unverified reviewed source cases')
        cid=min(c['candidate_id']for c in cases);case=next(c for c in cases if c['candidate_id']==cid)
        candidate=next((c for c in study['candidates']if c['candidate_id']==cid),None)
        _require(candidate is not None,'Reviewed candidate absent from public study')
        recipe=candidate['recipe'];locator=f"CSV line {case['source']['csv_line']}; {cid}"
        selected.append({'source_family':'doi:10.1126/science.aar5169','source_case_id':sid,
            'target':canonical_smiles(study['target']),
            'edges':[{'product':recipe['product'],'reactants':list(recipe['reactants']),
                      'reagents':list(recipe['reagents']),
                      'conditions':[f'{k}={v}'for k,v in sorted(candidate['conditions'].items())]}],
            'source_url':study['source_url'],'source_content_sha256':study['dataset_sha256'],
            'source_locator':locator,'claim_kind':'measured',
            'source_provenance':[_provenance(anchor,f'cases: {sid}/{cid}')],'candidate_id':cid})
        seen=seen|{study['target']}
        if len(selected)==4:break
    _require(len(selected)==4,'Require four distinct reviewed Doyle product groups')
    return selected


def select_sources(route_review,condition_review,studies,*,provenance):
    """Select reviewed identities without inspecting recorded yields or scores."""
    return _paroutes_sources(route_review,provenance['paroutes'])+_doyle_sources(condition_review,studies,provenance['doyle'])


def _sources(spec,retrieved_at):
    return [SourceRecord(record_id='source-'+digest([spec['source_case_id'],i])[:24],
        document_id=spec['source_family'],source_url=spec['source_url'],
        locator=f"{spec['source_locator']}; edge {i}",reactants=edge['reactants'],product=edge['product'],
        claim_kind=spec['claim_kind'],conditions_scope='unknown',conditions=edge['conditions'],
        retrieved_at=aware_datetime(retrieved_at),source_content_sha256=spec['source_content_sha256']).model_dump(mode='json')
        for i,edge in enumerate(spec['edges'])]


def _route(spec,sources,case_id,slot):
    route_id='route-'+digest([case_id,slot,'route'])[:24]
    return RouteCandidate.model_validate({'route_id':route_id,'target':spec['target'],'steps':[
        {'step_id':'step-'+digest([route_id,i])[:24],'product':edge['product'],
         'reactants':[{'smiles':v}for v in edge['reactants']],
         'reagents':[{'smiles':v}for v in edge['reagents']],
         'conditions':edge['conditions'],'conditions_complete':False,
         'source_tool':'preloaded-development-candidate','source_version':'srg09-v1',
         'evidence_ids':[sources[i]['record_id']]}for i,edge in enumerate(spec['edges'])]}).model_dump(mode='json')


def _task(spec,case_id,route,index):
    produced={s['product']for s in route['steps']}
    required={u['smiles']for s in route['steps']for u in s['reactants']+s['reagents']if u['smiles']not in produced}
    inventory=[{'smiles':v,'source':'Compact source-derived identity inventory; not original full-stock search.'}for v in sorted(required)]
    if index==4:
        first=route['steps'][0]['reactants'][0]['smiles']
        inventory=[{**v,'available_mmol':1 if v['smiles']==first else 4,
                    'source':'synthetic-test inventory amount; not a measured source quantity'}for v in inventory]
    return Task.model_validate({'task_id':case_id,'target':spec['target'],'inventory':inventory,
        'target_amount_mmol':1 if index==4 else None,
        'budget':{'max_actions':80,'max_expansions':6,'max_wall_seconds':600,'max_llm_tokens':350000,'top_k':3}}).model_dump(mode='json')


def _amounts(route,index):
    if index!=4:return route
    return {**route,'steps':[{**s,'product_amount_mmol':1,
        'reactants':[{**u,'amount_mmol':1}for u in s['reactants']],
        'reagents':[{**u,'amount_mmol':1}for u in s['reagents']]}for s in route['steps']]}


def _hard_mutation(route,task,index):
    result=deepcopy(route);step=result['steps'][0];kind=MUTATIONS[index]
    if kind=='missing_material':
        stock={v['smiles']for v in task['inventory']}
        missing=next(v for v in ('CC#N','O','[He]')if canonical_smiles(v)not in stock)
        step['reagents']=[*step['reagents'],{'smiles':missing}]
        return result,['missing_materials'],kind
    if kind=='cycle':
        step['reactants']=[{'smiles':step['product']}]
        return result,['route_structure'],kind
    if kind=='equipment':
        step['required_equipment']=['declared_comparison_reactor']
        return result,['constraint_violation'],kind
    if kind=='quantity_deficit':
        step['reactants']=[{**step['reactants'][0],'amount_mmol':2},*step['reactants'][1:]]
        return result,['quantity_conflict'],kind
    if kind=='wrong_target':
        result['target']='C' if task['target']!='C'else'CC'
        return result,['route_structure'],kind
    _require('@'in route['target'],'Stereo mutation requires encoded target stereochemistry')
    opposite=route['target'].replace('@@','@',1) if '@@'in route['target']else route['target'].replace('@','@@',1)
    result['target']=canonical_smiles(opposite)
    result['steps']=[{**s,'product':result['target']}if s['product']==route['target']else s for s in result['steps']]
    return result,['route_structure','stereochemistry'],kind


def _third_mutation(route,decoy,index):
    result=deepcopy(route)
    if index<4:
        if index%2:
            result['steps'][0]['predicted_yield']=0.99
            return result,'uncalibrated_prediction',['model_domain_mismatch']
        result['steps']=[{**s,'reactants':list(reversed(s['reactants']))}for s in result['steps']]
        return result,'condition_uncertainty',[]
    if index in {4,6}:
        result['steps'][0]['evidence_ids']=[decoy['record_id']]
        return result,'citation_mismatch',[]
    result['steps'][0]['reactants']=[*result['steps'][0]['reactants'],deepcopy(result['steps'][0]['reactants'][0])]
    return result,'reaction_multiset_mismatch',[]


def _consistent(route,sources):
    index={s['record_id']:s for s in sources}
    return all(any(ident in index and reaction_identity([u['smiles']for u in step['reactants']],step['product'])==
        reaction_identity(index[ident]['reactants'],index[ident]['product'])for ident in step['evidence_ids'])for step in route['steps'])


def _label(route,task,sources,*,hard_valid,kind,error_categories=(),extra_reviews=()):
    a=assess_route(Task.model_validate(task),RouteCandidate.model_validate(route))
    actual=a.graph_valid and a.inventory_complete and a.constraint_compliant and a.quantity_status in {'complete','not_requested'}
    _require(actual==hard_valid,'Controlled edit differs from its independently declared hard-validity label')
    consistent=_consistent(route,sources);reviews=sorted({'incomplete_conditions','unsupported_transformation',*extra_reviews})
    return {'hard_valid':hard_valid,'source_consistent':consistent,'retain':hard_valid and consistent,
        'expected_categories':sorted(set(error_categories)|set(reviews)),
        'expected_error_categories':sorted(set(error_categories)),
        'expected_review_categories':reviews,'mutation_kind':kind}


def build_case(spec,decoy_spec,*,index,retrieved_at):
    _require(type(index)is int and 0<=index<8,'Case index must be 0..7')
    case_id='critic-case-'+digest([spec['source_family'],spec['source_case_id'],'srg09-v1'])[:24]
    sources=_sources(spec,retrieved_at);decoy=_sources(decoy_spec,retrieved_at)[0]
    _require(decoy['record_id']not in {s['record_id']for s in sources},'Decoy source must be distinct')
    all_sources=sorted([*sources,decoy],key=lambda s:s['record_id'])
    routes=[_amounts(_route(spec,sources,case_id,slot),index)for slot in range(3)]
    task=_task(spec,case_id,routes[0],index)
    hard,errors,kind=_hard_mutation(routes[1],task,index)
    third,third_kind,reviews=_third_mutation(routes[2],decoy,index)
    normalized=[RouteCandidate.model_validate(v).model_dump(mode='json')for v in [routes[0],hard,third]]
    labels={normalized[0]['route_id']:_label(normalized[0],task,all_sources,hard_valid=True,kind='source_consistent'),
        normalized[1]['route_id']:_label(normalized[1],task,all_sources,hard_valid=False,kind=kind,error_categories=errors),
        normalized[2]['route_id']:_label(normalized[2],task,all_sources,hard_valid=True,kind=third_kind,extra_reviews=reviews)}
    _require(sum(row['retain']for row in labels.values())==(2 if index<4 else 1),'Source inconsistency edit is ineffective')
    public={'schema_version':'srg-critic-development-case-v1','data_role':'previously_used_development',
        'case_id':case_id,'task':task,'routes':sorted(normalized,key=lambda r:r['route_id']),
        'sources':all_sources,'source_family':spec['source_family'],'source_case_id':spec['source_case_id'],
        'source_provenance':spec['source_provenance'],'limitations':[
            'Reused development source records; not final or fresh held-out chemistry.',
            'Compact source-derived inventory defines a new shortlist task, not original inventory search.',
            'Source matching does not establish complete conditions, selectivity, safety or experimental route success.',
            'Model scores and incomplete operational conditions remain uncertain.']}
    if index==4:public['limitations']+=['All declared amounts are counterfactual synthetic-test constraints, not source measurements or a validated process balance.']
    binding=case_inputs_digest(public)
    private={'schema_version':'srg-critic-labels-v1','case_id':case_id,'case_inputs_sha256':binding,'routes':labels,
        'label_basis':'Frozen controlled edits and separately reviewed source identities; not critic opinions or new chemistry experiments.'}
    public={**public,'case_inputs_sha256':binding,'label_sha256':hashlib.sha256(serialized(private)).hexdigest()}
    PublicCase.model_validate(public);validate_critic_labels(public,private)
    return public,private
