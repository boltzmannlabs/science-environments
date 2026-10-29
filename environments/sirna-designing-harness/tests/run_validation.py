#!/usr/bin/env python3
"""Execute technical software/contract checks and write real receipts; no model dispatch."""
from pathlib import Path
import argparse,datetime,json,re,subprocess,sys,hashlib,tempfile
ENV=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--scratch',required=True);p.add_argument('--evidence-root');p.add_argument('--tag',default='');a=p.parse_args()
    scratch=Path(a.scratch).expanduser().resolve();scratch.mkdir(parents=True,exist_ok=True)
    if a.tag and not re.fullmatch('[A-Za-z0-9_-]+',a.tag):raise ValueError('Unsafe validation tag')
    suffix='.'+a.tag if a.tag else '';results=ENV/'results';results.mkdir(exist_ok=True);checks=[];passed=True
    with tempfile.TemporaryDirectory(prefix='sirna-technical-cli-',dir=scratch) as temp:
        commands=[
            ('environment_tests',[sys.executable,'-B',str(ENV/'tests/test_environment.py'),'--scratch',str(scratch)],0),
            ('technical_report_tests',[sys.executable,'-B',str(ENV/'tests/test_technical_reporting.py'),'--scratch',str(scratch)],0),
            ('portable_skill_tests',[sys.executable,'-B',str(ENV/'skills/sirna-harness/scripts/test_portable.py'),'--scratch',str(scratch)],0),
            ('project_structure',[sys.executable,'-B',str(ENV/'scripts/run.py'),'check-project'],0),
            ('skill_integrity',[sys.executable,'-B',str(ENV/'scripts/run.py'),'check-skill'],0),
            ('benchmark_snapshot_integrity',[sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-benchmark'],0),
            ('technical_case_integrity',[sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-technical-case'],0),
            ('recorded_technical_report_replay',[sys.executable,'-B',str(ENV/'scripts/run.py'),'technical-report','--bundle',str(ENV/'results/case_studies/KRAS_14_technical_validation/bundle.json'),'--out',str(Path(temp)/'new-report')],0),
            ('empty_config_expected_block',[sys.executable,'-B',str(ENV/'scripts/run.py'),'preflight','--config',str(ENV/'config/environment.example.json')],2)]
        if a.evidence_root:commands.append(('historical_receipt_verification',[sys.executable,'-B',str(ENV/'scripts/run.py'),'verify-history','--evidence-root',str(Path(a.evidence_root).expanduser().resolve())],0))
        for name,argv,expected in commands:
            proc=subprocess.run(argv,capture_output=True,text=True,timeout=180);log=results/(name+suffix+'.log')
            log.write_text('ARGV: '+json.dumps(argv)+'\nRETURN_CODE: '+str(proc.returncode)+'\nSTDOUT:\n'+proc.stdout+'\nSTDERR:\n'+proc.stderr)
            ok=proc.returncode==expected;item={'check':name,'status':'PASSED' if ok else 'FAILED','returncode':proc.returncode,'expected_returncode':expected,'log':log.name,'log_sha256':sha(log)}
            count=re.search(r'Ran (\d+) tests',proc.stderr)
            if count:item['software_tests']=int(count.group(1))
            if name=='historical_receipt_verification' and ok:item['source_summary_receipt_files_verified']=json.loads(proc.stdout)['files_checked']
            if name=='recorded_technical_report_replay' and ok:
                replay=json.loads(proc.stdout);ok=replay['status']=='PASSED_DECLARED_TECHNICAL_GATES' and replay['technical_pass_count']==14 and replay['new_scientific_jobs']==0
                item.update(status='PASSED' if ok else 'FAILED',technical_pass_count=replay['technical_pass_count'])
            passed=passed and ok;checks.append(item)
    implementation={str(path.relative_to(ENV)):sha(path) for folder in ('scripts','tests','config','tasks') for path in (ENV/folder).rglob('*') if path.is_file() and path.suffix in ('.py','.json') and '__pycache__' not in path.parts}
    receipt={'implementation_files':implementation,'technical_case_snapshot_sha256':sha(ENV/'results/case_studies/KRAS_14_technical_validation/snapshot_manifest.json'),'verification':'PASSED' if passed else 'FAILED','scope':'Portable technical software/contracts plus recorded evidence replay; scientific models are not rerun by these checks','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':sys.version,'python_executable':sys.executable,'software_tests_passed':sum(x.get('software_tests',0) for x in checks if x['status']=='PASSED'),'checks':checks,'new_generation_inference_folding_screening_runs':0,'recorded_KRAS14_technical_passes':14 if any(x.get('technical_pass_count')==14 and x['status']=='PASSED' for x in checks) else None,'fresh_backend_deployment_verified':False,'technical_component':'IMPLEMENTED_AND_TESTED' if passed else 'TEST_FAILURE','lifecycle':'In Progress','github_issue_PR_review':'PENDING_REMOTE_ISSUE_PR_AND_MAINTAINER_REVIEW'}
    (results/('validation_receipt'+suffix+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
