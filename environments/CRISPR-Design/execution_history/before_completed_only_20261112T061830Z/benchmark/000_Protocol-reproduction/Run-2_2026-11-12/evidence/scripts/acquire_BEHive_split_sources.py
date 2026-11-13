import pathlib,json,urllib.request,hashlib
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
sha='6234a17883268b31ac71dabd509bc70183c4f99b';files=['be_anyedit_models.py','fig_model_anyedit_12kChar_traintest.py','be_efficiency_CBE_models.py','_data.py','_lib.py','_config.py']
for name in files:
 try:
  u='https://raw.githubusercontent.com/maxwshen/lib-analysis/'+sha+'/'+name
  with urllib.request.urlopen(u,timeout=45) as f:b=f.read()
  p=ROOT/'sources/BEHive_analysis'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(b);print('BE_SOURCE',name,len(b))
 except Exception as e:print('BE_SOURCE_ERROR',name,e)
# Fetch the single frozen, editor/cell-matched released efficiency model for later compatibility validation.
try:
 sha='fbd495910d6c95b24081649015d6257a8badc9d7';name='HEK293T_12kChar_BE4_bestmodel.pkl';u='https://raw.githubusercontent.com/maxwshen/be_predict_efficiency/'+sha+'/params/'+name
 with urllib.request.urlopen(u,timeout=60) as f:b=f.read()
 p=ROOT/'sources/be_efficiency/params'/name;p.parent.mkdir(exist_ok=True);p.write_bytes(b);print('BE_MODEL',len(b),hashlib.sha256(b).hexdigest())
except Exception as e:print('BE_MODEL_ERROR',e)
