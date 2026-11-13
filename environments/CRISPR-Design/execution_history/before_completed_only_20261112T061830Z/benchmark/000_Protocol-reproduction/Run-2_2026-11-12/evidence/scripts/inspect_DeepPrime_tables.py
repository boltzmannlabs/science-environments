import pathlib,openpyxl,json,pandas as pd,ast
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
p=ROOT/'downloads/DeepPrime_mmc2.xlsx';w=openpyxl.load_workbook(p,read_only=True,data_only=True)
for name in ['Summary','1','2','3','4','5','6','7','8','9','10']:
 s=w[name];print('\nDEEPPRIME_SHEET',name,'ROWS',s.max_row,'COLS',s.max_column)
 for row in s.iter_rows(min_row=1,max_row=min(5,s.max_row),values_only=True):print(str(row)[:6000])
w.close()
tree=json.loads((ROOT/'sources/DeepPrime_tree.json').read_text());print('\nBASE_MODEL_FILES')
for r in tree['tree']:
 if r['type']=='blob' and ('base' in r['path'].lower() or r['path'].startswith('src/') and r['path'].endswith('.py')):print(r['path'],r.get('size'))
p=ROOT/'sources/bacterial_crispri/3_Segregating_gene_effects/test/iteration_predictions.csv'
x=pd.read_csv(p,sep='\t');print('\nBACTERIAL_REPLAY_ROWS',x.shape,list(x.columns));print(x.iloc[0].map(lambda v:str(v)[:150]).to_dict())
for col in ['log2FC','pred','dataset','clusters']:
 a=ast.literal_eval(x[col].iloc[0]);print('PARSED',col,len(a),a[:4])
