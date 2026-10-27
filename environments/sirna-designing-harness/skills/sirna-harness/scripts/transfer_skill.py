#!/usr/bin/env python3
"""Check/copy this instruction-only skill to an explicit destination. Never install models."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,sys,tempfile
from pathlib import Path,PurePosixPath
MANIFEST='assets/portable-manifest.json'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  while True:
   b=f.read(1048576)
   if not b:break
   h.update(b)
 return h.hexdigest()
def inventory(source):
 source=Path(source)
 if source.is_symlink():raise ValueError('Source symlink refused')
 result=[]
 for p in sorted(source.rglob('*')):
  if p.is_symlink():raise ValueError('Symlinks refused: '+str(p))
  if not p.is_file():continue
  rel=p.relative_to(source).as_posix()
  if '__pycache__' in p.parts:raise ValueError('Remove bytecode caches before packaging')
  if rel==MANIFEST:continue
  if p.name.startswith('.env') or p.suffix in {'.pth','.pt','.h5','.pkl','.fa','.fasta','.xlsx','.zip'}:raise ValueError('Credentials/model/dataset/archive payload not allowed: '+rel)
  if rel!='SKILL.md' and PurePosixPath(rel).parts[0] not in {'references','scripts','templates','assets'}:raise ValueError('Unexpected payload path: '+rel)
  result.append({'relative_path':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
 return result
def check(source):
 source=Path(source);manifest_path=source/MANIFEST
 if not (source/'SKILL.md').is_file() or not manifest_path.is_file():raise ValueError('SKILL.md and portable manifest required')
 data=json.loads(manifest_path.read_text(encoding='utf-8'))
 if data.get('skill_name')!='sirna-harness' or data.get('version')!='2.0.0':raise ValueError('Package identity/version mismatch')
 for record in data['files']:
  rel=PurePosixPath(record['relative_path'])
  if rel.is_absolute() or '..' in rel.parts or '\\' in str(rel):raise ValueError('Unsafe manifest path')
 if inventory(source)!=data['files']:raise ValueError('Package files/hash/size differ from manifest')
 text=(source/'SKILL.md').read_text(encoding='utf-8')
 if not text.startswith('---\n') or '\nname: sirna-harness\n' not in text or '\nversion: 2.0.0\n' not in text:raise ValueError('Skill frontmatter identity/version missing')
 return {'status':'PASSED','skill':'sirna-harness','version':data['version'],'files_verified':len(data['files']),'manifest_sha256':sha(manifest_path),'meaning':'Package integrity only; no scientific backend validated'}
def install(source,destination,apply=False):
 source=Path(source);result=check(source);destination=Path(destination).expanduser()
 if not destination.is_absolute():raise ValueError('Explicit absolute active-profile destination required')
 if destination.exists() or destination.is_symlink():raise FileExistsError('Destination already exists; no overwrite performed')
 if source.resolve()==destination.resolve() or source.resolve() in destination.resolve().parents:raise ValueError('Destination cannot be inside source package')
 for parent in destination.parents:
  if parent.is_symlink():raise ValueError('Destination ancestor symlink refused')
 result.update(destination=str(destination),mode='apply' if apply else 'dry_run',scientific_assets_installed=False)
 if not apply:return result
 destination.parent.mkdir(parents=True,exist_ok=True);created=False
 try:
  with tempfile.TemporaryDirectory(prefix='.sirna-stage-',dir=destination.parent) as temp:
   staging=Path(temp)/'sirna-harness';shutil.copytree(source,staging);check(staging)
   destination.mkdir(exist_ok=False);created=True
   shutil.copytree(staging,destination,dirs_exist_ok=True);check(destination)
  result['installed']=True;return result
 except Exception:
  if created:shutil.rmtree(destination)
  raise

def main():
 parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
 for action in ['check','install']:
  p=sub.add_parser(action);p.add_argument('--source',required=True)
  if action=='install':p.add_argument('--destination',required=True);p.add_argument('--apply',action='store_true')
 args=parser.parse_args()
 try:result=check(args.source) if args.action=='check' else install(args.source,args.destination,args.apply);print(json.dumps(result,indent=2));return 0
 except (ValueError,OSError,KeyError,TypeError) as e:print(json.dumps({'status':'FAILED','error_type':type(e).__name__,'error':str(e)},indent=2));return 2
if __name__=='__main__':raise SystemExit(main())
