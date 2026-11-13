#!/usr/bin/env python3
"""Extract attributable HER2 logs and controls; never execute archive code."""
import argparse,hashlib,json,tarfile,time
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--source-run',type=Path,required=True);a=p.parse_args();out=a.source_run/'inputs'/'released_archive';out.mkdir(parents=True,exist_ok=True)
 archive=a.source_run/'inputs'/'ab_seldon_trastuzumab_optimization_tests_v2.tar.gz'; saved=[];n=0;t=time.monotonic()
 with tarfile.open(archive,mode='r|gz') as tar:
  for m in tar:
   n+=1;name=m.name;low=name.lower();rel=Path(name)
   if not m.isfile():continue
   her2='/her2_test_data/' in low
   wanted=(her2 and (('/analyses/' in low and name.endswith(('.log','.csv','.py','.txt'))) or ('final_' in low and any(x in low for x in ['div6_000024','ran4_000015']) and name.endswith(('.pdb','.anarci','.fasta'))) or name.endswith(('min.in','tleap_imp.in','parmed.in','swap_settings.cfg'))))
   # The archive's paper-v6.2 code is authoritative over a later GitHub revision.
   wanted |= '/ab-seldon-paper-v6.2/' in name and name.endswith(('.py','.cfg','.sh','.in','.fasta','.pdb'))
   if wanted and m.size<25_000_000:
    if rel.is_absolute() or '..' in rel.parts:raise ValueError('unsafe member')
    f=out/rel;f.parent.mkdir(parents=True,exist_ok=True);data=tar.extractfile(m).read();f.write_bytes(data)
    saved.append({'member':name,'path':str(f.relative_to(a.source_run)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 (out/'extraction_manifest.json').write_text(json.dumps({'archive':str(archive),'members_seen':n,'elapsed_seconds':time.monotonic()-t,'saved':saved},indent=2)+'\n')
 print('MEMBERS',n,'SAVED',len(saved),'SECONDS',time.monotonic()-t)
 for x in saved:
  if '/her2_test_data/' in x['member']:print(x['member'],x['bytes'])
if __name__=='__main__':main()
