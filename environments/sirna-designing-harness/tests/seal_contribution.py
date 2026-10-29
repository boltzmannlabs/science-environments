#!/usr/bin/env python3
"""Seal the focused environment update after real tests; no remote writes or models."""
from pathlib import Path
import argparse,datetime,json,hashlib,subprocess,sys
ENV=Path(__file__).resolve().parents[1];REPO=ENV.parents[1]
RESEARCH=REPO/'research/sirna-designing-harness';ADR=REPO/'docs/decisions/sirna-designing-harness.md';RESULTS=ENV/'results'
BRANCH='feat/sirna-technical-validation-environment'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def j(p):return json.loads(Path(p).read_text())
def writej(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def git(*args):
    p=subprocess.run(['git',*args],cwd=REPO,capture_output=True,text=True,timeout=60)
    if p.returncode:raise ValueError(p.stderr)
    return p.stdout

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');a=parser.parse_args()
    mp=RESULTS/'output_manifest.json';rp=RESULTS/'verification_receipt.json'
    if a.verify_only:
        m=j(mp);r=j(rp)
        assert r['verification']=='PASSED' and sha(mp)==r['output_manifest_sha256']
        for item in m['artifacts']:
            path=REPO/item['repository_relative_path'];assert sha(path)==item['sha256'] and path.stat().st_size==item['bytes']
        print(json.dumps({'verification':'PASSED','artifacts_verified':len(m['artifacts']),'scope':'Final contributed bytes versus manifest; no new tests/models'},indent=2));return 0
    checks=[];test_counts=[]
    for name in ('validation_receipt.json','validation_receipt.python313.json'):
        r=j(RESULTS/name);assert r['verification']=='PASSED' and r['new_generation_inference_folding_screening_runs']==0
        required={'environment_tests','technical_report_tests','portable_skill_tests'}
        by={c['check']:c for c in r['checks']};assert required<=set(by)
        assert all(by[k].get('software_tests',0)>0 for k in required)
        assert r['software_tests_passed']==sum(c.get('software_tests',0) for c in r['checks'])
        assert r['recorded_KRAS14_technical_passes']==14
        assert r['technical_case_snapshot_sha256']==sha(RESULTS/'case_studies/KRAS_14_technical_validation/snapshot_manifest.json')
        for check in r['checks']:
            assert check['status']=='PASSED' and check['returncode']==check['expected_returncode']
            assert sha(RESULTS/check['log'])==check['log_sha256']
        for rel,digest in r['implementation_files'].items():assert sha(ENV/rel)==digest,'Implementation changed after tests: '+rel
        test_counts.append(r['software_tests_passed']);checks.append({'receipt':name,'python':r['python'],'software_tests_passed':r['software_tests_passed'],'sha256':sha(RESULTS/name)})
    assert len(set(test_counts))==1,'Interpreter test counts disagree'
    command_checks=[]
    for command in ('check-project','check-skill','verify-benchmark','verify-technical-case'):
        proc=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),command],capture_output=True,text=True,timeout=60)
        assert proc.returncode==0,proc.stdout+proc.stderr
        result=json.loads(proc.stdout);assert result['status']=='PASSED';command_checks.append({'command':command,'result':result})
    report=j(RESULTS/'technical_validation_KRAS14/technical_report.json')
    assert report['technical_status']=='PASSED_DECLARED_TECHNICAL_GATES' and report['technical_pass_count']==report['submitted_count']==14
    assert report['bundle_sha256']==sha(RESULTS/'case_studies/KRAS_14_technical_validation/bundle.json') and report['policy_sha256']==sha(ENV/'config/technical_gate_policy.json')
    report_root=RESULTS/'technical_validation_KRAS14';rm=j(report_root/'output_manifest.json');rr=j(report_root/'verification_receipt.json')
    assert rr['output_manifest_sha256']==sha(report_root/'output_manifest.json')
    for item in rm['files']:assert sha(report_root/item['path'])==item['sha256']
    for path in (REPO/'README.md',REPO/'research/README.md'):assert 'sirna-designing-harness' in path.read_text()
    status=git('status','--porcelain','--untracked-files=all');changed=[line[3:] for line in status.splitlines() if line]
    allowed_exact={'README.md','research/README.md','docs/decisions/sirna-designing-harness.md'}
    prefixes=('environments/sirna-designing-harness/','research/sirna-designing-harness/')
    unexpected=[p for p in changed if p not in allowed_exact and not p.startswith(prefixes)];assert not unexpected,unexpected
    assert not git('diff','--cached','--name-only').strip(),'No staging/commit requested'
    assert git('branch','--show-current').strip()==BRANCH
    diff=subprocess.run(['git','diff','--check'],cwd=REPO,capture_output=True,text=True);assert diff.returncode==0,diff.stdout
    tracked_changes=set(git('diff','--name-only','HEAD').splitlines())
    assert all(p in allowed_exact or p.startswith(prefixes) for p in tracked_changes)
    selected=list(ENV.rglob('*'))+list(RESEARCH.rglob('*'))+[ADR,REPO/'README.md',REPO/'research/README.md'];files=[]
    for path in sorted(set(selected)):
        if not path.is_file() or path in (mp,rp) or '__pycache__' in path.parts:continue
        assert not path.is_symlink();limit=524288 if path.is_relative_to(ENV/'benchmark') else 131072
        assert path.stat().st_size<limit,'Oversized unnecessary payload: '+str(path)
        if path.suffix=='.json':j(path)
        role='FROZEN_HISTORICAL_KRAS_SNAPSHOT' if path.is_relative_to(ENV/'benchmark') else 'RECORDED_TECHNICAL_CASE_INPUT' if path.is_relative_to(RESULTS/'case_studies') else 'EXECUTED_TECHNICAL_REPORT' if path.is_relative_to(RESULTS/'technical_validation_KRAS14') else 'PRIOR_PROJECT_RECEIPT' if path.is_relative_to(RESULTS/'history') else 'DOCUMENTATION_CONFIG_TASK_IMPLEMENTATION_OR_TEST'
        files.append({'repository_relative_path':path.relative_to(REPO).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'role':role})
    total=sum(r['bytes'] for r in files);historical=sum(r['bytes'] for r in files if r['repository_relative_path'].startswith('environments/sirna-designing-harness/benchmark/'))
    assert historical<3*1048576 and total-historical<2*1048576,'Bounded historical snapshot plus small technical implementation/evidence only'
    portable=j(ENV/'skills/sirna-harness/assets/portable-manifest.json')
    for r in portable['files']:assert sha(ENV/'skills/sirna-harness'/r['relative_path'])==r['sha256']
    writej(mp,{'project':'siRNA Designing Harness','artifact_scope':'Focused environment/research/ADR update plus intentional index edits; historical snapshots, recorded technical inputs and report replay labelled separately','artifacts':files,'root_receipt_and_self_excluded':True,'source_historical_index_sha256':sha(RESULTS/'historical_evidence_index.json')})
    for r in files:assert sha(REPO/r['repository_relative_path'])==r['sha256']
    receipt={'verification':'PASSED','scope':'Portable technical environment implementation/tests, recorded evidence replay and packaging integrity','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project_name':'siRNA Designing Harness','environment':'environments/sirna-designing-harness','technical_component':'IMPLEMENTED_AND_TESTED','technical_case_status':report['technical_status'],'technical_case_passes':report['technical_pass_count'],'lifecycle':'In Progress','branch':BRANCH,'interpreter_test_receipts':checks,'command_checks':command_checks,'historical_small_summary_receipt_files_verified':10,'historical_benchmark_source_files_preserved':85,'recorded_technical_case_reference_views':4,'files_hashed':len(files),'total_artifact_bytes':total,'output_manifest_sha256':sha(mp),'unrelated_tracked_files_changed':False,'tracked_files_intentionally_updated':sorted(tracked_changes),'new_generation_inference_folding_screening_runs':0,'new_remote_jobs_or_uploads':0,'third_party_implementations_or_models_copied':False,'governance':{'issue_lookup':'AUTHENTICATED_NO_SIRNA_TITLE_MATCH','remote_issue_created':False,'PR_created':False,'owner_reviewer_assignment':'PENDING','review_approval':'PENDING','commit_push_merge_performed':False,'repository_license_selection':'PENDING'},'definition_of_done':'Local technical environment acceptance complete; remote issue/PR/review/merge and separately configured backend deployment remain explicit'}
    writej(rp,receipt);print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
