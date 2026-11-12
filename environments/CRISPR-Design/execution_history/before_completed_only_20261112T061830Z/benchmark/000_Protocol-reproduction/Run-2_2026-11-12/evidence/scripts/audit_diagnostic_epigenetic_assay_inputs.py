import pathlib,json,urllib.request,urllib.parse,openpyxl,hashlib,re
ROOT=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt').read_text();ROOT=pathlib.Path(ROOT);manifest=[]
sha='5c06a30d0a43be28a958831587f6ab706c2d4876'
for name in ['README.md','data/Table S1.xlsx','data/Table S2.xlsx','data/Table S3.xlsx','data/Table S4.xlsx']:
 url='https://raw.githubusercontent.com/scRNA-Compt/EasyDesign/'+sha+'/'+urllib.parse.quote(name)
 try:
  p=ROOT/'sources/EasyDesign'/name;p.parent.mkdir(parents=True,exist_ok=True)
  with urllib.request.urlopen(url,timeout=45) as f:p.write_bytes(f.read())
  manifest.append({'url':url,'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  if p.suffix=='.xlsx':
   w=openpyxl.load_workbook(p,read_only=True,data_only=True);print('DIAGNOSTIC_DATA_TABLE',name,w.sheetnames)
   for s in w:
    print('DIAGNOSTIC_SHEET',s.title,'rows',s.max_row,'cols',s.max_column)
    # Metadata/schema only: do not print biological target or guide sequences.
    for row in s.iter_rows(min_row=1,max_row=min(2,s.max_row),values_only=True):
     print('HEADER_CELLS',[str(v)[:120] if not (isinstance(v,str) and re.fullmatch('[ACGTUacgtu]{15,}',v)) else '[sequence omitted]' for v in row[:12]])
   w.close()
  else:print('DIAGNOSTIC_README_AVAILABLE',len(p.read_bytes()))
 except Exception as e:print('DIAGNOSTIC_ASSET_ERROR',name,str(e))
# Verify the epigenetic reference accession and actual assay families; no nuclease-score substitution.
url='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE168012&targ=self&form=text&view=full'
try:
 with urllib.request.urlopen(url,timeout=60) as f:b=f.read()
 p=ROOT/'sources/CRISPRoff_GSE168012_series_metadata.txt';p.write_bytes(b);text=b.decode(errors='replace')
 lines=[line for line in text.splitlines() if any(k in line for k in ['!Series_title','!Series_type','!Series_relation','!Series_supplementary_file','!Series_summary'])];print('EPIGENETIC_ASSAY_METADATA','\n'.join(lines)[:12000]);manifest.append({'url':url,'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'series_headers_present':bool(lines)})
except Exception as e:print('EPIGENETIC_METADATA_ERROR',str(e))
(ROOT/'downloads/diagnostic_epigenetic_data_manifest.json').write_text(json.dumps(manifest,indent=2))
