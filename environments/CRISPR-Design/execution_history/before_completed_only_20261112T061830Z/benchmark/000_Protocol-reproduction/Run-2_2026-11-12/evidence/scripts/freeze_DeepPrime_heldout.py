import pathlib,json,urllib.request,concurrent.futures,hashlib,openpyxl,collections,pandas as pd
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT);sha='99272383d1420576551d271d865b9972a63466c0'
tree=json.loads((ROOT/'sources/DeepPrime_tree.json').read_text());jobs=[r['path'] for r in tree['tree'] if r['type']=='blob' and (r['path'].startswith('models/DeepPrime/DeepPrime_base/') or r['path'] in ['src/dprime.py','src/utils.py','models/load_model.py'])]
def get(name):
 p=ROOT/'sources/DeepPrime_release'/name;p.parent.mkdir(parents=True,exist_ok=True);u='https://raw.githubusercontent.com/hkimlab/DeepPrime/'+sha+'/'+name
 if not p.exists():
  with urllib.request.urlopen(u,timeout=60) as f:p.write_bytes(f.read())
 return {'path':name,'url':u,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
manifest=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(get,jobs));(ROOT/'downloads/DeepPrime_model_manifest.json').write_text(json.dumps(manifest,indent=2))
p=ROOT/'downloads/DeepPrime_mmc2.xlsx';w=openpyxl.load_workbook(p,read_only=True,data_only=True)
s=list(w['Summary'].iter_rows(min_row=5,values_only=True));print('DEEPPRIME_CONDITIONS');print('\n'.join(str(r) for r in s[:5]))
cols=['split','model','Target74','Edited74','PBSlen','RTlen','RT_PBSlen','Edit_pos','Edit_len','RHA_len','type_sub','type_ins','type_del','Tm1','Tm2','Tm2new','Tm3','Tm4','TmD','nGCcnt1','nGCcnt2','nGCcnt3','fGCcont1','fGCcont2','fGCcont3','MFE3','MFE4','DeepSpCas9_score','Measured_PE_efficiency','Fold']
train_keys=set();test=[];count=collections.Counter();train_target=set()
for rownum,row in enumerate(w['1'].iter_rows(min_row=5,values_only=True),5):
 if row[0] is None:continue
 row=list(row[:30]);key=hashlib.sha256(json.dumps(row[2:4]+[float(v) for v in row[4:28]],separators=(',',':')).encode()).hexdigest();count[str(row[0])]+=1
 if row[0]=='Train':train_keys.add(key);train_target.add(row[2])
 elif row[0]=='Test':test.append(dict(zip(cols,row),source_excel_row=rownum,input_sha256=key))
 else:raise RuntimeError('Unexpected original split token '+str(row[0]))
 if rownum%50000==0:print('SCANNED_DEEPPRIME',rownum,flush=True)
w.close();test=pd.DataFrame(test);assert len(test)>0;test['exact_predictive_input_training_overlap']=test.input_sha256.isin(train_keys);test['unedited_target74_training_overlap']=test.Target74.isin(train_target)
test.to_csv(ROOT/'data/DeepPrime_base_author_test.csv',index=False)
protocol={'model':'DeepPrime base','source_commit':sha,'primary_source':'Cell2023 supplementaryTableS2, sheet1 Library-ClinVar-HEK293T-PE2','workbook_url':'https://ars.els-cdn.com/content/image/1-s2.0-S0092867423003318-mmc2.xlsx','workbook_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'condition_summary_row':list(s[1]),'split_counts':dict(count),'test_rows':len(test),'exact_predictive_input_train_test_overlaps':int(test.exact_predictive_input_training_overlap.sum()),'target74_train_test_overlaps':int(test.unedited_target74_training_overlap.sum()),'input_features':'Provided74nt unedited+masked edited target and all native24 numerical features, not regenerated approximations','labels':'Measured_PE_efficiency from source workbook; no target labels passed to predictor','prediction':'Native DeepPrime_base5-checkpoint ensemble, source normalization mean/std, no fine-tuned other-cell/editor models','feature_scope':'exact original HEK293T/PE2/conventional scaffold condition; not generalized across8 systems/7 cells','frozen_before_inference':True}
(ROOT/'protocols/DeepPrime_base_heldout.json').write_text(json.dumps(protocol,indent=2));print(json.dumps(protocol,indent=2))
for name in ['src/dprime.py','models/load_model.py','src/utils.py']:
 print('\nNATIVE_SOURCE',name);print((ROOT/'sources/DeepPrime_release'/name).read_text())
