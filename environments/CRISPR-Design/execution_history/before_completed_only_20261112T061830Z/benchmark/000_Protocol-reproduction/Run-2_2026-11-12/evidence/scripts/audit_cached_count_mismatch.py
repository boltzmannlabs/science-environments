import pathlib,json,urllib.request
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
n=json.loads((ROOT/'sources/rs_dev/code/07_test_seq_model.ipynb').read_text())
for i in [3,5,6,8,9,10]:
 print('\nRS3_CACHED_CELL',i)
 for o in n['cells'][i].get('outputs',[]):
  text=''.join(o.get('data',{}).get('text/plain',[])) or ''.join(o.get('text',[]));print(text[:6000])
t=json.loads((ROOT/'sources/bacterial_crispri_tree.json').read_text());sha='2dad9153ea61db49001e2cb48095fbb2eac46003'
for r in t['tree']:
 if r['type']=='blob' and r['path'].startswith('3_Segregating_gene_effects/') and r['path'].endswith('.py'):
  print('BACTERIAL_METRIC_SOURCE',r['path']);url='https://raw.githubusercontent.com/BarquistLab/CRISPRi_guide_efficiency_bacteria/'+sha+'/'+r['path']
  with urllib.request.urlopen(url,timeout=60) as f:b=f.read()
  p=ROOT/'sources/bacterial_crispri'/r['path'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
