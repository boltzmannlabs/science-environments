"""Full, checkpointed masked-marginal inference using upstream fair-esm.

This is a scientific adapter, not an agent/runtime or a new model implementation.
No sequence truncation, down-sized checkpoint, or sampled substitution subset.
"""
import argparse
import csv
import datetime
import fcntl
import hashlib
import json
import math
import os
import pathlib
import resource
import sys
import time
import traceback

ARM = pathlib.Path(__file__).resolve().parents[1]
AA = 'ACDEFGHIKLMNPQRSTVWY'


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda: f.read(8*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, obj):
    path = pathlib.Path(path)
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False)+'\n')
    os.replace(temp, path)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def scores_from_logits(values, wt_index):
    check(all(math.isfinite(x) for x in values), 'Nonfinite raw logits')
    high = max(values)
    log_z = high + math.log(sum(math.exp(v-high) for v in values))
    lp = [v-log_z for v in values]
    return lp, [lp[wt_index]-v for v in lp]


def export_tables(out, name, seq, alphabet_tokens):
    records = [json.loads(line) for line in (out/'raw_masked_logits.jsonl').read_text().splitlines()]
    check([r['position'] for r in records] == list(range(1,len(seq)+1)), 'Raw position grid incomplete/duplicated')
    token_ids = {aa:alphabet_tokens.index(aa) for aa in AA}
    rows = []
    for record in records:
        pos = record['position']
        wt = seq[pos-1]
        check(record['wild_type']==wt, 'Raw WT mismatch')
        lp, scores = scores_from_logits(record['logits'], token_ids[wt])
        for mutant in AA:
            token = token_ids[mutant]
            rows.append({'background':name,'position':pos,'wild_type':wt,'mutant':mutant,'mutation':f'{wt}{pos}{mutant}','identity_control':mutant==wt,'wt_masked_log_probability':lp[token_ids[wt]],'mutant_masked_log_probability':lp[token],'negative_log_likelihood_ratio':scores[token],'mutant_minus_wt_logit':-scores[token],'below_minus_1_5':scores[token] < -1.5,'prediction_not_activity_measurement':True})
    fields = list(rows[0])
    substitutions = [r for r in rows if not r['identity_control']]
    ranked = sorted(substitutions,key=lambda r:(r['negative_log_likelihood_ratio'],r['position'],r['mutant']))
    best = [min((r for r in substitutions if r['position']==pos),key=lambda r:(r['negative_log_likelihood_ratio'],r['mutant'])) for pos in range(1,len(seq)+1)]
    best.sort(key=lambda r:(r['negative_log_likelihood_ratio'],r['position']))
    tables = {'all_scores_including_identity.csv':rows,'all_substitutions.csv':substitutions,'ranked_substitutions.csv':ranked,'thresholded_substitutions.csv':[r for r in ranked if r['below_minus_1_5']],'best_per_position.csv':best,'thresholded_best_per_position.csv':[r for r in best if r['below_minus_1_5']]}
    for filename, table in tables.items():
        with (out/filename).open('w',newline='') as f:
            writer = csv.DictWriter(f,fieldnames=fields)
            writer.writeheader()
            writer.writerows(table)
    return {'positions':len(records),'nonidentity_substitutions':len(substitutions),'identity_controls':len(seq),'thresholded_substitutions':len(tables['thresholded_substitutions.csv']),'thresholded_best_positions':len(tables['thresholded_best_per_position.csv']),'tables':{fn:{'rows':len(table),'sha256':sha(out/fn)} for fn,table in tables.items()}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    manifest = json.loads((ARM/'INPUT_MANIFEST.json').read_text())
    plan = json.loads((ARM/'RUN_PLAN.json').read_text())
    check(plan['status']=='frozen_executable_independent_ESM_stages', 'Plan is not frozen')
    check(manifest['esm2']['runner_sha256']==sha(__file__), 'Runner changed after freeze')
    checkpoint = ARM/manifest['esm2']['checkpoint']['path']
    check(sha(checkpoint)==manifest['esm2']['checkpoint']['sha256'], 'Checkpoint digest mismatch')
    for record in manifest['sequences'].values():
        check(sha(record['fasta'])==record['fasta_sha256'], 'FASTA digest mismatch')
    run_dir = ARM/'runs'/args.run_id
    check(not run_dir.exists(), 'Run ID already exists; do not duplicate/relaunch an unknown job')
    run_dir.mkdir(parents=True)
    started_wall = time.monotonic()
    job = {'run_id':args.run_id,'pid':os.getpid(),'execution':'local_CPU_full_scientific_inference','command':sys.argv,'started_utc':utc(),'status':'waiting_CPU_model_slot','input_manifest_sha256':sha(ARM/'INPUT_MANIFEST.json'),'run_plan_sha256':sha(ARM/'RUN_PLAN.json'),'model_runtime_seconds':0.0,'cases':{},'remote_document_id':None,'platform_billing':'not_applicable','delegations':0}
    save(run_dir/'job.json',job)
    lock_path = pathlib.Path(plan['resources']['lock'])
    # Creation/use of this lock is explicitly required by ENVIRONMENT_SPEC; no scientific data is written to shared_sources.
    with lock_path.open('a+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        slot_time = time.monotonic()
        job.update(status='loading_model',lock_acquired_utc=utc(),lock_wait_seconds=slot_time-started_wall)
        save(run_dir/'job.json',job)
        resource.setrlimit(resource.RLIMIT_AS,(12*1024**3,12*1024**3))
        os.environ['CUDA_VISIBLE_DEVICES']=''
        for name in ('OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            os.environ[name]='4'
        import torch
        import esm
        import importlib.metadata
        torch.set_num_threads(4)
        torch.set_num_interop_threads(1)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        check(torch.version.cuda is None,'CPU-only torch expected')
        load_start = time.monotonic()
        model, alphabet = esm.pretrained.load_model_and_alphabet_local(str(checkpoint))
        model = model.eval().cpu().float()
        check((model.num_layers,model.embed_dim,model.attention_heads)==(33,1280,20),'Unexpected ESM-2 architecture')
        converter = alphabet.get_batch_converter()
        tokens_vocab = list(alphabet.all_toks)
        job['model_identity'] = {'name':'esm2_t33_650M_UR50D','parameters':sum(p.numel() for p in model.parameters()),'layers':model.num_layers,'embed_dim':model.embed_dim,'attention_heads':model.attention_heads,'parameter_dtype':str(next(model.parameters()).dtype),'device':str(next(model.parameters()).device),'torch':torch.__version__,'fair_esm':importlib.metadata.version('fair-esm'),'alphabet':tokens_vocab,'torch_threads':torch.get_num_threads(),'interop_threads':torch.get_num_interop_threads(),'address_space_soft_hard_bytes':list(resource.getrlimit(resource.RLIMIT_AS))}
        job['model_load_seconds']=time.monotonic()-load_start
        save(run_dir/'job.json',job)
        with torch.inference_mode():
            for name in ['cellulase_M2','beta_glucanase_M5']:
                seq = manifest['sequences'][name]['sequence']
                out = run_dir/name
                out.mkdir()
                _,_,tokens = converter([(name,seq)])
                check(tokens.shape==(1,len(seq)+2),'Input truncated or unexpected special-token length')
                check([alphabet.get_tok(int(t)) for t in tokens[0,1:-1]]==list(seq),'Tokenizer changed sequence')
                case_start = time.monotonic()
                case = {'status':'running','sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),'positions_expected':len(seq),'substitutions_expected':len(seq)*19,'positions_completed':0,'started_utc':utc()}
                job['cases'][name]=case
                job['status']='running_full_inference'
                save(run_dir/'job.json',job)
                with (out/'raw_masked_logits.jsonl').open('x') as raw:
                    for pos,wt in enumerate(seq,1):
                        masked = tokens.clone()
                        masked[0,pos]=alphabet.mask_idx
                        check(int((masked==alphabet.mask_idx).sum())==1,'Not exactly one masked position')
                        begin = time.monotonic()
                        result = model(masked,repr_layers=[],return_contacts=False)
                        logits = result['logits'][0,pos].detach().cpu().tolist()
                        elapsed = time.monotonic()-begin
                        check(len(logits)==len(tokens_vocab) and all(math.isfinite(v) for v in logits),'Invalid logits')
                        raw.write(json.dumps({'run_id':args.run_id,'background':name,'position':pos,'wild_type':wt,'sequence_sha256':case['sequence_sha256'],'input_tokens':int(tokens.shape[1]),'mask_count':1,'logits':logits,'forward_seconds':elapsed},allow_nan=False)+'\n')
                        raw.flush()
                        os.fsync(raw.fileno())
                        job['model_runtime_seconds']+=elapsed
                        case['positions_completed']=pos
                        case['elapsed_seconds']=time.monotonic()-case_start
                        job['max_rss_KiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                        if pos%10==0 or pos==len(seq):
                            save(run_dir/'job.json',job)
                            print(json.dumps({'utc':utc(),'background':name,'positions_completed':pos,'positions_expected':len(seq),'inference_seconds':job['model_runtime_seconds'],'max_rss_KiB':job['max_rss_KiB']}),flush=True)
                        del result,masked
                case.update(status='completed',completed_utc=utc(),raw_logits_sha256=sha(out/'raw_masked_logits.jsonl'),coverage=export_tables(out,name,seq,tokens_vocab))
                save(run_dir/'job.json',job)
        job.update(status='completed_full_ESM_inference',completed_utc=utc(),elapsed_including_lock_seconds=time.monotonic()-started_wall,model_slot_seconds=time.monotonic()-slot_time,process_cpu_user_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_utime,process_cpu_system_seconds=resource.getrusage(resource.RUSAGE_SELF).ru_stime,max_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        save(run_dir/'job.json',job)
        print(json.dumps(job,indent=2),flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as exc:
        trace = traceback.format_exc()
        print(trace,file=sys.stderr,flush=True)
        # Preserve any model/position progress; a failed producer is not successful science.
        run_id = sys.argv[sys.argv.index('--run-id')+1] if '--run-id' in sys.argv else 'unknown'
        target = ARM/'runs'/run_id/'job.json'
        if target.exists():
            job = json.loads(target.read_text())
            job.update(status='failed',failed_utc=utc(),error=repr(exc),traceback=trace)
            save(target,job)
        with (ARM/'errors.jsonl').open('a') as f:
            f.write(json.dumps({'utc':utc(),'category':'scientific_adapter_failure','run_id':run_id,'error':repr(exc),'traceback':trace})+'\n')
        raise
