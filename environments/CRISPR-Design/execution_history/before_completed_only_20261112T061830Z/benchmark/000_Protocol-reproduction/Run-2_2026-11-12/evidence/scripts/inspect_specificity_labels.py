import pathlib,urllib.request,json,hashlib,pandas as pd
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text());u='https://ccsm.uth.edu/CRISPRoffT/table_summary/allframe_update_addEpige.txt';p=ROOT/'data/CRISPRoffT_allframe.tsv'
if not p.exists():
 with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CRISPR-validation-research'}),timeout=120) as f:b=f.read()
 p.write_bytes(b)
x=pd.read_csv(p,sep='\t',low_memory=False);print('SHAPE',x.shape,'COLUMNS',list(x.columns));print(x.head(3).to_string(index=False)[:18000])
for c in x.columns:
 if any(t in c.lower() for t in ['valid','tech','eff','rate','cas','method','indel','cell','pmid','stud']):
  print('\nFIELD',c,'UNIQUE',x[c].nunique(),'TOP',x[c].astype(str).value_counts().head(12).to_dict())
(ROOT/'protocols/specificity_data_identity.json').write_text(json.dumps({'url':u,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'rows':len(x),'columns':list(x.columns),'status':'DOWNLOADED_NOT_YET_CLASSIFIED; do not interpret unvalidated rows as negative assays'},indent=2))
