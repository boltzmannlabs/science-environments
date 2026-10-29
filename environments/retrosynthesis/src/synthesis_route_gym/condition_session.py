"""Persistent main-profile sessions for finite measured-condition decisions."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
from .agent_bridge import BridgeError, run_agent_scientist_bridge
from .agent_runner import AgentBudget, resolve_main_profile
from .episode_store import EpisodeStore


def condition_tool_schemas():
    candidate = {'type':'string','minLength':1,'maxLength':200}
    def schema(name, description, properties, required):
        return {'name':name,'description':description,'parameters':{
            'type':'object','properties':properties,'required':required,'additionalProperties':False}}
    return [
        schema('inspect','Read candidates, predictions, revealed measurements and remaining resources.',{},[]),
        schema('observe_condition','Reveal one registered measured replay outcome; a new observation consumes allowance.',
               {'candidate_id':candidate},['candidate_id']),
        schema('predict_reaction_yield','Read pinned precomputed predictions. These are not measurements.',
               {'candidate_ids':{'type':'array','items':candidate,'minItems':1,'maxItems':64,'uniqueItems':True}},['candidate_ids']),
        schema('submit','Select an already observed candidate, or null to abstain. This ends the episode.',
               {'candidate_id':{'anyOf':[candidate,{'type':'null'}]}},['candidate_id']),
    ]


def condition_prompt(episode):
    view = episode.public_view()
    public = {key:view[key] for key in ('schema_version','study_id','substrate','target','domain_status','measurement')}
    public = {**public,'candidate_count':len(view['candidates']),
              'initial_observation_count':view['resources']['initial_observations']}
    return (
        'Optimize the measured yield within this finite registered condition study. Start by inspecting '
        'the candidate pool, observations and remaining allowance. Choose informative unobserved candidates, '
        'observe their recorded outcomes, and update your choices using that feedback. Aim to find and '
        'submit the best observed candidate within the allowed number of observations. You may submit '
        'earlier when justified. Submit only an already observed candidate, or null to abstain. Use submit '
        'before ending your response. Prediction values are frozen pretrained-model outputs with unknown '
        'transfer accuracy and calibration; they are not measurements. Observations replay a source dataset '
        'and are not new experiments. Do not invent conditions, outcomes or source support. The evaluator '
        'and unqueried source measurements are unavailable. On resume inspect current state; previous '
        'observations and consumed resources persist.\nStudy summary:\n'
        + json.dumps(public,sort_keys=True,allow_nan=False))


def _binding(args, episode, limits):
    profile = resolve_main_profile(args.profile_home)
    package = Path(__file__).parent
    sources = sorted(package.glob('*.py')) + sorted((package/'adapters').glob('*.py'))
    return {'schema_version':'srg-condition-session-binding-v1',
            'episode':episode.binding_fingerprint,'mode':args.method,'budget':asdict(limits),
            'profile':{'model':profile.model,'provider':profile.provider,'home':str(profile.home)},
            'scientist_python':str(Path(args.scientist_python).resolve()),
            'scientist_source':str(Path(args.scientist_source).resolve()),
            'implementation_hashes':{str(path.relative_to(package)):hashlib.sha256(path.read_bytes()).hexdigest()
                                     for path in sources}}


def run_condition_agent(args, episode, runtime_path, *, resume=False):
    if args.method not in {'main','main_condition_scientist'}:
        raise ValueError('Unknown condition agent method')
    if getattr(args, 'budget_regime', 'budgeted') == 'unbudgeted':
        if any(getattr(args,key,None) is not None for key in ('model_calls','max_actions','wall_seconds','max_tokens')):
            raise ValueError('Unbudgeted condition agent cannot impose finite ceilings')
        limits = AgentBudget.unbudgeted()
    else:
        limits = AgentBudget(max_model_calls=args.model_calls,max_tool_calls=args.max_actions,
                             wall_seconds=args.wall_seconds,max_total_tokens=args.max_tokens)
    binding = _binding(args,episode,limits)
    store = EpisodeStore(runtime_path)
    if resume:
        record, revision = store.load()
        if record.get('binding') != binding:
            raise ValueError('Condition runtime binding differs from requested configuration')
    else:
        record = {'binding':binding,'runtime':None,'result':None}
        revision = store.initialize(record)

    def checkpoint(state):
        nonlocal record, revision
        updated = {**record,'runtime':state}
        revision = store.commit(updated,expected_revision=revision)
        record = updated

    view = episode.public_view()
    remaining_seconds = view['resources']['remaining_seconds']
    if remaining_seconds is not None and remaining_seconds <= 0:
        episode.cancel('episode_deadline_expired')
    snapshot = episode.export()
    closed = (view['submission']['status'] != 'not_submitted'
              or snapshot.get('stop_reason') not in {None, 'candidate_space_exhausted'}
              or snapshot.get('terminated') or snapshot.get('truncated'))
    profile_identity = {'model':binding['profile']['model'],
                        'provider':binding['profile']['provider'],
                        'identity_source':'frozen session main-profile binding'}
    if closed:
        result = record.get('result') or {**profile_identity,'completed':False,
            'stop_reason':'episode_already_closed','resource_accounting':'no_new_provider_request'}
    else:
        try:
            result = run_agent_scientist_bridge(condition_prompt(episode),episode.dispatch,
                tool_schemas=condition_tool_schemas(),scientist_python=args.scientist_python,
                scientist_source=args.scientist_source,profile_home=args.profile_home,
                mode=args.method,budget=limits,resume_state=record['runtime'],checkpoint=checkpoint,
                cancel=episode.cancel,action_executor=episode.dispatch,
                remaining_seconds=None if remaining_seconds is None else max(0.001, remaining_seconds))
        except BridgeError:
            result = {**profile_identity,'completed':False,'error_type':'BridgeError',
                      'stop_reason':'bridge_interrupted',
                      'resource_accounting':'unknown_after_bridge_interruption'}
        updated = {**record,'result':result}
        revision = store.commit(updated,expected_revision=revision)
        record = updated
    exported = episode.export()
    return {'method':args.method,'agent':result,'episode':exported,
            'submission_status':exported['submission']['status']}
