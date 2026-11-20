"""PRIDICT2 measured-label OOF inference, using only the matching held-out-fold checkpoints.
No target labels are passed to prepare_data/predict. Original source files remain unchanged.
"""
import pathlib,sys,json,hashlib,os,time
import numpy as np,pandas as pd,torch
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/06_completed_benchmark_retry/Run_20261112T060348Z')
release=next((ROOT/'sources/PRIDICT2_release').glob('PRIDICT2-*'));sys.path.insert(0,str(release))
from pridict.pridictv2.predict_outcomedistrib import PRIEML_Model
from scipy.stats import spearmanr
from sklearn.metrics import mean_absolute_error
os.environ['CUDA_VISIBLE_DEVICES']='-1';torch.set_num_threads(1);torch.set_num_interop_threads(1)
x=pd.read_csv(release/'dataset/proc_v2/data_23k_v1.csv');folds=json.loads((ROOT/'data/PRIDICT2_original_grouped_folds.json').read_text());nans=json.loads((ROOT/'data/PRIDICT2_cell_missing_indices.json').read_text())
assert x.seq_id.is_unique
out=ROOT/'predictions/PRIDICT2_OOF';out.mkdir(exist_ok=True)
models=[('model_A','pridict1_1','exp_2023-08-25_20-55-53'),('model_B','pridict1_2','exp_2023-08-28_22-22-26')]
protocol={'model':'PRIDICT2.0, source CLI August2023 model_A/model_B ensemble','source_commit':'c133c35e205062e766bf515d1766169167e993b9','dataset':'Library-Diverse 22956 preprocessed rows','cell_heads':['HEK','K562'],'normalization':'official max normalization, wsize20, no MFE/addendum features','prediction_rule':'Use each row only in its own grouped held-out fold; average two base-pretraining families within that fold, never average the5 folds','split_identity':'protocols/PRIDICT2_fold_identity.json','frozen_before_inference':True,'qualification':'Group disjointness verified within Library-Diverse fine-tuning; source pretraining libraries are not fully present here, so overlap with >400k base training cannot be fully audited. Do not call this independently unseen-locus evaluation across all pretraining data.','hardware':f'CPU, torch{torch.__version__}, one compute thread; Python{sys.version.split()[0]}, pandas{pd.__version__}, NumPy{np.__version__}','labels':'native HEK/K562 averageedited,averageunedited,averageunintended_clamped; cell-specific missing indices excluded, not treated as zeros'}
(ROOT/'protocols/PRIDICT2_evaluation.json').write_text(json.dumps(protocol,indent=2))
for fold in range(5):
 ids=folds[str(fold)]['test'];df=x.iloc[ids].copy();df=df.drop(columns=[c for c in df if c.startswith(('HEKaverage','K562average')) or c.startswith('Correction_') and c!='Correction_Type' and c!='Correction_Length'],errors='ignore')
 # Drop only redundant precomputed dummy flags; native source regenerates identical categories.
 for c in ['Correction_Deletion','Correction_Insertion','Correction_Replacement']:
  if c in df:df=df.drop(columns=c)
 # Native prediction API expects integer IDs (as its CLI constructs); restore source IDs after inference.
 df['seq_id']=np.asarray(ids,dtype=np.int64)
 native=PRIEML_Model(torch.device('cpu'),wsize=20,normalize='max',include_MFE=False,include_addendumfeat=False,fdtype=torch.float32)
 # Process once per fold with official sequence/PBS/RTT annotation construction.
 dl=native.prepare_data(df,None,cell_types=['HEK','K562'],y_ref=[],batch_size=128)
 for tag,group,exp in models:
  p=out/f'{tag}_fold{fold}.csv'
  if p.exists():print('RESUME_VALIDATED_FILE',p,flush=True);continue
  checkpoint=release/'trained_models'/group/exp/'train_val'/f'run_{fold}'
  assert checkpoint.is_dir(),checkpoint
  start=time.monotonic();pred=native.predict_from_dloader(dl,str(checkpoint),y_ref=['averageedited','averageunedited','averageindel'])
  assert len(pred)==2*len(df);pred['source_row_index']=pred['seq_id'].astype(int);pred['seq_id']=x.iloc[pred['source_row_index'].to_numpy()]['seq_id'].to_numpy();pred['fold']=fold;pred['model_family']=tag
  pred.to_csv(p,index=False);print('PRIDICT2_FOLD_DONE',tag,fold,len(pred),'seconds',time.monotonic()-start,'COLS',list(pred.columns),flush=True)
# Ensemble only the2 pretraining families for each OOF row/head; keep all labels separate.
a=pd.concat([pd.read_csv(p) for p in out.glob('model_*_fold*.csv')],ignore_index=True)
assert len(a)==4*len(x)
pcols=[c for c in a if c.startswith('pred_')];assert len(pcols)==3,pcols
assert not a.duplicated(['seq_id','dataset_name','fold','model_family']).any()
oof=a.groupby(['seq_id','dataset_name','fold'],as_index=False)[pcols].mean();oof=oof.merge(x[['seq_id','grp_id']+[c for c in x if c.startswith(('HEKaverage','K562average'))]],on='seq_id',validate='many_to_one');oof.to_csv(out/'OOF_ensemble_predictions_with_labels.csv',index=False)
metrics=[]
for cell,z in oof.groupby('dataset_name'):
 validids=set(x.iloc[[i for i in range(len(x)) if i not in set(nans[cell])]].seq_id);z=z[z.seq_id.isin(validids)]
 for predcol,lab in [('pred_averageedited','averageedited'),('pred_averageunedited','averageunedited'),('pred_averageindel','averageunintended')]:
  if predcol not in z:raise RuntimeError('Unexpected native prediction columns:'+str(z.columns))
  truth=z[cell+lab+'_clamped'].to_numpy();pred=z[predcol].to_numpy();assert np.isfinite(pred).all();assert np.isfinite(truth).all()
  row=dict(cell=cell,endpoint=lab,n=len(z),OOF_spearman=float(spearmanr(truth,pred).statistic),MAE=float(mean_absolute_error(truth,pred)))
  vals=[]
  for b in range(1000):
   i=np.random.RandomState(b).choice(len(z),len(z),replace=True);vals.append(float(spearmanr(truth[i],pred[i]).statistic))
  row.update(guide_bootstrap_ci_low=float(np.quantile(vals,.025)),guide_bootstrap_ci_high=float(np.quantile(vals,.975)));metrics.append(row);print(json.dumps(row),flush=True)
pd.DataFrame(metrics).to_csv(ROOT/'reports/PRIDICT2_measured_label_OOF_metrics.csv',index=False)
(ROOT/'reports/PRIDICT2_status.json').write_text(json.dumps({'status':'COMPLETED_QUALIFIED_OOF_REPRODUCTION','qualifications':protocol['qualification'],'metrics':metrics},indent=2))
