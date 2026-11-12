import pathlib,json,re,pandas as pd
R=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt');ROOT=pathlib.Path(R.read_text())
for repo,files in {'rs_dev':['06_train_seq_model.ipynb','07_test_seq_model.ipynb','16_test_target_model.ipynb','17_ess_noness_tiling.ipynb'],'PRIDICT2':['process_23kdataset_v1.ipynb','train_test_multitask_models_finetuning_basemodels_v1.ipynb']}.items():
 for fn in files:
  ps=list((ROOT/'sources'/repo).rglob(fn))
  if not ps:continue
  p=ps[0];d=json.loads(p.read_text());cells=[('CELL '+str(i)+'\n'+''.join(c.get('source',[]))) for i,c in enumerate(d['cells']) if c['cell_type']=='code'];text='\n\n'.join(cells)
  (ROOT/'sources'/f'{repo}_{fn}.code.txt').write_text(text)
  print('\nNOTEBOOK',repo,fn);print(text[:22000])
for p in [ROOT/'sources/rs3_manuscript/Data/Tiling_Library_lfc_v1.csv',ROOT/'sources/rs_dev/data/processed/seq_cnn_predictions.csv']:
 if p.exists():
  x=pd.read_csv(p,nrows=3);print('\nTABLE',p.name,list(x.columns));print(x.to_string(index=False)[:5000])
