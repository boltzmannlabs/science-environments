"""Six requested investigation roles backed by local bounded specialist contracts.

SCI delegation is disabled. These roles are orchestrated functions, not six
independent AI processes, and they make no unsupported scientific claims.
"""
import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from agents.evidence_auditor import AuditRequest, audit
from agents.formulation_design import DesignRequest, propose
from agents.compatibility_stability import CompatibilityRequest, assess
from agents.property_prediction import PredictionRequest, predict
from environment.state import Episode
from evaluation.verifier import verify
from run import investigate, TASK_ID

CASE = 'D-0092-2024'


@dataclass(frozen=True)
class InvestigationRequest:
    episode_path: Path
    raw_dir: Path
    demo_path: Path | None = None

    def __post_init__(self):
        if not isinstance(self.episode_path,Path) or not isinstance(self.raw_dir,Path):
            raise TypeError('episode and raw paths required')


def coordinate(request: InvestigationRequest) -> dict:
    if not isinstance(request,InvestigationRequest):
        raise TypeError('InvestigationRequest required')
    state = Episode.load(request.episode_path)
    if state.task.get('task_id') != TASK_ID or state.task.get('case_id') != CASE:
        raise ValueError('only the selected Glenmark 500 mg recall case is in scope')
    mapping = {'FDA-RES-'+CASE:'fda-res-D-0092-2024.json',
        'FDA-SPL-0cf58732-c242-49b0-8e3f-248778b4458d':'fda-spl-glenmark.json',
        'FDA-DAILYMED-0cf58732-c242-49b0-8e3f-248778b4458d':'dailymed-glenmark.xml'}
    hashes = {}
    for sid, filename in mapping.items():
        if sid not in state.sources or not (request.raw_dir/filename).is_file():
            raise ValueError('missing primary public source snapshot: '+sid)
        match = hashlib.sha256((request.raw_dir/filename).read_bytes()).hexdigest() == state.sources[sid].get('sha256')
        hashes[sid] = match
        if not match:
            raise ValueError('source hash mismatch: '+sid)
    review = investigate(state)
    audit_result = audit(AuditRequest(tuple(state.evidence),state.sources))
    missing = review['unknowns']
    if state.candidates or state.predictions or state.experiments:
        raise ValueError('unexpected candidate, predictions or experiments in selected public-only case')
    design = propose(DesignRequest(state.materials,{}))
    compatibility = assess(CompatibilityRequest(('ranolazine',)))
    prediction = predict(PredictionRequest(TASK_ID,'unassigned',{}))
    demo = None
    if request.demo_path and request.demo_path.exists():
        obj = json.loads(request.demo_path.read_text())
        if obj.get('status') != 'software_demonstration_only' or obj.get('product') != 'not_ranolazine':
            raise ValueError('untrusted or mislabeled model demonstration')
        demo = {'version':obj['version'],'purpose':'OpenPKFlow software smoke test only; no recalled-lot fitting'}
    roles = {
        'Recall Research Agent':{'status':'FDA_recall_listed','source_ids':['FDA-RES-'+CASE],
            'finding':'Glenmark 500 mg lot and reported dissolution issue documented; specific causal factor unknown'},
        'Evidence Retrieval Agent':{'status':'public_sources_verified_gaps_remain', 'source_hashes_match':hashes,
            'unknowns':missing,'source_ids':list(state.sources)},
        'Formulation Analysis Agent':{'status':design.status,'compatibility':compatibility.status,
            'conclusion':'qualitative labeling only; no batch-specific ingredient fractions or process setpoints'},
        'Dissolution Modeling Agent':{'status':prediction.status,'openpkflow':demo,
            'osp_particle_dissolution':'not_run_missing_particle_distribution_solubility_and_case_profile',
            'prediction':'not_available','uncertainty':'not_calibrated'},
        'Experimental Design and Bayesian Optimization Agent':{'status':'not_run_missing_verified_objective_bounds_and_measurements',
            'next_step':'request controlled dissolution SOP, failing/passing lot results and batch/process records',
            'physical_experiments':'approval_required'},
        'Independent Validation Agent':{'status':'accept_public_provenance_only' if audit_result.decision == 'accept' and not verify(state) else 'revise',
            'auditor':audit_result.decision,'verifier_findings':verify(state),'limitations':['FDA recall listing does not identify root cause','no optimized formulation can be validated']},
    }
    return {'task_id':TASK_ID,'case_id':CASE,'status':'insufficient_data_for_optimization',
        'roles':roles,'reported_facts':review['verified_facts'], 'hypotheses':[],
        'candidate_compositions':[],'predicted_dissolution_profiles':[],
        'objective_scores':None,'validation':'not_established',
        'source_type':'public FDA/NLM labeling and recall; NOT lot-level experimental dataset'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--episode',type=Path,required=True)
    p.add_argument('--raw-dir',type=Path,required=True)
    p.add_argument('--demo',type=Path)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    report=coordinate(InvestigationRequest(args.episode,args.raw_dir,args.demo))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'case_id':report['case_id'],
                      'roles':list(report['roles']),'out':str(args.out)}))


if __name__=='__main__':main()
