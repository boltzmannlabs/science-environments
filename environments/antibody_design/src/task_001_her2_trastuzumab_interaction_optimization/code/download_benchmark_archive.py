#!/usr/bin/env python3
"""Retrieve a public benchmark archive using verified byte ranges; resume safely."""
import argparse,concurrent.futures,hashlib,json,os,time,urllib.request
from pathlib import Path
URL='https://zenodo.org/api/records/15803983/files/ab_seldon_trastuzumab_optimization_tests_v2.tar.gz/content';SIZE=4098846633

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--part-mib',type=int,default=64);a=p.parse_args()
 parts=a.output.with_suffix(a.output.suffix+'.parts');parts.mkdir(parents=True,exist_ok=True);chunk=a.part_mib*1024**2;t=time.monotonic()
 def fetch(i):
  start=i*chunk;end=min(SIZE-1,start+chunk-1);file=parts/f'{i:04d}.part';expected=end-start+1
  if file.exists() and file.stat().st_size==expected:return i,expected,'retained'
  for attempt in range(3):
   try:
    req=urllib.request.Request(URL+f'?audit_range={start}',headers={'User-Agent':'ScientificBenchmarkAudit/1.0','Range':f'bytes={start}-{end}'})
    with urllib.request.urlopen(req,timeout=100) as r:
     if r.status!=206 or not str(r.headers.get('Content-Range','')).startswith(f'bytes {start}-{end}/'):raise RuntimeError('server did not honor requested range')
     tmp=file.with_suffix('.partial')
     with tmp.open('wb') as w:
      while True:
       b=r.read(1024**2)
       if not b:break
       w.write(b)
    if tmp.stat().st_size!=expected:raise RuntimeError('range length mismatch')
    tmp.rename(file);return i,expected,'downloaded'
   except Exception:
    if attempt==2:raise
    time.sleep(2**attempt)
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
  for i,size,status in pool.map(fetch,range((SIZE+chunk-1)//chunk)):print('RANGE',i,size,status,flush=True)
 h=hashlib.md5();sha=hashlib.sha256()
 with a.output.open('wb') as w:
  for f in sorted(parts.glob('*.part')):
   with f.open('rb') as r:
    while True:
     b=r.read(1024**2)
     if not b:break
     w.write(b);h.update(b);sha.update(b)
 print(json.dumps({'path':str(a.output),'bytes':a.output.stat().st_size,'md5':h.hexdigest(),'sha256':sha.hexdigest(),'elapsed_seconds':time.monotonic()-t}),flush=True)
 # Range files are byte-identical staging copies of the complete, hashed archive.
 for f in parts.glob('*.part'):f.unlink()
 parts.rmdir()
if __name__=='__main__':main()
