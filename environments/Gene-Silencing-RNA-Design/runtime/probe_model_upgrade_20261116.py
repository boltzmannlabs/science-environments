"""Probe installed scientific dependencies, checkpoint shape and author preprocessing safeguards.
No efficacy values produced from incomplete input features.
"""
import pathlib,json,sys,importlib,ast,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1];B=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16';P=json.loads((B/'acquisition_provenance.json').read_text());A=pathlib.Path(P['local_asset_root'])
def main():
 versions={}
 for n in ['torch','numpy','pandas','scipy','sklearn','Bio','flask','fm','torch_geometric']:
  try:m=importlib.import_module(n);versions[n]=getattr(m,'__version__','available')
  except Exception as e:versions[n]={'unavailable':str(e)}
 import torch
 d=torch.load(A/'checkpoints/best_model_fold.pt',map_location='cpu',weights_only=True)
 print('VERSIONS',versions); print('CHECKPOINT',[(k,list(v.shape)) for k,v in d.items() if k.startswith(('proj_','fc_mlp1'))])
 sys.path.insert(0,str(A));from model import SiaRNA
 model=SiaRNA(d['proj_mRNA.weight'].shape[1],d['proj_siRNA.weight'].shape[1],d['fc_mlp1.weight'].shape[1]-160)
 model.load_state_dict(d,strict=True);print('EXACT_STATE_DICT_LOAD_OK')
 # Executable proof of random-feature substitution, extracted verbatim via AST.
 tree=ast.parse((A/'preprocess.py').read_text());f=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='main')
 bad=next(x for x in f.body if isinstance(x,ast.Assign) and isinstance(x.value,ast.ListComp) and 'np.random.randn' in ast.unparse(x))
 import numpy as np
 code=compile(ast.Module(body=[bad],type_ignores=[]),str(A/'preprocess.py'),'exec');ns={'np':np,'df_mrna':[np.ones(100)]}
 exec(code,ns);first=np.array(ns['df_mrna']);exec(code,ns);second=np.array(ns['df_mrna'])
 assert first.shape==(2,100) and not np.array_equal(first,second)
 report={'versions':versions,'checkpoint_strict_load':'PASSED','checkpoint_shapes':{k:list(v.shape) for k,v in d.items() if k.startswith(('proj_','fc_mlp1'))},'preprocessing_random_override':{'file':'preprocess.py','line':bad.lineno,'code':ast.unparse(bad),'demonstration':'Executed exact upstream assignment twice; replaces prior biological feature vector with two random 100-element vectors; outputs differ. These are software diagnostics, not biological predictions.','max_absolute_difference':float(np.max(np.abs(first-second)))},'model_status':'BLOCKED_FOR_VALID_EFFICACY_COMPARISON','reason':'Native preprocessing overwrites actual mRNA folding features with unseeded random numbers; native inference prints/returns first pair only; genuine AGO2 features are not supplied for the measured cohort. Do not invent or zero-fill learned inputs.'}
 (B/'siarna_software_probe.json').write_text(json.dumps(report,indent=2)+'\n')
 url='https://drive.google.com/uc?export=download&id=1XHuFuqW7s93lBmCrZH70jN-41hmsF071'
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'scientific-reproducibility-audit','Range':'bytes=0-4095'})
  with urllib.request.urlopen(req,timeout=45) as r:
   chunk=r.read(4096);drive={'status':r.status,'content_type':r.headers.get('Content-Type'),'content_length':r.headers.get('Content-Length'),'first_bytes_hex':chunk[:16].hex(),'url':url,'zip_header':chunk.startswith(b'PK')}
   if b'<html' in chunk.lower() or b'<!doctype' in chunk.lower():(B/'sources/ENsiRNA_structures_access_response.html').write_bytes(chunk)
 except Exception as e:drive={'url':url,'error':str(e)}
 (B/'ENsiRNA_structure_access_probe.json').write_text(json.dumps(drive,indent=2)+'\n');print('STRUCTURE_ACCESS',drive)
 # Training-table schema discovery only, no training or evaluation here.
 base=pathlib.Path('/home/boltzmann13/IMRAN/OCT26/siRNA-Bench/external/siRNADiscovery')
 import pandas as pd
 for name in ['siRNA_split/siRNA_split_datasets/split0/train.csv','siRNA_split/siRNA_split_datasets/split0/dev.csv','siRNA_split/siRNA_split_datasets/split0/test.csv','Data/Simone/Simone_efficacy.csv']:
  p=base/name
  if p.exists():
   x=pd.read_csv(p);print('DATA_SCHEMA',name,len(x),list(x.columns));print('ID_SAMPLE',x[[c for c in x.columns if c in ['siRNA','mRNA','label','efficacy']]].head(2).to_dict('records'))
 print('PROBE_COMPLETED_NO_EFFICACY_PREDICTIONS')
if __name__=='__main__':main()
