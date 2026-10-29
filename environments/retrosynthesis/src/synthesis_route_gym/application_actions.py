"""Host route-step workflows with explicit evidence access and shared budgets."""
from .application_contracts import ApplicationConfig,APPLICATION_INPUTS,ReportRequest,digest,plain
from .scientific_execution import RETRIEVAL_ACTIONS,execute_scientific


def configure(value,study):
    config=ApplicationConfig.model_validate(plain(value)if value is not None else {})
    if config.condition_binding is not None:
        from .portfolio_condition_binding import validate_binding
        validate_binding(study,config.condition_binding)
    return config,digest(config)


def reference(route,step=None):
    result={'route_id':route.route_id,'route_sha256':digest(route),'parent_route_id':route.parent_route_id}
    if step is not None:result={**result,'step_id':step.step_id,'step_sha256':digest(step)}
    return result


def stored_step(env,route_id,step_id):
    route=env._route(route_id)
    if len(route.steps)>12:raise ValueError('Application route step bound exceeded')
    selected=[s for s in route.steps if s.step_id==step_id]
    if len(selected)!=1:raise ValueError('Expected one unambiguous stored step')
    return route,selected[0],reference(route,selected[0])


def matching_events(env,binding,actions):
    return [row for row in env._events if row['action']in actions and row.get('result',{}).get('route_step_reference')==binding]


def observations(env,binding):
    return [r['result']['tool_result']['data']for r in matching_events(env,binding,{'observe_route_condition'})if r['status']=='ok']


def condition_context(env,step):
    from .portfolio_condition_binding import validate_step_binding
    study=env._science_options['condition_study'];binding=env._application_config.condition_binding
    if study is None or binding is None:raise ValueError('No route-bound condition study configured')
    validate_step_binding(step,study,binding)
    return study,binding


def _observation_resources(env,study):
    actions={'observe_route_condition','observe_condition','condition_observation'}
    records=(*env._events,*([env._pending]if env._pending else []))
    attempted=set(study.observed_ids)
    attempted.update(row.get('arguments',{}).get('candidate_id')for row in records
                     if row['action']in actions and isinstance(row.get('arguments',{}).get('candidate_id'),str))
    used=env._scientific_usage.get('observe_condition',0)
    limits = [value for value in (env._scientific_limits.observation_calls,
              None if study.budget is None else study.budget-len(study.observed_ids)) if value is not None]
    limit = min(limits) if limits else None
    return {'schema_version':'srg-route-observation-resources-v1','calls_used':used,
            **({'regime':'unbudgeted'} if limit is None else {}),
            'call_limit':limit,'remaining_calls':None if limit is None else max(0,limit-used),
            'attempted_candidate_ids':sorted(attempted)}


def _catalog(env,step,binding,*,offset=0,limit=20,latest=None):
    from .portfolio_condition_binding import condition_catalog
    study,config=condition_context(env,step)
    revealed=observations(env,binding)
    if latest is not None:revealed=[*revealed,latest]
    catalog=condition_catalog(step,study,config,observations=revealed)
    candidates=catalog['candidates']
    return {**catalog,'candidates':candidates[offset:offset+limit],'candidate_count':len(candidates),
        'offset':offset,'next_offset':offset+limit if offset+limit<len(candidates)else None,
        'route_step_reference':binding,'application_configuration_sha256':env._application_fingerprint,
        'observation_resources':_observation_resources(env,study)}


def _condition_options(env,args,step,binding):
    return 'ok',_catalog(env,step,binding,offset=args.offset,limit=args.limit)


def _observe(env,args,step,binding):
    from .portfolio_condition_binding import validate_step_binding
    study,config=condition_context(env,step);public=validate_step_binding(step,study,config)
    if args.candidate_id not in {r['candidate_id']for r in public['candidates']}:raise ValueError('Unknown registered candidate')
    for row in env._events:
        if row['action']in {'observe_route_condition','observe_condition','condition_observation'} and row['arguments'].get('candidate_id')==args.candidate_id:
            raise ValueError('Condition observation already attempted')
    status,result=execute_scientific(env,'observe_condition',{'candidate_id':args.candidate_id})
    catalog=_catalog(env,step,binding,latest=result['data']if status=='ok'else None)
    return status,{'route_step_reference':binding,'tool_result':result,'condition_catalog':catalog}


def _predict(env,args,step,binding):
    arguments={'reactants':[u.smiles for u in step.reactants],'product':step.product,'top_k':args.top_k}
    status,result=execute_scientific(env,'predict_impurities',arguments)
    return status,{'route_step_reference':binding,'prediction':{'action':'predict_impurities','arguments':arguments,'result':result}}


def _retrieve(env,args,binding):
    if env._source_access_mode!='evidence_retrieval':return 'unavailable',{'reason':'closed_information','route_step_reference':binding}
    if (env._scientific_limits.retrieval_calls is not None
            and sum(env._scientific_usage.get(n,0)for n in RETRIEVAL_ACTIONS)>env._scientific_limits.retrieval_calls):
        return 'error',{'reason':'access_budget_exhausted','route_step_reference':binding}
    config=env._application_config
    records=config.impurity_annotations if args.application=='impurity_analysis'else config.biocatalytic_records
    selected=records[args.offset:args.offset+args.limit]
    return 'ok',{'schema_version':'srg-application-source-retrieval-v1','application':args.application,
        'route_step_reference':binding,'records':[plain(r)for r in selected],'record_count':len(records),
        'next_offset':args.offset+args.limit if args.offset+args.limit<len(records)else None,
        'catalog_sha256':digest([plain(r)for r in records]),'evidence_status':'host_registered_source_claims_not_independently_verified'}


def _retrieved_records(events,application):
    records={};key='annotation_id'if application=='impurity_analysis'else'record_id'
    for row in events:
        result=row['result']
        if row['action']=='retrieve_application_sources' and row['status']=='ok' and result['application']==application:
            for record in result['records']:
                ident=record[key]
                if ident in records and records[ident]!=record:raise ValueError('Retrieved source changed')
                records={**records,ident:record}
    return list(records.values())


def _step_report(env,args,step,binding):
    actions={'retrieve_application_sources'}
    if args.application=='condition_optimization':actions={'observe_route_condition'}
    if args.application=='impurity_analysis':actions|={'predict_route_impurities'}
    events=matching_events(env,binding,actions)
    if args.application=='condition_optimization':
        from .portfolio_condition_binding import build_condition_report
        study,config=condition_context(env,step)
        result=build_condition_report(step,study,config,observations=observations(env,binding),selected_candidate_id=args.candidate_id)
    elif args.application=='impurity_analysis':
        from .portfolio_impurities import build_impurity_report
        predictions=[r['result']['prediction']for r in events if r['action']=='predict_route_impurities'and 'prediction'in r['result']]
        result=build_impurity_report(step,prediction=predictions[-1]if predictions else None,annotations=_retrieved_records(events,args.application))
    else:
        from .portfolio_biocatalysis import build_biocatalysis_report
        result=build_biocatalysis_report(env.task,step,records=_retrieved_records(events,args.application))
    return result,events


def _report(env,args):
    routes=[env._route(i)for i in args.route_ids];binding=None
    if any(len(r.steps)>12 for r in routes):raise ValueError('Application route step bound exceeded')
    if args.step_id is not None:
        route,step,binding=stored_step(env,args.route_ids[0],args.step_id);result,events=_step_report(env,args,step,binding)
    elif args.application=='inventory_planning':
        from .portfolio_inventory import build_inventory_report
        result=build_inventory_report(env.task,routes,events=list(env._events));events=list(env._events)
    else:
        from .portfolio_process import build_process_report
        basis=env._application_config.process_basis or env._science_options.get('process_basis')
        result=build_process_report(env.task,routes,basis=basis);events=[]
    return 'ok',plain({'schema_version':'srg-application-report-v1','application':args.application,
        'task_sha256':env._task_sha256,'application_configuration_sha256':env._application_fingerprint,
        'route_references':[reference(r)for r in routes],'route_step_reference':binding,
        'input_event_references':[{'index':r['index'],'action':r['action'],'status':r['status'],'sha256':r['sha256']}for r in events],
        'result':result,'claims_experimental_validation':False,
        'validation_status':'software_contract_checked_scientific_validation_not_established',
        'limitations':['Recorded predictions and source claims retain their original authority.',
                       'Reporting does not modify, select or independently validate a synthesis.']})


def execute_application(env,name,arguments):
    args=APPLICATION_INPUTS[name].model_validate(arguments)
    if isinstance(args,ReportRequest):return _report(env,args)
    route,step,binding=stored_step(env,args.route_id,args.step_id)
    if name=='condition_options':return _condition_options(env,args,step,binding)
    if name=='observe_route_condition':return _observe(env,args,step,binding)
    if name=='predict_route_impurities':return _predict(env,args,step,binding)
    return _retrieve(env,args,binding)
