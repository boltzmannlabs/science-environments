"""Run the frozen complete EvoEF1 panel; one local launch, no agent/model delegation."""
import pathlib,json,hashlib,sys,os,resource,subprocess,time,datetime,traceback
from decimal import Decimal
from evoef_io import protein_view,parse_total
W=pathlib.Path(__file__).resolve().parents[1];ROOT=W/'local_evoef';PLAN=ROOT/'PLAN.json'
plan=json.loads(PLAN.read_text());binary=pathlib.Path(plan['binary'])
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p,data):pathlib.Path(p).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
if sha(binary)!=plan['binary_sha256']:raise ValueError('Binary changed')
for job in plan['jobs']:
 root=pathlib.Path(job['working_directory'])
 if sha(root/'source_parent.pdb')!=job['source_sha256'] or sha(job['source_path'])!=job['source_sha256']:raise ValueError('Source changed')
 if sha(root/'parent.pdb')!=job['input_qa']['view_sha256'] or sha(root/'mutants.txt')!=job['mutant_file_sha256']:raise ValueError('Reviewed input changed')
 protein_view((root/'parent.pdb').read_text(),job['parent_sequence'])
if '--validate-only' in sys.argv:
 print(json.dumps({'parents':len(plan['jobs']),'variants':sum(len(j['variants']) for j in plan['jobs']),'status':'verified_read_only_no_science'}));sys.exit(0)
if sys.argv[1:]!=['--run']:raise ValueError('Use --validate-only or --run')
intent={'started_utc':now(),'plan_sha256':sha(PLAN),'runner_sha256':sha(__file__),'binary_sha256':sha(binary),'status':'local_scientific_execution_started','command':[sys.executable,*sys.argv]}
with (ROOT/'RUN_INTENT.json').open('x') as f:json.dump(intent,f,indent=2)
os.sched_setaffinity(0,plan['resource_controls']['CPU_affinity']);resource.setrlimit(resource.RLIMIT_AS,(plan['resource_controls']['address_space_limit_bytes'],)*2);os.environ['CUDA_VISIBLE_DEVICES']=''
started=time.monotonic();ledger={'started_utc':intent['started_utc'],'status':'running','native_commands_started':0,'native_commands_completed':0,'jobs':[],'device':'CPU','process_affinity':sorted(os.sched_getaffinity(0)),'max_address_space_bytes':resource.getrlimit(resource.RLIMIT_AS)[0]};save(ROOT/'RUN_STATUS.json',ledger)
try:
 for job in plan['jobs']:
  root=pathlib.Path(job['working_directory']);record={'local_job':job['local_job'],'parent':job['parent'],'status':'running','started_utc':now(),'commands':[],'predictions':[]};ledger['jobs'].append(record)
  # Native command records are flushed before execution. Commands are never replayed by this script.
  schedule=[('repair',[str(binary),'--command=RepairStructure','--pdb=parent.pdb','--num_of_runs=3']),('build',[str(binary),'--command=BuildMutant','--pdb=parent_Repair.pdb','--mutant_file=mutants.txt','--num_of_runs=10'])]
  for step,args in schedule:
   cmd={'step':step,'argv':args,'cwd':str(root),'started_utc':now(),'status':'started'};record['commands'].append(cmd);ledger['native_commands_started']+=1;save(ROOT/'RUN_STATUS.json',ledger)
   t=time.monotonic()
   with (root/(step+'.stdout.log')).open('wb') as out,(root/(step+'.stderr.log')).open('wb') as err:
    proc=subprocess.run(args,cwd=root,stdout=out,stderr=err,timeout=900,check=False)
   cmd.update(exit_code=proc.returncode,elapsed_seconds=time.monotonic()-t,finished_utc=now(),status='completed' if proc.returncode==0 else 'failed');save(ROOT/'RUN_STATUS.json',ledger)
   if proc.returncode!=0:raise RuntimeError('Native command failed: '+job['local_job']+'/'+step)
   ledger['native_commands_completed']+=1
   if step=='repair':
    _,qa=protein_view((root/'parent_Repair.pdb').read_text(),job['parent_sequence']);save(root/'repair_identity_QA.json',qa)
   else:
    for idx,v in enumerate(job['variants'],1):
     for suffix,seq in [('',v['sequence']),('_WT',job['parent_sequence'])]:
      model=root/f'parent_Repair_Model_{idx:04d}{suffix}.pdb';_,qa=protein_view(model.read_text(),seq);save(model.with_suffix('.identity_QA.json'),qa)
  for idx,variant in enumerate(job['variants'],1):
   energies={};paths={}
   for label,suffix in [('mutant',''),('paired_WT','_WT')]:
    model=root/f'parent_Repair_Model_{idx:04d}{suffix}.pdb';step=f'energy_{idx:04d}_{label}';args=[str(binary),'--command=ComputeStability','--pdb='+model.name]
    cmd={'step':step,'argv':args,'cwd':str(root),'input_sha256':sha(model),'started_utc':now(),'status':'started'};record['commands'].append(cmd);ledger['native_commands_started']+=1;save(ROOT/'RUN_STATUS.json',ledger);t=time.monotonic()
    stdout=root/(step+'.stdout.log');stderr=root/(step+'.stderr.log')
    with stdout.open('wb') as out,stderr.open('wb') as err:proc=subprocess.run(args,cwd=root,stdout=out,stderr=err,timeout=300,check=False)
    cmd.update(exit_code=proc.returncode,elapsed_seconds=time.monotonic()-t,finished_utc=now(),stdout_sha256=sha(stdout),stderr_sha256=sha(stderr),status='completed' if proc.returncode==0 else 'failed');save(ROOT/'RUN_STATUS.json',ledger)
    if proc.returncode!=0:raise RuntimeError('Native energy failed '+step)
    energies[label]=str(parse_total(stdout.read_text()));paths[label]=str(model.relative_to(W));ledger['native_commands_completed']+=1
   ddg=Decimal(energies['mutant'])-Decimal(energies['paired_WT'])
   prediction={'ids':variant['ids'],'sequence_sha256':variant['sequence_sha256'],'mutation':variant['mutation'],'common_WT':job['parent'],'native_energy_terms_kcal_mol':energies,'delta_delta_G_folding_kcal_mol':str(ddg),'delta_delta_G_unfolding_kcal_mol':str(-ddg),'model_paths':paths,'precision_note':'Native CLI totals serialized to 0.01 kcal/mol; subtraction uses exact decimal returned totals, not hidden full-precision energies.','status':'completed_native_pair_identity_verified'}
   record['predictions'].append(prediction);save(ROOT/'RUN_STATUS.json',ledger);print(json.dumps({'local_job':job['local_job'],**prediction}),flush=True)
  record.update(status='completed_artifact_verified',completed_utc=now());save(root/'RESULT.json',record);save(ROOT/'RUN_STATUS.json',ledger)
 ledger.update(status='completed_artifact_verified',completed_utc=now(),elapsed_seconds=time.monotonic()-started);save(ROOT/'RUN_STATUS.json',ledger)
 print(json.dumps({'status':ledger['status'],'native_commands_started':ledger['native_commands_started'],'native_commands_completed':ledger['native_commands_completed'],'unique_variant_predictions':sum(len(j['predictions']) for j in ledger['jobs'])}),flush=True)
except BaseException as exc:
 ledger.update(status='failed_preserved_no_automatic_retry',error=repr(exc),traceback=traceback.format_exc(),elapsed_seconds=time.monotonic()-started,failed_utc=now());save(ROOT/'RUN_STATUS.json',ledger);raise
