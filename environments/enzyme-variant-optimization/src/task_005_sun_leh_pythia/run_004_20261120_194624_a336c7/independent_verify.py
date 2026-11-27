import csv,json,hashlib,math
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent
load=lambda p:list(csv.DictReader((R/p).open()))
rows=load('all_scores.csv');ident=load('identity_controls.csv');best=load('best_per_position.csv');selection=load('selection.csv');lib=load('library_primary_sum_lt_minus2.csv'); alpha='ACDEFGHIKLMNPQRSTVWY';raw={c:np.load(R/f'raw_{c}.npz') for c in ['monomer_A','dimer_AB']};err=0.; mx=0.
for r in rows+ident:
    x=raw[r['context']];i=int(r['model_index_zero_based']);j=alpha.index(r['mutant']);wi=alpha.index(r['wild_type']);assert int(x['token'][i])==wi
    c=float(-np.log(x['probabilities_c'][i,j]/x['probabilities_c'][i,wi]));p=float(-np.log(x['probabilities_p'][i,j]/x['probabilities_p'][i,wi]));v=[c,p,c+p,(c+p)/2]
    mx=max(mx,max(abs(float(r[k])-z) for k,z in zip(['score_c','score_p','score_sum','score_mean'],v)))
    for model in ['c','p']:
        v=x['logits_'+model][i];q=np.exp(v-np.max(v));q/=q.sum();assert np.allclose(x['probabilities_'+model][i],q,atol=1e-6)
assert mx<1e-7
for r in best:
    a=[x for x in rows if all(x[k]==r[k] for k in ['context','chain','native_position'])];assert len(a)==19
    assert min(a,key=lambda x:(float(x['score_sum']),x['mutant']))['mutation']==r['mutation']
expected=sorted([x for x in best if x['context']=='monomer_A' and x['chain']=='A' and float(x['score_sum']) < -2],key=lambda x:(float(x['score_sum']),int(x['native_position']),x['mutant']))
assert [x['mutation'] for x in expected]==[x['mutation'] for x in lib]==[x['candidate_id'] for x in selection]
seqs={};txt=(R/'candidates.fasta').read_text().splitlines()
for line in txt:
    if line.startswith('>'): key=line[1:].split()[0];seqs[key]=''
    else:seqs[key]+=line.strip()
parent=seqs['parent_Q9ZAG3'];assert len(parent)==149
for r in selection:
    seq=seqs[r['candidate_id']];assert len(seq)==149 and sum(a!=b for a,b in zip(seq,parent))==1;assert hashlib.sha256(seq.encode()).hexdigest()==r['sequence_sha256']
    mid=r['candidate_id']; pos=int(mid[1:-1]); assert parent[pos-1]==mid[0] and seq[pos-1]==mid[-1] and seq==parent[:pos-1]+mid[-1]+parent[pos:]
seal=json.loads((R/'selection_seal.json').read_text());assert hashlib.sha256((R/'selection.csv').read_bytes()).hexdigest()==seal['selection_sha256']
for field,path in [('ranked_all_scores_sha256','ranked_all_scores.csv'),('primary_library_sha256','library_primary_sum_lt_minus2.csv'),('verification_sha256','verification.json')]: assert hashlib.sha256((R/path).read_bytes()).hexdigest()==seal[field]
print(json.dumps({'independent_full_grid_reconstruction':'passed','rows_reconstructed':len(rows)+len(ident),'max_abs_difference':mx,'best_per_position_recomputed':len(best),'primary_selection_recomputed':len(expected),'candidate_full_sequence_hashes_verified':len(selection),'selection_seal':'verified','raw_probability_to_logits':'C and P model verified across all rows'},indent=2))
