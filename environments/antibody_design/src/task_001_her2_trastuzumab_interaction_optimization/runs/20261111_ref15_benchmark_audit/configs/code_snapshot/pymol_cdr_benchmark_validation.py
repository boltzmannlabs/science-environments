#!/usr/bin/env python3
"""Benchmark-like PyMOL whole-Fv alignment + Martin CDR CA current RMSD.
Complexes produced here impose the released HER2 pose; they are NOT docked or Amber-minimized.
"""
import argparse,csv,json,math
from pathlib import Path
import pymol
from pymol import cmd

def main():
 p=argparse.ArgumentParser();p.add_argument('--result-run',type=Path,required=True);p.add_argument('--benchmark-reference',type=Path,required=True);a=p.parse_args();raw=a.result_run/'evidence/raw';raw.mkdir(parents=True,exist_ok=True)
 # The released INPUT PDB has sequential H numbering 108..227, not Martin numbers.
 # Map via the native REF_1N8Z ANARCI record before selecting benchmark CDRs.
 from Bio.PDB import PDBParser,PDBIO
 from Bio.SeqUtils import seq1
 reference=PDBParser(QUIET=True).get_structure('native',a.benchmark_reference)
 numbered=json.loads((raw/'abodybuilder2/REF_1N8Z.json').read_text())['numbered_sequences'];mapping=[]
 for chain in ['H','L']:
  ch=reference[0][chain];rs=[r for r in ch if r.id[0]==' ']
  assert len(rs)==len(numbered[chain])
  saved=[r.copy() for r in rs]
  for r in list(ch):ch.detach_child(r.id)
  for r,n in zip(saved,numbered[chain]):
   assert seq1(r.resname)==n['amino_acid']
   mapping.append({'chain':chain,'source_residue':str(r.id),'martin_number':n['residue_number'],'insertion_code':n['insertion_code']})
   r.id=(' ',n['residue_number'],n['insertion_code'] or ' ');ch.add(r)
 refdir=a.result_run/'evidence/reference';refdir.mkdir(parents=True,exist_ok=True);prepared=refdir/'benchmark_reference_martin.pdb'
 writer=PDBIO();writer.set_structure(reference);writer.save(str(prepared))
 mapdir=a.result_run/'evidence/mappings';mapdir.mkdir(parents=True,exist_ok=True);(mapdir/'benchmark_martin_mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
 ranges={'H1':('H',26,32),'H2':('H',52,56),'H3':('H',95,102),'L1':('L',24,34),'L2':('L',50,56),'L3':('L',89,97)}
 rows=[]
 for f in sorted((a.result_run/'structures').glob('*_abodybuilder2_vhvl.pdb')):
  cid=f.name.removesuffix('_abodybuilder2_vhvl.pdb');cmd.reinitialize();cmd.load(str(prepared),'ref');cmd.load(str(f),'ab')
  alignment=cmd.align('ab and chain H+L','ref and chain H+L',quiet=1)
  record={'candidate_id':cid,'whole_fv_align_rmsd_A':alignment[0],'aligned_atoms':alignment[1]}
  for region,(chain,start,end) in ranges.items():
   mobile=f'ab and chain {chain} and resi {start}-{end} and name CA';target=f'ref and chain {chain} and resi {start}-{end} and name CA'
   n=cmd.count_atoms(mobile);m=cmd.count_atoms(target)
   if n==0 or n!=m: raise ValueError(f'{cid} {region}: CA mapping mismatch ({n}, {m})')
   rms=cmd.rms_cur(mobile,target,matchmaker=4,quiet=1)
   if not math.isfinite(rms) or rms<0: raise ValueError('invalid RMSD')
   errors=[v.b for v in cmd.get_model(mobile).atom]
   record[region+'_rmsd_A']=float(rms) if rms is not None else None;record[region+'_n_ca']=n;record[region+'_reference_n_ca']=m
   record[region+'_ensemble_error_mean_A']=sum(errors)/len(errors) if errors else None
  cmd.create('complex','(ab and chain H+L) or (ref and chain C)')
  target=a.result_run/'structures'/f'{cid}_template_pose_complex.pdb';cmd.save(str(target),'complex');record['template_complex_path']=str(target.relative_to(a.result_run));rows.append(record);print(json.dumps(record),flush=True)
 (raw/'pymol_cdr_validation.json').write_text(json.dumps({'pymol_version':cmd.get_version(),'alignment':'cmd.align whole Fv all atoms with default outlier rejection; rms_cur loop CA matchmaker=4','reference':str(a.benchmark_reference),'records':rows},indent=2)+'\n')
 fields=['candidate_id','whole_fv_align_rmsd_A']+[key for region in ranges for key in [region+'_rmsd_A',region+'_ensemble_error_mean_A']]
 with (a.result_run/'cdr_conformation.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()
