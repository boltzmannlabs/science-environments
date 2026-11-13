import pathlib,urllib.request,json,openpyxl,hashlib,pandas as pd
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
u='https://raw.githubusercontent.com/Schwank-Lab/epridict/c024f806a9590b1395b85a337276629caac134a5/SupplFile1_Library_Diverse_Editing_Results_with_test_splits.xlsx';p=ROOT/'data/PRIDICT2_published_results_with_test_splits.xlsx'
if not p.exists():
 with urllib.request.urlopen(u,timeout=120) as f:p.write_bytes(f.read())
w=openpyxl.load_workbook(p,read_only=True,data_only=True);print('OFFICIAL_SPLIT_WORKBOOK',w.sheetnames)
for s in w:
 print('SHEET',s.title,s.max_row,s.max_column)
 for row in s.iter_rows(min_row=1,max_row=min(5,s.max_row),values_only=True):print(str(row)[:10000])
w.close();(ROOT/'protocols/PRIDICT2_official_split_workbook_identity.json').write_text(json.dumps({'url':u,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()},indent=2))
# Published author-output reference distribution, not a new RF fit.
p=ROOT/'sources/Cas13_original/PredictiveModel_AllScreens/data/Learning_approaches_Spearman_v3.csv';x=pd.read_csv(p);a=x.RandomForest
r={'mode':'AUTHOR_OUTPUT_METRIC_REFERENCE_ONLY','source':'Original CompareModels.R takes median RandomForest column','source_rows':len(a),'median_spearman':float(a.median()),'mean_spearman':float(a.mean()),'published_output_percentiles':a.quantile([.025,.975]).to_list(),'not_new_inference':True};(ROOT/'reports/cas13_author_metric_reference.json').write_text(json.dumps(r,indent=2));print('CAS13_AUTHOR_REFERENCE',json.dumps(r))
