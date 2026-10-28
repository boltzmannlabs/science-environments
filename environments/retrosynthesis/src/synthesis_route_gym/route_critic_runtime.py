"""One tool-free Route Critic consultation on an explicit host review packet."""
import hashlib
import json
from .resource_policy import agent_resources, advisor_admissible
from .agent_accounting import CheckpointError


def build_context(*args):
    from .route_critic import build_context as function
    return function(*args)


def context_fingerprint(*args):
    from .route_critic import context_fingerprint as function
    return function(*args)


def parse_report(*args):
    from .route_critic import parse_report as function
    return function(*args)


def hydrate_report(*args):
    from .route_critic import hydrate_report as function
    return function(*args)


def initial_state():
    return {'schema_version':'srg-route-critic-runtime-v1','consultation':None,
            'runs':[],'delivery_pending':False}


def restore_state(value):
    if (not isinstance(value,dict) or set(value)!={'schema_version','consultation','runs','delivery_pending'}
            or value['schema_version']!='srg-route-critic-runtime-v1'
            or not isinstance(value['runs'],list) or len(value['runs'])>1
            or type(value['delivery_pending'])is not bool
            or len(json.dumps(value,allow_nan=False))>300000):
        raise ValueError('Invalid Route Critic runtime checkpoint')
    copied=json.loads(json.dumps(value,allow_nan=False));consultation=copied['consultation']
    if consultation is None:
        if copied['runs'] or copied['delivery_pending']:
            raise ValueError('Invalid Route Critic delivery or run without consultation')
        return copied
    if (not isinstance(consultation,dict) or consultation.get('status') not in
            {'pending','accepted','rejected','failed','interrupted','skipped_budget','disabled_observation'}
            or consultation.get('evidence_status')!='agent_proposal'):
        raise ValueError('Invalid Route Critic consultation checkpoint')
    status=consultation['status']
    expected_runs=0 if status in {'pending','skipped_budget','disabled_observation'} else 1
    if (len(copied['runs'])!=expected_runs
            or (status=='accepted')!=isinstance(consultation.get('report'),dict)
            or any(not isinstance(run,dict) or run.get('role')!='route_critic'for run in copied['runs'])):
        raise ValueError('Inconsistent Route Critic consultation and run')
    if status=='accepted':
        run=copied['runs'][0]
        try:
            report=parse_report(run['final_response'],run['context'])
            if (report!=consultation['report']
                    or hydrate_report(report,run['context'])!=consultation.get('recommendation')
                    or context_fingerprint(run['context'])!=consultation.get('context_sha256')):
                raise ValueError('Changed report')
        except (ValueError,TypeError,KeyError) as exc:
            raise ValueError('Invalid Route Critic persisted report')from exc
    if status=='pending':
        copied={**copied,'consultation':{**consultation,'status':'interrupted','report':None,
            'reason':'Interrupted consultation is consumed; no automatic replay.'},
            'runs':[{'role':'route_critic','completed':False,'usage':{},
                     'error_type':'InterruptedConsultation','consultation_status':'interrupted'}]}
    return {**copied,'delivery_pending':True}


def _resources(ledger):
    return agent_resources(ledger)


def _prompt(context):
    shape={'schema_version':'srg-route-critic-report-v1','context_sha256':context_fingerprint(context),
           'findings':[],'recommended_recheck_id':None,'evidence_status':'agent_proposal'}
    finding={'route_id':'known route ID','step_id':None,'category':'route_structure','severity':'review',
             'supporting_fact_ids':[],'source_record_ids':[],'requested_revision':'retain_uncertainty',
             'rationale':'A bounded evidence-qualified concern.'}
    return ('You are the Route Critic advising the main controller on a registered shortlist. '
            'You have no tools and cannot execute actions, change routes, reject submissions or grant resources. '
            'Inspect only the host packet and separate definite contract errors from unresolved chemistry. '
            'Missing conditions, source ambiguity, incomplete atom accounting or uncertain model transfer do not '
            'prove a reaction impossible. A source connectivity match does not establish experimental feasibility. '
            'Prioritize concise, material concerns; at most eight findings is a limit, not a quota. '
            'Use only known route, step, fact and source IDs. '
            'Use severity error only when citing a host deterministic error for the exact same route, step and category. '
            'Other concerns use review or info; do not upgrade source claims or your opinions into host authority. '
            'The categories are route_structure, constraint_violation, unsupported_transformation, missing_materials, '
            'stereochemistry, quantity_conflict, incomplete_conditions and model_domain_mismatch. '
            'Each finding must include every field shown below; rationale is at most 600 characters. '
            'requested_revision is revise_route, recheck, retain_uncertainty or none. '
            'You may recommend at most one recheck ID from the host menu, otherwise null. '
            'Main decides whether to execute ordinary metered rechecks or revisions. Empty findings are valid. '
            'Return exactly the report JSON without Markdown or extra fields. The host hydrates exact cited facts '
            'and sources; do not invent numeric values, recipes, evidence, labels or hidden evaluator answers.\n'
            'Required report shape: '+json.dumps(shape,sort_keys=True)+
            '\nFinding shape: '+json.dumps(finding,sort_keys=True)+
            '\nHost context: '+json.dumps(context,sort_keys=True))


def _admissible(ledger,resources,prompt):
    return advisor_admissible(ledger, resources, prompt)


def _attach(response,consultation):
    return {**response,'route_critic_advice':json.loads(json.dumps(consultation,allow_nan=False))}


def after_tool(action,args,response,*,state,update,runtime,profile,ledger):
    """Review only a successful, open host shortlist; advice never executes tools."""
    from .agent_runner import RuntimeContractError, sanitize_run_artifact
    if state['consultation']is not None:
        if (state['delivery_pending'] and action!='submit' and isinstance(response,dict)
                and state['consultation']['status']!='disabled_observation'):
            update({**state,'delivery_pending':False})
            return _attach(response,state['consultation'])
        return response
    if (action!='review_routes' or not isinstance(response,dict) or response.get('status')!='ok'
            or response.get('terminated') or response.get('truncated')):
        return response
    resources=_resources(ledger)
    try:
        context=build_context(response['result'],resources)
        if context is None:
            consultation={'status':'skipped_budget','report':None,'evidence_status':'agent_proposal',
                          'reason':'No critic context admitted with exhausted shared resources.'}
            update({**state,'consultation':consultation})
            return _attach(response,consultation)
        prompt=_prompt(context)
    except (ValueError,TypeError,KeyError):
        update({**state,'consultation':{'status':'disabled_observation','report':None,
            'evidence_status':'agent_proposal','reason':'Host review exceeded bounded context contract.'}})
        return response
    base={'context_sha256':context_fingerprint(context),'evidence_status':'agent_proposal','report':None,
          'action_policy':'Main chooses and executes existing metered rechecks, revisions and submission.'}
    if not _admissible(ledger,resources,prompt):
        consultation={**base,'status':'skipped_budget','reason':'Main finalization resources protected.'}
        update({**state,'consultation':consultation})
        return _attach(response,consultation)
    current={**state,'consultation':{**base,'status':'pending'}};update(current)
    def forbidden_executor(*_args,**_kwargs):
        raise RuntimeContractError('Route Critic advice cannot execute environment tools')
    ledger.set_stage('route_critic')
    try:
        try:
            result=runtime.run(profile=profile,prompt=prompt,tool_schemas=[],executor=forbidden_executor,
                               ledger=ledger,role='route_critic',model_call_limit=1)
        except (RuntimeContractError,CheckpointError):
            raise
        except Exception as exc:
            result={'completed':False,'final_response':'','messages':[],'usage':{},
                    'model':profile.model,'provider':profile.provider,'error_type':type(exc).__name__}
        if result.get('model')!=profile.model or result.get('provider')!=profile.provider:
            raise RuntimeContractError('Route Critic changed configured main model/provider')
        result=sanitize_run_artifact(result)
        ledger.settle_stage(result.get('usage',{}).get('total_tokens'),result.get('token_confirmations'),
                            stage_id='route_critic:advice:1')
        consultation={**base,'status':'failed','reason':'Route Critic did not complete a valid response.'}
        if result.get('completed'):
            try:
                report=parse_report(result.get('final_response',''),context)
                consultation={**base,'status':'accepted','report':report,'recommendation':hydrate_report(report,context)}
            except (ValueError,TypeError,KeyError):
                consultation={**base,'status':'rejected','reason':'Response did not match bounded report contract.'}
        fields=('completed','usage','token_confirmations','model','provider','error_type','provider_request_failures')
        text=result.get('final_response','');text=text if isinstance(text,str)else''
        accepted=consultation['status']=='accepted'
        stored=json.dumps(consultation['report'],sort_keys=True,allow_nan=False)if accepted else text[:16000]
        run={**{key:result[key]for key in fields if key in result},'role':'route_critic',
             'consultation_status':consultation['status'],'context':context,
             'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'final_response':stored,
             'response_truncated':not accepted and len(text)>16000,'raw_response_chars':len(text),
             'raw_response_sha256':hashlib.sha256(text.encode()).hexdigest()}
        update({**current,'consultation':consultation,'runs':[run]})
        return _attach(response,consultation)
    finally:
        ledger.set_stage('main')
