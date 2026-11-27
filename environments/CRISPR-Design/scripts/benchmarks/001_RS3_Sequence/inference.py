"""Fresh RS3 Sequence inference using published 30nt/tracr features, not archived scores."""
import sys,os,json,pathlib,hashlib
os.environ['OMP_NUM_THREADS']='2';os.environ['OPENBLAS_NUM_THREADS']='1'
import pandas as pd,numpy as np,joblib,sglearn
ROOT=pathlib.Path(sys.argv[1]);src=ROOT/'data/rs3_published_common_holdout.csv';x=pd.read_csv(src)
modelpath=pathlib.Path('/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38/bootstrap/runtime/lib/R/library/crisprScoreData/rs3/RuleSet3.pkl')
model=joblib.load(modelpath)
# Freeze identities before first inference output.
manifest={'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'model_path':str(modelpath),'model_sha256':hashlib.sha256(modelpath.read_bytes()).hexdigest(),'python':sys.version,'featurizer':'sglearn.featurize_guides plus Hsu2013/Chen2013 indicators, as rs_dev','scoring_precision':'native float, no six-decimal truncation','n':len(x)}
(ROOT/'protocols/RS3_inference_identity.json').write_text(json.dumps(manifest,indent=2))
seqs=x['sgRNA Context Sequence'].to_list();feat=sglearn.featurize_guides(seqs,n_jobs=1)
for tr in ['Hsu2013','Chen2013']:feat[tr+' tracr']=(x['tracr']==tr).astype(int).to_list()
pred=model.predict(feat);assert np.isfinite(pred).all();x['RS3_Sequence_fresh']=pred
x.to_csv(ROOT/'predictions/RS3_common_holdout_fresh.csv',index=False)
print('FRESH_RS3',len(x),'features',feat.shape,'model_sha256',manifest['model_sha256'],flush=True)
