import csv,sys,json,hashlib,datetime,time,os
from pathlib import Path
import numpy as np, torch
from Bio.PDB.Polypeptide import index_to_one
R=Path(__file__).resolve().parent
S=Path('retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433')
sys.path.insert(0,str(S))
from pythia.pdb_utils import read_pdb_to_protbb,get_neighbor
from pythia.masked_ddg_scan import get_torch_model
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
plan=json.loads((R/'RUN_PLAN.json').read_text()); manifest=json.loads((R/'INPUT_MANIFEST.json').read_text())
for name,h in manifest['source_files_sha256'].items(): assert sha(S/name)==h
assert sha(R/'parent.fasta')==manifest['parent_fasta_sha256'];assert sha(R/'residue_map.csv')==manifest['residue_map_sha256']
for ctx in manifest['contexts'].values(): assert sha(R/ctx['file'])==ctx['sha256']
torch.set_num_threads(4);models={m:get_torch_model(str(S/f'pythia/pythia-{m}.pt'),device='cpu') for m in 'cp'}
rows=list(csv.DictReader((R/'residue_map.csv').open()));parent=''.join((R/'parent.fasta').read_text().splitlines()[1:]); alpha=''.join(index_to_one(i) for i in range(20)); allrows=[]; ident=[]; stats={}; start=time.monotonic(); started=datetime.datetime.now(datetime.timezone.utc).isoformat()
for label,chains in [('monomer_A','A'),('dimer_AB','AB')]:
    prot=read_pdb_to_protbb(str(R/manifest['contexts'][label]['file']));node,edge,tokens=get_neighbor(prot,neighbor=32,noise_level=0.0,train=False)
    mapping=[r for r in rows if r['chain'] in chains and r['supported']=='True'];assert len(mapping)==len(tokens)
    probs={};logits={}
    with torch.no_grad():
        for m,model in models.items():
            out,_=model(node,edge); logits[m]=out.detach().cpu().numpy();probs[m]=torch.softmax(out,dim=-1).detach().cpu().numpy()
    np.savez_compressed(R/f'raw_{label}.npz',logits_c=logits['c'],logits_p=logits['p'],probabilities_c=probs['c'],probabilities_p=probs['p'],token=tokens.numpy(),pdb_resseq=prot.resseq.numpy(),chain_num=prot.chain_num.numpy(),amino_acids=np.array(alpha))
    assert np.isfinite(logits['c']).all() and np.isfinite(logits['p']).all() and np.isfinite(probs['c']).all() and np.isfinite(probs['p']).all() and (probs['c']>0).all() and (probs['p']>0).all()
    for i,r in enumerate(mapping):
        wt=r['wild_type'];assert alpha[int(tokens[i])]==wt and int(prot.resseq[i])==int(r['pdb_resseq']) and int(prot.chain_num[i])==chains.index(r['chain']);wi=alpha.index(wt)
        for j,mut in enumerate(alpha):
            c=float(-np.log(probs['c'][i,j]/probs['c'][i,wi]));p=float(-np.log(probs['p'][i,j]/probs['p'][i,wi])); summ=c+p
            rec={'context':label,'chain':r['chain'],'native_position':int(r['native_position']),'pdb_resseq':int(r['pdb_resseq']),'insertion_code':r['insertion_code'],'model_index_zero_based':i,'wild_type':wt,'mutant':mut,'mutation':f"{wt}{r['native_position']}{mut}",'score_c':c,'score_p':p,'score_sum':summ,'score_mean':summ/2,'catalytic_site_concern':int(r['native_position']) in [53,55,99,101,132],'qualification':'unknown_not_evaluated'}
            (ident if mut==wt else allrows).append(rec)
    stats[label]={'positions':len(mapping),'nonidentity':len(mapping)*19,'identity':len(mapping),'chain_positions':{c:sum(x['chain']==c for x in mapping) for c in chains}}
fields=list(allrows[0])
def writecsv(p,rr,cols=fields):
    with (R/p).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rr)
writecsv('all_scores.csv',allrows);writecsv('identity_controls.csv',ident)
ranked=sorted(allrows,key=lambda x:(x['context'],x['chain'],x['score_sum'],x['native_position'],x['mutant']));writecsv('ranked_all_scores.csv',ranked)
best=[]
for context,chain in [('monomer_A','A'),('dimer_AB','A'),('dimer_AB','B')]:
    for n in sorted({r['native_position'] for r in allrows if r['context']==context and r['chain']==chain}):
        options=[r for r in allrows if r['context']==context and r['chain']==chain and r['native_position']==n];best.append(min(options,key=lambda r:(r['score_sum'],r['mutant'])))
writecsv('best_per_position.csv',best)
sel=sorted([r for r in best if r['context']=='monomer_A' and r['score_sum'] < -2],key=lambda r:(r['score_sum'],r['native_position'],r['mutant']))
mean=sorted([r for r in best if r['context']=='monomer_A' and r['score_mean'] < -2],key=lambda r:(r['score_mean'],r['native_position'],r['mutant']))
writecsv('library_primary_sum_lt_minus2.csv',sel);writecsv('library_mean_sensitivity_lt_minus2.csv',mean)
for c in 'AB':writecsv(f'library_dimer_{c}_sum_lt_minus2.csv',sorted([r for r in best if r['context']=='dimer_AB' and r['chain']==c and r['score_sum'] < -2],key=lambda r:(r['score_sum'],r['native_position'],r['mutant'])))
selection=[]; fasta=['>parent_Q9ZAG3\n'+parent+'\n']; hist=[]
for k,r in enumerate(sel,1):
    i=r['native_position']-1;assert parent[i]==r['wild_type'];seq=parent[:i]+r['mutant']+parent[i+1:];h=hashlib.sha256(seq.encode()).hexdigest();selection.append({'candidate_id':r['mutation'],'rank':k,'sequence_sha256':h});fasta.append(f">{r['mutation']} parent=Q9ZAG3 context=monomer_A score_sum={r['score_sum']:.9g}\n{seq}\n");hist.append({'candidate_id':r['mutation'],'parent_id':'Q9ZAG3','mutation':r['mutation'],'sequence_sha256':h,'generation':'Pythia C+P masked scan','score_sum':r['score_sum'],'catalytic_site_concern':r['catalytic_site_concern'],'qualification':r['qualification']})
writecsv('selection.csv',selection,['candidate_id','rank','sequence_sha256']);writecsv('candidate_history.csv',hist,['candidate_id','parent_id','mutation','sequence_sha256','generation','score_sum','catalytic_site_concern','qualification']);(R/'candidates.fasta').write_text(''.join(fasta))
assert len({(r['context'],r['chain'],r['native_position'],r['mutant']) for r in allrows})==len(allrows);assert all(np.isfinite(r[k]) for r in allrows for k in ('score_c','score_p','score_sum','score_mean'));assert all(r['score_sum']==0 and r['score_c']==0 and r['score_p']==0 for r in ident)
for label in stats:
    for ch,n in stats[label]['chain_positions'].items():
        rr=[x for x in allrows if x['context']==label and x['chain']==ch];assert len(rr)==19*n
        assert all(len([x for x in rr if x['native_position']==pos])==19 for pos in {x['native_position'] for x in rr})
verify={'counts':stats,'nonidentity_total':len(allrows),'identity_controls':len(ident),'all_finite':True,'identity_controls_zero':True,'mapping_agreement':True,'unique_grid':True,'strict_primary_selection_count':len(sel),'strict_mean_sensitivity_count':len(mean),'catalytic_hits':[r['mutation'] for r in sel if r['catalytic_site_concern']],'score_reconstruction':'computed from retained float32 softmax probabilities as source negative log ratio; sum in Python float, mean half sum','unscored_ledger':'missing_positions.csv','outputs_sha256':{p.name:sha(p) for p in R.iterdir() if p.is_file() and (p.suffix in ['.csv','.npz','.fasta'])}}
(R/'verification.json').write_text(json.dumps(verify,indent=2)+'\n')
seal={'selection_sha256':sha(R/'selection.csv'),'ranked_all_scores_sha256':sha(R/'ranked_all_scores.csv'),'primary_library_sha256':sha(R/'library_primary_sum_lt_minus2.csv'),'verification_sha256':sha(R/'verification.json'),'sealed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'note':'sealed before paper outcome data access; process cannot independently prove prior knowledge restrictions'};(R/'selection_seal.json').write_text(json.dumps(seal,indent=2)+'\n')
finished=datetime.datetime.now(datetime.timezone.utc).isoformat();duration=time.monotonic()-start
(R/'jobs.json').write_text(json.dumps({'scientific_remote_jobs':[],'local_processes':[{'name':'Pythia C/P complete monomer and dimer scan','pid':os.getpid(),'start_utc':started,'end_utc':finished,'elapsed_seconds':duration,'state':'completed','device':'cpu','threads':4,'outputs':['all_scores.csv','raw_monomer_A.npz','raw_dimer_AB.npz']}], 'preparation':'evidence/preparation.log'},indent=2)+'\n')
print(json.dumps({'verification':verify,'selection_seal':seal,'elapsed_seconds':duration},indent=2))
