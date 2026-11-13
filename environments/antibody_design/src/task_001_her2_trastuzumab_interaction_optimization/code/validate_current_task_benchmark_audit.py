#!/usr/bin/env python3
"""Validate actual current-task audit identities, paths, numerical checks and hashes."""
import ast,csv,hashlib,json,math,re
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1
TASK='task_001_her2_trastuzumab_interaction_optimization';RUN='20261111_ref15_benchmark_audit'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 root=Path.cwd();r=root/'results'/TASK/RUN;s=root/'src'/TASK/'runs'/RUN;checks={};issues=[]
 def check(name,value):checks[name]=bool(value);issues.extend([] if value else [name])
 for f in list(r.rglob('*.json'))+list((s/'configs').rglob('*.json'))+[s/'provenance.json']:
  try:json.load(open(f));ok=True
  except Exception:ok=False
  check('json_parse:'+str(f.relative_to(root)),ok)
 for f in r.glob('*.csv'):
  v=list(csv.reader(open(f,newline='')));check('csv_widths:'+f.name,bool(v) and all(len(x)==len(v[0]) for x in v) and len(set(v[0]))==len(v[0]))
 panel=list(csv.DictReader(open(r/'candidates.csv')));ids=[x['candidate_id'] for x in panel]
 check('only_existing_five_design_ids',set(ids)=={'AB_04','AB_05','AB_08','AB_13','AB_20'} and len(ids)==5)
 fasta={};key=None
 for line in (r/'sequences.fasta').read_text().splitlines():
  if line.startswith('>'):key=line[1:];fasta[key]=''
  elif line.strip():fasta[key]+=line.strip()
 check('fasta_10_records',len(fasta)==10)
 parent={x['candidate_id']:x for x in csv.DictReader(open(s/'inputs/parent_candidates.csv'))};check('parent_generation_inventory_20',len(parent)==20)
 parser=PDBParser(QUIET=True);ref=parser.get_structure('r',r/'evidence/reference/benchmark_reference_martin.pdb')[0];refseq=''.join(seq1(x.resname) for x in ref['C'] if x.id[0]==' ')
 allseq=True;allO=True;antigen=True
 for x in panel:
  cid=x['candidate_id'];p=parser.get_structure(cid,r/f'structures/{cid}_openmm_refined_complex.pdb')[0]
  for c,label in [('H','heavy'),('L','light')]:
   rs=[v for v in p[c] if v.id[0]==' '];seq=''.join(seq1(v.resname) for v in rs)
   allseq &= seq==x[label+'_chain']==parent[cid][label+'_chain']==fasta[cid+'|chain='+label]
   allO &= all('O' in v for v in rs)
  antigen &= ''.join(seq1(v.resname) for v in p['C'] if v.id[0]==' ')==refseq and len(refseq)==122
 check('sequence_matches_structure_and_parent',allseq);check('new_Fv_backbone_carbonyl_O_complete',allO);check('correct_122aa_antigen_sequence',antigen)
 # Independent recomputation of current-RMSD from transformed saved coordinates.
 data=json.load(open(r/'evidence/raw/pymol_cdr_validation.json'))['records'];numeric=True;maps=True
 for d in data:
  m=parser.get_structure('m',r/d['template_complex_path'])[0]
  for region,c,start,end in [('H1','H',26,32),('H2','H',52,56),('H3','H',95,102),('L1','L',24,34),('L2','L',50,56),('L3','L',89,97)]:
   a={v.id:v['CA'].coord for v in m[c] if v.id[0]==' ' and start<=v.id[1]<=end};b={v.id:v['CA'].coord for v in ref[c] if v.id[0]==' ' and start<=v.id[1]<=end}
   maps &= set(a)==set(b) and len(a)>0
   if set(a)!=set(b):numeric=False;continue
   direct=float(np.sqrt(np.mean([sum((a[k]-b[k])**2) for k in sorted(a)])))
   numeric &= abs(direct-d[region+'_rmsd_A'])<0.002
 check('all_CDR_CA_numbering_maps_equal',maps);check('independent_RMSD_recalculation_matches_PyMOL',numeric)
 check('six_ABodyBuilder_predictions_completed',len(json.load(open(r/'evidence/raw/abodybuilder2/run_status.json')))==6 and all(x['status']=='completed' for x in json.load(open(r/'evidence/raw/abodybuilder2/run_status.json'))))
 refined=json.load(open(r/'evidence/raw/complex_refinement.json'));check('six_complex_refinements_successful',len(refined)==6 and all(x['success'] for x in refined))
 plogs=list((s/'logs').glob('prodigy_*.log'));check('fifteen_Prodigy_logs_exit_0',len(plogs)==15 and all('\nEXIT 0\n' in f.read_text() for f in plogs))
 p=list(csv.DictReader(open(r/'published_endpoints.csv')));check('sixteen_original_endpoint_logs',len(p)==16 and len({(v['arm'],v['run']) for v in p})==16)
 localbench=(root/'benchmark/monoclonal_antibody_design'/f'{TASK}.md').read_text();check('matched_task_benchmark_identity',TASK in localbench and 'HER2' in localbench)
 check('published_winner_values_match_task_benchmark',any(v['arm']=='diversity' and v['run']=='6' and abs(float(v['final_REF15_REU'])-(-94.8663))<0.0001 for v in p) and any(v['arm']=='random' and v['run']=='4' and abs(float(v['final_REF15_REU'])-(-92.6947))<0.0001 for v in p))
 outputs=list(csv.DictReader(open(r/'predictions.csv')));check('REF15_not_fabricated',len(outputs)==5 and all(v['REF15_REU']=='' for v in outputs))
 for f in [r/'report.md',r/'README.md',s/'execution.md']:
  for rel in re.findall(r'\]\(([^)]+)\)',f.read_text()):
   if '://' not in rel:check('link:'+str(f.relative_to(root))+':'+rel,(f.parent/rel.split('#')[0]).resolve().exists())
 for v in json.load(open(s/'configs/code_hashes.json')):
  f=s/v['path'];check('code_hash:'+f.name,sha(f)==v['sha256']);ast.parse(f.read_text())
 prov=json.load(open(s/'provenance.json'));check('source_result_run_id_agrees',prov['task_id']==TASK and prov['run_id']==RUN and (s/prov['results_directory']).resolve()==r.resolve())
 # Exclude the manifest and this validation record themselves to avoid self-hashes.
 manifest=[{'path':str(f.relative_to(r)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(r.rglob('*')) if f.is_file() and f.name not in ['validation.json','artifact_checksums.json']]
 (r/'evidence/artifact_checksums.json').write_text(json.dumps(manifest,indent=2)+'\n');check('artifact_hashes_recomputed',all(sha(r/v['path'])==v['sha256'] for v in manifest))
 result={'task_id':TASK,'run_id':RUN,'validated_at_UTC':datetime.now(timezone.utc).isoformat(),'packaging_validation':'passed' if all(checks.values()) else 'failed','scientific_benchmark_reproduction':'PARTIAL_PRIMARY_REF15_BLOCKED','counts':{'inherited_designs':5,'native_ABodyBuilder_controls':1,'published_optimized_controls':2,'source_log_runs':16,'abodybuilder_predictions':6,'complex_refinements':6,'prodigy_invocations':15,'metric_gap_categories':len(list(csv.DictReader(open(r/'metric_gaps.csv')))),'comparison_rows':len(list(csv.DictReader(open(r/'benchmark_comparison.csv'))))},'checks':checks,'issues':issues,'scope':'Current task only. Packaging and execution verification is not proof of REF15 reproduction or affinity improvement.'}
 (r/'evidence/validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'packaging':result['packaging_validation'],'scientific':result['scientific_benchmark_reproduction'],'check_count':len(checks),'counts':result['counts'],'issues':issues},indent=2))
 if issues:raise SystemExit(1)
if __name__=='__main__':main()
