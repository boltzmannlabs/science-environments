#!/usr/bin/env python3
"""Sequential CPU ABodyBuilder2 validation, using the benchmark's Martin scheme."""
import argparse,csv,hashlib,json,os,time,traceback
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='';os.environ['OMP_NUM_THREADS']='4';os.environ['OPENMM_CPU_THREADS']='2'
import numpy as np,torch
from ImmuneBuilder import ABodyBuilder2
from Bio.PDB import PDBParser
from Bio.SeqUtils import seq1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--parent-run',type=Path,required=True);p.add_argument('--result-run',type=Path,required=True);a=p.parse_args();out=a.result_run/'structures';out.mkdir(parents=True,exist_ok=True);raw=a.result_run/'evidence/raw/abodybuilder2';raw.mkdir(parents=True,exist_ok=True)
 cands={r['candidate_id']:r for r in csv.DictReader(open(a.parent_run/'candidates.csv'))};ids=[r['candidate_id'] for r in csv.DictReader(open(a.parent_run/'shortlist.csv'))]
 ref=PDBParser(QUIET=True).get_structure('ref',a.parent_run/'evidence/reference/1N8Z_deposited_complex.pdb')[0]
 seq=lambda c,n:''.join(seq1(r.resname) for r in ref[c] if r.id[0]==' ')[:n]
 records=[('REF_1N8Z',{'H':seq('B',120),'L':seq('A',107)})]+[(cid,{'H':cands[cid]['heavy_chain'],'L':cands[cid]['light_chain']}) for cid in ids]
 torch.set_num_threads(4);np.random.seed(37);torch.manual_seed(37);predictor=ABodyBuilder2(numbering_scheme='martin')
 print('DEVICE',predictor.device,flush=True);assert predictor.device=='cpu'
 status=[]
 for cid,seqs in records:
  start=time.monotonic();target=out/f'{cid}_abodybuilder2_vhvl.pdb';f=raw/f'{cid}.json'
  if target.exists() and f.exists():status.append(json.loads(f.read_text()));print('RETAINED',cid,flush=True);continue
  print('START',cid,flush=True)
  try:
   ab=predictor.predict(seqs);ab.save(str(target),check_for_strained_bonds=False,n_threads=2)
   errors=ab.error_estimates.mean(0).sqrt().cpu().numpy();np.save(raw/f'{cid}_residue_error_A.npy',errors)
   numbered={c:[{'residue_number':int(num[0]),'insertion_code':str(num[1]).strip(),'amino_acid':aa} for num,aa in ab.numbered_sequences[c]] for c in ['H','L']}
   d={'candidate_id':cid,'status':'completed','seconds':time.monotonic()-start,'structure_path':str(target.relative_to(a.result_run)),'structure_sha256':sha(target),'residue_error_mean_A':float(errors.mean()),'residue_error_type':'ABodyBuilder2 ensemble positional dispersion, not pLDDT','numbered_sequences':numbered,'sequence_input':seqs,'selected_model_index':int(ab.ranking[0]),'device':predictor.device,'check_for_strained_bonds':False,'n_threads_refinement':2}
  except Exception as e:
   d={'candidate_id':cid,'status':'failed','seconds':time.monotonic()-start,'error':repr(e),'traceback':traceback.format_exc()}
  f.write_text(json.dumps(d,indent=2)+'\n');status.append(d);print('FINISH',cid,d['status'],d['seconds'],flush=True)
 (raw/'run_status.json').write_text(json.dumps(status,indent=2)+'\n')
 print('COUNTS',len(records),sum(x['status']=='completed' for x in status),flush=True)
if __name__=='__main__':main()
