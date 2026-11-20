"""Execute package/regression validation, verify references/figures/historical hashes, freeze Run-6."""
import pathlib,sys,subprocess,json,os,runpy,builtins,contextlib,hashlib,re
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];B=ROOT/'benchmark/014_Workflow-rerun/Run-6_2026-11-16';RUN='Run-6_2026-11-16'
def main():
 original=ROOT/'tests/validation.json';before=original.read_bytes();realopen=builtins.open
 def opener(file,mode='r',*a,**kw):
  try:match=pathlib.Path(file).resolve()==original.resolve()
  except (TypeError,ValueError):match=False
  if match and any(x in mode for x in 'wax+'):file=B/'spec_validation.json'
  return realopen(file,mode,*a,**kw)
 code=0
 with realopen(B/'spec_validation.log','w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log),patch('builtins.open',opener):
  try:runpy.run_path(str(ROOT/'tests/validate_spec.py'),run_name='__main__')
  except SystemExit as e:code=e.code
 assert original.read_bytes()==before
 p=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_*.py'],cwd=ROOT,capture_output=True,text=True,timeout=240,env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'})
 text=p.stdout+p.stderr;(B/'unittest.log').write_text(text);n=re.search(r'Ran (\d+) tests',text)
 docs=[B/'REPORT.md',B.parent/'README.md',B.parent/'BENCHMARK_RUNS.md',ROOT/'config/README.md']+list((ROOT/'config').glob('*/README.md'));broken=[]
 for d in docs:
  for link in re.findall(r'\]\(([^)]+)\)',d.read_text()):
   if not link.startswith(('http:','https:')) and not (d.parent/link.split('#')[0]).exists():broken.append({'source':str(d.relative_to(ROOT)),'target':link})
 historical=[]
 for f in [ROOT/'benchmark/011_Campaign-reproduction/Run-3_2026-11-11/PROVENANCE.sha256',ROOT/'benchmark/012_Config-sweep/Run-4_2026-11-16/PROVENANCE.sha256',ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16/PROVENANCE.sha256']:
  entries=f.read_text().splitlines()
  for line in entries:
   expected,path=line.split('  ',1);assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
  historical.append({'manifest':str(f.relative_to(ROOT)),'verified_entries':len(entries)})
 from PIL import Image,ImageStat
 images=json.loads((B/'figure_validation.json').read_text())
 for r in images:
  with Image.open(ROOT/r['path']) as im:im.verify()
  with Image.open(ROOT/r['path']) as im:assert im.width==r['width'] and im.height==r['height'] and max(ImageStat.Stat(im.convert('RGB')).stddev)>5
 cli='/home/boltzmann13/.sci/profiles/imran-sirna-task/skills/research/grounded-citations/scripts/sources.py'
 cite=subprocess.run([sys.executable,cli,'--ledger',str(B/'sources/citation_ledger.json'),'verify',str(B/'REPORT.md'),'--strict','--evidence'],capture_output=True,text=True,timeout=60);(B/'citation_verification.log').write_text(cite.stdout+cite.stderr)
 validation={'spec_exit_code':code,'spec_validation':json.loads((B/'spec_validation.json').read_text()),'unittest_exit_code':p.returncode,'tests_executed':int(n.group(1)) if n is not None else None,'historical_validation_file_preserved':True,'historical_manifests':historical,'new_broken_relative_links':broken,'decoded_nonblank_figures':len(images),'citation_exit_code':cite.returncode,'scope':'Software/artifact consistency and experimental-reference calculations, not biological/clinical validation or complete design acceptance.'}
 (B/'validation_summary.json').write_text(json.dumps(validation,indent=2)+'\n');print((B/'spec_validation.log').read_text());print(text);print(cite.stdout+cite.stderr);print('BROKEN_LINKS',broken)
 if code or p.returncode or cite.returncode or broken:raise SystemExit(1)
 (B/'verified_completion.json').write_text(json.dumps({'status':'EXECUTED_RUNNABLE_BENCHMARKS_AND_VERIFIED_RESULTS','new_training':False,'new_generation':False,'matched_published_protocol_superiority_claims':0,'complete_application_design_tasks':0,'new_model_blockers_retained':True,'tests_passed':validation['tests_executed'],'unique_decoded_figures':len(images)},indent=2)+'\n')
 files=[]
 for folder in ['config','results','benchmark']:
  for d in (ROOT/folder).glob('*/'+RUN):files.extend(f for f in d.rglob('*') if f.is_file() and not f.is_symlink() and f.name!='PROVENANCE.sha256' and '__pycache__' not in f.parts)
 files+=list((ROOT/'runtime').glob('*workflow_rerun_20261116.py'))+[ROOT/'runtime/oligoformer_pairs_20261116.py',ROOT/'tests/test_workflow_rerun_20261116.py',B.parent/'README.md',B.parent/'BENCHMARK_RUNS.md'];files=sorted(set(files))
 manifest=B/'PROVENANCE.sha256';manifest.write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+str(f.relative_to(ROOT))+'\n' for f in files));q=subprocess.run(['sha256sum','-c',str(manifest.relative_to(ROOT))],cwd=ROOT,capture_output=True,text=True,timeout=120)
 print('MANIFEST_ENTRIES',len(files),'INDEPENDENT_CHECK_RETURN_CODE',q.returncode)
 if q.returncode:print(q.stdout+q.stderr);raise SystemExit(q.returncode)
 print('RUN6_REPORT',B/'REPORT.md')
if __name__=='__main__':main()
