#!/usr/bin/env python3
"""Retrieve pinned primary benchmark sources, never execute downloaded code."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
PARSER=argparse.ArgumentParser(); PARSER.add_argument('--source-run',type=Path,required=True)
def main():
 a=PARSER.parse_args(); out=a.source_run/'inputs'/'benchmark_sources';out.mkdir(parents=True,exist_ok=True)
 commit='9f5df3cadc96a64d78c977b426ae87c108bce4ba'; base=f'https://raw.githubusercontent.com/SFBBGroup/Ab-SELDON/{commit}/'
 paths=['README.md','paper-ready-to-run/README.md']
 p='paper-ready-to-run/ab-seldon-paper-v6.2/diversity/'
 paths += [p+x for x in ['memory_frame_v6.2.py','mutagenesis_v6.2.py','prepare_v2.7.py','swap_nai_bnk_v6.2.py','swap_nai_h3_v6.2.py','swap_nai_rep_v6.2.py','swap_settings.cfg','complex_1n8z-frk-reduced.pdb','1n8z-frk-reduced.fasta']]
 # Also retain minimization files at the same pinned revision.
 tree_url=f'https://api.github.com/repos/SFBBGroup/Ab-SELDON/git/trees/{commit}?recursive=1'
 req=lambda u: urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'ScientificBenchmarkAudit/1.0'}),timeout=60)
 tree=json.load(req(tree_url))
 paths += [x['path'] for x in tree['tree'] if x['path'].startswith(p) and any(y in x['path'].lower() for y in ['min_imp','leap','minim']) and x['type']=='blob']
 manifest=[]
 for path in dict.fromkeys(paths):
  target=out/path;target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():target.write_bytes(req(base+path).read())
  manifest.append({'path':str(target.relative_to(a.source_run)),'url':base+path,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size})
  print(path,target.stat().st_size,flush=True)
 meta_url='https://zenodo.org/api/records/15803983'; meta=req(meta_url).read(); target=out/'zenodo_record_15803983.json';target.write_bytes(meta)
 manifest.append({'path':str(target.relative_to(a.source_run)),'url':meta_url,'sha256':hashlib.sha256(meta).hexdigest(),'bytes':len(meta)})
 (out/'sources_manifest.json').write_text(json.dumps({'github_commit':commit,'sources':manifest},indent=2)+'\n')
 print('SOURCES',len(manifest))
if __name__=='__main__':main()
