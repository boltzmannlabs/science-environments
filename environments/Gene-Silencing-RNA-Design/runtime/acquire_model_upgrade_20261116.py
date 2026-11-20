"""Acquire only reviewed SiaRNA inference assets; verify Git blob SHA/size at pinned commit.
No package installation and no upstream code execution. User approved local use.
"""
import json,pathlib,urllib.request,hashlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[1];B=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16'
CACHE=pathlib.Path('/home/boltzmann13/.sci/profiles/imran-sirna-task/workspace/model-backends')
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'siRNA-model-audit'}),timeout=120) as f:return f.read()
def main():
 assert (B/'installation_approval.json').exists()
 t=json.loads((B/'sources/drugparadigm_SiaRNA_tree.json').read_text());commit=t['sha'];dest=CACHE/'SiaRNA'/commit;dest.mkdir(parents=True,exist_ok=True)
 paths=['README.md','environment.yaml','infer.py','preprocess.py','model.py','utils.py','efficacy_dataset.py','training.py','siRNA_param_pytorch.json','data/mRNA.fa','data/siRNA.fa','checkpoints/best_model_fold.pt'];files=[]
 for name in paths:
  item=next(x for x in t['tree'] if x['path']==name);p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
  if not p.exists():p.write_bytes(get('https://raw.githubusercontent.com/drugparadigm/SiaRNA/'+commit+'/'+name))
  data=p.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  if len(data)!=item['size'] or blob!=item['sha']:raise RuntimeError('Asset verification failed '+name)
  files.append({'path':str(p),'relative_path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha':blob})
  print('VERIFIED',name,len(data),flush=True)
 # ENsiRNA source inspection only; do not acquire Rosetta, RNA-FM or checkpoints yet.
 e=json.loads((B/'sources/tanwenchong_ENsiRNA_tree.json').read_text())
 for name in ['ENsiRNA/README.md','ENsiRNA/test.py','ENsiRNA/data/dataset.py','ENsiRNA/data/get_pdb.py','ENsiRNA/design.sh']:
  if any(x['path']==name for x in e['tree']):
   (B/'sources'/('ENsiRNA_'+name.replace('/','_'))).write_bytes(get('https://raw.githubusercontent.com/tanwenchong/ENsiRNA/'+e['sha']+'/'+name))
 record={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model':'SiaRNA','author_repository':'https://github.com/drugparadigm/SiaRNA','commit':commit,'local_asset_root':str(dest),'files':files,'license_status':'No first-party license found; explicit user confirmation of research-use permission recorded; no redistribution.','publisher_checksum':'Git blob hashes and sizes from pinned author repository tree; SHA-256 locally measured, not a publisher SHA-256 attestation.','code_execution_performed':False,'package_installation_performed':False}
 (B/'acquisition_provenance.json').write_text(json.dumps(record,indent=2)+'\n');print('ASSET_ROOT',dest)
if __name__=='__main__':main()
