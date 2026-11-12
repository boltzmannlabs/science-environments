"""Verify completed campaign artifacts and save real test outputs without overwriting historical validation.json."""
import pathlib,json,subprocess,sys,os,runpy,builtins,contextlib,hashlib
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'benchmark/011_Campaign-reproduction/Run-3_2026-11-11';OUT.mkdir(parents=True,exist_ok=True)
realopen=builtins.open
historical=ROOT/'tests/validation.json';before=historical.read_bytes()
def redirected_open(file,mode='r',*args,**kwargs):
 try:matches=pathlib.Path(file).resolve()==historical.resolve()
 except (TypeError,ValueError):matches=False
 if matches and any(c in mode for c in 'wax+'):file=OUT/'spec_validation.json'
 return realopen(file,mode,*args,**kwargs)
code=0
with realopen(OUT/'spec_validation.log','w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log),patch('builtins.open',redirected_open):
 try:runpy.run_path(str(ROOT/'tests/validate_spec.py'),run_name='__main__')
 except SystemExit as e:code=e.code
assert historical.read_bytes()==before,'Historical validation artifact was changed'
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=180)
(OUT/'unittest.log').write_text(p.stdout+p.stderr)
record={'spec_exit_code':code,'spec':json.loads((OUT/'spec_validation.json').read_text()),'unittest_exit_code':p.returncode,'unittest_command':[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],'historical_validation_preserved':True,'scope':'Software/artifact consistency only; not biological validation.'}
(OUT/'validation_summary.json').write_text(json.dumps(record,indent=2)+'\n')
print((OUT/'spec_validation.log').read_text());print(p.stdout+p.stderr)
# Additional immutable backend and orchestration provenance.
files=[ROOT/'runtime/immune_scan.py',ROOT/'runtime/rank_by_requirements.py',ROOT/'runtime/explore_design.py',ROOT/'config/thresholds.v1.0.frozen.json',ROOT/'runtime/run_campaign_20261111.py',ROOT/'runtime/benchmark_campaign_20261111.py',ROOT/'runtime/finalize_campaign_20261111.py',ROOT/'runtime/report_campaign_20261111.py',ROOT/'tests/test_campaign_20261111.py',pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/RN.Ai-predict/RN.Ai-predict.model.keras'),pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/RNAiSpline/checkpoints/best_model.pth'),pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/.cache/seed7_counts_gencode_v50.npy')]
backend=[]
for f in files:
 if f.is_file():backend.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
versions={}
for tool in ('RNAfold','RNAduplex','bowtie2'):
 q=subprocess.run(['/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/envs/biotools/bin/'+tool,'--version'],capture_output=True,text=True,timeout=30)
 versions[tool]={'returncode':q.returncode,'output':q.stdout+q.stderr}
backend_record={'files':backend,'versions':versions,'python':sys.version,'local_backend_root':'/home/boltzmann13/IMRAN/OCT26/siRNA-Bench','OligoFormer_checkpoint_hashes':'Per-fresh-generation manifest.json; historical-reuse manifests explicitly identify source pools.','script_revision_note':'Final script hashes include postprocessing masks for the inherited blended rank field and context-manager cleanup; no source model/refit or biological gate change. Per-task earlier runner hashes are execution-time snapshots, not hashes of every later cosmetic script revision.','raw_native_artifact_note':'Disposable generated runtime trees were removed after preserving native tabular output and generator manifests; no third-party code/weights redistributed.'}
(OUT/'backend_provenance.json').write_text(json.dumps(backend_record,indent=2)+'\n')
if code or p.returncode:sys.exit(1)
