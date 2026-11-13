"""Full, non-pilot Pythia inference using unchanged pinned upstream modules."""
from pathlib import Path
from datetime import datetime, timezone
import csv, fcntl, hashlib, json, os, resource, sys, time, traceback

ARM=Path(__file__).resolve().parent

def now():
    return datetime.now(timezone.utc).isoformat()

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def dump(p,v):
    p.write_text(json.dumps(v,indent=2)+'\n')

def append(p,v):
    with p.open('a') as f:
        f.write(json.dumps({'utc':now(),**v})+'\n')

def main():
    started=time.perf_counter()
    manifest=json.loads((ARM/'INPUT_MANIFEST.json').read_text())
    plan=json.loads((ARM/'RUN_PLAN.json').read_text())
    freeze=json.loads((ARM/'EXECUTION_FREEZE.json').read_text())
    for rec in freeze['files']+manifest['immutable_files']+manifest['checkpoints']+manifest['structure']['contexts']:
        if sha(rec['path'])!=rec['sha256']:
            raise RuntimeError('Frozen byte mismatch '+rec['path'])
    if os.environ.get('CUDA_VISIBLE_DEVICES')!='':
        raise RuntimeError('CUDA_VISIBLE_DEVICES must be explicitly empty')
    for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        if os.environ.get(key)!='4':
            raise RuntimeError('Required max4 CPU-thread environment: '+key)
    resource.setrlimit(resource.RLIMIT_AS,(plan['resource_limits']['RLIMIT_AS_bytes'],)*2)
    jobs=json.loads((ARM/'jobs.json').read_text())
    out=ARM/'results'
    history=jobs['scientific_attempts']
    last=history[-1] if history else None
    retry_failed_import=bool(last and last['status']=='failed' and not last['model_forward_passes']
        and last.get('error')=="ModuleNotFoundError(\"No module named 'pkg_resources'\")"
        and not Path('/proc',str(last['pid'])).exists()
        and os.environ.get('RECOVERY_FROM_ATTEMPT')==last['attempt_id'])
    if history and not retry_failed_import:
        old=last
        if (old['status']!='waiting_for_CPU_model_slot'
                or old['model_forward_passes'] or Path('/proc',str(old['pid'])).exists()
                or (out/'model_identity.json').exists()
                or os.environ.get('RESUME_WAITING_ATTEMPT')!=old['attempt_id']):
            raise RuntimeError('Existing scientific attempt is not a verified dead pre-inference waiter; do not duplicate')
        job=old
        job.setdefault('interrupted_wait_launches',[]).append({'pid':job['pid'],
            'original_started_utc':job['started_utc'],'absence_verified_utc':now(),
            'forward_passes':0,'termination':'native foreground420s timeout; PID absence confirmed; exact termination timestamp unavailable'})
        job.update(pid=os.getpid(),resumed_utc=now(),resume_command=[sys.executable,str(Path(__file__).resolve())],
                   resumed_execution_freeze_sha256=sha(ARM/'EXECUTION_FREEZE.json'))
        out.mkdir(exist_ok=True)
    else:
        out.mkdir()
        job={'attempt_id':f'sun-leh-agent-alone-full-{len(history)+1:03d}','location':'local_CPU','status':'waiting_for_CPU_model_slot',
         'native_session_id':os.environ.get('SCI_SESSION_ID'),'native_launch_call_id':None,'pid':os.getpid(),
         'command':[sys.executable,str(Path(__file__).resolve())], 'started_utc':now(),
         'working_directory':str(ARM),'execution_freeze_sha256':sha(ARM/'EXECUTION_FREEZE.json'),
         'GPU_used':False,'threads':4,'address_space_limit_bytes':resource.getrlimit(resource.RLIMIT_AS)[0],
             'model_forward_passes':[],'remote_job_id':None,'platform_billing':'not_applicable_local_CPU'}
        jobs['scientific_attempts'].append(job)
    dump(ARM/'jobs.json',jobs)
    state=json.loads((ARM/'stage_evidence.json').read_text())
    state.update(status=job['status'],full_scan=job['status'],attempt_id=job['attempt_id'])
    dump(ARM/'stage_evidence.json',state)
    try:
        # The only shared write is creating/opening the explicitly required coordination lock;
        # no contents are written to it and all scientific artifacts remain under ARM.
        with open(plan['resource_limits']['lock'],'a+') as lock:
            print('Waiting for the shared single-CPU-model-process slot.',flush=True)
            fcntl.flock(lock,fcntl.LOCK_EX)
            acquired=time.perf_counter()
            job.update(status='running_full_inference',slot_acquired_utc=now(),lock_wait_seconds=acquired-started,
                       end_to_end_seconds_to_slot_including_interruption=(datetime.now(timezone.utc)-datetime.fromisoformat(job['started_utc'])).total_seconds())
            dump(ARM/'jobs.json',jobs)
            state.update(status='running_full_inference',full_scan='running')
            dump(ARM/'stage_evidence.json',state)
            print('Slot acquired: beginning complete frozen model inference.',flush=True)
            sys.path.insert(0,str(ARM/'vendor'))
            import numpy as np
            import torch
            import torch.nn.functional as F
            from pythia.masked_ddg_scan import get_torch_model
            from pythia.pdb_utils import read_pdb_to_protbb,get_neighbor
            from Bio.PDB.Polypeptide import index_to_one
            torch.set_num_threads(4)
            torch.set_num_interop_threads(1)
            torch.manual_seed(0)
            np.random.seed(0)
            torch.use_deterministic_algorithms(True)
            if torch.get_num_threads()!=4:
                raise RuntimeError('Unexpected torch thread count')
            models={}
            identities=[]
            for rec in manifest['checkpoints']:
                label='C' if rec['name']=='pythia-c.pt' else 'P'
                model=get_torch_model(rec['path'],device='cpu')
                models[label]=model
                state_digest=hashlib.sha256()
                for key,val in sorted(model.state_dict().items()):
                    state_digest.update(key.encode())
                    state_digest.update(val.detach().cpu().contiguous().numpy().tobytes())
                identities.append({'model':label,'checkpoint_sha256':rec['sha256'],
                    'loaded_state_digest_sha256':state_digest.hexdigest(),
                    'parameter_count':sum(v.numel() for v in model.parameters()),
                    'training_mode':model.training,'parameter_device':str(next(model.parameters()).device),
                    'parameter_dtype':str(next(model.parameters()).dtype),'strict_state_dict_load':True})
            dump(out/'model_identity.json',{'models':identities,'torch':torch.__version__,
                'model_module':str(sys.modules['pythia.model'].__file__),
                'feature_module':str(sys.modules['pythia.pdb_utils'].__file__),
                'scoring_module':str(sys.modules['pythia.masked_ddg_scan'].__file__)})
            all_rows=[]
            model_runtime=0.0
            for ctx in manifest['structure']['contexts']:
                dest=out/ctx['id']
                dest.mkdir()
                bb=read_pdb_to_protbb(ctx['path'])
                node,edge,target=get_neighbor(bb,neighbor=32,noise_level=0.0)
                wt_indices=bb.seq.squeeze(-1).long().numpy()
                arrays={'wt_indices':wt_indices,'node':node.numpy(),'edge':edge.numpy()}
                energies={}
                for label,model in models.items():
                    t=time.perf_counter()
                    with torch.no_grad():
                        logits,_=model(node.to('cpu'),edge.to('cpu'))
                        prob=F.softmax(logits,dim=-1).detach().cpu().numpy()
                    duration=time.perf_counter()-t
                    model_runtime+=duration
                    energy=-np.log(prob/prob[np.arange(len(wt_indices)),wt_indices,None])
                    energies[label]=energy
                    arrays['logits_'+label]=logits.detach().cpu().numpy()
                    arrays['probabilities_'+label]=prob
                    arrays['negative_logratio_'+label]=energy
                    job['model_forward_passes'].append({'context':ctx['id'],'model':label,
                        'all_residues':ctx['residues'],'logits_shape':list(logits.shape),
                        'runtime_seconds':duration,'completed_utc':now()})
                    dump(ARM/'jobs.json',jobs)
                    print(f"{ctx['id']} model {label}: {ctx['residues']} complete positions, {duration:.6f} seconds",flush=True)
                summed=np.zeros((len(wt_indices),21),dtype=np.float64)
                for label in ['C','P']:
                    summed+=energies[label]
                arrays['score_sum']=summed
                arrays['score_mean']=summed/2
                np.savez_compressed(dest/'raw_inference.npz',**arrays)
                rows=[]
                with (dest/'upstream_equivalent_pred_mask.txt').open('w') as raw_file:
                    for i,wt_idx in enumerate(wt_indices):
                        chain=ctx['chains'][int(bb.chain_num[i].item())]
                        pos=int(bb.resseq[i].item())
                        wt=index_to_one(int(wt_idx))
                        for j in range(20):
                            mut=index_to_one(j)
                            raw_file.write(f'{wt}{i+1}{mut} {summed[i,j]}\n')
                            row={'context':ctx['id'],'model_index_1based':i+1,'chain':chain,'position':pos,
                                 'insertion_code':'','wildtype':wt,'mutant':mut,'mutation':f'{wt}{pos}{mut}',
                                 'score_C':float(energies['C'][i,j]),'score_P':float(energies['P'][i,j]),
                                 'log_ratio_C':-float(energies['C'][i,j]),'log_ratio_P':-float(energies['P'][i,j]),
                                 'score_sum':float(summed[i,j]),'score_mean':float(summed[i,j]/2)}
                            if mut!=wt:
                                rows.append(row)
                with (dest/'all_scores.csv').open('w') as f:
                    w=csv.DictWriter(f,list(rows[0]));w.writeheader();w.writerows(rows)
                all_rows.extend(rows)
                dump(dest/'coverage_producer.json',{'positions':ctx['residues'],'nonself_rows':len(rows),
                    'expected_nonself_rows':ctx['eligible_nonself_substitutions'],'no_crops':True,
                    'scores_units':'dimensionless raw model negative log probability ratios'})
            with (out/'all_contexts_all_scores.csv').open('w') as f:
                w=csv.DictWriter(f,list(all_rows[0]));w.writeheader();w.writerows(all_rows)
            job.update(status='completed_inference_pending_independent_QA',finished_utc=now(),
                       scientific_model_runtime_seconds=model_runtime,
                       slot_held_seconds=time.perf_counter()-acquired,
                       wall_elapsed_including_wait_seconds=time.perf_counter()-started,
                       process_CPU_user_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,
                       process_CPU_system_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,
                       maximum_RSS_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       exit_status=0)
            dump(ARM/'jobs.json',jobs)
            usage=json.loads((ARM/'usage.json').read_text())
            usage.update(scientific_model_runtime_seconds=model_runtime,
                         scientific_process_wall_seconds_including_wait=job['wall_elapsed_including_wait_seconds'],
                         CPU_slot_wait_seconds=job['lock_wait_seconds'],local_scientific_attempts=len(jobs['scientific_attempts']),
                         local_model_forward_passes=len(job['model_forward_passes']))
            dump(ARM/'usage.json',usage)
            state.update(status='inference_completed_pending_independent_QA',full_scan='completed_actual_model_inference',
                         local_scientific_attempts=len(jobs['scientific_attempts']),model_forward_passes=len(job['model_forward_passes']),
                         nonself_score_rows=len(all_rows),scientific_model_runtime_seconds=model_runtime)
            dump(ARM/'stage_evidence.json',state)
            print(json.dumps({'inference_completed':True,'local_scientific_attempts':len(jobs['scientific_attempts']),
                              'model_forward_passes':len(job['model_forward_passes']),
                              'nonself_score_rows':len(all_rows),'model_runtime_seconds':model_runtime}),flush=True)
    except BaseException as exc:
        job.update(status='failed',finished_utc=now(),error=repr(exc),traceback=traceback.format_exc(),
                   wall_elapsed_including_wait_seconds=time.perf_counter()-started,exit_status=1)
        dump(ARM/'jobs.json',jobs)
        append(ARM/'errors.jsonl',{'stage':'scientific_inference','attempt_id':job['attempt_id'],
                                 'error':repr(exc),'traceback':traceback.format_exc()})
        state.update(status='failed',full_scan='failed',error=repr(exc))
        dump(ARM/'stage_evidence.json',state)
        raise

if __name__=='__main__':
    main()
