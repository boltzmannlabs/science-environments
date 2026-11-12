import pathlib,json,urllib.request,urllib.parse,re,xml.etree.ElementTree as ET,hashlib,tarfile
R=pathlib.Path('/home/boltzmann13/IMRAN/NOV26/cirspr-sci-env/05_validated_benchmarks/CURRENT.txt');ROOT=pathlib.Path(R.read_text());manifest=[]
def get(url,name):
 dest=ROOT/'downloads'/name
 if not dest.exists():
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'CRISPR-validation-research'}),timeout=90) as f:b=f.read()
  dest.write_bytes(b)
 b=dest.read_bytes();manifest.append({'url':url,'path':str(dest),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)});return b
# Correct published DeepPrime implementation, rather than inferring from a newer wrapper.
for name,repo in [('DeepPrime','hkimlab/DeepPrime'),('CRISPRoffT','')]:
 if not repo:continue
 try:
  data=json.loads(get('https://api.github.com/repos/'+repo+'/git/trees/HEAD?recursive=1',name+'_tree.json'));(ROOT/'sources'/f'{name}_tree.json').write_text(json.dumps(data,indent=2))
  print('REPO',repo,'SHA',data.get('sha'))
  for f in data.get('tree',[]):
   if f['type']=='blob':print(f['path'],f.get('size'))
 except Exception as e:print('FAILED_REPO',repo,e)
# Obtain benchmark repository URLs from primary literature, not guessed mirrors.
for pid in ['39526384']:
 url='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'EXT_ID:'+pid+' AND SRC:MED','format':'json','resultType':'core'})
 try:
  rec=json.loads(get(url,pid+'_metadata.json'))['resultList']['result'][0];print('PAPER',pid,rec.get('pmcid'),rec.get('abstractText'))
  if rec.get('pmcid'):
   raw=get('https://www.ebi.ac.uk/europepmc/webservices/rest/'+rec['pmcid']+'/fullTextXML',pid+'.xml');x=ET.fromstring(raw)
   for e in x.iter():
    href=e.attrib.get('{http://www.w3.org/1999/xlink}href','')
    if href and (e.tag in ['media','supplementary-material'] or any(s in href.lower() for s in ['github','gitlab','download','crisprofft','zenodo'])):print('SOURCE_URL',e.tag,href)
 except Exception as e:print('FAILED_PAPER',pid,e)
# Review Figshare measured-data file inventories without downloading unknown large datasets.
for article in ['10673816','10678097']:
 try:
  data=json.loads(get('https://api.figshare.com/v2/articles/'+article,'figshare_'+article+'.json'));print('FIGSHARE',article,data.get('title'))
  for f in data.get('files',[]):print('DATAFILE',f['name'],f['size'],f['download_url'])
 except Exception as e:print('FAILED_FIGSHARE',article,e)
try:
 url='https://gitlab.com/api/v4/projects/'+urllib.parse.quote('sanjanalab/cas13',safe='')+'/repository/tree?recursive=true&per_page=100'
 data=json.loads(get(url,'Cas13_GitLab_tree.json'));print('CAS13_GITLAB',data)
except Exception as e:print('CAS13_GITLAB_BLOCKER',e)
# Download the real PRIDICT2 code and checkpoints together at a pinned commit.
try:
 sha='c133c35e205062e766bf515d1766169167e993b9';raw=get('https://codeload.github.com/uzh-dqbm-cmi/PRIDICT2/tar.gz/'+sha,'PRIDICT2_'+sha+'.tar.gz')
 with tarfile.open(ROOT/'downloads'/('PRIDICT2_'+sha+'.tar.gz')) as tf:
  out=ROOT/'sources/PRIDICT2_release';out.mkdir(exist_ok=True);tf.extractall(out,filter='data')
 print('PRIDICT2_RELEASE_BYTES',len(raw))
except Exception as e:print('PRIDICT2_RELEASE_BLOCKER',e)
(ROOT/'downloads/additional_manifest.json').write_text(json.dumps(manifest,indent=2))
