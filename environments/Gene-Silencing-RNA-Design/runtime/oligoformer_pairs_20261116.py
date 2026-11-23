"""Fresh native OligoFormer paired inference; isolate writes and preserve author sources.
Run with the already installed OligoFormer interpreter. No training, installs or downloads.
Native CLI pos is an input ordinal for -i2, not a transcript coordinate: map by identity.
"""
import argparse,pathlib,json,hashlib,os,subprocess,shutil,sys,time,math
ASSETS=pathlib.Path('/home/boltzmann13/.sci/profiles/imran/workspace')
SOURCE=ASSETS/'tools/OligoFormer';RNAFM=ASSETS/'tools/RNA-FM';INSTALL=ASSETS/'oligoformer-integration'
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def rc(s):return s.translate(str.maketrans('AUCG','UAGC'))[::-1]
def execute(input_path,out):
 if out.exists():raise RuntimeError('Refuse to overwrite an existing native inference job')
 data=json.loads(input_path.read_text());tx=data['transcript'];pairs=data['pairs'];assert set(tx)<=set('AUCG') and pairs
 for r in pairs:
  assert len(r['guide'])==19 and set(r['guide'])<=set('AUCG')
  assert tx.find(rc(r['guide']))==r['site_index_0based'],'Native first-match coordinate differs from source audit'
 assert len({r['row_id'] for r in pairs})==len(pairs)
 out.mkdir(parents=True);cwd=out/'runtime';cwd.mkdir();(cwd/'scripts').symlink_to(SOURCE/'scripts',target_is_directory=True);(cwd/'model').symlink_to(SOURCE/'model',target_is_directory=True);(cwd/'data').mkdir();(cwd/'result').mkdir()
 stage=cwd/'RNA-FM';stage.mkdir();shutil.copytree(RNAFM/'redevelop',stage/'redevelop',ignore=shutil.ignore_patterns('__pycache__','*.pyc'));(stage/'fm').symlink_to(RNAFM/'fm',target_is_directory=True)
 # Private cache shares immutable checkpoints via symlinks; never writes the source profile.
 cache=out/'torch-cache/hub/checkpoints';cache.mkdir(parents=True)
 for checkpoint in (INSTALL/'torch-cache/hub/checkpoints').iterdir():
  if checkpoint.is_file():(cache/checkpoint.name).symlink_to(checkpoint)
 (cwd/'target.fa').write_text('>target\n'+tx+'\n');(cwd/'guides.fa').write_text(''.join('>RNA'+str(i)+'\n'+r['guide']+'\n' for i,r in enumerate(pairs)))
 import torch
 t=time.monotonic();tracked=[SOURCE/'model/best_model.pth',SOURCE/'scripts/infer.py',INSTALL/'torch-cache/hub/checkpoints/RNA-FM_pretrained.pth'];before={str(p):sha(p) for p in tracked}
 env=os.environ.copy()
 for k in ['PYTHONPATH','PYTHONHOME','VIRTUAL_ENV']:env.pop(k,None)
 env.update(PATH=str(pathlib.Path(sys.executable).parent)+os.pathsep+env.get('PATH',''),PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',TORCH_HOME=str(out/'torch-cache'),MPLCONFIGDIR=str(out/'mpl-cache'),OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',CUDA_VISIBLE_DEVICES='0',HF_HUB_OFFLINE='1')
 cmd=[sys.executable,'-B',str(INSTALL/'launch_upstream.py'),'--infer','1','-i1',str(cwd/'target.fa'),'-i2',str(cwd/'guides.fa'),'--output_dir',str(cwd/'result')+'/']
 with (out/'execution.log').open('w') as log:p=subprocess.run(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
 metadata={'command':cmd,'returncode':p.returncode,'elapsed_seconds':time.monotonic()-t,'input_sha256':sha(input_path),'input_accession':data['accession'],'pairs_requested':len(pairs),'labels_supplied_to_model':False,'python':sys.executable,'torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'rng_seed':42,'native_model_mode':'Author inference CLI does not call eval(); training-mode/dropout behavior retained. Subset/order can affect scores even with a fixed seed. Not a claimed model improvement.','score_units':'native_class1_times_1.341_not_calibrated_percent','author_files':before,'status':'FAILED' if p.returncode else 'VALIDATING'}
 (out/'execution.json').write_text(json.dumps(metadata,indent=2)+'\n')
 if p.returncode:raise RuntimeError('Native paired inference failed; see '+str(out/'execution.log'))
 import pandas as pd
 raw=cwd/'result/target.txt';df=pd.read_csv(raw,sep='\t');assert len(df)==len(pairs)
 result=[]
 for i,(r,n) in enumerate(zip(pairs,df.to_dict('records'))):
  assert n['siRNA']==r['guide'] and n['sense']==rc(r['guide']) and int(n['pos'])==i+1
  v=float(n['efficacy']);assert math.isfinite(v)
  result.append({'row_id':r['row_id'],'accession':data['accession'],'guide':r['guide'],'site_index_0based':r['site_index_0based'],'score':v,'native_input_ordinal':i+1,'execution':'FRESH_NATIVE_OLIGOFORMER_PAIRED_INFERENCE'})
 shutil.copyfile(raw,out/'native_predictions.tsv');(out/'predictions.json').write_text(json.dumps(result,indent=2)+'\n')
 assert all(sha(p)==v for p,v in before.items())
 metadata.update(status='COMPLETED',pairs_returned=len(result),original_assets_unchanged=True,source_commit=subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),rnafm_commit=subprocess.check_output(['git','-C',str(RNAFM),'rev-parse','HEAD'],text=True).strip(),output_sha256=sha(out/'predictions.json'))
 # Remove only this job's disposable execution tree/cache links, not original sources or final artifacts.
 assert cwd.parent==out and cwd.name=='runtime';shutil.rmtree(cwd);shutil.rmtree(out/'torch-cache');metadata['disposable_execution_tree_removed']=True
 (out/'execution.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=pathlib.Path);p.add_argument('--out',required=True,type=pathlib.Path);a=p.parse_args();execute(a.input,a.out)
