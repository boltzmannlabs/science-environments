#!/usr/bin/env python3
"""Independent current-task benchmark audit; never substitutes Prodigy for REF15."""
import argparse,csv,hashlib,importlib.metadata,json,math,re,shutil,subprocess,time
from pathlib import Path
import numpy as np
from scipy.spatial.distance import cdist
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def table(p,rows):
 if not rows:return
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def residues(m,c):return [r for r in m[c] if r.id[0]==' ']
def seq(m,c,n=None):return ''.join(seq1(r.resname) for r in residues(m,c))[:n]
def contacts(m,ab='HL',ag='C'):
 aa=[a for c in ab for a in m[c].get_atoms() if a.element not in ('H','D')];bb=[a for a in m[ag].get_atoms() if a.element not in ('H','D')];d=cdist([a.coord for a in aa],[a.coord for a in bb]);i,j=np.where(d<5.5)
 pairs=set((aa[x].parent.parent.id,aa[x].parent.id,bb[y].parent.id) for x,y in zip(i,j))
 ag_res=residues(m,ag);ag_index={id(z):i+1 for i,z in enumerate(ag_res)}
 return {'contact_atom_pairs_lt5_5A':len(i),'contact_residue_pairs_lt5_5A':len(pairs),'severe_interchain_atom_pairs_lt2A':int((d<2).sum()),'min_interchain_distance_A':float(d.min()),'epitope_indices_1based':sorted(set(ag_index[id(bb[y].parent)] for y in j))}
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent-run',type=Path,required=True);p.add_argument('--source-run',type=Path,required=True);p.add_argument('--result-run',type=Path,required=True);a=p.parse_args();r=a.result_run;raw=r/'evidence/raw';raw.mkdir(parents=True,exist_ok=True);logs=a.source_run/'logs';logs.mkdir(parents=True,exist_ok=True)
 b=a.source_run/'inputs/released_archive/ab_seldon_trastuzumab_optimization_tests';her2=b/'her2_test_data';parser=PDBParser(QUIET=True)
 # Recalculate published values directly from original non-indented initial/final records.
 published=[]
 for arm in ['diversity','random']:
  for n in range(1,9):
   f=her2/f'analyses/energy/swap_001_{arm}{n}.log';v=[]
   for line in f.read_text().splitlines():
    if line.startswith(('bs1_','FINAL_')):
     tokens=line.split('|')
     try:v.append((tokens[0],float(tokens[1])))
     except (IndexError,ValueError):pass
   initial=v[0];final=[x for x in v if x[0].startswith('FINAL_')][-1]
   published.append({'arm':arm,'run':n,'initial_id':initial[0],'initial_REF15_REU':initial[1],'final_id':final[0],'final_REF15_REU':final[1],'delta_REU':final[1]-initial[1],'source_log':str(f.relative_to(a.source_run)),'log_sha256':sha(f)})
 table(r/'published_endpoints.csv',published)
 # Audit historical coordinates and masks against archived generation settings.
 cands={x['candidate_id']:x for x in csv.DictReader(open(a.parent_run/'candidates.csv'))};sids=[x['candidate_id'] for x in csv.DictReader(open(a.parent_run/'shortlist.csv'))]
 native=parser.get_structure('native',a.parent_run/'evidence/reference/1N8Z_deposited_complex.pdb')[0];rh=seq(native,'B',120);rl=seq(native,'A',107)
 executed={'B':set(range(26,33))|set(range(50,66))|set(range(97,110)),'A':set(range(24,35))|set(range(50,57))|set(range(89,98))}
 early_scope=json.load(open(a.parent_run/'evidence/mappings/design_scope.json'));declared={c:set(j for z in early_scope['editable'][c] for j in range(z['seq_range_1based'][0],z['seq_range_1based'][1]+1)) for c in ['A','B']}
 quality=[];detail={}
 for cid in sids:
  x=cands[cid];m=parser.get_structure(cid,a.parent_run/f'structures/{cid}_reconstructed.pdb')[0];changes=[];missing=[];outside=[];outside_declared=[];bc=[]
  for chain,key,refseq in [('B','heavy_chain',rh),('A','light_chain',rl)]:
   rs=residues(m,chain)
   for i,(aa,bb) in enumerate(zip(refseq,x[key]),1):
    if aa!=bb:
     changes.append(f'{chain}:{aa}{i}{bb}');names={z.name for z in rs[i-1]}
     if 'O' not in names:missing.append(f'{chain}:{i}')
     if i not in executed[chain]:outside.append(f'{chain}:{i}')
     if i not in declared[chain]:outside_declared.append(f'{chain}:{i}')
   bc.extend([np.linalg.norm(rs[i-1]['CA'].coord-residues(native,chain)[i-1]['CA'].coord) for i in range(1,len(refseq)+1)])
  row={'candidate_id':cid,'heavy_edits':sum(x!=y for x,y in zip(rh,x['heavy_chain'])),'light_edits':sum(x!=y for x,y in zip(rl,x['light_chain'])),'outside_executed_mask':len(outside),'outside_early_declared_mask':len(outside_declared),'extra_heavy_cysteines':x['heavy_chain'].count('C')-rh.count('C'),'legacy_missing_carbonyl_O_at_mutated_residues':len(missing),'legacy_ca_rmsd_A':float(np.sqrt(np.mean(np.square(bc)))),'legacy_structural_binding_claim_valid':False}
  quality.append(row);detail[cid]={'changes':changes,'missing_backbone_O_residues':missing,'outside_executed_mask':outside,'outside_early_declared_mask':outside_declared}
 table(r/'sequence_geometry_audit.csv',quality);dump(raw/'sequence_geometry_details.json',detail)
 # Preserve a traceable candidate assessment panel, not a newly generated library.
 table(r/'candidates.csv',[{'candidate_id':cid,'parent_id':'REF_1N8Z','role':'historical_shortlisted_design_under_validation','heavy_chain':cands[cid]['heavy_chain'],'light_chain':cands[cid]['light_chain'],'paired_sha256':hashlib.sha256((cands[cid]['heavy_chain']+'|'+cands[cid]['light_chain']).encode()).hexdigest(),'new_generation':False,'abodybuilder2_structure':f'structures/{cid}_abodybuilder2_vhvl.pdb','ref15_status':'blocked_missing_PyRosetta_and_Amber'} for cid in sids])
 with (r/'sequences.fasta').open('w') as f:
  for cid in sids:
   for ch,key in [('heavy','heavy_chain'),('light','light_chain')]:f.write(f'>{cid}|chain={ch}\n{cands[cid][key]}\n')
 # Explicit construct comparison.
 paper=b/'ab-seldon-paper-v6.2/diversity/complex_1n8z-frk-reduced.pdb';pm=parser.get_structure('paper',paper)[0]
 dump(raw/'construct_comparison.json',{'historical_chain_lengths':{c:len(residues(native,c)) for c in ['A','B','C']},'paper_chain_lengths':{c:len(residues(pm,c)) for c in ['H','L','C']},'reference_variable_domain_sequences_match':seq(pm,'H')==rh and seq(pm,'L')==rl,'paper_antigen_sequence':seq(pm,'C'),'paper_antigen_region':'HER2 486-607 with gap restored from 8FFJ (SI)','old_full_antigen_sha256':hashlib.sha256(seq(native,'C').encode()).hexdigest(),'paper_antigen_sha256':hashlib.sha256(seq(pm,'C').encode()).hexdigest()})
 # Independent Prodigy validation: explicit settings; original published REF15 is never called Prodigy.
 paths=[('BENCHMARK_NATIVE','released_input',paper,'H,L')]
 for arm,label,fragment in [('diversity','PUBLISHED_DIV6','div6_000024'),('random','PUBLISHED_RAN4','ran4_000015')]:
  f=next((her2/'experiments/final_complexes').glob(f'*{fragment}.pdb'));paths.append((label,'published_optimized_control',f,'H,L'))
 refined=json.load(open(raw/'complex_refinement.json'))
 for q in refined:
  if q['success']:paths.append((q['candidate_id'],'new_ABodyBuilder2_OpenMM_complex',r/q['output'],'H,L'))
 # Re-run old estimates as a reproducibility check, never as physically valid candidate claims.
 paths += [('REF_1N8Z','legacy_full_construct',a.parent_run/'structures/REF_1N8Z_reference.pdb','A,B')]+[(cid,'legacy_full_construct',a.parent_run/f'structures/{cid}_reconstructed.pdb','A,B') for cid in sids]
 results=[];geom=[]
 for cid,scope,f,selection in paths:
  cmd=['/home/boltzmann10/anaconda3/bin/prodigy',str(f),'--selection',selection,'C','--temperature','25','--distance-cutoff','5.5','--acc-threshold','0.05','-np','1'];t=time.monotonic();run=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
  (logs/f'prodigy_{scope}_{cid}.log').write_text('COMMAND '+json.dumps(cmd)+'\nEXIT '+str(run.returncode)+'\n'+run.stdout+'\nSTDERR\n'+run.stderr)
  print('PRODIGY',cid,scope,'exit',run.returncode,flush=True)
  def extract(pattern):
   match=re.search(pattern,run.stdout);return float(match.group(1)) if match else None
  dg=extract(r'Predicted binding affinity.*?:\s*([-+\d.eE]+)');kd=extract(r'Predicted dissociation constant.*?:\s*([-+\d.eE]+)');ic=extract(r'No\. of intermolecular contacts:\s*(\d+)')
  if run.returncode!=0 or dg is None:raise RuntimeError(f'Prodigy failed for {cid}, see log')
  results.append({'candidate_id':cid,'structural_scope':scope,'dG_kcal_mol':dg,'KD_M':kd,'IC_residue_pairs':int(ic),'seconds':time.monotonic()-t,'original_benchmark_REF15':False,'source_sha256':sha(f)})
  if scope!='legacy_full_construct':
   m=parser.get_structure('x',f)[0];g=contacts(m);g.update(candidate_id=cid,scope=scope);geom.append(g)
 table(r/'prodigy_crosscheck.csv',results);dump(raw/'interface_geometry.json',geom)
 # Independent candidate-pair diversity, descriptive only (no source acceptance cutoff).
 diversity=[]
 for i,cid in enumerate(sids):
  for other in sids[i+1:]:diversity.append({'candidate_1':cid,'candidate_2':other,'paired_hamming_distance':sum(x!=y for key in ['heavy_chain','light_chain'] for x,y in zip(cands[cid][key],cands[other][key]))})
 table(r/'pairwise_diversity.csv',diversity)
 versions={name:importlib.metadata.version(name) for name in ['biopython','numpy','scipy','prodigy-prot']};dump(raw/'audit_tool_versions.json',versions)
 print('PUBLISHED_RUNS',len(published),'SHORTLIST',len(sids),'PRODIGY_RECORDS',len(results));print('QUALITY',json.dumps(quality));print('PRODIGY',json.dumps(results))
if __name__=='__main__':main()
