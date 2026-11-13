import pathlib,json,urllib.request,urllib.parse,hashlib,importlib.util,pandas as pd,numpy as np,re
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text());D=json.loads((ROOT/'sources/repository_discovery.json').read_text())
extra=[('azimuth_training','https://raw.githubusercontent.com/MicrosoftResearch/Azimuth/master/azimuth/data/FC_plus_RES_withPredictions.csv',ROOT/'data/Azimuth_FC_plus_RES.csv'),('deepspcas9_published_predictions','https://raw.githubusercontent.com/gpp-rnd/rs_dev/'+D['rs_dev']['tree_sha']+'/data/external/DeepSpCas9_rs_dev_all_sgrnas.csv',ROOT/'sources/rs_dev/data/external/DeepSpCas9_rs_dev_all_sgrnas.csv')]
for name,url,out in extra:
 try:
  with urllib.request.urlopen(url,timeout=60) as f:b=f.read()
  out.write_bytes(b);print(name,len(b),hashlib.sha256(b).hexdigest())
 except Exception as e:print('FAILED',name,e)
# Authors' dataset objects only read local CSVs; inspect these source functions before import.
spec=importlib.util.spec_from_file_location('rs3_paper_datasets',ROOT/'sources/rs_dev/code/datasets.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
train_names=set(pd.read_csv(ROOT/'sources/rs_dev/data/processed/train_data_names.csv')['name']);allrows=[];rs3_train=set();study={}
for ds in mod.dataset_list:
 ds.filepath=str(ROOT/'sources/rs_dev/data/processed'/pathlib.Path(ds.filepath).name);ds.load_data();ds.set_sgrnas()
 if ds.name in train_names:rs3_train|=ds.sgrnas
 x=ds.get_sg_df(include_group=True,include_activity=True);x['dataset']=ds.name;x['tracr']=ds.tracr;x['genomewide']=ds.genomewide
 if 'sgRNA Target' not in x:x['sgRNA Target']=x['sgRNA Sequence']
 allrows.append(x)
x=pd.concat(allrows,ignore_index=True);x['RS3_train_overlap']=x['sgRNA Sequence'].isin(rs3_train)
cp_train=set(pd.read_csv(ROOT/'sources/rs_dev/data/external/CRISPRon_train.csv')['sgRNA Sequence']);x['CRISPRon_train_overlap']=x['sgRNA Sequence'].isin(cp_train)
a=pd.read_csv(ROOT/'data/Azimuth_FC_plus_RES.csv');print('AZIMUTH_COLS',list(a.columns));az_train=set(a['30mer'].str[4:24]);x['Azimuth_train_overlap']=x['sgRNA Sequence'].isin(az_train)
kim=pd.read_csv(ROOT/'sources/rs_dev/data/processed/Kim2019_train_activity.csv');kimtrain=set(kim['sgRNA Sequence']);x['DeepSpCas9_train_overlap']=x['sgRNA Sequence'].isin(kimtrain)
# Reproduce the source notebook's common-availability join, retaining published comparator values as audit columns only.
for file,col in [('data/external/DeepSpCas9_rs_dev_all_sgrnas.csv','DeepSpCas9'),('data/external/Rule_Set_2_rs_dev_all_sgrnas.csv','Rule Set 2'),('data/external/crispron_rs_dev_all_sgrnas.csv','CRISPRon')]:
 p=ROOT/'sources/rs_dev'/file;y=pd.read_csv(p);print('PRED_COLS',p.name,list(y.columns))
 if '30mer' in y:y=y.rename(columns={'30mer':'sgRNA Context Sequence'})
 if 'sgRNA Context Sequence' in y:
  # Join only exact contexts. The paper also joins spacer and PAM; derive and assert consistency.
  if col=='CRISPRon' and col not in y and 'CRISPRon' in y:pass
  y=y[['sgRNA Context Sequence',col]].drop_duplicates();assert not y['sgRNA Context Sequence'].duplicated().any()
  x=x.merge(y.rename(columns={col:col+'_author_archive'}),on='sgRNA Context Sequence',how='inner',validate='many_to_one')
 else:raise RuntimeError('No exact context join for '+file)
mask=~x[['RS3_train_overlap','CRISPRon_train_overlap','Azimuth_train_overlap','DeepSpCas9_train_overlap']].any(axis=1)
held=x[mask].copy();held['candidate_id']=['RS3_holdout_%06d'%i for i in range(len(held))]
assert held['sgRNA Context Sequence'].str.len().eq(30).all();assert (held['sgRNA Context Sequence'].str[4:24]==held['sgRNA Sequence']).all()
held.to_csv(ROOT/'data/rs3_published_common_holdout.csv',index=False);x.to_csv(ROOT/'data/rs3_common_before_exclusion.csv',index=False)
expected={'Aguirre2016':7828,'Behan2019':7025,'Chari2015':1130,'Kim2019_test':518,'Koike-Yusa2014':6718,'Shalem2014':3968};counts=held.groupby('dataset').size().to_dict()
protocol={'model':'RS3 Sequence','source':'gpp-rnd/rs_dev/code/07_test_seq_model.ipynb','source_commit':D['rs_dev']['tree_sha'],'training_datasets':sorted(train_names),'train_exclusion':'exact 20mer union for RS3, CRISPRon, Azimuth and DeepSpCas9, as official RS3 notebook; not the different CRISPRon <=3mm publication protocol','training_20mers':len(rs3_train),'before_exclusion_rows':len(x),'heldout_rows':len(held),'unique_contexts':held['sgRNA Context Sequence'].nunique(),'dataset_counts':counts,'expected_counts_from_notebook':expected,'counts_match':counts==expected,'features':'30nt contexts plus per-dataset Hsu2013/Chen2013 tracr; no target model substitution','labels':'official author-processed activity columns via datasets.py, exact source transformations retained','metrics':{'spearman':'dataset-wise, as original','bootstrap':'1000 resamples with random_state i=0..999, as core.py; guide-row CIs primary, target-cluster sensitivity secondary','ndcg':'supplemental within-gene rank-relevance nDCG@20, explicitly not an original RS3 endpoint','rank_loss':'within-gene mean absolute rank error for genomewide datasets, original metric'},'frozen_before_scoring':True}
(ROOT/'protocols/cas9_RS3.json').write_text(json.dumps(protocol,indent=2));print(json.dumps(protocol,indent=2))
# Separate model-specific cohort, not joint-exclusion cohort, also frozen before scoring.
solo=pd.concat(allrows,ignore_index=True);solo=solo[~solo['sgRNA Sequence'].isin(rs3_train)].copy();solo.to_csv(ROOT/'data/rs3_model_specific_holdout.csv',index=False)
print('RS3_MODEL_SPECIFIC',solo.groupby('dataset').size().to_dict())
for name in ['bacterial_crispri','PRIDICT2','GenET']:
 tree=json.loads((ROOT/'sources'/f'{name}_tree.json').read_text());print('\nIMPORTANT_PATHS',name)
 for r in tree['tree']:
  p=r['path']
  if r['type']=='blob' and (('5_' in p or 'validation' in p.lower() or 'partition' in p.lower() or 'testset' in p.lower() or 's1' in p.lower()) and r.get('size',0)>100):print(p,r.get('size'))
