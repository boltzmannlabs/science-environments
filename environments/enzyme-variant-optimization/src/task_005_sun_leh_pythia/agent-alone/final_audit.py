"""Final read-only artifact/state-dict/coordinate audit; no model construction or inference."""
from pathlib import Path
from datetime import datetime,timezone
import csv,hashlib,json,os,sqlite3
import torch

ARM=Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    m=json.loads((ARM/'INPUT_MANIFEST.json').read_text())
    identities=json.loads((ARM/'results/model_identity.json').read_text())['models']
    state_checks=[]
    for rec,observed in zip(m['checkpoints'],identities):
        tensors=torch.load(rec['path'],map_location='cpu',weights_only=True)
        digest=hashlib.sha256()
        for key,value in sorted(tensors.items()):
            digest.update(key.encode())
            digest.update(value.detach().cpu().contiguous().numpy().tobytes())
        if digest.hexdigest()!=observed['loaded_state_digest_sha256']:
            raise ValueError('Loaded state does not match published checkpoint tensor bytes')
        if sum(v.numel() for v in tensors.values())!=observed['parameter_count']:
            raise ValueError('Parameter-count mismatch')
        state_checks.append({'model':observed['model'],'checkpoint_sha256':sha(rec['path']),
                             'tensor_digest':digest.hexdigest(),'matches_loaded_state':True,'parameters':observed['parameter_count']})
        del tensors
    source=(ARM/'sources/1NWW.pdb').read_text().splitlines()
    source_records={l[:16]+' '+l[17:] for l in source if l.startswith('ATOM')}
    coord_checks=[]
    for ctx in m['structure']['contexts']:
        lines=[l for l in Path(ctx['path']).read_text().splitlines() if l.startswith('ATOM')]
        if not all(l in source_records for l in lines):
            raise ValueError('Prepared atom changed beyond frozen altloc-field normalization')
        coord_checks.append({'context':ctx['id'],'ATOM_records':len(lines),'coordinate_and_identity_preservation':True,
                             'source_PDB_sha256':sha(ARM/'sources/1NWW.pdb'),'derived_PDB_sha256':sha(ctx['path'])})
    inventory=json.loads((ARM/'result_artifact_inventory.json').read_text())
    for rec in inventory:
        p=Path(rec['path'])
        if not p.exists() or p.stat().st_size!=rec['bytes'] or sha(p)!=rec['sha256']:
            raise ValueError('Result artifact changed: '+str(p))
    usage=json.loads((ARM/'usage.json').read_text())
    snap=usage['llm_usage']
    if snap['recursive_child_count']!=0 or snap['delegation_tool_calls']!=0 or not snap['blank_task_equals_primary']:
        raise ValueError('Native usage/delegation reconciliation failed')
    calls=snap['scientific_launch_call_evidence']
    if len(calls)!=4 or len(set(c['native_call_id'] for c in calls))!=4:
        raise ValueError('Expected four unique native launch calls (one gate block, original waiter, resume/import failure, full retry)')
    classifications=[]
    for call in calls:
        cmd=call['command']
        if 'RECOVERY_FROM_ATTEMPT=sun-leh-agent-alone-full-001' in cmd:
            phase='attempt002_full_inference_and_QA'
        elif 'RESUME_WAITING_ATTEMPT=sun-leh-agent-alone-full-001' in cmd:
            phase='attempt001_resume_wait_then_import_failure'
        elif call['background']:
            phase='pre_scientific_hash_gate_rejection'
        else:
            phase='attempt001_initial_wait_interrupted'
        classifications.append({**call,'phase':phase})
    db=Path(os.environ['SCI_HOME'])/'state.db'
    c=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True)
    native_receipts=[]
    for call in classifications:
        rows=c.execute('SELECT id,role,tool_call_id,tool_name,content,timestamp FROM messages WHERE session_id=? AND tool_call_id=? ORDER BY id',('RUN_0003',call['native_call_id'])).fetchall()
        native_receipts.append({'call':call,'native_result_messages':[{'message_id':r[0],'role':r[1],'call_id':r[2],
            'tool_name':r[3],'content':r[4],'timestamp':r[5]} for r in rows]})
    (ARM/'native_dispatch_audit.json').write_text(json.dumps(native_receipts,indent=2)+'\n')
    jobs=json.loads((ARM/'jobs.json').read_text())
    byphase={r['phase']:r for r in classifications}
    jobs['scientific_attempts'][0]['native_launch_call_id']=byphase['attempt001_initial_wait_interrupted']['native_call_id']
    jobs['scientific_attempts'][0]['native_resume_call_id']=byphase['attempt001_resume_wait_then_import_failure']['native_call_id']
    jobs['scientific_attempts'][1]['native_launch_call_id']=byphase['attempt002_full_inference_and_QA']['native_call_id']
    jobs['native_dispatch_reconciliation']={'unique_launch_calls':4,'pre_scientific_gate_rejections':1,
        'scientific_execution_attempts':2,'failed_import_attempts':1,'completed_full_scan_attempts':1,
        'pending_or_running':0,'actual_model_forward_passes':4,'remote_submissions':0,
        'pre_scientific_gate_rejection_call_id':byphase['pre_scientific_hash_gate_rejection']['native_call_id']}
    (ARM/'jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
    intervals=[]
    for job in jobs['scientific_attempts']:
        dt=lambda key:datetime.fromisoformat(job[key])
        intervals.append({'attempt_id':job['attempt_id'],'status':job['status'],
            'original_start_to_finish_envelope_seconds':(dt('finished_utc')-dt('started_utc')).total_seconds(),
            'recorded_final_process_wall_including_wait_seconds':job.get('wall_elapsed_including_wait_seconds'),
            'recorded_final_process_time_to_slot_seconds':job.get('lock_wait_seconds'),
            'interrupted_prior_process_actual_wall_seconds':None if job.get('interrupted_wait_launches') else 'not_applicable',
            'model_forward_passes':len(job['model_forward_passes']),
            'recorded_model_runtime_seconds':job.get('scientific_model_runtime_seconds'),
            'unreported_failed_attempt_runtime_note':'No model loaded/forwarded; failure was import-only' if job['status']=='failed' else None})
    usage['scientific_history_accounting']={'attempt_intervals':intervals,
        'cumulative_attempt_envelope_seconds':sum(x['original_start_to_finish_envelope_seconds'] for x in intervals),
        'first_attempt_start_to_success_finish_seconds':(datetime.fromisoformat(jobs['scientific_attempts'][-1]['finished_utc'])-datetime.fromisoformat(jobs['scientific_attempts'][0]['started_utc'])).total_seconds(),
        'envelope_semantics':'Includes interrupted wait, inter-attempt preparation/recovery and elapsed gaps; NOT all active model runtime',
        'actual_model_runtime_seconds':sum(float(v.get('scientific_model_runtime_seconds') or 0) for v in jobs['scientific_attempts']),
        'interrupted_process_usage':'Exact terminated-waiter CPU/RSS/wall telemetry unavailable; do not assign zero',
        'platform_scientific_billing':'not_applicable_local_CPU_no_remote_job',
        'native_dispatch_counts':jobs['native_dispatch_reconciliation']}
    (ARM/'usage.json').write_text(json.dumps(usage,indent=2)+'\n')
    result={'utc':datetime.now(timezone.utc).isoformat(),'all_passed':True,'new_model_inference_calls':0,
        'checkpoint_tensor_identity':state_checks,'prepared_coordinate_identity':coord_checks,
        'result_artifacts_hash_verified':len(inventory),'native_launch_call_classifications':[{k:r[k] for k in ['native_call_id','message_id','phase']} for r in classifications],
        'native_result_message_counts':[len(r['native_result_messages']) for r in native_receipts],
        'scientific_dispatch_counts':jobs['native_dispatch_reconciliation'],
        'boundary':'Completed supplied-native-reference method scan; exact Sun numerical reproduction remains unresolved'}
    (ARM/'final_artifact_QA.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'final_artifact_QA':'passed','result_artifacts':len(inventory),'state_dicts':len(state_checks),
                      'native_dispatch_counts':jobs['native_dispatch_reconciliation'],
                      'cumulative_scientific_envelope_seconds':usage['scientific_history_accounting']['first_attempt_start_to_success_finish_seconds']}))

if __name__=='__main__':
    main()
