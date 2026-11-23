"""Run real package/artifact tests, preserve old validation outputs, and hash immutable sweep artifacts."""
import pathlib,json,sys,subprocess,os,runpy,builtins,contextlib,hashlib,csv,re
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'benchmark/012_Config-sweep/Run-4_2026-11-16';RUN='Run-4_2026-11-16'
realopen=builtins.open;old=ROOT/'tests/validation.json';before=old.read_bytes()
def opener(file,mode='r',*args,**kwargs):
 try:matched=pathlib.Path(file).resolve()==old.resolve()
 except (TypeError,ValueError):matched=False
 if matched and any(c in mode for c in 'wax+'):file=OUT/'spec_validation.json'
 return realopen(file,mode,*args,**kwargs)
exitcode=0
with realopen(OUT/'spec_validation.log','w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log),patch('builtins.open',opener):
 try:runpy.run_path(str(ROOT/'tests/validate_spec.py'),run_name='__main__')
 except SystemExit as e:exitcode=e.code
assert old.read_bytes()==before
p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=ROOT,capture_output=True,text=True,timeout=180,env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'})
(OUT/'unittest.log').write_text(p.stdout+p.stderr)
# Check all new relative prose links, including config and result indexes.
paths=[ROOT/'config/README.md',OUT.parent/'README.md',OUT.parent/'BENCHMARK_RUNS.md']+list((ROOT/'benchmark').glob('*/'+RUN+'/README.md'))
broken=[]
for path in paths:
 for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
  if not target.startswith(('http:','https:')) and not (path.parent/target.split('#')[0]).exists():broken.append({'source':str(path),'target':target})
record={'spec_exit_code':exitcode,'spec':json.loads((OUT/'spec_validation.json').read_text()),'unittest_exit_code':p.returncode,'unittest_command':[sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],'old_validation_preserved':True,'broken_new_links':broken,'scope':'Software/artifact consistency only; not biological validation.'}
(OUT/'validation_summary.json').write_text(json.dumps(record,indent=2)+'\n')
print((OUT/'spec_validation.log').read_text());print(p.stdout+p.stderr);print('BROKEN_LINKS',broken)
if exitcode or p.returncode or broken:sys.exit(1)
# Record final scripts/checkpoints; models are referenced, not redistributed.
files=list((ROOT/'runtime').glob('*20261116.py'))+[ROOT/'runtime/sirna_context_audit.py',ROOT/'tests/test_config_sweep_20261116.py']
for x in ['external/RN.Ai-predict/RN.Ai-predict.model.keras','external/RNAiSpline/checkpoints/best_model.pth','external/RN.Ai-predict/features.py']:
 files.append(pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench')/x)
backend=[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files if f.is_file()]
(OUT/'code_model_provenance.json').write_text(json.dumps({'files':backend,'note':'No upstream files edited; no checkpoints copied. Final code includes plotting-label and overwrite-guard hardening after inference, which do not change model scores or frozen configs.'},indent=2)+'\n')
# Keep checksums over immutable run/config artifacts only. Mutable README indexes are excluded.
artifacts=[]
for tree in ['config','results','benchmark']:
 for d in (ROOT/tree).glob('*/'+RUN):
  artifacts.extend(f for f in d.rglob('*') if f.is_file() and not f.is_symlink() and f.name!='PROVENANCE.sha256' and '__pycache__' not in f.parts)
artifacts+=list((ROOT/'runtime').glob('*20261116.py'))+[ROOT/'runtime/sirna_context_audit.py',ROOT/'tests/test_config_sweep_20261116.py']
manifest=''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(ROOT))+'\n' for f in sorted(set(artifacts)))
(OUT/'PROVENANCE.sha256').write_text(manifest)
q=subprocess.run(['sha256sum','-c',str((OUT/'PROVENANCE.sha256').relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True,timeout=180)
print('CHECKSUM_RETURN_CODE',q.returncode,'VERIFIED_ENTRIES',len(set(artifacts)))
if q.returncode:print(q.stdout+q.stderr);sys.exit(q.returncode)
print('RUN4_REPORT',OUT/'REPORT.md')
