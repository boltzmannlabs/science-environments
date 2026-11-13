import pathlib,json,re,gzip,zipfile,urllib.request,concurrent.futures,subprocess,os
import openpyxl
REPO=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env');ROOT=pathlib.Path((REPO/'05_validated_benchmarks/CURRENT.txt').read_text())
archive=json.loads((REPO/'04_workflow_runs/LATEST_SESSION_ARCHIVE.json').read_text());P=pathlib.Path(archive['archive_root'])/'crispr_published_comparison_20261111T101946Z/papers'
for pid in ['34050182','36068235','32518401','32533916','38907037','37119812','32541958','38200565','27661255']:
 txt='\n'.join(p.read_text() for p in (P/pid).glob('*evidence.txt'))
 urls=sorted(set(re.findall(r'https?://[^\s<>\)\]"\\]+',txt)))
 print('\nPAPER',pid,'REPO/DATA URLS')
 for u in urls:
  if any(k in u.lower() for k in ['github','gitlab','zenodo','figshare','osf.io','geo','gse','gpp','pridict','deepprime']):print(u[:250])
 print('Supplementary hrefs')
 for f in (P/pid).glob('fulltext.xml'):
  import xml.etree.ElementTree as ET
  x=ET.fromstring(f.read_bytes())
  for e in x.iter():
   if e.tag in ['supplementary-material','ext-link','media']:
    href=e.attrib.get('{http://www.w3.org/1999/xlink}href','')
    if href and (e.tag!='ext-link' or any(t in href for t in ['github','gitlab','zenodo','figshare'])):print(e.tag,href[:200])
for f in (REPO/'02_benchmarks/datasets/crispron_paper').glob('*.xlsx'):
 wb=openpyxl.load_workbook(f,read_only=True,data_only=True);print('\nXLSX',f.name)
 for s in wb:
  print('SHEET',s.title,'rows',s.max_row,'cols',s.max_column)
  for row in list(s.iter_rows(min_row=1,max_row=min(4,s.max_row),values_only=True)):print(str(row)[:1500])
 wb.close()
# Inventory inherited exact scientific executables without changing them.
for f in [REPO/'03_environment/rs3-env/lib/python3.8/site-packages/rs3-0.0.0.dist-info/METADATA']:
 if f.exists():print(f, f.read_text()[:1000])
