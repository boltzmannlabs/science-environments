#!/usr/bin/env python3
"""Run real technical tests and capture receipts; never run scientific backends."""
from pathlib import Path
import argparse,datetime,json,re,subprocess,sys,hashlib
ENV=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',required=True);p.add_argument('--evidence-root');p.add_argument('--tag',default='');a=p.parse_args();scratch=Path(a.scratch).expanduser().resolve();scratch.mkdir(parents=True,exist_ok=True)
 if a.tag and not re.fullmatch('[A-Za-z0-9_-]+',a.tag):raise ValueError('Unsafe validation tag')
 suffix='.'+a.tag if a.tag else '';results=ENV/'results';results.mkdir(exist_ok=True);checks=[];passed=True
 commands=[('environment_tests',[sys.executable,'-B',str(ENV/'tests/test_environment.py'),'--scratch',str(scratch)],0),('portable_skill_tests',[sys.executable,'-B',str(ENV/'skills/sirna-harness/scripts/test_portable.py'),'--scratch',str(scratch)],0),('project_structure',[sys.executable,'-B',str(ENV/'scripts/run.py'),'check-project'],0),('skill_integrity',[sys.executable,'-B',str(ENV/'scripts/run.py'),'check-skill'],0),('benchmark_snapshot_integrity',[sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-benchmark'],0),('empty_config_expected_block',[sys.executable,'-B',str(ENV/'scripts/run.py'),'preflight','--config',str(ENV/'config/environment.example.json')],2)]
 if a.evidence_root:commands.append(('historical_receipt_verification',[sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-history','--evidence-root',str(Path(a.evidence_root).expanduser().resolve())],0))
 for name,argv,expected in commands:
  proc=subprocess.run(argv,capture_output=True,text=True,timeout=180);log=results/(name+suffix+'.log');log.write_text('ARGV: '+json.dumps(argv)+'\nRETURN_CODE: '+str(proc.returncode)+'\nSTDOUT:\n'+proc.stdout+'\nSTDERR:\n'+proc.stderr);ok=proc.returncode==expected;passed=passed and ok;item={'check':name,'status':'PASSED' if ok else 'FAILED','returncode':proc.returncode,'expected_returncode':expected,'log':log.name,'log_sha256':sha(log)}
  count=re.search(r'Ran (\d+) tests',proc.stderr)
  if count:item['software_tests']=int(count.group(1))
  if name=='historical_receipt_verification' and ok:item['source_summary_receipt_files_verified']=json.loads(proc.stdout)['files_checked']
  checks.append(item)
 receipt={'verification':'PASSED' if passed else 'FAILED','scope':'Software/structure and optionally small historical-receipt checks; no scientific model-performance or biological validation','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'python_executable':sys.executable,'software_tests_passed':sum(x.get('software_tests',0) for x in checks if x['status']=='PASSED'),'checks':checks,'new_generation_inference_folding_screening_runs':0,'fresh_backend_deployment_verified':False,'lifecycle':'In Progress','biology':'PARTIAL','github_issue_PR_review':'PENDING_AUTHENTICATION_AND_MAINTAINER_REVIEW'};(results/('validation_receipt'+suffix+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
