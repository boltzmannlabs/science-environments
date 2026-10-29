#!/usr/bin/env python3
"""siRNA design and technical validation: portable checks/reports; no backend dispatch."""
from __future__ import annotations
import argparse,hashlib,json,os,re,subprocess,sys
from pathlib import Path
ENV=Path(__file__).resolve().parents[1];REPO=ENV.parents[1];SKILL=ENV/'skills/sirna-harness'

def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def describe():return {'project_name':'siRNA Designing Harness','display_scope':'siRNA design and technical validation','lifecycle':'In Progress','implemented_surface':'Portable technical checks, evidence-bound candidate property reports and agent workflow/task contracts','technical_success_label':'PASSED_DECLARED_TECHNICAL_GATES','technical_report_command':'technical-report','scientific_backend_dispatch':False,'biological_validation':False,'independent_benchmark_status':'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','mutation_arm_default':'BLOCKED_PENDING_MUTATION_SPECIFICATION','scientific_modes':['DESIGN','TECHNICAL_VALIDATION','AUDIT','SENSITIVITY','BENCHMARK'],'third_party_assets_bundled':False}
def project_check():
 required=['README.md','ENVIRONMENT_SPEC.md','STATUS.md','config/README.md','config/environment.example.json','config/objective.example.json','config/gates.example.json','config/capability_registry.json','config/output_contracts.json','tasks/README.md','tasks/kras-shared-review.json','tasks/kras-mutation-blocked.json','tasks/audit.json','tasks/sensitivity.json','tasks/benchmark.json','tasks/literature-comparison.json','tasks/ISSUE_DRAFT.md','tasks/PR_DRAFT.md','scripts/run.py','tests/run_validation.py','tests/test_environment.py','skills/sirna-harness/SKILL.md','skills/sirna-harness/assets/LICENSE.txt','skills/sirna-harness/assets/portable-manifest.json','results/historical_evidence_index.json','results/portable_skill_origin.json','benchmark/README.md','benchmark/KRAS/README.md','benchmark/KRAS/copy_provenance.json','benchmark/KRAS/external_artifact_index.json','benchmark/KRAS/snapshot_manifest.json','benchmark/KRAS/snapshot_verification.json','tests/seal_benchmark.py']
 required += ['scripts/technical_reporting.py','config/technical_gate_policy.json','tasks/technical-validation.json','tests/test_technical_reporting.py','results/case_studies/KRAS_14_technical_validation/bundle.json','results/case_studies/KRAS_14_technical_validation/snapshot_manifest.json']
 missing=[p for p in required if not (ENV/p).is_file()];errors=[];json_count=0
 for path in ENV.rglob('*.json'):
  if path.is_symlink():errors.append('Symlink JSON refused: '+str(path));continue
  try:load(path);json_count+=1
  except (ValueError,OSError) as e:errors.append(str(path)+': '+str(e))
 docs=list(ENV.rglob('*.md'))+list((REPO/'research/sirna-designing-harness').glob('*.md'))+[REPO/'docs/decisions/sirna-designing-harness.md'];local_links=0
 for path in docs:
  if not path.is_file():errors.append('Required document absent: '+str(path));continue
  for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
   if link.startswith(('http://','https://','mailto:','#')):continue
   target=link.split('#',1)[0]
   if not target:continue
   local_links+=1
   if not (path.parent/target).exists():errors.append('Broken local Markdown link: '+str(path)+' -> '+link)
 registry=load(ENV/'config/capability_registry.json');categories=registry.get('capabilities',[])
 if len(categories)!=15 or len({r['category'] for r in categories})!=15:errors.append('Expected15 unique capability categories')
 unexpected=[]
 for path in ENV.rglob('*'):
  if not path.is_file():continue
  if path.is_symlink():unexpected.append(str(path))
  if path.suffix.lower() in {'.pth','.pt','.pkl','.h5','.hdf5','.fa','.fasta','.xlsx','.parquet','.zip','.tar','.gz'} or path.name.startswith('.env'):unexpected.append(str(path))
 status='FAILED' if missing or errors or unexpected else 'PASSED'
 return {'status':status,'missing_required_files':missing,'errors':errors,'unexpected_payloads':unexpected,'json_files_parsed':json_count,'local_markdown_links_checked':local_links,'capability_categories':len(categories),'scope':'Local structure/contracts only; external URL reachability and scientific readiness not tested'}
def verify_history(root):
 root=Path(root).expanduser().resolve();index=load(ENV/'results/historical_evidence_index.json');checks=[];missing=[];mismatch=[]
 for record in index['records']:
  for source in record['source_files']:
   relative=Path(source['relative_path'])
   if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe historical relative path')
   path=(root/relative).resolve()
   if not path.is_relative_to(root):raise ValueError('Historical path escapes approved evidence root')
   if not path.is_file():missing.append(source['relative_path']);continue
   current=sha(path);ok=current==source['sha256'] and path.stat().st_size==source['bytes'];checks.append({'relative_path':source['relative_path'],'hash_match':ok})
   if not ok:mismatch.append(source['relative_path'])
  summary=root/record['source_files'][0]['relative_path']
  if summary.is_file():
   payload=load(summary)
   for name,value in record['metrics'].items():
    if payload.get(name)!=value:mismatch.append(record['evidence_id']+':'+name)
  receipt=root/record['source_files'][1]['relative_path']
  if receipt.is_file() and load(receipt).get('verification')!='PASSED':mismatch.append(record['evidence_id']+':receipt_state')
 # Hash again; never invoke the old verifier or mutate original files.
 for record in index['records']:
  for source in record['source_files']:
   path=root/source['relative_path']
   if path.is_file() and sha(path)!=source['sha256'] and source['relative_path'] not in mismatch:mismatch.append(source['relative_path'])
 return {'status':'FAILED' if mismatch else 'BLOCKED_MISSING_EVIDENCE' if missing else 'PASSED','files_checked':len(checks),'checks':checks,'missing_files':missing,'mismatches':mismatch,'source_writes':0,'scientific_runs':0,'meaning':'Expected historical summary and receipt bytes/selected aggregate values only; not a new scientific validation'}
def verify_benchmark():
 root=ENV/'benchmark/KRAS';manifest_path=root/'snapshot_manifest.json';receipt_path=root/'snapshot_verification.json'
 if not manifest_path.is_file() or not receipt_path.is_file():return {'status':'BLOCKED_MISSING_EVIDENCE','reason':'Benchmark snapshot has not been sealed','scientific_runs':0}
 manifest=load(manifest_path);receipt=load(receipt_path)
 if receipt.get('verification')!='PASSED' or receipt.get('snapshot_manifest_sha256')!=sha(manifest_path):return {'status':'FAILED','reason':'Benchmark manifest/receipt binding mismatch','scientific_runs':0}
 expected=set();errors=[]
 for item in manifest['artifacts']:
  relative=Path(item['relative_path'])
  if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe benchmark manifest path')
  path=(root/relative).resolve()
  if not path.is_relative_to(root.resolve()):raise ValueError('Benchmark path escapes root')
  expected.add(relative.as_posix())
  if not path.is_file() or path.is_symlink() or sha(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:errors.append(relative.as_posix())
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p not in [manifest_path,receipt_path]}
 if actual!=expected:errors.append('unmanifested_or_missing_files')
 return {'status':'FAILED' if errors else 'PASSED','copied_source_files':receipt['copied_source_files'],'snapshot_files_verified':len(expected),'errors':errors,'biological_status':'PARTIAL','independent_benchmark_status':'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','mutation_arm_status':'BLOCKED_PENDING_MUTATION_SPECIFICATION','scientific_runs':0,'meaning':'Frozen report/result snapshot integrity only; no inference or independent experimental validation'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 for name in ['describe','check-project','check-skill','verify-benchmark','verify-technical-case']:sub.add_parser(name)
 p=sub.add_parser('technical-report');p.add_argument('--bundle',required=True);p.add_argument('--policy',default=str(ENV/'config/technical_gate_policy.json'));p.add_argument('--out',required=True)
 p=sub.add_parser('verify-history');p.add_argument('--evidence-root',required=True)
 p=sub.add_parser('preflight');p.add_argument('--config',required=True)
 p=sub.add_parser('validate-objective');p.add_argument('--objective',required=True)
 p=sub.add_parser('validate-candidates');p.add_argument('--candidates',required=True);p.add_argument('--fasta',required=True);p.add_argument('--reference-alphabet',required=True,choices=['DNA','RNA'])
 p=sub.add_parser('check-gates');p.add_argument('--gates',required=True)
 p=sub.add_parser('audit-label-table');p.add_argument('--dataset',required=True);p.add_argument('--sequence-column',required=True);p.add_argument('--label-column',required=True);p.add_argument('--label-unit',required=True)
 args=parser.parse_args()
 try:
  if args.command=='describe':result=describe()
  elif args.command=='check-project':result=project_check()
  elif args.command=='verify-benchmark':result=verify_benchmark()
  elif args.command=='verify-history':result=verify_history(args.evidence_root)
  elif args.command=='technical-report':
   from technical_reporting import write_report
   result=write_report(args.bundle,args.policy,args.out)
  elif args.command=='verify-technical-case':
   from technical_reporting import verify_case
   result=verify_case(ENV/'results/case_studies/KRAS_14_technical_validation')
  else:
   if args.command=='check-skill':cmd=[sys.executable,'-B',str(SKILL/'scripts/transfer_skill.py'),'check','--source',str(SKILL)]
   else:
    cmd=[sys.executable,'-B',str(SKILL/'scripts/sirna_portable.py'),args.command]
    for key,value in vars(args).items():
     if key!='command':cmd.extend(['--'+key.replace('_','-'),str(value)])
   env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1';return subprocess.run(cmd,env=env,check=False).returncode
  print(json.dumps(result,indent=2,allow_nan=False));return 2 if result.get('status') in {'FAILED','BLOCKED_MISSING_EVIDENCE','FAILED_DECLARED_TECHNICAL_GATES','BLOCKED_MISSING_TECHNICAL_EVIDENCE'} else 0
 except (ValueError,OSError,KeyError,TypeError) as e:
  print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'error':str(e)},indent=2));return 2
if __name__=='__main__':raise SystemExit(main())
