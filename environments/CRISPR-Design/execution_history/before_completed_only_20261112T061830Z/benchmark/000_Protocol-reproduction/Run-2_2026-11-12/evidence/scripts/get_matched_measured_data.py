import pathlib,json,urllib.request,urllib.parse,re,concurrent.futures,hashlib
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text());manifest=[]
def fetch(url,dest):
 if dest.exists():b=dest.read_bytes()
 else:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CRISPR-validation-research'}),timeout=60) as r:b=r.read()
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 manifest.append(dict(url=url,path=str(dest),bytes=len(b),sha256=hashlib.sha256(b).hexdigest()));return b
project=urllib.parse.quote('sanjanalab/cas13',safe='');base='https://gitlab.com/api/v4/projects/'+project
try:
 meta=json.loads(fetch(base,ROOT/'sources/Cas13_GitLab_project.json'));branch=meta['default_branch'];commit=json.loads(fetch(base+'/repository/commits/'+branch,ROOT/'sources/Cas13_GitLab_commit.json'))['id'];print('CAS13_PINNED_COMMIT',commit)
 for folder in ['PredictiveModel_AllScreens/scripts','PredictiveModel_AllScreens/data']:
  url=base+'/repository/tree?'+urllib.parse.urlencode({'path':folder,'recursive':'true','per_page':100,'ref':commit})
  tree=json.loads(fetch(url,ROOT/'sources'/('Cas13_'+folder.replace('/','_')+'_tree.json')))
  for r in tree:
   if r['type']!='blob':continue
   p=r['path'];print('CAS13_FILE',p)
   if p.endswith(('.R','.r','.Rmd','.csv','.txt')) and ('scripts' in p or any(k in p for k in ['Train','Input','input','Model','DataFrame'])):
    url=base+'/repository/files/'+urllib.parse.quote(p,safe='')+'/raw?ref='+commit
    fetch(url,ROOT/'sources/Cas13_original'/p)
except Exception as e:print('CAS13_SOURCE_ERROR',e)
# Select exactly editor/cell-matched measured efficiency labels; model training/test provenance audited next.
try:
 meta=json.loads((ROOT/'downloads/figshare_10673816.json').read_text());f=next(f for f in meta['files'] if f['name']=='HEK293T_12kChar_BE4.csv');b=fetch(f['download_url'],ROOT/'data/BEHive_HEK293T_BE4_efficiency.csv');print('BE_HIVE_DATA',f['name'],len(b),b[:500])
except Exception as e:print('BE_HIVE_DATA_ERROR',e)
# Inspect the actual database download links; do not label unassayed sites as negatives.
for url in ['https://ccsm.uth.edu/CRISPRoffT/','https://ccsm.uth.edu/CRISPRoffT/download.php']:
 try:
  b=fetch(url,ROOT/'sources'/('CRISPRoffT_'+('index' if url.endswith('/') else 'download')+'.html'));txt=b.decode(errors='replace');links=sorted(set(re.findall(r'(?:href|src)=["\']([^"\']+)',txt)))
  print('OFFTARGET_PAGE',url,'bytes',len(b))
  for u in links:
   if any(t in u.lower() for t in ['download','data','csv','tsv','zip','xlsx','js/']):print('OFFTARGET_LINK',urllib.parse.urljoin(url,u))
 except Exception as e:print('OFFTARGET_PAGE_ERROR',url,e)
(ROOT/'downloads/targeted_data_manifest.json').write_text(json.dumps(manifest,indent=2))
