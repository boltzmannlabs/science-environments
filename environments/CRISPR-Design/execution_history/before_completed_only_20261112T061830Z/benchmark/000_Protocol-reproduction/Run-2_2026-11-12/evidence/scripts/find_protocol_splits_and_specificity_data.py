import pathlib,json,urllib.request,urllib.parse,re,pandas as pd
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text())
def get(url,path):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CRISPR-validation-research'}),timeout=60) as f:b=f.read()
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b);return b
url='https://ccsm.uth.edu/CRISPRoffT/download.html'
try:
 b=get(url,ROOT/'sources/CRISPRoffT_download.html');txt=b.decode(errors='replace')
 print('OFFTARGET_DOWNLOAD_LINKS')
 for href in sorted(set(re.findall(r'(?:href|src)=["\']([^"\']+)',txt))):
  if any(s in href.lower() for s in ['download','csv','tsv','xlsx','zip','data']):print(urllib.parse.urljoin(url,href))
 print('DOWNLOAD_CONTEXT',re.sub('<[^>]+>',' ',txt)[-16000:])
except Exception as e:print('OFFTARGET_DOWNLOAD_ERROR',e)
try:
 b=get('https://raw.githubusercontent.com/hkimlab/DeepPrime/99272383d1420576551d271d865b9972a63466c0/README.md',ROOT/'sources/DeepPrime_README.md');print('DEEPPRIME_README',b.decode()[:18000])
except Exception as e:print('DEEPPRIME_ERROR',e)
x=pd.read_csv(ROOT/'data/BEHive_HEK293T_BE4_efficiency.csv');print('BEHIVE_SHAPE',x.shape);print('BEHIVE_COLUMNS',list(x.columns));print(x.head(2).to_string(index=False)[:5000]);print('POSSIBLE_SPLIT_COLS',[c for c in x if re.search('train|test|split|fold|predict',c,re.I)])
# Find the original BE-Hive analysis repository's evaluation split artifacts.
try:
 d=json.loads(get('https://api.github.com/repos/maxwshen/lib-analysis/git/trees/HEAD?recursive=1',ROOT/'sources/BEHive_analysis_tree.json'));print('BEHIVE_ANALYSIS_SHA',d.get('sha'))
 for r in d.get('tree',[]):
  if r['type']=='blob' and re.search('train|test|split|efficiency|bystander|predict|model',r['path'],re.I):print('BEHIVE_ANALYSIS_FILE',r['path'],r.get('size'))
except Exception as e:print('BEHIVE_SPLIT_SOURCE_ERROR',e)
