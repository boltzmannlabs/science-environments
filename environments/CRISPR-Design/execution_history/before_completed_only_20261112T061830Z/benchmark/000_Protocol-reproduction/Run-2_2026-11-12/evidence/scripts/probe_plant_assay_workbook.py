import pathlib,urllib.request,concurrent.futures,json,hashlib,openpyxl
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT)
urls=[
 'https://pmc.ncbi.nlm.nih.gov/articles/PMC13109197/bin/299_2026_3820_MOESM1_ESM.xlsx',
 'https://europepmc.org/articles/PMC13109197/bin/299_2026_3820_MOESM1_ESM.xlsx',
 'https://static-content.springer.com/esm/art%3A10.1007%2Fs00299-026-03820-x/MediaObjects/299_2026_3820_MOESM1_ESM.xlsx',
 'https://static-content.springer-cdn.com/esm/art%3A10.1007%2Fs00299-026-03820-x/MediaObjects/299_2026_3820_MOESM1_ESM.xlsx',
 'https://pmc.ncbi.nlm.nih.gov/utils/oa/oa.fcgi?id=PMC13109197']
def get(pair):
 i,u=pair
 try:
  with urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'CRISPR-validation-research'}),timeout=35) as r:b=r.read()
  p=ROOT/'downloads'/f'plant_asset_probe{i}.bin';p.write_bytes(b)
  result={'url':u,'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
  if b.startswith(b'PK'):
   dest=ROOT/'data/plant_published_supplement.xlsx';dest.write_bytes(b);w=openpyxl.load_workbook(dest,read_only=True,data_only=True);result.update(status='VERIFIED_WORKBOOK',sheets=w.sheetnames)
   for s in w:
    print('PLANT_SHEET',s.title,s.max_row,s.max_column,flush=True)
    for row in s.iter_rows(min_row=1,max_row=min(5,s.max_row),values_only=True):print(str(row)[:5000],flush=True)
   w.close()
  else:result.update(status='NON_WORKBOOK_RESPONSE',body_preview=b[:150].decode(errors='replace'))
  return result
 except Exception as e:return {'url':u,'status':'FAILED','error':str(e)}
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(get,enumerate(urls)));(ROOT/'downloads/plant_asset_probe_results.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
