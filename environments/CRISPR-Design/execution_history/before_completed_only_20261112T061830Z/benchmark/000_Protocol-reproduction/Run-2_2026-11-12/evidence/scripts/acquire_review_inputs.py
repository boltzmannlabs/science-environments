import pathlib,json,urllib.request,urllib.parse,concurrent.futures,hashlib,os,gzip
import pandas as pd
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text())
D=json.loads((ROOT/'sources/repository_discovery.json').read_text());jobs=[]
# Download only selected, reviewed input categories at pinned upstream commits.
for name in ['rs_dev','rs3','rs3_manuscript','PRIDICT2','be_bystander','be_efficiency','crispria','bacterial_crispri','GenET']:
 tree=json.loads((ROOT/'sources'/f'{name}_tree.json').read_text());repo=D[name]['repository'];sha=D[name]['tree_sha']
 for r in tree.get('tree',[]):
  if r['type']!='blob':continue
  p=r['path'];size=r.get('size',0);take=False
  if name=='rs_dev':take=(p.startswith('data/processed/') or p in ['data/external/CRISPRon_train.csv','data/external/Kim2019_train_activity_v1.csv','data/external/crispron_rs_dev_all_sgrnas.csv','data/external/Rule_Set_2_rs_dev_all_sgrnas.csv'] or p.startswith('code/'))
  elif name=='rs3':take=p.endswith(('.py','.md','.txt')) and not p.startswith('docs/')
  elif name=='rs3_manuscript':take=True
  elif name=='PRIDICT2':take=p.endswith(('.py','.ipynb','.md','.yml','.yaml','.txt')) or p.startswith('dataset/')
  elif name in ['be_bystander','be_efficiency']:take=p.endswith(('.py','.md','.csv','.txt','.ipynb'))
  elif name=='crispria':take=True
  elif name=='bacterial_crispri':take=p.endswith(('.py','.md','.txt','.csv','.ipynb')) and ('5_Validation' in p or '6_' in p or p.lower().endswith('readme.md') or 'iteration_predictions' in p)
  elif name=='GenET':take=p.endswith(('.py','.md','.csv','.ipynb','.json','.yaml')) and (p.startswith('genet/predict') or p.startswith('tests/') or p=='README.md')
  if take and size<60_000_000:jobs.append((name,p,'https://raw.githubusercontent.com/'+repo+'/'+sha+'/'+urllib.parse.quote(p)))
manifest=[]
def get(job):
 name,p,url=job;dest=ROOT/'sources'/name/p;dest.parent.mkdir(parents=True,exist_ok=True)
 try:
  if dest.exists():
   data=dest.read_bytes();return dict(name=name,path=p,url=url,status='DOWNLOADED',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),reused_completed_download=True)
  with urllib.request.urlopen(url,timeout=30) as f:data=f.read()
  if data.startswith(b'version https://git-lfs.github.com'):return dict(name=name,path=p,url=url,status='LFS_POINTER_NOT_DATA')
  dest.write_bytes(data);return dict(name=name,path=p,url=url,status='DOWNLOADED',bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
 except Exception as e:return dict(name=name,path=p,url=url,status='FAILED',error=str(e))
for r in concurrent.futures.ThreadPoolExecutor(max_workers=5).map(get,jobs):
 manifest.append(r);(ROOT/'downloads/source_download_manifest.json').write_text(json.dumps(manifest,indent=2))
 if len(manifest)%20==0:print('DOWNLOAD_PROGRESS',len(manifest),'/',len(jobs),r['name'],flush=True)
(ROOT/'downloads/source_download_manifest.json').write_text(json.dumps(manifest,indent=2));print('SOURCE_FILES',len(manifest),'FAILED',sum(r['status']!='DOWNLOADED' for r in manifest))
for p in [ROOT/'sources/rs_dev/data/processed/train_data_names.csv',ROOT/'sources/rs_dev/data/external/CRISPRon_train.csv',ROOT/'sources/rs_dev/data/processed/Chari2015_activity.csv',ROOT/'sources/PRIDICT2/dataset/proc_v2/data_23k_v1.csv']:
 if p.exists():
  x=pd.read_csv(p);print('\nTABLE',p.relative_to(ROOT),'SHAPE',x.shape,'COLUMNS',list(x.columns));print(x.head(2).to_string(index=False)[:4000])
# Inspect the actual inherited RFcombined feature/response data; this is not held-out inference.
BASE=pathlib.Path('/home/boltzmann13/.sci/profiles/generate-sirna/workspace/crispr_design_gene_knockout_001_KIF11_GRCh38')
p=BASE/'bootstrap/R-library/crisprScore/casrxrf/Cas13designGuidePredictorInput.csv.gz'
x=pd.read_csv(p);print('\nRF_FEATURE_DATA',x.shape,list(x.columns));print(x.head(2).to_string()[:6000])
(ROOT/'data/cas13_feature_table.source_path.txt').write_text(str(p));(ROOT/'data/cas13_feature_table.csv').write_text(x.to_csv(index=False))
