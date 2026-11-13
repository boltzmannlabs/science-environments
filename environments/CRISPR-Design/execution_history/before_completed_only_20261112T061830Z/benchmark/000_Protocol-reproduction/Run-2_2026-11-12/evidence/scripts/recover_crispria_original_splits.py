import pathlib,pandas as pd,json,pickle,numpy as np
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
for mode in ['CRISPRi','CRISPRa']:
 p=ROOT/'sources/crispria/data_files'/('%s_trainingdata_traintestsets.txt'%mode)
 try:
  obj=pd.read_pickle(str(p));print('SOURCE_SPLITS_RECOVERED',mode,type(obj).__name__,len(obj))
  def schema(v,depth=0):
   if depth>2:return str(type(v))
   if isinstance(v,(list,tuple)):return {'type':str(type(v)),'n':len(v),'first':[schema(a,depth+1) for a in v[:3]]}
   if isinstance(v,pd.DataFrame):return {'type':'DataFrame','shape':list(v.shape),'columns':[str(c) for c in v.columns.tolist()],'index_head':[str(a) for a in v.index[:2]],'head_values':v.head(2).astype(str).values.tolist()}
   if isinstance(v,np.ndarray):return {'type':'ndarray','shape':list(v.shape),'head':v[:5].astype(str).tolist()}
   return {'type':str(type(v)),'repr':str(v)[:500]}
  s=schema(obj);print(json.dumps(s,indent=2));(ROOT/'protocols'/('%s_recovered_split_schema.json'%mode)).write_text(json.dumps(s,indent=2))
  (ROOT/'data'/('%s_author_train_test_indices.json'%mode)).write_text(json.dumps({'train':[int(v) for v in obj[0]],'test':[int(v) for v in obj[1]]}))
  if isinstance(obj[2],(pd.DataFrame,pd.Series)):obj[2].to_csv(ROOT/'data'/('%s_author_split_index_object.csv'%mode))
 except Exception as e:print('SOURCE_SPLIT_LEGACY_LOAD_BLOCKER',mode,type(e).__name__,str(e))
