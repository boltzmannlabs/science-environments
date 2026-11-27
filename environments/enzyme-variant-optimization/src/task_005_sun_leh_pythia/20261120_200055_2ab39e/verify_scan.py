import collections,csv,hashlib,json,math,pathlib
import numpy as np
from Bio.PDB.Polypeptide import index_to_one
R=pathlib.Path(__file__).resolve().parent;O=R/'results/local/task_005_sun_leh_pythia/v2/assisted/fresh-20261120'; sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read(n):
 with (O/n).open(newline='') as f:return list(csv.DictReader(f))
man=json.loads((O/'INPUT_MANIFEST.json').read_text()); plan=json.loads((O/'RUN_PLAN.json').read_text()); seal=json.loads((O/'selection_seal.json').read_text()); receipt=json.loads((O/'inference_receipt.json').read_text()); rows=read('all_scores.csv');ids=read('identity_controls.csv');mapping=read('residue_map.csv');best=read('best_per_position.csv');sel=read('selection.csv'); primary=read('library_sum_monomer_A.csv');mean=read('library_mean_monomer_A.csv'); raw=np.load(O/'native_model_outputs.npz');alphabet=''.join(index_to_one(i) for i in range(20)); amap={x:i for i,x in enumerate(alphabet)}; parent=''.join(x.strip() for x in (O/'parent.fasta').read_text().splitlines() if not x.startswith('>'))
assert sha(O/'INPUT_MANIFEST.json')==plan['input_manifest_sha256'] and sha(O/'selection.csv')==seal['selection_sha256'] and sha(O/'all_scores_ranked.csv')==seal['ranking_sha256'] and sha(O/'RUN_PLAN.json')==seal['plan_sha256']; assert hashlib.sha256(parent.encode()).hexdigest()==man['parent_sequence_sha256']
expected={k:int(v) for k,v in man['expected_nonidentity'].items()}; actual=collections.Counter(r['context']+':'+r['chain'] for r in rows);assert dict(actual)==expected and len(ids)==sum(man['eligible'].values())
keys=set(); bypos=collections.defaultdict(list); max_logerr=0.;max_proberr=0.; max_sumerr=0.; max_id=0.
for r in rows+ids:
 c=r['context']; i=int(r['model_index_1based'])-1; wt=r['wild_type'];mut=r['mutant'];pos=int(r['parent_position']); assert parent[pos-1]==wt
 k=(c,r['chain'],pos,mut);assert k not in keys;keys.add(k)
 if r in []:pass
 vals=[]
 for m in ('c','p'):
  logits=raw[c+'_'+m+'_logits']; probs=raw[c+'_'+m+'_probabilities']; v=float(r['score_'+m]); expected_prob=-math.log(float(probs[i,amap[mut]])/float(probs[i,amap[wt]]));expected_log=float(logits[i,amap[wt]])-float(logits[i,amap[mut]])
  assert math.isfinite(v); max_proberr=max(max_proberr,abs(v-expected_prob));max_logerr=max(max_logerr,abs(v-expected_log));vals.append(v)
 sm=float(r['score_sum']);mn=float(r['score_mean']);max_sumerr=max(max_sumerr,abs(sm-sum(vals)),abs(mn-sm/2))
 if wt==mut:max_id=max(max_id,abs(sm),abs(vals[0]),abs(vals[1]))
 else:bypos[(c,r['chain'],pos)].append(r)
assert max_proberr<2e-6 and max_logerr<2e-5 and max_sumerr<1e-12 and max_id==0
for c in ('monomer_A','dimer_AB'):
 for m in ('c','p'):
  a=raw[c+'_'+m+'_probabilities'];b=raw[c+'_'+m+'_logits'];assert a.shape==b.shape==(145 if c=='monomer_A' else 291,21) and np.isfinite(a).all() and np.isfinite(b).all() and np.allclose(a.sum(axis=1),1,atol=2e-6)
assert len(bypos)==sum(man['eligible'].values()) and all(len(v)==19 and len({r['mutant'] for r in v})==19 for v in bypos.values())
expectedbest={k:min(v,key=lambda r:(float(r['score_sum']),r['mutant'])) for k,v in bypos.items()};assert len(best)==len(expectedbest)
for r in best:
 k=(r['context'],r['chain'],int(r['parent_position']));assert r==expectedbest[k]
exp_primary=sorted((r for r in expectedbest.values() if r['context']=='monomer_A' and float(r['score_sum']) < -2),key=lambda r:(float(r['score_sum']),int(r['parent_position']),r['mutant']))
exp_mean=sorted((r for r in expectedbest.values() if r['context']=='monomer_A' and float(r['score_mean']) < -2),key=lambda r:(float(r['score_sum']),int(r['parent_position']),r['mutant']))
assert primary==exp_primary and mean==exp_mean and len(sel)==len(primary)
fasta={};name=None
for line in (O/'candidates.fasta').read_text().splitlines():
 if line.startswith('>'):name=line[1:].split('|')[0];fasta[name]=''
 else:fasta[name]+=line.strip()
assert len(fasta)==len(sel)
for idx,(s,r) in enumerate(zip(sel,primary),1):
 assert int(s['rank'])==idx and s['candidate_id']==r['mutation']; x=fasta[s['candidate_id']]; p=int(r['parent_position'])-1; assert x==parent[:p]+r['mutant']+parent[p+1:] and hashlib.sha256(x.encode()).hexdigest()==s['sequence_sha256']
files=['RUN_PLAN.json','INPUT_MANIFEST.json','original_1NWW.pdb','monomer_A.pdb','parent.fasta','residue_map.csv','missing_positions.csv','preflight.json','native_model_outputs.npz','all_scores.csv','all_scores_ranked.csv','identity_controls.csv','best_per_position.csv','library_sum_monomer_A.csv','library_mean_monomer_A.csv','library_sum_dimer_AB_by_chain.csv','candidates.fasta','selection.csv','selection_seal.json','inference_receipt.json']
out={'verified':True,'expected_nonidentity':expected,'observed_nonidentity':dict(actual),'identity_controls':len(ids),'identity_max_abs':max_id,'unique_context_chain_position_mutant':len(keys),'positions':len(bypos),'nineteen_unique_nonidentity_each':True,'max_probability_reconstruction_error':max_proberr,'max_logit_reconstruction_error':max_logerr,'max_aggregation_error':max_sumerr,'finite_scores':True,'softmax_sum_checked':True,'score_threshold_and_best_per_position_checked':True,'full_length_mutants_checked':True,'selection_count':len(sel),'primary_mean_sensitivity_count':len(mean),'unscored':man['unscored'],'file_sha256':{x:sha(O/x) for x in files},'numerical_tolerances':{'probability_reconstruction':2e-6,'logit_reconstruction':2e-5,'aggregation':1e-12}}
(O/'verification.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
