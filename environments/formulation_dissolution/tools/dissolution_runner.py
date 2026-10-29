"""Persisted dissolution run controller; fixture jobs never produce measured evidence."""
import json
from pathlib import Path
from uuid import uuid4
from tools.dissolution_analysis import analyze

MODES=('analyze_history','predict','replay','laboratory')


def submit(mode, store, *, rows=None, plan=None, authorization=None, backend=None, dry_run=False):
    """Dispatch only documented local modes; never infer approval from a CLI token."""
    if mode not in MODES: raise ValueError('unknown mode')
    if mode=='analyze_history': return {'status':'success','mode':mode,'evidence_label':'derived','result':analyze(rows or [])}
    if mode=='predict': return {'status':'insufficient_data','mode':mode,'reason':'no validated ranolazine commercial tablet predictor configured'}
    if mode=='replay': return {'status':'tool_unavailable','mode':mode,'reason':'requires an evaluator-controlled historical pool'}
    if not plan or not plan.get('method_id') or not plan.get('sample_ids'):
        return {'status':'insufficient_data','mode':mode,'reason':'method_id and sample_ids required'}
    if dry_run: return {'status':'dry_run','mode':mode,'intended_backend':backend,'cost':'unknown','submitted':False}
    if not authorization: return {'status':'approval_required','mode':mode}
    # Approval must exist in a separately provisioned and signed registry; string alone is never enough.
    approvals=Path(store)/'approvals.json'
    if not approvals.exists(): return {'status':'approval_required','mode':mode,'reason':'no approval registry'}
    allowed=json.loads(approvals.read_text()).get(authorization)
    if not allowed or allowed.get('status')!='approved' or allowed.get('plan_id')!=plan.get('plan_id') or not allowed.get('issuer'):
        return {'status':'approval_required','mode':mode,'reason':'approval record does not authorize this plan'}
    if backend!='fixture': return {'status':'tool_unavailable','mode':mode,'reason':'no verified laboratory adapter configured'}
    if not plan.get('idempotency_key'): return {'status':'insufficient_data','reason':'idempotency_key required'}
    root=Path(store)/'runs';root.mkdir(parents=True,exist_ok=True)
    for file in root.glob('*.json'):
        old=json.loads(file.read_text())
        if old.get('idempotency_key')==plan['idempotency_key']:
            return old
    rid=str(uuid4())
    run={'run_id':rid,'mode':mode,'backend':'fixture','status':'submitted','job_id':'fixture-'+rid,
         'authorization_record':authorization,'plan_id':plan['plan_id'],'method_id':plan['method_id'],
         'sample_ids':plan['sample_ids'],'idempotency_key':plan['idempotency_key'],
         'evidence_label':None,'fixture_only':True}
    (root/(rid+'.json')).write_text(json.dumps(run,indent=2))
    return run


def poll(store,run_id):
    """Read an existing run without manufacturing completion."""
    file=Path(store)/'runs'/(run_id+'.json')
    return json.loads(file.read_text()) if file.is_file() else {'status':'not_found','run_id':run_id}


def ingest(store,run_id,artifact=None):
    """Never turn fixture or unauthenticated results into measured observations."""
    run=poll(store,run_id)
    if run.get('status')=='not_found': return run
    if run.get('fixture_only'): return {'status':'not_evaluated','run_id':run_id,'reason':'fixture incapable of producing measured evidence'}
    return {'status':'tool_unavailable','run_id':run_id,'reason':'validated result ingestion backend not configured'}
