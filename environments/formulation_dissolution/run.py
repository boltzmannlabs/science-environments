"""Local orchestrator: evidence-first triage and explicit specialist abstention."""
import argparse
import json
from pathlib import Path
from environment.state import Episode
from environment.budget import Budget
from environment.actions import Action, execute
from agents.evidence_auditor import AuditRequest, audit
from evaluation.baselines import run as baseline
from evaluation.holdout_benchmark import benchmark
from evaluation.verifier import verify
from agents.formulation_design import DesignRequest, propose
from agents.constraint_critic import CriticRequest, critique
from agents.compatibility_stability import CompatibilityRequest, assess
from agents.property_prediction import PredictionRequest, predict
from agents.experimental_design import ExperimentRequest, design

TASK_ID = 'ranolazine_er_dissolution_investigation'


def investigate(state: Episode, *, budget: Budget | None = None, adapters=None) -> dict:
    """Call only specialists whose input contracts are satisfied; abstain otherwise."""
    if state.task.get('task_id') != TASK_ID:
        raise ValueError('unexpected task identity')
    budget = budget or Budget({'actions': 100, 'tool_calls': 0, 'proposed_experiments': 0, 'completed_experiments': 0})
    # Task metadata alone is not evidence: require attested source-linked records.
    missing = [field for field in baseline(state.task)['unknowns']
               if not any(field in src.get('verified_fields', []) for src in state.sources.values())]
    claims = tuple(state.evidence)
    decision = audit(AuditRequest(claims, state.sources))
    findings = verify(state)
    # Run read-only specialist triage on known identity. Other specialists
    # remain gated on a real candidate or a specified hypothesis.
    specialist_status = {
        'evidence_auditor': decision.decision,
        'formulation_design': propose(DesignRequest(state.materials, {})).status,
        'compatibility_stability': assess(CompatibilityRequest(('ranolazine',))).status,
        'property_prediction': predict(PredictionRequest(TASK_ID, 'unassigned', {})).status,
        'constraint_critic': 'not_called_no_batch_candidate',
        'experimental_design': 'not_called_no_discriminating_hypothesis',
    }
    reviews = []
    proposals = []
    for cid, entry in state.candidates.items():
        candidate = entry['candidate']
        critique_result = critique(CriticRequest(candidate, state.constraints.get('bounds'), state.constraints.get('process_limits')))
        design_result = propose(DesignRequest(state.materials, candidate, state.constraints.get('bounds')))
        reviews.append({'candidate_id':cid,'design_status':design_result.status,'constraints':critique_result.as_dict(),
                        'compatibility':assess(CompatibilityRequest(tuple(p['material_id'] for p in candidate.get('ingredients', []) if isinstance(p,dict) and p.get('material_id')))).status if any(isinstance(p,dict) and p.get('material_id') for p in candidate.get('ingredients', [])) else 'insufficient_data',
                        'prediction_status':predict(PredictionRequest(TASK_ID,cid,{})).status})
    for hypothesis in state.hypotheses:
        if all(hypothesis.get(k) for k in ('text','factors','responses','controls','replicates','rationale')):
            try:
                request = ExperimentRequest(hypothesis['text'],tuple(hypothesis['factors']),tuple(hypothesis['responses']),tuple(hypothesis['controls']),hypothesis['replicates'],hypothesis['rationale'],hypothesis.get('cost'))
                proposals.append({'hypothesis':request.hypothesis,'status':design(request).status,'approval_required':True})
            except (ValueError, TypeError):
                proposals.append({'hypothesis':hypothesis.get('text'),'status':'invalid_proposal'})
    return {'task_id': TASK_ID, 'case_id': state.task.get('case_id'), 'status': 'insufficient_data' if missing or decision.decision != 'accept' or findings else 'review_required', 'verified_facts': [c for c in claims if c.get('label') in ('measured','literature_reported') and c.get('source_id') in state.sources] if decision.decision == 'accept' and not findings else [], 'hypotheses': state.hypotheses, 'predictions': list(state.predictions.values()), 'candidate_reviews':reviews, 'experiment_proposals':proposals, 'specialist_status':specialist_status, 'unknowns': missing, 'proposed_next_analyses': ['obtain missing controlled QC method, acceptance criteria, measured profiles and batch records'] if 'primary_recall_record' not in missing else ['obtain primary recall record and controlled method/lot records'], 'auditor': {'decision':decision.decision,'reasons':decision.reasons}, 'verifier_findings': findings, 'budget': budget.snapshot(), 'limitations':['FDA enforcement reporting verifies a recall listing, not laboratory observations or root cause' if 'primary_recall_record' not in missing else 'recall not verified without primary evidence','no root cause established']}


def main():
    parser = argparse.ArgumentParser(description='Evidence-first ranolazine investigation')
    parser.add_argument('command', choices=['sample','baseline','benchmark'])
    parser.add_argument('--state', help='Existing episode JSON (read only)')
    parser.add_argument('--dataset', help='Authorized measured JSON rows for benchmark')
    parser.add_argument('--materials', nargs='*')
    parser.add_argument('--unit')
    args = parser.parse_args()
    task = {'task_id':TASK_ID, 'reported_issue':'dissolution_specification_failure', 'recall_status':'unverified'}
    if args.command == 'baseline':
        result = baseline(task)
    elif args.command == 'benchmark':
        rows = json.loads(Path(args.dataset).read_text()) if args.dataset else []
        result = benchmark(rows, tuple(args.materials or ()), args.unit or '')
    else:
        result = investigate(Episode.load(args.state) if args.state else Episode(task))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
