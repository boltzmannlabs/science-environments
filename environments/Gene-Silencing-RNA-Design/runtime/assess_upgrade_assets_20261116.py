"""Second public-asset access attempt and ENsiRNA training/test overlap audit.
Read metadata and author CSVs only; never log access tokens or signed URLs.
"""
import pathlib,json,urllib.request,urllib.parse,re,hashlib,csv,html
ROOT=pathlib.Path(__file__).resolve().parents[1];B=ROOT/'benchmark/013_Model-upgrade/Run-5_2026-11-16'
def main():
 (B/'training_scope_decision.json').write_text(json.dumps({'user_response':'Only pursue published pretrained models. Do not train new research baselines; report missing assets or reproducibility blockers if they cannot be resolved.','custom_training_permitted':False},indent=2)+'\n')
 t=json.loads((B/'sources/tanwenchong_ENsiRNA_tree.json').read_text());records=[]
 for name in ['ENsiRNA/dataset/test.csv']+['ENsiRNA/dataset/train_'+str(i)+'.csv' for i in range(1,6)]:
  url='https://raw.githubusercontent.com/tanwenchong/ENsiRNA/'+t['sha']+'/'+name
  p=B/'sources'/('ENsiRNA_'+name.replace('/','_'))
  if not p.exists():
   with urllib.request.urlopen(url,timeout=60) as r:p.write_bytes(r.read())
  data=p.read_bytes();entry=next(x for x in t['tree'] if x['path']==name);blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==entry['sha']
  with p.open() as f:rr=list(csv.DictReader(f))
  print('DATASET',name,len(rr),'COLUMNS',list(rr[0]),'IDS',[(r.get('siRNA'),r.get('mRNA')) for r in rr[:3]])
  records.append({'source':url,'saved_path':str(p.relative_to(ROOT)),'rows':len(rr),'columns':list(rr[0]),'sha256':hashlib.sha256(data).hexdigest(),'git_blob_verified':True})
 probe=[]
 for url in ['https://drive.google.com/uc?export=download&id=1XHuFuqW7s93lBmCrZH70jN-41hmsF071','https://drive.google.com/file/d/1XHuFuqW7s93lBmCrZH70jN-41hmsF071/view']:
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r:
    buf=r.read(1200000);ctype=r.headers.get('Content-Type','');finalhost=urllib.parse.urlparse(r.geturl()).hostname
    result={'requested_url':url,'status':r.status,'content_type':ctype,'content_length':r.headers.get('Content-Length'),'final_host':finalhost,'bytes_inspected':len(buf),'zip_header':buf.startswith(b'PK')}
    if 'html' in ctype:
     text=buf.decode(errors='replace');result['title']=re.findall(r'<title>(.*?)</title>',text,re.S);text=re.sub(r'<(style|script)\b[^>]*>.*?</\1>',' ',text,flags=re.S);text=html.unescape(re.sub('<[^>]+>',' ',text));result['visible_text_excerpt']=' '.join(text.split())[:1800]
    probe.append(result);print('ACCESS_ATTEMPT',json.dumps(result,indent=2))
  except Exception as e:probe.append({'requested_url':url,'error':str(e)});print('ACCESS_ERROR',str(e))
 (B/'ENsiRNA_asset_assessment.json').write_text(json.dumps({'repository_commit':t['sha'],'license_declaration':'Root author README says ENsiRNA is released under Apache v2.0. No Rosetta license accepted.','datasets':records,'public_structure_access_attempts':probe},indent=2)+'\n')
if __name__=='__main__':main()
