import pathlib,json,urllib.request,xml.etree.ElementTree as ET,re,tarfile,io,hashlib,pandas as pd
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text());archive=json.loads((REPO/'04_workflow_runs/LATEST_SESSION_ARCHIVE.json').read_text());P=pathlib.Path(archive['archive_root'])/'crispr_published_comparison_20261111T101946Z/papers';manifest=[]
for pid,pmc,name in [('42029722','PMC13109197','plant'),('39135699','PMC11316927','diagnostics')]:
 p=P/pid/'fulltext.xml'
 if p.exists():
  a=ET.fromstring(p.read_bytes());print('\nP4_SOURCE',name)
  for e in a.iter():
   href=e.attrib.get('{http://www.w3.org/1999/xlink}href','')
   if href and (e.tag in ['media','supplementary-material'] or any(k in href.lower() for k in ['github','zenodo','figshare'])):print('ASSET_POINTER',href)
  for sec in a.iter('sec'):
   title=sec.findtext('title') or ''
   if any(s in title.lower() for s in ['availability','data sharing']):print('DATA_ACCESS_TEXT',''.join(sec.itertext())[:4000])
 url='https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id='+pmc
 try:
  with urllib.request.urlopen(url,timeout=40) as f:b=f.read()
  (ROOT/'sources'/f'{name}_OA_inventory.xml').write_bytes(b);oa=ET.fromstring(b)
  errors=oa.findall('.//error')
  if errors:print('OA_ACCESS_LIMIT',name,[e.text for e in errors]);continue
  links=oa.findall('.//link')
  tgz=next((e.attrib['href'] for e in links if e.attrib.get('format')=='tgz'),None)
  if not tgz:continue
  public=tgz.replace('ftp://','https://',1)
  with urllib.request.urlopen(public,timeout=120) as f:b=f.read()
  target=ROOT/'downloads'/f'{name}_OA_package.tar.gz';target.write_bytes(b);print('OA_PACKAGE',name,len(b));manifest.append({'source_inventory':url,'source_archive_url':tgz,'requested_https_url':public,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
  with tarfile.open(fileobj=io.BytesIO(b),mode='r:gz') as tar:
   for member in tar.getmembers():
    if member.isfile() and member.name.lower().endswith(('.csv','.xlsx','.xls','.tsv','.txt')):
     data=tar.extractfile(member).read();d=ROOT/'data'/f'{name}_supplementary'/pathlib.Path(member.name).name;d.parent.mkdir(exist_ok=True);d.write_bytes(data);print('MATCHED_ASSAY_ASSET',d.name,len(data))
     if d.suffix=='.xlsx':
      book=pd.ExcelFile(d);print('SHEETS',book.sheet_names)
      for s in book.sheet_names[:4]:print('ASSET_HEADER',s,pd.read_excel(book,s,nrows=3).to_string(index=False)[:3500])
 except Exception as e:print('OA_ASSET_RETRIEVAL_BLOCKER',name,str(e));manifest.append({'source_inventory':url,'status':'FAILED','error':str(e)})
# Inspect relevant data scope, not score-tune it.
c=pd.read_csv(ROOT/'data/specificity_assayed_cohort.csv');print('SPECIFICITY_ASSEMBLY',c.Assembly.value_counts().to_dict());print('SPECIFICITY_BULGE_FIELDS',{f:c[f].fillna('MISSING').value_counts().head().to_dict() for f in ['Bulge','Bulge2']});print('VALIDATION_DISAGREEMENTS',pd.crosstab(c.Validation,c.positive).to_dict())
# Public source Box folder; no authentication bypass, no credentials or upload.
try:
 u='https://ucsf.box.com/s/s4ds471in2ngjer7okavzf5cqf2ebrqj'
 with urllib.request.urlopen(u,timeout=45) as f:b=f.read()
 (ROOT/'sources/Horlbeck_public_feature_folder.html').write_bytes(b);print('HORLBECK_PUBLIC_FOLDER_RESPONSE',len(b),'HTML only; model/feature archive not automatically accepted')
except Exception as e:print('HORLBECK_FEATURE_ACCESS_BLOCKER',str(e))
(ROOT/'downloads/specialized_assay_asset_manifest.json').write_text(json.dumps(manifest,indent=2))
