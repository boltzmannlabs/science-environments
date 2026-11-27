import csv,hashlib,json,math,os,pathlib,sys,time
import numpy as np
import torch
from Bio.PDB.Polypeptide import index_to_one
R=pathlib.Path(__file__).resolve().parent; O=R/'results/local/task_005_sun_leh_pythia/v2/assisted/fresh-20261120'
S=pathlib.Path('retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433')
sys.path.insert(0,str(S))
from pythia.masked_ddg_scan import get_torch_model
from pythia.pdb_utils import read_pdb_to_protbb,get_neighbor
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
man=json.loads((O/'INPUT_MANIFEST.json').read_text()); plan=json.loads((O/'RUN_PLAN.json').read_text()); pre=json.loads((O/'preflight.json').read_text())
assert plan['status']=='frozen_before_inference' and sha(O/'INPUT_MANIFEST.json')==plan['input_manifest_sha256']
assert sha(O/'original_1NWW.pdb')==man['input_pdb_sha256'] and sha(O/'monomer_A.pdb')==man['monomer_A_pdb_sha256'] and sha(O/'residue_map.csv')==man['residue_map_sha256']
for f,h in {**man['source_files_sha256'],**man['checkpoints_sha256']}.items(): assert sha(S/f)==h
mapping=list(csv.DictReader((O/'residue_map.csv').open())); torch.set_num_threads(4); torch.set_num_interop_threads(1);torch.manual_seed(0)
models={c:get_torch_model(str(S/f'pythia/pythia-{c}.pt'),'cpu') for c in ('c','p')}; alphabet=''.join(index_to_one(i) for i in range(20)); assert len(set(alphabet))==20
fields=['context','chain','parent_position','pdb_resseq','insertion_code','model_index_1based','wild_type','mutant','mutation','score_c','score_p','score_sum','score_mean','catalytic_site_concern']
allrows=[]; identities=[]; raw={}; t0=time.time()
for context,path in [('monomer_A',O/'monomer_A.pdb'),('dimer_AB',O/'original_1NWW.pdb')]:
 p=read_pdb_to_protbb(str(path)); n,e,seq=get_neighbor(p,neighbor=32,noise_level=0.0,train=False); rec=[r for r in mapping if r['context']==context and r['eligible']=='True']; assert len(rec)==len(seq)
 with torch.no_grad():
  result={}
  for k,m in models.items():
   logits,_=m(n.float(),e.float()); probs=torch.softmax(logits,dim=-1); assert logits.shape==(len(rec),21) and torch.isfinite(logits).all() and torch.isfinite(probs).all()
   result[k]=(logits.cpu().numpy(),probs.cpu().numpy())
   raw[context+'_'+k+'_logits']=result[k][0];raw[context+'_'+k+'_probabilities']=result[k][1]
 for i,r in enumerate(rec):
  wi=int(seq[i]); assert index_to_one(wi)==r['wt'] and int(r['retained_index_1based'])==i+1
  for a in range(20):
   vals={k:float(-np.log(result[k][1][i,a]/result[k][1][i,wi])) for k in ('c','p')}
   sm=vals['c']+vals['p']; alt=index_to_one(a); pos=int(r['parent_position'])
   row=dict(context=context,chain=r['chain'],parent_position=pos,pdb_resseq=int(r['pdb_resseq']),insertion_code=r['insertion_code'],model_index_1based=i+1,wild_type=r['wt'],mutant=alt,mutation=f"{r['wt']}{pos}{alt}",score_c=vals['c'],score_p=vals['p'],score_sum=sm,score_mean=sm/2,catalytic_site_concern=pos in (53,55,99,101,132))
   (identities if a==wi else allrows).append(row)
 print(context,'scored residues',len(rec),'elapsed_s',round(time.time()-t0,3),flush=True)
np.savez_compressed(O/'native_model_outputs.npz',**raw)
def write(name,rows,cols=fields):
 with (O/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
write('all_scores.csv',allrows);write('identity_controls.csv',identities)
ranked=sorted(allrows,key=lambda r:(r['context'],r['chain'],r['score_sum'],r['parent_position'],r['mutant']))
write('all_scores_ranked.csv',ranked)
best={}
for r in allrows:
 k=(r['context'],r['chain'],r['parent_position']); old=best.get(k)
 if old is None or (r['score_sum'],r['mutant'])<(old['score_sum'],old['mutant']):best[k]=r
bestrows=sorted(best.values(),key=lambda r:(r['context'],r['chain'],r['score_sum'],r['parent_position'],r['mutant']))
write('best_per_position.csv',bestrows)
primary=[r for r in bestrows if r['context']=='monomer_A' and r['score_sum'] < -2]
mean=[r for r in bestrows if r['context']=='monomer_A' and r['score_mean'] < -2]
dimer=[r for r in bestrows if r['context']=='dimer_AB' and r['score_sum'] < -2]
write('library_sum_monomer_A.csv',primary);write('library_mean_monomer_A.csv',mean);write('library_sum_dimer_AB_by_chain.csv',dimer)
parent=''.join(l.strip() for l in (O/'parent.fasta').read_text().splitlines() if not l.startswith('>'))
selections=[]
with (O/'candidates.fasta').open('w') as f:
 for rank,r in enumerate(primary,1):
  idx=r['parent_position']-1;assert parent[idx]==r['wild_type']; mutant=parent[:idx]+r['mutant']+parent[idx+1:]; assert len(mutant)==len(parent) and sum(a!=b for a,b in zip(mutant,parent))==1
  ident=r['mutation']; digest=hashlib.sha256(mutant.encode()).hexdigest(); selections.append({'candidate_id':ident,'rank':rank,'sequence_sha256':digest});f.write('>'+ident+'|monomer_A|score_sum='+str(r['score_sum'])+'\n'+mutant+'\n')
write('selection.csv',selections,['candidate_id','rank','sequence_sha256'])
seal={'selection_sha256':sha(O/'selection.csv'),'ranking_sha256':sha(O/'all_scores_ranked.csv'),'parent_sequence_sha256':man['parent_sequence_sha256'],'plan_sha256':sha(O/'RUN_PLAN.json'),'cutoff':'strict sum < -2','selection_count':len(selections),'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'comparison_started':False}
(O/'selection_seal.json').write_text(json.dumps(seal,indent=2)+'\n')
summary={'context_counts':{k:sum(r['context']==k.split(':')[0] and r['chain']==k.split(':')[1] for r in allrows) for k in man['expected_nonidentity']},'identity_controls':len(identities),'selected_sum_primary':len(primary),'selected_mean_sensitivity':len(mean),'selected_dimer_sum_chainwise':len(dimer),'elapsed_seconds':time.time()-t0,'process_id':os.getpid(),'finished_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
(O/'inference_receipt.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
