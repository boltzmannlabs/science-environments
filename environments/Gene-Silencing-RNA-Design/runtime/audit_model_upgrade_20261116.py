"""Read-only public model metadata audit; does not install or run model code."""
import json,pathlib,urllib.request,urllib.parse,datetime,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'siRNA-reproducibility-audit','Accept':'application/vnd.github+json'})
 with urllib.request.urlopen(req,timeout=45) as f:return json.load(f)
def main():
 OUT.mkdir(parents=True,exist_ok=True);src=OUT/'sources';src.mkdir(exist_ok=True)
 results=[]
 for query in ['ENsiRNA','SiaRNA']:
  url='https://api.github.com/search/repositories?q='+urllib.parse.quote(query)
  try:
   d=get(url);(src/(query+'_github_search.json')).write_text(json.dumps(d,indent=2)+'\n')
   print('SEARCH',query,[(r['full_name'],r['description']) for r in d['items'][:5]])
  except Exception as e:print('SEARCH_ERROR',query,str(e));continue
  for repo in d['items'][:2]:
   name=repo['full_name'];base='https://api.github.com/repos/'+name
   record={k:repo.get(k) for k in ['full_name','html_url','description','default_branch','license','size','pushed_at']}
   try:
    tree=get(base+'/git/trees/'+repo['default_branch']+'?recursive=1')
    (src/(name.replace('/','_')+'_tree.json')).write_text(json.dumps(tree,indent=2)+'\n')
    record['files']=[{'path':f['path'],'size':f.get('size')} for f in tree['tree'] if f['type']=='blob' and (f['path'].lower().endswith(('.pt','.pth','.pkl','.pickle','.h5','.keras','.ckpt')) or any(x in f['path'].lower() for x in ['readme','requirement','environment','license']))]
    readme=get(base+'/readme');import base64
    text=base64.b64decode(readme['content']).decode();(src/(name.replace('/','_')+'_README.md')).write_text(text)
    record['readme_url']=readme['html_url'];print('REPO',json.dumps(record,indent=2));print('README',text[:14000])
   except Exception as e:record['error']=str(e)
   results.append(record)
 (OUT/'model_metadata_audit.json').write_text(json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Public metadata/documentation retrieval only. No model code downloaded, installed or executed.','models':results},indent=2)+'\n')
def release_audit():
 records=[]
 for repo in ['ChengkuiZhao/siRNABERT','tanwenchong/ENsiRNA']:
  url='https://api.github.com/repos/'+repo+'/releases'
  try:
   data=get(url);r={'repository':repo,'source':url,'releases':[{'tag':x['tag_name'],'assets':[{'name':a['name'],'size':a['size'],'url':a['browser_download_url']} for a in x.get('assets',[])]} for x in data]}
  except Exception as e:r={'repository':repo,'source':url,'error':str(e)}
  records.append(r);print('RELEASE_ASSET_AUDIT',json.dumps(r))
 (OUT/'additional_release_assets_audit.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':
 import sys
 release_audit() if '--releases' in sys.argv else main()
