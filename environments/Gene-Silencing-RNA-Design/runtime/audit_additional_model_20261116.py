"""Additional published-pretrained candidate metadata audit; no model installation."""
import urllib.request,urllib.parse,json,pathlib,base64
ROOT=pathlib.Path(__file__).resolve().parents[1];B=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16'
def get(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'scientific-reproducibility-audit'}),timeout=45) as r:return json.load(r)
def main():
 import sys
 query=sys.argv[1] if len(sys.argv)>1 else 'BERT-siRNA in:name';d=get('https://api.github.com/search/repositories?q='+urllib.parse.quote(query));out=[]
 for item in d['items'][:5]:
  base='https://api.github.com/repos/'+item['full_name'];r={k:item.get(k) for k in ['full_name','html_url','description','license','default_branch']}
  try:
   t=get(base+'/git/trees/'+item['default_branch']+'?recursive=1');r['commit']=t['sha'];r['weight_files']=[{'path':x['path'],'bytes':x.get('size')} for x in t['tree'] if x['type']=='blob' and x['path'].endswith(('.bin','.pt','.pth','.ckpt','.h5','.safetensors'))]
   rm=get(base+'/readme');text=base64.b64decode(rm['content']).decode();p=B/'sources'/(item['full_name'].replace('/','_')+'_README.md');p.write_text(text);r['readme_path']=str(p.relative_to(ROOT));print('README',text[:10000])
   (B/'sources'/(item['full_name'].replace('/','_')+'_tree.json')).write_text(json.dumps(t,indent=2)+'\n')
  except Exception as e:r['error']=str(e)
  print('CANDIDATE',json.dumps(r,indent=2));out.append(r)
 existing_path=B/'additional_pretrained_candidates.json'
 previous=json.loads(existing_path.read_text()) if existing_path.exists() else None
 existing_path.write_text(json.dumps({'query':query,'total_github_matches':d['total_count'],'candidates':out,'previous_search':previous,'scope':'Metadata/docs only; no weights or executable code acquired. Any pathogen-specific datasets or outputs excluded.'},indent=2)+'\n')
if __name__=='__main__':main()
