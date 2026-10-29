"""Public shortlist selection and separately invoked controlled-label scoring."""
import hashlib
import json
import math
from collections import defaultdict
from .chemistry import reaction_identity
from .schemas import RouteCandidate, RouteAssessment

ARMS=('direct_tool','main','main_route_critic')
SCOPE='closed_route_review_development_not_final_chemistry_benchmark'
CATEGORIES=frozenset({'route_structure','constraint_violation','unsupported_transformation',
    'missing_materials','stereochemistry','quantity_conflict','incomplete_conditions','model_domain_mismatch'})


def _require(condition,message):
    if not condition:raise ValueError(message)


def case_digest(public):
    value={key:value for key,value in public.items()if key not in {'case_inputs_sha256','label_sha256'}}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def _routes(public):
    rows=public.get('routes')
    _require(isinstance(rows,list)and 1<=len(rows)<=3,'Require one to three registered routes')
    parsed=[RouteCandidate.model_validate(row)for row in rows]
    _require(len({r.route_id for r in parsed})==len(parsed),'Duplicate route IDs')
    return {row.route_id:row for row in parsed}


def select_review_routes(packet):
    """Retain every nonblocking route matching public source reaction identities."""
    _require(packet.get('schema_version')=='srg-route-review-v1','Unsupported public review packet')
    routes=_routes(packet);raw=packet.get('assessments')
    _require(isinstance(raw,list)and len(raw)==len(routes),'Assessment count differs')
    for row in raw:
        _require(all(type(row.get(key))is bool for key in ('graph_valid','inventory_complete',
                 'constraint_compliant','acquisition_only')),'Invalid assessment flags')
    assessments={row.route_id:row for row in (RouteAssessment.model_validate(r)for r in raw)}
    _require(set(assessments)==set(routes),'Assessment route identities differ')
    sources={row['record_id']:reaction_identity(row['reactants'],row['product'])for row in packet['sources']}
    retained=[]
    for ident,route in routes.items():
        a=assessments[ident]
        valid=a.graph_valid and a.inventory_complete and a.constraint_compliant and not a.acquisition_only and a.quantity_status in {'complete','not_requested'}
        consistent=bool(route.steps)and all(any(sources.get(source_id)==reaction_identity(
            [u.smiles for u in s.reactants],s.product)for source_id in s.evidence_ids)for s in route.steps)
        if valid and consistent:retained.append(ident)
    return sorted(retained)


def critic_selection_prompt(public):
    routes=_routes(public)
    summary={'case_id':public['case_id'],'task_id':public['task']['task_id'],'target':public['task']['target'],'candidate_route_ids':list(routes)}
    return ('Review this closed shortlist and submit every source-consistent, nonblocking candidate, up to '
        'task top_k. Start with review_routes for the complete candidate pool; it gives canonical routes, '
        'deterministic checks and the public source records available to all methods. You may inspect or '
        'validate for a bounded recheck. Match exact reaction participants and stereochemistry to sources. '
        'Each step must cite at least one matching source record in its declared evidence_ids. Evaluate '
        'the candidate as written: an uncited matching record does not repair a mismatched citation in this '
        'closed selection task. Source consistency does not establish experimental feasibility. Missing conditions, unverified '
        'stoichiometry or predictor-domain uncertainty alone are reasons to retain uncertainty, not reject '
        'a source-consistent route without a definite constraint violation. Predictions are not measured '
        'yield. Do not select definite invalid routes or routes lacking source-consistent connectivity for '
        'this specific task. Submit all eligible IDs, or empty if none qualify. This diagnostic allows '
        'selection and rechecks only, not fresh route generation or revision. Always call submit before '
        'ending. The independent evaluator and labels are unavailable.\n'+json.dumps(summary,sort_keys=True,allow_nan=False))


def critic_selection_schemas():
    from .planning import environment_tool_schemas
    names={'inspect','review_routes','validate','submit'}
    schemas=[row for row in environment_tool_schemas()if row['name']in names]
    _require({row['name']for row in schemas}==names,'Closed-review tools are not fully integrated')
    return schemas


def run_direct_critic_policy(env,route_ids):
    response=env.dispatch('review_routes',{'route_ids':list(route_ids)})
    if response.get('status')!='ok':
        return {'method':'direct_tool','episode':env.export(),'selection_completed':False,'error_type':'ReviewUnavailable','review_packet':None}
    packet=response['result'];selected=select_review_routes(packet)
    submission=env.dispatch('submit',{'route_ids':selected})
    return {'method':'direct_tool','episode':env.export(),'selection_completed':submission.get('status')=='ok','review_packet':packet}


def _label_rows(public,labels):
    # File-byte label commitments are checked by the frozen evaluator before parsing.
    _require(public.get('schema_version')=='srg-critic-development-case-v1'and public.get('data_role')=='previously_used_development','Expected development case')
    binding=case_digest(public)
    _require(public.get('case_inputs_sha256')==binding,'Public scientific inputs changed')
    _require(labels.get('schema_version')=='srg-critic-labels-v1'and labels.get('case_id')==public['case_id']and labels.get('case_inputs_sha256')==binding,'Hidden labels do not match public inputs')
    routes=_routes(public);rows=labels.get('routes')
    _require(isinstance(rows,dict)and set(rows)==set(routes),'Hidden label route identities differ')
    for row in rows.values():
        _require(all(type(row.get(key))is bool for key in ('hard_valid','source_consistent','retain')),'Labels require actual boolean decisions')
        _require(row['retain']==(row['hard_valid']and row['source_consistent']),'Retention label contradicts gates')
        for key in ('expected_error_categories','expected_review_categories','expected_categories'):
            value=row.get(key)
            _require(isinstance(value,list)and len(value)==len(set(value))and set(value)<=CATEGORIES,'Invalid expected categories')
        _require(set(row['expected_categories'])==set(row['expected_error_categories'])|set(row['expected_review_categories']),'Expected category union differs')
        _require(not row['hard_valid']or not row['expected_error_categories'],'Hard-valid control cannot have expected blocking findings')
    return rows


def score_critic_decision(public,labels,decision):
    """Score requested IDs; empty and missing submissions retain their false rejections."""
    rows=_label_rows(public,labels);ids=decision.get('submitted_route_ids');status=decision.get('submission_status')
    _require(decision.get('case_id')==public['case_id'],'Decision case differs')
    _require(isinstance(ids,list)and all(isinstance(v,str)for v in ids)and len(ids)==len(set(ids))and set(ids)<=set(rows),'Unknown or duplicate submitted IDs')
    _require(status in {'submitted_routes','submitted_empty','not_submitted'}and (status=='submitted_routes')==bool(ids),'Submission status differs from IDs')
    expected={key for key,row in rows.items()if row['retain']};selected=set(ids)
    invalid=sum(not rows[key]['hard_valid']for key in ids)
    unsupported=sum(rows[key]['hard_valid']and not rows[key]['source_consistent']for key in ids)
    retained=len(selected&expected)
    return {'scope':SCOPE,'case_id':public['case_id'],'case_inputs_sha256':public['case_inputs_sha256'],
        'submitted_route_ids':ids[:],'submission_status':status,'missing_submission':status=='not_submitted',
        'submitted_count':len(ids),'invalid_submitted_count':invalid,'invalid_submitted_fraction':invalid/len(ids)if ids else None,
        'unsupported_submitted_count':unsupported,'unsupported_submitted_fraction':unsupported/len(ids)if ids else None,
        'source_controls_total':len(expected),'source_controls_retained':retained,'source_control_retention':retained/len(expected)if expected else None,
        'false_rejection_count':len(expected-selected),'false_rejection_fraction':len(expected-selected)/len(expected)if expected else None,
        'strict_selection_success':status!='not_submitted'and selected==expected,
        'invalid_label_scope':'Controlled deterministic contradiction; unsupported source identity is separate.','experimental_validation':False}


def score_critic_findings(public,labels,findings):
    """Unmatched review concerns stay unlabeled; they are not negative chemistry truths."""
    rows=_label_rows(public,labels);_require(isinstance(findings,list)and len(findings)<=200,'Invalid finding list')
    seen=set();true_errors=false_errors=matched_reviews=unlabeled_reviews=0;matched=set()
    expected={(ident,category)for ident,row in rows.items()for category in row['expected_error_categories']}
    for item in findings:
        ident,category,severity=(item.get(k)for k in ('route_id','category','severity'));key=(ident,category,severity)
        _require(ident in rows and category in CATEGORIES and severity in {'error','review','info'},'Unknown finding identity')
        if key in seen:continue
        seen.add(key)
        if severity=='error':
            if (ident,category)in expected:true_errors+=1;matched.add((ident,category))
            else:false_errors+=1
        elif severity=='review':
            if category in rows[ident]['expected_review_categories']:matched_reviews+=1
            else:unlabeled_reviews+=1
    return {'unit':'unique_route_category_severity','true_error_findings':true_errors,'false_error_findings':false_errors,'matched_review_findings':matched_reviews,
        'unlabeled_review_findings':unlabeled_reviews,'error_category_precision':true_errors/(true_errors+false_errors)if true_errors+false_errors else None,
        'error_category_recall':len(matched)/len(expected)if expected else None,'expected_error_categories':len(expected),
        'matched_error_categories':len(matched),'annotation_scope':'Controlled-edit categories; review labels are not exhaustive chemistry truth.'}


def _resource(value,key,integer=True):
    if value is None:return None
    _require(type(value)is int if integer else type(value)in (int,float),f'Invalid resource {key}')
    _require(math.isfinite(value)and value>=0,f'Invalid resource {key}')
    return value


def summarize_critic_run(public,run,score,*,repeat_id):
    arm=run.get('method');_require(arm in ARMS and type(repeat_id)is int and repeat_id>=0,'Invalid arm/repeat')
    episode=run['episode'];agent=run.get('agent')or{};fixed=arm=='direct_tool'
    _require(case_digest(public)==public['case_inputs_sha256']==score['case_inputs_sha256'],'Scoring input changed')
    _require(episode['task']==public['task']and episode['routes']==public['routes'],'Run public candidate pool changed')
    _require(episode['submitted_route_ids']==score['submitted_route_ids'],'Run and decision differ')
    ledger=agent.get('ledger')or{};usage=episode['usage'];state=agent.get('route_critic_state')or{}
    consultation=state.get('consultation')or{};advisor_runs=agent.get('route_critic_runs')or[]
    counts={key:_resource(0 if fixed else ledger.get(key),key)for key in
            ('model_calls','actual_tokens','charged_tokens','reserved_tokens','unsettled_requests')}
    settled=counts['actual_tokens']if counts['reserved_tokens']==0 and counts['unsettled_requests']==0 else None
    actions=_resource(usage.get('actions'),'actions');bootstrap=_resource(run.get('bootstrap',{}).get('actions'),'bootstrap')
    _require(actions is not None and bootstrap is not None and actions>=bootstrap,'Missing or invalid bootstrap accounting')
    events=episode.get('events',[]);review_index=next((i for i,e in enumerate(events)if e['action']=='review_routes'and e['status']=='ok'),None)
    later=events[review_index+1:]if review_index is not None else []
    rechecks=[e for e in later if e['action']=='validate']
    recommendation=(consultation.get('recommendation')or{}).get('recommended_recheck')
    recommended_attempts=[e for e in rechecks if e['action']==recommendation['action']and e['arguments']==recommendation['arguments']]if recommendation else []
    attempted=bool(recommended_attempts)if recommendation else None
    used=any(e['status']=='ok'for e in recommended_attempts)if recommendation else None
    return {**score,'arm':arm,'repeat_id':repeat_id,'source_family':public['source_family'],
        'source_case_id':public['source_case_id'],'model':None if fixed else agent.get('model'),
        'provider':None if fixed else agent.get('provider'),'conversation_completed':None if fixed else bool(agent.get('conversation_completed',False)),
        'critic_status':consultation.get('status'),'critic_invocations':max(len(advisor_runs),int(consultation.get('status')in {'pending','interrupted'})),
        'critic_rejected_report_count':int(consultation.get('status')=='rejected'),
        'critic_failed_consultation_count':int(consultation.get('status')in {'failed','interrupted','pending'}),
        'critic_recommended_recheck_attempted':attempted,'critic_recommended_recheck_used':used,
        'rechecks':len(rechecks),'completed_rechecks':sum(e['status']=='ok'for e in rechecks),
        'environment_actions':actions,'bootstrap_actions':bootstrap,'policy_actions':actions-bootstrap,
        'elapsed_seconds':_resource(usage.get('wall_seconds'),'wall_seconds',integer=False),
        'error_type':agent.get('error_type')or run.get('error_type'),
        'fully_settled_actual_tokens':settled,**counts}


def _sum_known(rows,key):
    values=[row.get(key)for row in rows]
    return sum(values)if all(value is not None for value in values)else None


def summarize_critic_comparison(rows):
    _require(isinstance(rows,list)and rows,'Comparison requires runs')
    indexed={};blocks=defaultdict(list)
    for row in rows:
        _require(row.get('scope')==SCOPE and row.get('arm')in ARMS,'Invalid comparison scope/arm')
        key=(row['case_id'],row['repeat_id'],row['arm']);_require(key not in indexed,'Duplicate comparison run')
        indexed[key]=row;blocks[key[:2]].append(row)
    paired=[]
    for (case,repeat),block in blocks.items():
        _require({r['arm']for r in block}==set(ARMS),'Every block must include all arms and failures')
        for key in ('case_inputs_sha256','source_family','source_case_id','source_controls_total'):
            _require(len({r[key]for r in block})==1,'Paired public inputs differ')
        main,assisted=(indexed[(case,repeat,arm)]for arm in ('main','main_route_critic'))
        _require((main['model'],main['provider'])==(assisted['model'],assisted['provider']),'Paired model/profile differs')
        paired.append((main,assisted))
    aggregate={}
    resource_keys=('model_calls','actual_tokens','charged_tokens','reserved_tokens','unsettled_requests',
        'fully_settled_actual_tokens','environment_actions','bootstrap_actions','policy_actions','elapsed_seconds','rechecks','completed_rechecks')
    for arm in ARMS:
        selected=[row for row in rows if row['arm']==arm]
        submitted=sum(r['submitted_count']for r in selected);controls=sum(r['source_controls_total']for r in selected)
        invalid=sum(r['invalid_submitted_count']for r in selected);unsupported=sum(r['unsupported_submitted_count']for r in selected)
        retained=sum(r['source_controls_retained']for r in selected);rejected=sum(r['false_rejection_count']for r in selected)
        aggregate[arm]={'runs':len(selected),'strict_selection_successes':sum(r['strict_selection_success']for r in selected),
            'missing_submissions':sum(r['missing_submission']for r in selected),
            'empty_submissions':sum(r['submission_status']=='submitted_empty'for r in selected),
            'incomplete_model_conversations':sum(r['conversation_completed']is False for r in selected),
            'submitted_count':submitted,'invalid_submitted_count':invalid,'invalid_submitted_fraction':invalid/submitted if submitted else None,
            'unsupported_submitted_count':unsupported,'unsupported_submitted_fraction':unsupported/submitted if submitted else None,
            'source_controls_total':controls,'source_controls_retained':retained,'source_control_retention':retained/controls if controls else None,
            'false_rejection_count':rejected,'false_rejection_fraction':rejected/controls if controls else None,
            'critic_invocations':sum(r['critic_invocations']for r in selected),
            'critic_rejected_reports':sum(r['critic_rejected_report_count']for r in selected),
            'critic_failed_consultations':sum(r['critic_failed_consultation_count']for r in selected),
            **{key:_sum_known(selected,key)for key in resource_keys}}
    differences=[int(a['strict_selection_success'])-int(m['strict_selection_success'])for m,a in paired]
    return {'scope':SCOPE,'case_count':len({r['case_id']for r in rows}),'paired_run_count':len(paired),
        'source_case_count':len({r['source_case_id']for r in rows}),'source_family_count':len({r['source_family']for r in rows}),
        'aggregate':aggregate,'paired_strict_selection':{'wins':sum(v>0 for v in differences),'ties':sum(v==0 for v in differences),'losses':sum(v<0 for v in differences)},
        'promotion_eligible':False,'default_changed':False,'experimental_validation':False,
        'limitations':['Reused development controls and controlled contract edits, not new chemical feasibility labels.',
            'Source/repeat cases are correlated; no independent held-out generalization claim.',
            'Empty and missing submissions remain false rejections; zero submission risk denominator is null.',
            'Confirmed tokens are lower bounds when unsettled reservations remain; charged units are not currency.',
            'Rechecks count validate attempts after review; completed_rechecks and recommended_recheck_used require status ok.']}
