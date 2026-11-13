"""Recreate original grouped PRIDICT2 folds under the source-era sklearn1.0.2 runtime."""
import pathlib,json,pickle,hashlib
import pandas as pd,numpy as np,sklearn
from sklearn.model_selection import GroupKFold,GroupShuffleSplit
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
x=pd.read_csv(ROOT/'sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv');groups=x.grp_id.to_numpy();np.random.seed(42);gkf=GroupKFold(n_splits=5);gss=GroupShuffleSplit(n_splits=2,test_size=.1,random_state=42)
folds={};audit=[]
for fold,(trainval,test) in enumerate(gkf.split(X=np.zeros(len(groups)),y=None,groups=groups)):
 for a,b in gss.split(X=np.zeros(len(trainval)),y=None,groups=groups[trainval]):train,val=trainval[a],trainval[b]
 assert not set(groups[train])&set(groups[test]);assert not set(groups[val])&set(groups[test]);assert not set(groups[val])&set(groups[train])
 folds[fold]={'train':train.tolist(),'validation':val.tolist(),'test':test.tolist()};audit.append({'fold':fold,'train':len(train),'validation':len(val),'test':len(test),'train_test_target_overlap':0})
(ROOT/'data/PRIDICT2_original_grouped_folds.json').write_text(json.dumps(folds))
# Different missing-label exclusions per cell type, as process_23kdataset_v1 notebook specifies.
nans={}
for cell,file in [('HEK','hek_indices_nan.pkl'),('K562','k562_indices_nan.pkl')]:
 a=pickle.load(open(ROOT/'sources/PRIDICT2/dataset/proc_v2'/file,'rb'));nans[cell]=[int(i) for i in a]
(ROOT/'data/PRIDICT2_cell_missing_indices.json').write_text(json.dumps(nans))
identity={'source_commit':'c133c35e205062e766bf515d1766169167e993b9','input_sha256':hashlib.sha256((ROOT/'sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv').read_bytes()).hexdigest(),'sklearn':sklearn.__version__,'numpy':np.__version__,'seed':42,'group_key':'grp_id','split':'GroupKFold5 then SECOND GroupShuffleSplit draw for validation, exactly as source function retains its second iteration','audit':audit,'missing_labels':{k:len(v) for k,v in nans.items()},'prediction_rule':'Each row may only be scored by its held-out fold model; never average predictions from all5 folds on a development-library row','status':'FROZEN_BEFORE_OUTCOME_INFERENCE'}
(ROOT/'protocols/PRIDICT2_fold_identity.json').write_text(json.dumps(identity,indent=2));print(json.dumps(identity,indent=2))
