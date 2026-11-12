#!/usr/bin/env python3
"""Safely stream the published tar.gz to retrieve only HER2 benchmark evidence."""
import argparse,hashlib,json,time,tarfile,urllib.request
from pathlib import Path
class BudgetReader:
 def __init__(self,raw,limit,deadline): self.raw=raw;self.limit=limit;self.deadline=deadline;self.bytes=0
 def read(self,n=-1):
  if self.bytes>=self.limit or time.monotonic()>self.deadline:raise TimeoutError('bounded archive scan exhausted')
  d=self.raw.read(n);self.bytes+=len(d);return d
 def close(self):self.raw.close()
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-run',type=Path,required=True);p.add_argument('--max-bytes',type=int,default=1073741824);p.add_argument('--seconds',type=int,default=240);a=p.parse_args()
 out=a.source_run/'inputs'/'released_archive';out.mkdir(parents=True,exist_ok=True)
 u='https://zenodo.org/api/records/15803983/files/ab_seldon_trastuzumab_optimization_tests_v2.tar.gz/content'
 names=[];saved=[];status='completed';reader=None;start=time.monotonic()
 try:
  raw=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'ScientificBenchmarkAudit/1.0'}),timeout=45)
  reader=BudgetReader(raw,a.max_bytes,start+a.seconds)
  with tarfile.open(fileobj=reader,mode='r|gz') as tar:
   for member in tar:
    names.append({'name':member.name,'size':member.size})
    name=member.name; low=name.lower()
    desired=('/her2_test_data/' in low and (('/analyses/energy/' in low and name.endswith(('.log','.csv'))) or (any(t in name for t in ['div6_000024','ran4_000015']) and name.endswith(('.pdb','.anarci','.fasta'))) or ('swap_settings' in low) or name.endswith(('min.in','tleap_imp.in','parmed.in'))))
    if member.isfile() and desired and member.size<20_000_000:
     rel=Path(name)
     if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe archive member')
     f=out/rel;f.parent.mkdir(parents=True,exist_ok=True);data=tar.extractfile(member).read();f.write_bytes(data)
     saved.append({'path':str(f.relative_to(a.source_run)),'member':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});print('SAVED',name,len(data),flush=True)
    if len(names)<=8:print('MEMBER',name,member.size,flush=True)
 except Exception as e:status=type(e).__name__+': '+str(e);print('SCAN_STOP',status,flush=True)
 record={'url':u,'status':status,'compressed_bytes_read':reader.bytes if reader else 0,'elapsed_seconds':time.monotonic()-start,'members_seen':len(names),'saved':saved,'members':names}
 (out/'archive_scan.json').write_text(json.dumps(record,indent=2)+'\n')
 print('SCAN_RESULT',json.dumps({k:v for k,v in record.items() if k not in ['members','saved']}),flush=True)
if __name__=='__main__':main()
