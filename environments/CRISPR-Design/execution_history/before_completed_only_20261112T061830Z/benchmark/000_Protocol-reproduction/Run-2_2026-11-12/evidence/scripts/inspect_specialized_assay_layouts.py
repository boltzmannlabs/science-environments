import pathlib,openpyxl,json,urllib.request
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
w=openpyxl.load_workbook(ROOT/'data/plant_published_supplement.xlsx',read_only=True,data_only=True)
for i,row in enumerate(w['Data 2'].iter_rows(values_only=True),1):print(i,row)
w.close()
# Correct verified Springer static host, keeping the literal supplementary filename from the primary XML.
u='https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-023-03153-y/MediaObjects/13059_2023_3153_MOESM2_ESM.xlsx'
try:
 p=ROOT/'data/bacterial_CRISPRi_primary_supplement.xlsx'
 if not p.exists():
  with urllib.request.urlopen(u,timeout=90) as f:p.write_bytes(f.read())
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);print('BACTERIAL_PRIMARY_SUPP_SHEETS',w.sheetnames)
 for name in w.sheetnames:
  if any(t in name.lower() for t in ['s13','s14','s2','s10','s12']):
   s=w[name];print('BACTERIAL_DATA_HEADER',name,s.max_row,s.max_column)
   for r in s.iter_rows(min_row=1,max_row=min(4,s.max_row),values_only=True):print(str(r)[:6000])
 w.close()
except Exception as e:print('BACTERIAL_PRIMARY_SUPPLEMENT_BLOCKER',e)
# Discover only public diagnostic benchmark assets; no pathogen guide design or new sequence scoring.
try:
 u='https://api.github.com/repos/scRNA-Compt/EasyDesign/git/trees/HEAD?recursive=1'
 with urllib.request.urlopen(u,timeout=60) as f:d=json.load(f)
 (ROOT/'sources/EasyDesign_tree.json').write_text(json.dumps(d,indent=2));print('EASYDESIGN_COMMIT',d.get('sha'))
 for r in d.get('tree',[]):
  if r['type']=='blob' and any(k in r['path'].lower() for k in ['test','csv','xls','result','readme','eval']):print('DIAGNOSTIC_ASSET',r['path'],r.get('size'))
except Exception as e:print('DIAGNOSTIC_DATA_DISCOVERY_BLOCKER',e)
