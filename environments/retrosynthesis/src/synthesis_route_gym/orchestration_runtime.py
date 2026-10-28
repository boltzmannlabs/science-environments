"""Persistent composition of existing tool-free advisors on one shared ledger.

The host must serialize the entire metered callback, including this function.
Only public observations are retained. Provider admission remains in each advisor.
"""
import copy
import importlib
import json
from .resource_policy import agent_resources, advisor_admissible
from .orchestration import ROLES, normalize_policy, policy_fingerprint, role_prompt_instructions

VERSION = 'srg-orchestration-runtime-v1'
MAX_DECISIONS = 256
_MODULES = {'strategist':'strategist_runtime', 'condition_scientist':'route_condition_runtime',
            'route_critic':'route_critic_runtime'}
_CONSUMED = {'pending','accepted','rejected','failed','interrupted'}


def _module(role):
    return importlib.import_module('.' + _MODULES[role], __package__)


def initial_state(mode, policy=None):
    normalized = normalize_policy(mode, policy)
    return {'schema_version': VERSION, 'mode': mode, 'policy': normalized,
            'policy_sha256': policy_fingerprint(normalized),
            'advisors': {role: _module(role).initial_state() for role in ROLES},
            'decisions': [], 'decision_count': 0, 'decisions_truncated': False,
            'consultation_order': [], 'closed': False, 'runs': []}


def _flatten(state):
    return [copy.deepcopy(run) for role in state['consultation_order']
            for run in state['advisors'][role]['runs']]


def _used(state):
    return sum((child['consultation'] or {}).get('status') in _CONSUMED
               for child in state['advisors'].values())


def _validate_checkpoint(value):
    keys = {'schema_version','mode','policy','policy_sha256','advisors','decisions',
            'decision_count','decisions_truncated','consultation_order','closed','runs'}
    if not isinstance(value, dict) or set(value) != keys or value['schema_version'] != VERSION:
        raise ValueError('Invalid orchestration checkpoint shape')
    if len(json.dumps(value, allow_nan=False)) > 2000000:
        raise ValueError('Orchestration checkpoint exceeds size bound')
    if (type(value['decision_count']) is not int or value['decision_count'] < 0
            or type(value['closed']) is not bool or type(value['decisions_truncated']) is not bool
            or not isinstance(value['decisions'], list) or len(value['decisions']) > MAX_DECISIONS
            or not isinstance(value['advisors'], dict) or set(value['advisors']) != set(ROLES)
            or not isinstance(value['consultation_order'], list)
            or any(role not in ROLES for role in value['consultation_order'])
            or len(set(value['consultation_order'])) != len(value['consultation_order'])):
        raise ValueError('Invalid orchestration checkpoint fields')
    count = value['decision_count']
    if (len(value['decisions']) != min(count, MAX_DECISIONS)
            or value['decisions_truncated'] != (count > MAX_DECISIONS)):
        raise ValueError('Invalid bounded orchestration decision history')
    for index, decision in enumerate(value['decisions'], start=count-len(value['decisions'])+1):
        _validate_decision(decision, index)
    consulted = {role for role, child in value['advisors'].items() if child.get('consultation') is not None}
    if consulted != set(value['consultation_order']) or value['runs'] != _flatten(value):
        raise ValueError('Inconsistent orchestration advisor accounting')


def _validate_decision(decision, index):
    keys = {'index','action','input_sha256','eligible_roles','chosen_role','reasons','context_sha256'}
    if (not isinstance(decision, dict) or set(decision) != keys
            or type(decision['index']) is not int or decision['index'] != index
            or not isinstance(decision['action'], str) or len(decision['action']) > 120
            or decision['chosen_role'] not in (None, *ROLES)
            or not isinstance(decision['eligible_roles'], list)
            or len(decision['eligible_roles']) > 3
            or any(role not in ROLES for role in decision['eligible_roles'])
            or len(set(decision['eligible_roles'])) != len(decision['eligible_roles'])
            or not isinstance(decision['reasons'], dict) or set(decision['reasons']) != set(ROLES)
            or any(not isinstance(reason, str) or len(reason) > 120 for reason in decision['reasons'].values())):
        raise ValueError('Invalid orchestration decision')
    digest = decision['input_sha256']
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        raise ValueError('Invalid orchestration input digest')
    chosen, context = decision['chosen_role'], decision['context_sha256']
    if ((chosen is None and context is not None) or (chosen is not None and
            (chosen not in decision['eligible_roles'] or not isinstance(context, str) or not 1 <= len(context) <= 128))):
        raise ValueError('Invalid orchestration context binding')


def restore_state(value, *, mode=None, policy=None):
    """Pin host policy and consume previously admitted pending consultations."""
    try:
        _validate_checkpoint(value)
        normalized = normalize_policy(value['mode'], value['policy'])
        if normalized != value['policy'] or policy_fingerprint(normalized) != value['policy_sha256']:
            raise ValueError('Changed orchestration policy hash')
        if mode is not None and (value['mode'] != mode or normalized != normalize_policy(mode, policy)):
            raise ValueError('Orchestration policy differs from host configuration')
        if mode is None and policy is not None and normalized != normalize_policy(value['mode'], policy):
            raise ValueError('Orchestration policy differs from host configuration')
        result = copy.deepcopy(value)
        result['advisors'] = {role: _module(role).restore_state(value['advisors'][role]) for role in ROLES}
        if _used(result) > normalized['max_consultations']:
            raise ValueError('Orchestration allowance exceeded')
        for role, child in result['advisors'].items():
            status = (child['consultation'] or {}).get('status')
            if status in _CONSUMED and role not in normalized['enabled_roles']:
                raise ValueError('Disabled advisor has a consumed consultation')
        result['runs'] = _flatten(result)
        return result
    except (TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValueError('Invalid orchestration checkpoint') from exc


def _resources(ledger):
    return agent_resources(ledger)


def _disabled(child):
    return {**child, 'consultation': {'status':'disabled_observation', 'evidence_status':'agent_proposal',
            'plan':None, 'report':None, 'reason':'Public observation failed bounded advisor validation.'}}


def _observe(role, child, action, args, response, resources):
    module = _module(role)
    if child['consultation'] is not None:
        return child, None, 'already_consulted'
    try:
        if role == 'route_critic':
            if action != 'review_routes' or not isinstance(response, dict) or response.get('status') != 'ok':
                return child, None, 'awaiting_route_review'
            context = module.build_context(response.get('result'), resources)
            return child, context, 'eligible' if context is not None else 'insufficient_public_context'
        current = {**child, 'observer':module.observe(child['observer'], action, args, response)}
        context = module.build_context(current['observer'], resources)
        return current, context, 'eligible' if context is not None else 'insufficient_public_context'
    except (ValueError, TypeError, KeyError):
        return _disabled(child), None, 'disabled_observation'


def _replace_child(state, role, child):
    order = list(state['consultation_order'])
    if child['consultation'] is not None and role not in order:
        order.append(role)
    result = {**state, 'advisors':{**state['advisors'], role:copy.deepcopy(child)}, 'consultation_order':order}
    return {**result, 'runs':_flatten(result)}


def _record(state, action, args, response, contexts, reasons, chosen):
    index = state['decision_count'] + 1
    decision = {'index': index, 'action': str(action)[:120],
                'input_sha256':policy_fingerprint({'action':action,'args':args,'response':response}),
                'eligible_roles':[role for role in ROLES if contexts[role] is not None],
                'chosen_role':chosen, 'reasons':reasons,
                'context_sha256':_module(chosen).context_fingerprint(contexts[chosen]) if chosen else None}
    decisions = (state['decisions'] + [decision])[-MAX_DECISIONS:]
    return {**state, 'decisions':decisions, 'decision_count':index,
            'decisions_truncated':index > MAX_DECISIONS}


def after_tool(action, args, response, *, state, update, runtime, profile, ledger):
    """Observe all roles; admit at most one eligible experimental advisor."""
    current = copy.deepcopy(state)
    closed = current['closed'] or action == 'submit' or (isinstance(response, dict) and
        bool(response.get('terminated') or response.get('truncated')))
    current = {**current, 'closed':closed}
    contexts, reasons = {}, {}
    resources = _resources(ledger)
    for role in ROLES:
        child, context, reason = _observe(role, current['advisors'][role], action, args, response, resources)
        current = _replace_child(current, role, child)
        contexts[role], reasons[role] = context, reason
    policy = current['policy']
    for role in ROLES:
        if closed: reasons[role] = 'closed'
        elif ledger.finalization_only: reasons[role] = 'finalization_reserved'
        elif role not in policy['enabled_roles']: reasons[role] = 'policy_disabled'
        elif _used(current) >= policy['max_consultations']: reasons[role] = 'consultation_cap'
    chosen = next((role for role in policy['priority'] if reasons[role] == 'eligible'), None)
    current = _record(current, action, args, response, contexts, reasons, chosen)
    update(copy.deepcopy(current))

    def save_child(role, child):
        nonlocal current
        current = _replace_child(current, role, child)
        consultation = child.get('consultation') or {}
        if role == chosen and consultation.get('context_sha256'):
            # The runtime recomputes remaining wall time immediately before
            # admission. Bind the decision to that actual, persisted context.
            decision = {**current['decisions'][-1], 'context_sha256':consultation['context_sha256']}
            current = {**current, 'decisions':current['decisions'][:-1] + [decision]}
        update(copy.deepcopy(current))

    if chosen:
        # Selected runtime observes the original state exactly once, while other
        # observers retain this callback's tentative observation.
        result = _module(chosen).after_tool(action, args, response, state=state['advisors'][chosen],
            update=lambda child:save_child(chosen, child), runtime=runtime, profile=profile, ledger=ledger)
        if isinstance(result, dict):
            return {**result, 'orchestration_advice':{'role':chosen, 'policy_sha256':current['policy_sha256'],
                    'consultation':copy.deepcopy(current['advisors'][chosen]['consultation'])}}
        return result
    if not closed:
        # Resume delivery never requests a new consultation. One delivery per
        # callback keeps the main response small and deterministic.
        for role in policy['priority']:
            child = current['advisors'][role]
            if child.get('delivery_pending') and child['consultation'] is not None:
                if child['consultation']['status'] == 'disabled_observation':
                    # Existing runtimes mark all restored consultations pending
                    # delivery, including this intentionally silent disposition.
                    save_child(role, {**child, 'delivery_pending':False})
                    continue
                return _module(role).after_tool(action, args, response, state=child,
                    update=lambda value:save_child(role, value), runtime=runtime, profile=profile, ledger=ledger)
    return response


def summarize_state(state):
    return {'schema_version':'srg-orchestration-result-v1', 'mode':state['mode'],
            'policy':copy.deepcopy(state['policy']), 'policy_sha256':state['policy_sha256'],
            'consultations_used':_used(state), 'consultation_order':list(state['consultation_order']),
            'advisor_status':{role:(child['consultation'] or {}).get('status','not_invoked')
                              for role, child in state['advisors'].items()},
            'decision_count':state['decision_count'], 'decisions_truncated':state['decisions_truncated'],
            'closed':state['closed'], 'evidence_status':'agent_proposal',
            'claims_specialist_benefit':False, 'claims_experimental_validation':False}
