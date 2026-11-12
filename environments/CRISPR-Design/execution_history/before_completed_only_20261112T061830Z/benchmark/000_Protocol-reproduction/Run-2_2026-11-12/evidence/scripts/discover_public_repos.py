import pathlib,json,urllib.request,urllib.parse,concurrent.futures,re,time
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text())
repos={'crispron':'RTH-tools/crispron','rs_dev':'gpp-rnd/rs_dev','rs3':'gpp-rnd/rs3','rs3_manuscript':'broadinstitute/rs3_manuscript','be_bystander':'maxwshen/be_predict_bystander','be_efficiency':'maxwshen/be_predict_efficiency','PRIDICT2':'uzh-dqbm-cmi/PRIDICT2','GenET':'Goosang-Yu/genet','bacterial_crispri':'BarquistLab/CRISPRi_guide_efficiency_bacteria','crispria':'mhorlbeck/CRISPRiaDesign','cas13':'sanjanalab/cas13','CHANGEseq':'tsailabSJ/changeseq'}
def get(item):
 name,repo=item;url='https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1'
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'CRISPR-validation-research','Accept':'application/vnd.github+json'})
  with urllib.request.urlopen(req,timeout=60) as f:data=json.load(f)
  (ROOT/'sources'/f'{name}_tree.json').write_text(json.dumps(data,indent=2));return name,repo,data
 except Exception as e:return name,repo,{'error':str(e)}
summary={}
for name,repo,data in concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,repos.items()):
 summary[name]={'repository':repo,'tree_sha':data.get('sha'),'truncated':data.get('truncated'),'error':data.get('error')}
 print('\nREPO',name,repo,'SHA',data.get('sha'),'ERROR',data.get('error'))
 files=[r for r in data.get('tree',[]) if r['type']=='blob'];print('FILES',len(files),'TOTAL_KNOWN_BYTES',sum(r.get('size',0) for r in files))
 matches=[r for r in files if re.search('train|test|held|split|data/|csv|tsv|rds|pkl|xlsx|validation|benchmark|README|readme|licen|cop',r['path'],re.I)]
 for r in matches[:65]:print(r['path'],r.get('size'))
(ROOT/'sources/repository_discovery.json').write_text(json.dumps(summary,indent=2))
