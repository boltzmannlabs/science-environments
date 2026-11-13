"""Native DeepPrime-base fixed-test benchmark; original measured features and five model weights.
Batching is only a memory control; eval-mode architecture/normalization/ensemble transform match source.
"""
import pathlib,sys,json,hashlib,os,time
import numpy as np,pandas as pd,torch
from scipy.stats import spearmanr,pearsonr
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
source=ROOT/'sources/DeepPrime_release';sys.path.insert(0,str(source));from src.dprime import GeneInteractionModel;from src.utils import seq_concat,select_cols
torch.set_num_threads(1);torch.set_num_interop_threads(1);device=torch.device('cpu')
x=pd.read_csv(ROOT/'data/DeepPrime_base_author_test.csv');assert len(x)==28883;assert not x.exact_predictive_input_training_overlap.any() and not x.unedited_target74_training_overlap.any();assert x.split.eq('Test').all()
df=x.rename(columns={'Target74':'WT74_On','Edited74':'Edited74_On','RT_PBSlen':'RT-PBSlen'}).reset_index(drop=True)
assert df.WT74_On.str.len().eq(74).all() and df.Edited74_On.str.len().eq(74).all()
modeldir=source/'models/DeepPrime/DeepPrime_base';mean=pd.read_csv(modeldir/'mean.csv',header=None,index_col=0).squeeze();std=pd.read_csv(modeldir/'std.csv',header=None,index_col=0).squeeze();features=select_cols(df);f=(features-mean)/std;assert f.shape==(len(x),24) and np.isfinite(f.to_numpy()).all()
g=seq_concat(df);assert g.shape==(len(x),2,74,4);assert set(np.unique(g))<=set([-1.,1.])
weights=sorted(modeldir.glob('model_*.pt'));assert len(weights)==5
identity={'torch':torch.__version__,'python':sys.version,'numpy':np.__version__,'pandas':pd.__version__,'n':len(x),'input_features':list(features),'input_normalization_sha256':{'mean':hashlib.sha256((modeldir/'mean.csv').read_bytes()).hexdigest(),'std':hashlib.sha256((modeldir/'std.csv').read_bytes()).hexdigest()},'weights':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in weights},'inference_batch_size':256,'ensemble':'exp(mean of five native softplus outputs))-1, exactly as source','device':'CPU','condition':'HEK293T, PE2, conventional scaffold, Library-ClinVar fixed Test set','no_test_normalization_fitting':True}
(ROOT/'protocols/DeepPrime_inference_identity.json').write_text(json.dumps(identity,indent=2))
allpred=[];g=torch.tensor(g,dtype=torch.float32);f=torch.tensor(f.to_numpy(),dtype=torch.float32)
for p in weights:
 model=GeneInteractionModel(hidden_size=128,num_layers=1).to(device);model.load_state_dict(torch.load(str(p),map_location=device));model.eval();v=[];start=time.monotonic()
 with torch.no_grad():
  for i in range(0,len(x),256):v.extend(model(g[i:i+256].permute(0,3,1,2),f[i:i+256]).cpu().numpy().reshape(-1).tolist())
 allpred.append(v);print('DEEPPRIME_MODEL_DONE',p.name,'n',len(v),'seconds',time.monotonic()-start,flush=True)
score=np.exp(np.mean(np.asarray(allpred),axis=0))-1;assert np.isfinite(score).all();x['DeepPrime_fresh_score']=score;x.to_csv(ROOT/'predictions/DeepPrime_base_fixed_test_predictions.csv',index=False)
truth=x.Measured_PE_efficiency.to_numpy();boots=[]
# Pair-level intervals; more appropriate74nt target-cluster intervals also reported.
groups=[z.index.to_numpy() for _,z in x.groupby('Target74')];cluster=[]
for b in range(1000):
 rng=np.random.RandomState(b);idx=rng.choice(len(x),len(x),replace=True);boots.append(float(spearmanr(truth[idx],score[idx]).statistic))
 ids=np.concatenate([groups[i] for i in rng.choice(len(groups),len(groups),replace=True)]);cluster.append(float(spearmanr(truth[ids],score[ids]).statistic))
metrics={'status':'COMPLETED_OFFICIAL_FIXED_TEST_REPRODUCTION','n':len(x),'target74_groups':len(groups),'train_rows':259910,'test_rows':28883,'exact_input_and74nt_target_overlap':0,'condition':'HEK293T/PE2/conventional scaffold','spearman':float(spearmanr(truth,score).statistic),'pearson':float(pearsonr(truth,score).statistic),'pair_bootstrap_spearman_ci95':np.quantile(boots,[.025,.975]).tolist(),'target_cluster_spearman_ci95':np.quantile(cluster,[.025,.975]).tolist(),'MAE_native_percent_units':float(np.mean(np.abs(truth-score))),'prediction_range':list(map(float,[np.min(score),np.median(score),np.max(score)])),'limitation':'One official matched system/cell dataset only; not evidence across all8 systems/7cells. Upstream DeepSpCas9 input scores are author-provided features, not recomputed with a different model. No unintended-edit/purity score inferred.'}
(ROOT/'reports/DeepPrime_base_heldout_metrics.json').write_text(json.dumps(metrics,indent=2));print(json.dumps(metrics,indent=2),flush=True)
