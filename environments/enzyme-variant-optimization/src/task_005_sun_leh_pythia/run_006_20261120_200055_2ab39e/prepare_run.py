import csv, hashlib, json, os, pathlib, shutil, sys, time
from Bio.PDB import PDBParser, Polypeptide

ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results/local/task_005_sun_leh_pythia/v2/assisted/fresh-20261120'
SRC=pathlib.Path('retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433')
OUT.mkdir(parents=True, exist_ok=False)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def fasta(p): return ''.join(x.strip() for x in p.read_text().splitlines() if not x.startswith('>'))
pdb=ROOT/'inputs/1NWW.pdb'; raw=pdb.read_text().splitlines(keepends=True)
assert sha(pdb)=='c3c3b27a3da81fff3ad1f8961f48b404e1a95bbab27387a13a4c1127c146fcbe'
seqs={x:[] for x in 'AB'}
for line in raw:
    if line.startswith('SEQRES') and line[11] in seqs: seqs[line[11]]+=line[19:70].split()
seqs={c:''.join(Polypeptide.protein_letters_3to1[x] for x in s) for c,s in seqs.items()}
rcsb=fasta(ROOT/'inputs/rcsb_1nww.fasta'); uni=fasta(ROOT/'inputs/uniprot_Q9ZAG3.fasta')
assert seqs['A']==seqs['B']==rcsb==uni and len(rcsb)==149
(OUT/'parent.fasta').write_text('>1NWW_SEQRES_Q9ZAG3_149_parent\n'+rcsb+'\n')
shutil.copyfile(pdb,OUT/'original_1NWW.pdb')
with (OUT/'monomer_A.pdb').open('w') as f:
    for line in raw:
        if line.startswith(('ATOM  ','ANISOU','HETATM','TER   ')) and line[21:22]=='A': f.write(line)
    f.write('END\n')
model=PDBParser(QUIET=True).get_structure('1nww',str(pdb))[0]
rows=[]
for context,chains in [('monomer_A',['A']),('dimer_AB',['A','B'])]:
    index=0
    for c in chains:
        residues=[r for r in model[c] if r.id[0]==' ']
        by_num={}
        for r in residues:
            if r.id[2]!=' ': raise ValueError('Insertion code requires explicit alignment: '+str(r.id))
            if r.id[1] in by_num: raise ValueError('Duplicate residue number')
            by_num[r.id[1]]=r
        for pos,wt in enumerate(rcsb,1):
            r=by_num.get(pos); atoms='' if r is None else ','.join(sorted(a.id for a in r)); ident='' if r is None else Polypeptide.protein_letters_3to1.get(r.resname,'?')
            if r is not None and ident!=wt: raise ValueError((c,pos,wt,ident))
            eligible=r is not None and all(a in r for a in ('N','CA','C','O'))
            if eligible: index+=1
            rows.append(dict(context=context,chain=c,parent_position=pos,pdb_resseq=pos,insertion_code='',wt=wt,coordinate_present=bool(r),eligible=eligible,retained_index_1based=index if eligible else '',reason='' if eligible else ('no_coordinate' if r is None else 'incomplete_backbone'),atoms=atoms))
with (OUT/'residue_map.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
with (OUT/'missing_positions.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(r for r in rows if not r['eligible'])
counts={f'{co}:{ch}':sum(r['eligible'] for r in rows if r['context']==co and r['chain']==ch) for co,ch in [('monomer_A','A'),('dimer_AB','A'),('dimer_AB','B')]}
sourcefiles=['pythia/masked_ddg_scan.py','pythia/predict_ddg.py','pythia/pdb_utils.py','pythia/model.py','pyproject.toml','requirements.txt','LICENSE']
checks=['pythia/pythia-c.pt','pythia/pythia-p.pt']
manifest={'input_pdb_sha256':sha(pdb),'monomer_A_pdb_sha256':sha(OUT/'monomer_A.pdb'),'parent_sequence_sha256':hashlib.sha256(rcsb.encode()).hexdigest(),'parent_fasta_sha256':sha(OUT/'parent.fasta'),'rcsb_fasta_sha256':sha(ROOT/'inputs/rcsb_1nww.fasta'),'uniprot_fasta_sha256':sha(ROOT/'inputs/uniprot_Q9ZAG3.fasta'),'all_sequence_sources_equal':True,'sequence_length':len(rcsb),'source_revision_claim':'e1943402092295ae96cde0c93073ddc933ffc433','source_revision_git_independently_verified':False,'source_files_sha256':{x:sha(SRC/x) for x in sourcefiles},'checkpoints_sha256':{x:sha(SRC/x) for x in checks},'residue_map_sha256':sha(OUT/'residue_map.csv'),'eligible':counts,'unscored':{f'{co}:{ch}':[r['parent_position'] for r in rows if r['context']==co and r['chain']==ch and not r['eligible']] for co,ch in [('monomer_A','A'),('dimer_AB','A'),('dimer_AB','B')]},'expected_nonidentity':{k:v*19 for k,v in counts.items()},'dbref_anomaly':'PDB DBREF Q9ZAG3 0..148 vs current UniProt and SEQRES both 149 residues, exact positionwise sequence match 1..149; no 0-based DBREF offset used.','assembly':'PDB REMARK 350 identity operator applied to A,B; biological dimer','sources':['https://www.rcsb.org/structure/1NWW','https://www.rcsb.org/fasta/entry/1NWW/display','https://rest.uniprot.org/uniprotkb/Q9ZAG3.fasta','https://www.rcsb.org/annotations/1NWW','https://doi.org/10.1093/emboj/cdg275']}
(OUT/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
plan={'status':'frozen_before_inference','created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'task':'task_005_sun_leh_pythia','approach':'assisted','sci_model':'codex','sci_provider':'boltzmann_models','scientific_model':'Pythia AMPNN C and P supplied checkpoints','input_manifest_sha256':sha(OUT/'INPUT_MANIFEST.json'),'method':'upstream masked_ddg_scan.py read_pdb_to_protbb and get_neighbor; inspect native source for implementation','feature':{'neighbor_count':32,'noise':0.0,'mask_center':True,'upstream_cb_imputation':True,'protein_only':True,'native_eval_mode':True},'contexts':{'primary':'monomer_A','secondary':'dimer_AB separate chain A and B, not simultaneous homodimer mutation'},'scoring':{'component':'-log(p_mut/p_wt) = logit_wt-logit_mut','primary':'C+P','sensitivity':'(C+P)/2','units':'unitless','lower_better':True},'selection':{'nonidentity_only':True,'best_per_position':'minimum sum, alphabetical mutant tie','primary_cutoff':'strict sum < -2','sensitivity_cutoff':'strict mean < -2; separately labeled','functional_filter':'none; annotate Y53 N55 R99 D101 D132'},'retention':'logits, probabilities, model components, identity controls, full rankings and candidate sequences','historical_uncertainties':['paper application of aggregation cutoff and structure context unresolved','source revision is supplied directory claim without git history','checkpoints hashed but publisher identity not independently attested'],'reference_boundary':'no benchmark outcomes or other-arm results before sealing','budget':{'scientific_remote_submissions_max':0,'local_scans':'all eligible positions for both contexts, both models; no separate candidate cap truncating required raw library','cpu_threads':4,'device':'cpu','wall_time':'no user-specified numerical ceiling; foreground process execution','financial':'no user-specified numerical ceiling; no paid remote scientific submissions','model_tokens':'no user-specified numerical ceiling; specialist usage captured where available','intervention':'do not change method, cutoff, inputs, source or protected output constraints after selection'},'native_pythia_source_difference':'predict_ddg.py independently unmasks substitutions and uses another sign; not used','pdb_xray_b_factors':'not pLDDT','allowed_scope':'task-scoped computational reproduction only; no MLDE, docking, MolProbity, or experiments','specialist_reviews':['sa-0-caf98776','sa-0-74822eb1'],'completion_vs_qualification':'scores are not biological qualification; catalytic concerns not excluded'}
(OUT/'RUN_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
(OUT/'jobs.json').write_text(json.dumps({'remote_submissions':[],'local_processes':[],'specialist_receipts':['sa-0-caf98776','sa-0-74822eb1'],'assignment_id':'ae68253530b04acc8d3deeb60c71c6bb'},indent=2)+'\n')
(OUT/'usage.json').write_text(json.dumps({'scientific_remote_attempts':0,'scientific_remote_cost':'not incurred; no submissions','specialist_model_usage':{'sa-0-caf98776':{'input_tokens':45678,'output_tokens':1322,'cost_status':'unknown'},'sa-0-74822eb1':{'input_tokens':59738,'output_tokens':1470,'cost_status':'unknown'}},'parent_model_usage':'not provided by runtime','local_runtime':'not yet measured'},indent=2)+'\n')
(OUT/'errors.md').write_text('# Errors and recovery\n\nNo scientific inference attempts yet. Original source snapshot has no Git metadata; revision is a supplied claim, not independently verified.\n')
(OUT/'decisions.md').write_text('# Decisions\n\nInitial method reviews sa-0-caf98776 and sa-0-74822eb1 support source-faithful masked scan. Pythia is absent from current Boltzmann contract; user authorizes source-pinned local implementation. No target-study result tables read.\n')
print(json.dumps({'output':str(OUT),'counts':counts,'unscored':manifest['unscored'],'expected_nonidentity':manifest['expected_nonidentity'],'parent_sequence_sha256':manifest['parent_sequence_sha256']},indent=2))
