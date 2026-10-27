#!/usr/bin/env python3
"""Portable technical checks, not a siRNA generator or biological validator. Python3.10+."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,re,shutil,sys,collections
from pathlib import Path
VERSION='2.0.0'
STATES={'PASSED','FAILED','BLOCKED_MISSING_EVIDENCE','NOT_RUN','NOT_APPLICABLE'}
MIN_GATES={'reference_identity','sequence_validation','transcript_coverage','efficacy_model_applicability','both_strand_specificity','specificity_acceptance','immune_assessment','construct_chemistry','delivery_assay_context','experimental_efficacy','independent_validation'}
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def secret_check(value):
 if isinstance(value,dict):
  for k,v in value.items():
   if k.lower() in {'api_key','access_token','refresh_token','password','secret','authorization'} and v not in (None,'',False):raise ValueError('Credential values must not be stored in portable configuration: '+k)
   secret_check(v)
 elif isinstance(value,list):
  for v in value:secret_check(v)
def localpath(value,base):
 p=Path(value).expanduser()
 return p.resolve() if p.is_absolute() else (base/p).resolve()
def preflight(config_path):
 cfg=load(config_path);secret_check(cfg);base=Path(config_path).resolve().parent;checks=[]
 if cfg.get('schema_version')!=1:raise ValueError('Unsupported environment schema_version')
 for name,value in cfg.get('executables',{}).items():
  resolved=None
  if value:
   if not isinstance(value,str):raise ValueError('Executable must be a path or program name')
   if Path(value).is_absolute() or '/' in value or '\\' in value:resolved=str(localpath(value,base))
   else:resolved=shutil.which(value)
  present=bool(resolved and Path(resolved).is_file() and os.access(resolved,os.X_OK));checks.append({'name':name,'kind':'executable','path':resolved,'present':present,'readiness':'AVAILABLE_UNVERIFIED' if present else 'REQUIRES_INSTALLATION','execution_verified':False})
 for asset in cfg.get('assets',[]):
  value=asset.get('path');path=localpath(value,base) if value else None;present=bool(path and path.is_file());expected=asset.get('sha256');actual=sha(path) if present else None
  if expected is not None and not re.fullmatch('[0-9a-f]{64}',expected):raise ValueError('Expected SHA256 must be64 lowercase hex characters')
  matched=present and expected is not None and expected==actual;checks.append({'name':asset['name'],'kind':'asset','path':str(path) if path else None,'present':present,'sha256':actual,'expected_sha256':expected,'checksum_match':matched,'readiness':'AVAILABLE_UNVERIFIED' if present else 'REQUIRES_INSTALLATION','execution_verified':False})
 errors=[c['name'] for c in checks if not c['present'] or c.get('expected_sha256') and not c.get('checksum_match')]
 if not checks:errors.append('No executable or asset checks configured')
 return {'helper_version':VERSION,'status':'BLOCKED_MISSING_CONFIGURATION' if errors else 'FILES_PRESENT_EXECUTION_UNVERIFIED','checks':checks,'missing_or_mismatched':errors,'backend_inference_verified':False,'biological_validation':'NOT_ESTABLISHED','rights_reviewed':cfg.get('rights_reviewed') is True,'note':'No command, model, download or service invoked; file presence and checksums are not inference.'}
def objective_check(path):
 obj=load(path);secret_check(obj);errors=[]
 if obj.get('schema_version')!=1:errors.append('schema_version must be1')
 if obj.get('design_type')!='sirna':errors.append('Only design_type=sirna is supported')
 if not isinstance(obj.get('experiment_id'),str) or not obj['experiment_id'].strip():errors.append('Explicit experiment_id required')
 if obj.get('organism')!='Homo sapiens':errors.append('Exercised default requires explicit Homo sapiens; other species need validated adapters/references')
 if obj.get('representation')!='paired19nt_RNA_cores':errors.append('Other representations need a separately validated adapter')
 if type(obj.get('requested_count')) is not int or obj['requested_count']<1:errors.append('requested_count must be a positive integer')
 target=obj.get('target');target=target if isinstance(target,dict) else {};acc=target.get('primary_accession_version');fasta=target.get('sequence_fasta')
 if not acc and not fasta:errors.append('Exact transcript.version or explicit sequence_fasta required')
 if acc and (not isinstance(acc,str) or not re.fullmatch(r'NM_[0-9]+\.[1-9][0-9]*',acc)):errors.append('Accession format invalid; preserve source token and resolve it, do not repair silently')
 if fasta and not localpath(fasta,Path(path).resolve().parent).is_file():errors.append('sequence_fasta does not exist')
 for reference in obj.get('coverage_references',[]):
  if not isinstance(reference,str) or not re.fullmatch(r'NM_[0-9]+\.[1-9][0-9]*',reference):errors.append('Invalid exact coverage-reference token')
 mode=obj.get('study_mode');mutation=obj.get('mutation_specification')
 if mode not in {'shared','comparative','mutation_selective'}:errors.append('study_mode must be shared/comparative/mutation_selective')
 if mode=='shared':arm='NOT_APPLICABLE'
 elif not isinstance(mutation,dict) or not all(isinstance(mutation.get(k),str) and mutation[k].strip() for k in ['exact_nucleotide_change_or_verified_mutant_sequence','reference_accession_version','mutant_vs_wild_type_objective']):arm='BLOCKED_PENDING_MUTATION_SPECIFICATION'
 else:arm='SPECIFIED_REQUIRES_REFERENCE_ALLELE_VALIDATION'
 return {'status':'FAILED' if errors else 'VALID_REQUEST_REFERENCE_VALIDATION_REQUIRED','errors':errors,'mutation_arm_status':arm,'shared_sequence_work_may_proceed':not errors and mode in {'shared','comparative'},'mutant_constructed':False,'biology':'PARTIAL','source_objective_sha256':sha(path)}
def fasta_read(path,alphabet):
 headers=[];sequences=[]
 for line in Path(path).read_text(encoding='utf-8').splitlines():
  if not line:continue
  if line.startswith('>'):headers.append(line[1:]);sequences.append('')
  else:
   if not sequences:raise ValueError('Sequence before FASTA header')
   sequences[-1]+=line
 if len(headers)!=1 or not sequences[0]:raise ValueError('Exactly one nonempty transcript required')
 allowed=set('ACGT' if alphabet=='DNA' else 'ACGU')
 if set(sequences[0])-allowed:raise ValueError('Reference alphabet/case/ambiguity mismatch; no silent repair')
 return headers[0],sequences[0].replace('T','U') if alphabet=='DNA' else sequences[0]
def csv_rows(path):
 with Path(path).open(newline='',encoding='utf-8-sig') as f:
  reader=csv.reader(f)
  try:header=next(reader)
  except StopIteration:raise ValueError('Empty CSV')
  if any(not k.strip() for k in header) or len(set(header))!=len(header):raise ValueError('Blank/repeated CSV headers require documented positional repair before parsing')
  result=[]
  for line,row in enumerate(reader,2):
   if not row:continue
   if len(row)!=len(header):raise ValueError('CSV width mismatch at physical record '+str(line))
   result.append(dict(zip(header,row)))
 return result
def sites(sequence,query):
 out=[];start=sequence.find(query)
 while start>=0:out.append(start+1);start=sequence.find(query,start+1)
 return out
def rc(sequence):return sequence.translate(str.maketrans('ACGU','UGCA'))[::-1]
def candidates_check(csv_path,fasta_path,alphabet):
 header,target=fasta_read(fasta_path,alphabet);data=csv_rows(csv_path);required={'candidate_id','guide_sequence','passenger_sequence','target_start','target_end'}
 if not data:raise ValueError('Candidate CSV contains no rows')
 if not required<=set(data[0]):raise ValueError('Required candidate columns missing: '+','.join(sorted(required-set(data[0]))))
 counts=collections.Counter(r['candidate_id'] for r in data);result=[]
 for row in data:
  errors=[];g=row['guide_sequence'];p=row['passenger_sequence'];cid=row['candidate_id']
  if not cid or counts[cid]!=1:errors.append('nonunique_or_empty_candidate_id')
  if len(g)!=19 or len(p)!=19 or set(g+p)-set('ACGU'):errors.append('requires_unambiguous_uppercase19nt_RNA_cores')
  if rc(g)!=p:errors.append('guide_passenger_not_complementary')
  try:
   start=int(row['target_start']);end=int(row['target_end'])
   if start<1 or end!=start+18 or end>len(target) or target[start-1:end]!=p:errors.append('primary_coordinates_not_exact')
  except ValueError:start=end=0;errors.append('invalid_integer_coordinates')
  if row.get('transcript_id') and row['transcript_id']!=header.split()[0]:errors.append('transcript_identifier_mismatch')
  matches=sites(target,p) if len(p)==19 else [];unique=len(matches)==1;full=start>=20 and end+19<=len(target)
  result.append({'candidate_id':cid,'core_sequence_status':'FAILED' if errors else 'PASSED','errors':errors,'exact_primary_sites_1based':matches,'unique_primary_site':unique,'full19nt_flanks':full,'default_model_input_eligible':not errors and unique and full,'qualification':'NOT_ESTABLISHED_BY_SEQUENCE_CHECK'})
 return {'status':'FAILED' if any(r['errors'] for r in result) else 'PASSED','rows':len(result),'records':result,'reference_header':header,'reference_alphabet_declared':alphabet,'comparison_transform':'TtoU in memory only' if alphabet=='DNA' else 'none','input_sha256':{'candidate_csv':sha(csv_path),'reference_fasta':sha(fasta_path)},'new_candidates_generated':0,'model_inference_runs':0}
def gates_check(path):
 obj=load(path);gates=obj.get('gates');errors=[];derived=[];seen=set();base=Path(path).resolve().parent
 if not isinstance(gates,list) or not gates:raise ValueError('Nonempty gates list required')
 for gate in gates:
  required_fields={'name','required','status','evidence_refs','failed_criteria','missing_evidence','warnings','method_version'}
  if not isinstance(gate,dict) or not required_fields<=set(gate):raise ValueError('Gate schema incomplete')
  if type(gate['required']) is not bool:raise ValueError('required must be a literal Boolean, not a string/number')
  if gate['name'] in seen:raise ValueError('Duplicate gate name')
  seen.add(gate['name'])
  if gate['status'] not in STATES:raise ValueError('Invalid gate status')
  for field in ['evidence_refs','failed_criteria','missing_evidence','warnings']:
   if not isinstance(gate[field],list) or any(not isinstance(x,str) for x in gate[field]):raise ValueError('Gate lists must contain strings')
  state=gate['status'];issues=[]
  if gate['required'] and state=='NOT_APPLICABLE':raise ValueError('Required gate cannot evade evidence as NOT_APPLICABLE')
  if gate['failed_criteria']:state='FAILED'
  elif gate['missing_evidence'] or state=='NOT_RUN':state='BLOCKED_MISSING_EVIDENCE'
  if state=='PASSED':
   if not gate['evidence_refs']:issues.append('PASSED_without_evidence_refs')
   for reference in gate['evidence_refs']:
    if not localpath(reference.split('#',1)[0],base).is_file():issues.append('evidence_file_unavailable:'+reference)
   if issues:state='BLOCKED_MISSING_EVIDENCE'
  derived.append({'name':gate['name'],'required':gate['required'],'source_status':gate['status'],'derived_state':state,'technical_issues':issues})
 missing=sorted(MIN_GATES-seen);mandatory=[g for g in derived if g['required']]
 # An optional node cannot satisfy a required minimum category.
 missing=sorted(set(missing)|{g['name'] for g in derived if g['name'] in MIN_GATES and not g['required']})
 state='FAILED' if any(g['derived_state']=='FAILED' for g in mandatory) else 'BLOCKED_MISSING_EVIDENCE' if missing or any(g['derived_state']!='PASSED' for g in mandatory) else 'PASSED'
 return {'configured_required_evidence_state':state,'gate_records':derived,'missing_required_categories':missing,'fully_qualified':False,'biology':'NOT_ESTABLISHED_BY_THIS_UTILITY','note':'Artifact existence and gate claims require scientific review; this helper never certifies biological validation.'}
def benchmark_check(path,sequence_column,label_column,unit):
 data=csv_rows(path)
 if not data or sequence_column not in data[0] or label_column not in data[0]:raise ValueError('Dataset/explicit sequence or label column missing')
 valid=[];missing=0;groups=collections.Counter()
 for row in data:
  try:value=float(row[label_column]);value=value if math.isfinite(value) else None
  except ValueError:value=None
  if value is None:missing+=1
  else:valid.append(value)
  sequence=row[sequence_column]
  if sequence and not set(sequence)-set('ACGU'):groups[min(sequence,rc(sequence))]+=1
 return {'status':'BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET','rows':len(data),'numeric_labels':len(valid),'missing_or_nonfinite_labels':missing,'source_label_unit_declared':unit,'numeric_min':min(valid) if valid else None,'numeric_max':max(valid) if valid else None,'repeated_sequence_groups':sum(n>1 for n in groups.values()),'independence_established':False,'predictions_attempted':0,'note':'Technical table audit only; final-checkpoint exposure, endpoint validity, study/target splits and chemistry require separate evidence.'}
def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
 p=sub.add_parser('preflight');p.add_argument('--config',required=True)
 p=sub.add_parser('validate-objective');p.add_argument('--objective',required=True)
 p=sub.add_parser('validate-candidates');p.add_argument('--candidates',required=True);p.add_argument('--fasta',required=True);p.add_argument('--reference-alphabet',required=True,choices=['DNA','RNA'])
 p=sub.add_parser('check-gates');p.add_argument('--gates',required=True)
 p=sub.add_parser('audit-label-table');p.add_argument('--dataset',required=True);p.add_argument('--sequence-column',required=True);p.add_argument('--label-column',required=True);p.add_argument('--label-unit',required=True)
 args=parser.parse_args()
 try:
  if args.command=='preflight':result=preflight(args.config)
  elif args.command=='validate-objective':result=objective_check(args.objective)
  elif args.command=='validate-candidates':result=candidates_check(args.candidates,args.fasta,args.reference_alphabet)
  elif args.command=='check-gates':result=gates_check(args.gates)
  else:result=benchmark_check(args.dataset,args.sequence_column,args.label_column,args.label_unit)
  print(json.dumps(result,indent=2,allow_nan=False));return 2 if result.get('status') in {'FAILED','BLOCKED_MISSING_CONFIGURATION','BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET'} or result.get('configured_required_evidence_state') in {'FAILED','BLOCKED_MISSING_EVIDENCE'} else 0
 except (ValueError,OSError,KeyError,TypeError) as e:
  print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'error':str(e),'helper_version':VERSION},indent=2));return 2
if __name__=='__main__':raise SystemExit(main())
