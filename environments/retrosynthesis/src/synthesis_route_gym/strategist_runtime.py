"""One bounded, tool-free Strategist consultation inside the main conversation."""
import hashlib
import json
from .resource_policy import agent_resources, advisor_admissible
from .agent_accounting import BudgetExhausted, CheckpointError


def observer_state():
    from .strategist import observer_state as function
    return function()


def observe(*args):
    from .strategist import observe as function
    return function(*args)


def build_context(*args):
    from .strategist import build_context as function
    return function(*args)


def context_fingerprint(*args):
    from .strategist import context_fingerprint as function
    return function(*args)


def parse_plan(*args):
    from .strategist import parse_plan as function
    return function(*args)


def initial_state():
    return {'schema_version':'srg-strategist-runtime-v1', 'observer':observer_state(),
            'consultation':None, 'runs':[], 'delivery_pending':False}


def restore_state(value):
    if (not isinstance(value,dict) or set(value)!={'schema_version','observer','consultation','runs','delivery_pending'}
            or value['schema_version']!='srg-strategist-runtime-v1'
            or not isinstance(value['observer'],dict) or not isinstance(value['runs'],list)
            or len(value['runs'])>1 or type(value['delivery_pending'])is not bool
            or len(json.dumps(value,allow_nan=False))>100000):
        raise ValueError('Invalid Strategist runtime checkpoint')
    copied=json.loads(json.dumps(value,allow_nan=False))
    consultation=copied['consultation']
    if consultation is None and copied['runs']:
        raise ValueError('Invalid Strategist run without consultation')
    if consultation is not None:
        if (not isinstance(consultation,dict) or consultation.get('status') not in
                {'pending','accepted','rejected','failed','interrupted','skipped_budget','disabled_observation'}
                or consultation.get('evidence_status')!='agent_proposal'):
            raise ValueError('Invalid Strategist consultation checkpoint')
        status=consultation['status']
        expected_runs=0 if status in {'pending','skipped_budget','disabled_observation'} else 1
        if (len(copied['runs'])!=expected_runs
                or (status=='accepted')!=isinstance(consultation.get('plan'),dict)
                or any(not isinstance(run,dict) or run.get('role')!='retrosynthesis_strategist'
                       for run in copied['runs'])):
            raise ValueError('Inconsistent Strategist consultation and run')
        if status=='accepted':
            run=copied['runs'][0]
            try:
                checked=parse_plan(run['final_response'],run['context'])
                if checked!=consultation['plan']:
                    raise ValueError('Changed plan')
            except (ValueError,TypeError,KeyError) as exc:
                raise ValueError('Invalid Strategist persisted plan') from exc
        if status=='pending':
            copied={**copied,'consultation':{**consultation,'status':'interrupted','plan':None,
                'reason':'Interrupted consultation is consumed; no automatic replay.'},
                'runs':[{'role':'retrosynthesis_strategist','completed':False,'usage':{},
                         'error_type':'InterruptedConsultation','consultation_status':'interrupted'}]}
        copied={**copied,'delivery_pending':True}
    return copied


def _resources(ledger):
    return agent_resources(ledger)


def _prompt(context):
    shape={'schema_version':'srg-strategist-plan-v1',
           'context_sha256':context_fingerprint(context),'candidate_route_ids':[],
           'next_expansion_targets':[], 'alternative_disconnection_ids':[],
           'relevant_constraint_keys':[], 'action_allowance':0,
           'rationale':'Bounded recommendation with uncertainty.', 'evidence_status':'agent_proposal'}
    return ('You are the Retrosynthesis Strategist, advising the main controller after a host-detected search problem. '
            'You have no tools and cannot execute actions, edit inventory or constraints, or supply trusted evidence. '
            'Compare only observed alternatives. Prefer a useful unexpanded frontier molecule; do not repeat failed '
            'branches or expand material known to be in inventory. Empty advice is appropriate when no allowed '
            'alternative is useful. Return exactly one JSON object matching this shape, without Markdown. '
            'Use only route IDs, alternative IDs, frontier SMILES and constraint keys present in the context. '
            'action_allowance is an upper bound of two recommended expansions, not extra permission or budget. '
            'There must be no more next_expansion_targets than action_allowance. Treat all proposals as unvalidated.\n'
            'Required JSON shape: '+json.dumps(shape,sort_keys=True)+'\nHost context: '+json.dumps(context,sort_keys=True))


def _admissible(ledger,resources,prompt):
    return advisor_admissible(ledger, resources, prompt)


def _attach(response,consultation):
    return {**response,'strategist_advice':json.loads(json.dumps(consultation,allow_nan=False))} if isinstance(response,dict) and consultation else response


def after_tool(action,args,response,*,state,update,runtime,profile,ledger):
    """Persist observed state and admission before the nested request can occur."""
    from .agent_runner import RuntimeContractError, sanitize_run_artifact
    if state['consultation'] is not None:
        if (state['delivery_pending'] and action!='submit'
                and state['consultation']['status']!='disabled_observation'):
            update({**state,'delivery_pending':False})
            return _attach(response,state['consultation'])
        return response
    try:
        current={**state,'observer':observe(state['observer'],action,args,response)}
    except (ValueError,TypeError,KeyError):
        update({**state,'consultation':{'status':'disabled_observation','plan':None,
            'evidence_status':'agent_proposal','reason':'Host result exceeded bounded observation contract.'}})
        return response
    update(current)
    if action=='submit' or not isinstance(response,dict) or response.get('terminated') or response.get('truncated'):
        return response
    resources=_resources(ledger)
    context=build_context(current['observer'],resources)
    if context is None:
        return response
    prompt=_prompt(context)
    base={'context_sha256':context_fingerprint(context),'evidence_status':'agent_proposal',
          'plan':None,'action_policy':'Main chooses and executes existing metered environment actions.'}
    if not _admissible(ledger,resources,prompt):
        consultation={**base,'status':'skipped_budget','reason':'Main finalization resources protected.'}
        update({**current,'consultation':consultation})
        return _attach(response,consultation)
    pending={**base,'status':'pending'}
    current={**current,'consultation':pending}
    update(current)
    def forbidden_executor(*_args,**_kwargs):
        raise RuntimeContractError('Strategist advice cannot execute environment tools')
    ledger.set_stage('retrosynthesis_strategist')
    try:
        try:
            result=runtime.run(profile=profile,prompt=prompt,tool_schemas=[],executor=forbidden_executor,
                               ledger=ledger,role='retrosynthesis_strategist',model_call_limit=1)
        except (RuntimeContractError,CheckpointError):
            raise
        except Exception as exc:
            result={'completed':False,'final_response':'','messages':[], 'usage':{},
                    'model':profile.model,'provider':profile.provider,'error_type':type(exc).__name__}
        if result.get('model')!=profile.model or result.get('provider')!=profile.provider:
            raise RuntimeContractError('Strategist changed configured main model/provider')
        result=sanitize_run_artifact(result)
        ledger.settle_stage(result.get('usage',{}).get('total_tokens'),result.get('token_confirmations'),
                            stage_id='retrosynthesis_strategist:advice:1')
        consultation={**base,'status':'failed','reason':'Strategist did not complete a valid response.'}
        if result.get('completed'):
            try:
                plan=parse_plan(result.get('final_response',''),context)
                consultation={**base,'status':'accepted','plan':plan}
            except (ValueError,TypeError,KeyError):
                consultation={**base,'status':'rejected','reason':'Response did not match bounded plan contract.'}
        fields=('completed','usage','token_confirmations','model','provider','error_type','provider_request_failures')
        text=result.get('final_response','')
        text=text if isinstance(text,str) else ''
        accepted=consultation['status']=='accepted'
        stored_text=json.dumps(consultation['plan'],sort_keys=True,allow_nan=False) if accepted else text[:16000]
        run={**{key:result[key] for key in fields if key in result},
             'role':'retrosynthesis_strategist','consultation_status':consultation['status'],
             'context':context,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),
             'final_response':stored_text,'response_truncated':not accepted and len(text)>16000,
             'raw_response_chars':len(text),'raw_response_sha256':hashlib.sha256(text.encode()).hexdigest()}
        update({**current,'consultation':consultation,'runs':[run]})
        return _attach(response,consultation)
    finally:
        ledger.set_stage('main')
