#!/usr/bin/env python3
"""Run the benchmark's ImmuneBuilder complex-refinement stage on CPU (not Amber)."""
import argparse,json,os,time,traceback
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OPENMM_CPU_THREADS']='2'
from ImmuneBuilder.refine import refine

def main():
 p=argparse.ArgumentParser();p.add_argument('--result-run',type=Path,required=True);a=p.parse_args();rows=[]
 for f in sorted((a.result_run/'structures').glob('*_template_pose_complex.pdb')):
  cid=f.name.removesuffix('_template_pose_complex.pdb');target=f.with_name(f'{cid}_openmm_refined_complex.pdb');start=time.monotonic()
  print('START',cid,flush=True)
  try:
   success=refine(str(f),str(target),n_threads=2)
   rows.append({'candidate_id':cid,'success':bool(success),'output':str(target.relative_to(a.result_run)) if target.exists() else None,'seconds':time.monotonic()-start,'method':'ImmuneBuilder.refine OpenMM ff14SB; NOT Amber ff14SBonlysc/HMR/igb8 minimization'})
  except Exception as e:rows.append({'candidate_id':cid,'success':False,'seconds':time.monotonic()-start,'error':str(e),'traceback':traceback.format_exc()})
  print('FINISH',cid,rows[-1]['success'],rows[-1]['seconds'],flush=True)
 (a.result_run/'evidence/raw/complex_refinement.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
