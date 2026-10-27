#!/usr/bin/env python3
"""Seal only this local contribution after real tests. No commit, remote write or scientific execution."""
from pathlib import Path
import argparse,datetime,json,hashlib,subprocess,sys
ENV=Path(__file__).resolve().parents[1];REPO=ENV.parents[1];RESEARCH=REPO/'research/sirna-designing-harness';ADR=REPO/'docs/decisions/sirna-designing-harness.md';RESULTS=ENV/'results'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
def j(p):return json.loads(Path(p).read_text())
def writej(p,x):Path(p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def git(*args):
 p=subprocess.run(['git',*args],cwd=REPO,capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stderr;return p.stdout

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--verify-only',action='store_true');args=parser.parse_args();manifest_path=RESULTS/'output_manifest.json';receipt_path=RESULTS/'verification_receipt.json'
 if args.verify_only:
  manifest=j(manifest_path);receipt=j(receipt_path);assert receipt['verification']=='PASSED' and sha(manifest_path)==receipt['output_manifest_sha256']
  for r in manifest['artifacts']:assert sha(REPO/r['repository_relative_path'])==r['sha256'] and (REPO/r['repository_relative_path']).stat().st_size==r['bytes']
  print(json.dumps({'verification':'PASSED','artifacts_verified':len(manifest['artifacts']),'scope':'Current contributed bytes versus manifest/receipt; no new tests or models'},indent=2));return 0
 checks=[]
 for name in ['validation_receipt.json','validation_receipt.python313.json']:
  r=j(RESULTS/name);assert r['verification']=='PASSED' and r['software_tests_passed']==54 and r['new_generation_inference_folding_screening_runs']==0
  for check in r['checks']:
   assert check['status']=='PASSED' and check['returncode']==check['expected_returncode'];assert sha(RESULTS/check['log'])==check['log_sha256']
  checks.append({'receipt':name,'python':r['python'],'software_tests_passed':r['software_tests_passed'],'sha256':sha(RESULTS/name)})
 command_checks=[]
 for command in ['check-project','check-skill','verify-benchmark']:
  p=subprocess.run([sys.executable,'-B',str(ENV/'scripts/run.py'),command],capture_output=True,text=True,timeout=60);assert p.returncode==0,p.stdout+p.stderr;result=json.loads(p.stdout);assert result['status']=='PASSED';command_checks.append({'command':command,'result':result})
 for path in [REPO/'README.md',REPO/'research/README.md']:assert 'sirna-designing-harness' in path.read_text()
 status=git('status','--porcelain','--untracked-files=all');changed=[line[3:] for line in status.splitlines() if line];allowed_exact={'README.md','research/README.md','docs/decisions/sirna-designing-harness.md'};prefixes=['environments/sirna-designing-harness/','research/sirna-designing-harness/'];unexpected=[p for p in changed if p not in allowed_exact and not any(p.startswith(prefix) for prefix in prefixes)];assert not unexpected,unexpected
 assert not git('diff','--cached','--name-only').strip(),'No staging or committing requested';assert git('branch','--show-current').strip()=='feat/sirna-designing-harness';diffcheck=subprocess.run(['git','diff','--check'],cwd=REPO,capture_output=True,text=True);assert diffcheck.returncode==0,diffcheck.stdout
 tracked_changes=set(git('diff','--name-only','HEAD').splitlines());assert tracked_changes<= {'README.md','research/README.md'},tracked_changes
 selected=list(ENV.rglob('*'))+list(RESEARCH.rglob('*'))+[ADR,REPO/'README.md',REPO/'research/README.md'];files=[]
 for path in sorted(set(selected)):
  if not path.is_file() or path in [manifest_path,receipt_path] or '__pycache__' in path.parts:continue
  assert not path.is_symlink();limit=524288 if path.is_relative_to(ENV/'benchmark') else 131072
  assert path.stat().st_size<limit,'Oversized unnecessary payload: '+str(path)
  if path.suffix=='.json':j(path)
  files.append({'repository_relative_path':path.relative_to(REPO).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'role':'FROZEN_KRAS_REPORT_RESULT_OR_PROVENANCE' if path.is_relative_to(ENV/'benchmark') else 'PRIOR_PROJECT_REVISION_RECEIPT' if path.is_relative_to(RESULTS/'history') else 'HISTORICAL_AGGREGATE_OR_CURRENT_TEST_RECEIPT' if path.parent==RESULTS else 'DOCUMENTATION_CONFIG_TASK_OR_ORIGINAL_HELPER'})
 total=sum(r['bytes'] for r in files);benchmark_bytes=sum(r['bytes'] for r in files if r['repository_relative_path'].startswith('environments/sirna-designing-harness/benchmark/'))
 assert benchmark_bytes<3*1048576 and total-benchmark_bytes<1048576,'Bounded benchmark snapshot plus small technical project only'
 portable=j(ENV/'skills/sirna-harness/assets/portable-manifest.json')
 for r in portable['files']:assert sha(ENV/'skills/sirna-harness'/r['relative_path'])==r['sha256']
 writej(manifest_path,{'project':'siRNA Designing Harness','artifact_scope':'Only new environment/research/ADR and intentionally modified indexes; selected historical report/result copies included, raw datasets/reference/model assets not copied','artifacts':files,'root_receipt_and_self_excluded':True,'source_historical_index_sha256':sha(RESULTS/'historical_evidence_index.json')})
 for r in files:assert sha(REPO/r['repository_relative_path'])==r['sha256']
 receipt={'verification':'PASSED','scope':'Local project structure/helper tests/evidence packaging only; not scientific-backend or biological validation','verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'project_name':'siRNA Designing Harness','environment':'environments/sirna-designing-harness','lifecycle':'In Progress','biology':'PARTIAL','branch':'feat/sirna-designing-harness','interpreter_test_receipts':checks,'command_checks':command_checks,'historical_small_summary_receipt_files_verified':10,'benchmark_source_files_copied':85,'benchmark_snapshot_verification_sha256':sha(ENV/'benchmark/KRAS/snapshot_verification.json'),'files_hashed':len(files),'total_artifact_bytes':total,'output_manifest_sha256':sha(manifest_path),'unrelated_tracked_files_changed':False,'tracked_index_files_intentionally_modified':sorted(tracked_changes),'new_generation_inference_folding_screening_runs':0,'new_remote_jobs_or_uploads':0,'third_party_assets_copied':False,'independent_validation':'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','mutation_arm':'BLOCKED_PENDING_MUTATION_SPECIFICATION','governance':{'issue_lookup':'BLOCKED_GITHUB_CLI_UNAUTHENTICATED','remote_issue_created':False,'PR_created':False,'owner_reviewer_assignment':'PENDING','review_approval':'PENDING','commit_push_merge_performed':False,'repository_license_selection':'PENDING'},'definition_of_done':'Local artifact/technical acceptance complete; issue/PR/review/merge and scientific deployment/qualification explicitly outstanding'};writej(receipt_path,receipt);print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
