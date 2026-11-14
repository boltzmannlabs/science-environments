"""Validated episode transitions; no physical experiment is executed here."""
from dataclasses import dataclass, field
from typing import Any
from environment.observations import Observation, Value
from environment.budget import Budget
from tools.mixture_validator import validate

KINDS = frozenset({'verify_source','register_material','validate_candidate','assess_compatibility','predict_dissolution','design_experiment','record_measurement','update_ranking','finalize_episode'})


@dataclass
class Action:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.kind not in KINDS or not isinstance(self.payload, dict):
            raise ValueError('invalid action')


def execute(state, action: Action, *, budget: Budget | None = None, adapters=None) -> Observation:
    """Apply one action or return a recoverable observation; log every attempt."""
    if not isinstance(action, Action):
        raise TypeError('expected Action')
    kind, p = action.kind, action.payload
    task_id = state.task['task_id']
    obs = Observation(task_id, 'success', 'derived', candidate_id=p.get('candidate_id'))
    try:
        if state.status == 'finalized':
            raise ValueError('episode finalized')
        if budget:
            budget.charge('actions')
            state.budget = budget.snapshot()
        if kind == 'verify_source':
            if not p.get('source_id') or not p.get('citation') or not p.get('verified_by') or not p.get('document_id'):
                raise ValueError('source needs source_id, citation, document_id, verified_by')
            if p.get('authorized_measurement') and not p.get('measurement_authorization_id'):
                raise ValueError('measurement source needs authorization identifier')
            state.sources[p['source_id']] = dict(p)
        elif kind == 'register_material':
            if not p.get('material_id') or not p.get('source_id') or p['source_id'] not in state.sources:
                raise ValueError('material needs identity and verified source')
            state.materials[p['material_id']] = dict(p)
        elif kind == 'validate_candidate':
            c = p.get('candidate')
            if not isinstance(c, dict) or not c.get('candidate_id'):
                raise ValueError('candidate and candidate_id required')
            if any(part.get('material_id') not in state.materials for part in c.get('ingredients', []) if isinstance(part, dict)):
                raise ValueError('candidate material not registered')
            check = validate(c, state.constraints.get('bounds'), state.constraints.get('process_limits'))
            obs.constraints = check.as_dict()
            state.candidates[c['candidate_id']] = {'candidate': c, 'status': 'valid' if check.valid else 'invalid', 'check': check.as_dict()}
            if not check.valid:
                obs.status = 'failure'
        elif kind in {'assess_compatibility','predict_dissolution'}:
            cid = p.get('candidate_id')
            if cid not in state.candidates or state.candidates[cid]['status'] != 'valid':
                raise ValueError('candidate must first be validated')
            capability = 'compatibility' if kind == 'assess_compatibility' else 'dissolution'
            if budget and adapters and capability in adapters.contracts:
                budget.charge('tool_calls')
            obs = adapters.call(capability, p, task_id=task_id) if adapters else Observation(task_id, 'tool_unavailable', candidate_id=cid, missing_data=[capability + ' approved tool'])
            if obs.status == 'success':
                if obs.result_type != 'predicted':
                    raise ValueError('prediction tool must return predicted evidence')
                state.predictions[cid + ':' + capability] = obs.to_dict()
        elif kind == 'design_experiment':
            eid = p.get('experiment_id')
            if not eid or eid in state.experiments or not p.get('factors') or not p.get('responses') or not p.get('controls') or not isinstance(p.get('replicates'), int) or p['replicates'] < 1 or not p.get('rationale'):
                raise ValueError('experiment requires unique id, factors, responses, controls, replicates, rationale')
            if budget:
                budget.charge('proposed_experiments')
            state.experiments[eid] = {'proposal': dict(p), 'status': 'proposed'}
            obs.status = 'approval_required'
            obs.next_actions = ['obtain explicit human approval before execution']
        elif kind == 'record_measurement':
            eid, source = p.get('experiment_id'), p.get('source_id')
            if not eid or eid not in state.experiments or not source or source not in state.sources or not state.sources[source].get('authorized_measurement') or not p.get('confirmed_by') or not p.get('approval_id'):
                raise ValueError('authorized measurement source, approval, confirmation and experiment required')
            if state.experiments[eid]['status'] == 'completed':
                raise ValueError('experiment already completed')
            values = [Value(**v) for v in p.get('values', [])]
            if not values or any(v.label != 'measured' or v.source_id != source for v in values):
                raise ValueError('only measured values from authorized source')
            if budget:
                budget.charge('completed_experiments')
            state.experiments[eid]['status'] = 'completed'
            state.experiments[eid]['values'] = [v.__dict__ for v in values]
            state.experiments[eid]['approval_id'] = p['approval_id']
            obs = Observation(task_id, 'success', 'measured', results=values, provenance={'tool':None,'version':None,'source_ids':[source]})
        elif kind == 'update_ranking':
            ranking = p.get('ranking')
            if not isinstance(ranking, list) or any(c not in state.candidates or state.candidates[c]['status'] != 'valid' for c in ranking) or len(ranking) != len(set(ranking)):
                raise ValueError('ranking needs distinct valid candidates')
            state.ranking = ranking
        elif kind == 'finalize_episode':
            from evaluation.verifier import verify
            findings = verify(state)
            from agents.evidence_auditor import AuditRequest, audit
            decision = audit(AuditRequest(tuple(state.evidence),state.sources))
            if decision.decision != 'accept':
                findings.append('evidence auditor: ' + decision.decision)
            if not any('primary_recall_record' in source.get('verified_fields', []) for source in state.sources.values()):
                findings.append('primary recall record not verified')
            if findings:
                obs.status = 'failure'
                obs.warnings = findings
            else:
                state.status = 'finalized'
    except (ValueError, RuntimeError, TypeError, KeyError) as exc:
        obs.status = 'failure'
        obs.warnings.append(str(exc))
    finally:
        state.log(kind, obs.status, {'warnings': obs.warnings, 'candidate_id': p.get('candidate_id')})
        if budget:
            state.budget = budget.snapshot()
    return obs
