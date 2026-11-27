import csv, hashlib, json, os, sys, shutil, datetime
from pathlib import Path
from Bio.PDB import PDBParser
from Bio.PDB.Polypeptide import protein_letters_3to1, three_to_index, index_to_one
R=Path(__file__).resolve().parent
P=R.parent/'inputs/1NWW.pdb'
S=Path('retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433')
sys.path.insert(0,str(S))
import torch, numpy as np, Bio, pytorch_lightning, torchmetrics
from pythia.pdb_utils import read_pdb_to_protbb, get_neighbor
from pythia.masked_ddg_scan import get_torch_model
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
raw=P.read_text(); seqres={c:[] for c in 'AB'}
for l in raw.splitlines():
    if l.startswith('SEQRES') and l[11] in seqres: seqres[l[11]] += l[19:70].split()
seqs={c:''.join(protein_letters_3to1[x] for x in seqres[c]) for c in seqres}
uni=''.join((R/'evidence/Q9ZAG3.fasta').read_text().splitlines()[1:]); assert seqs['A']==seqs['B']==uni and len(uni)==149
(R/'parent.fasta').write_text('>Q9ZAG3_1NWW_native_parent\n'+uni+'\n')
mono=''.join(l+'\n' for l in raw.splitlines() if (l.startswith(('ATOM  ','HETATM','ANISOU','TER   ')) and l[21:22]=='A'))+'END\n'
(R/'contexts/monomer_A.pdb').write_text(mono); shutil.copyfile(P,R/'contexts/dimer_AB.pdb')
structure=PDBParser(QUIET=True).get_structure('x',str(P))[0]
rows=[]
for c in 'AB':
    chain=structure[c]; observed={}
    for res in chain:
        if res.id[0]!=' ': continue
        assert res.id[2]==' ', (c,res.id)
        n=res.id[1]; assert 1<=n<=len(uni) and n not in observed
        aa=protein_letters_3to1[res.resname]; assert aa==uni[n-1], (c,n,aa,uni[n-1])
        atoms=set(a.id for a in res); good={'N','CA','C','O'}.issubset(atoms)
        observed[n]=(aa,good,','.join(sorted({'N','CA','C','O'}-atoms)))
    for n,aa in enumerate(uni,1):
        rec=observed.get(n); rows.append({'chain':c,'native_position':n,'pdb_resseq':n,'insertion_code':'','wild_type':aa,'coordinate_present':bool(rec),'supported':bool(rec and rec[1]),'reason':('missing_residue' if rec is None else ('missing_backbone:'+rec[2] if not rec[1] else ''))})
with (R/'residue_map.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
with (R/'missing_positions.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows([x for x in rows if not x['supported']])
contexts={}
for label,chains in [('monomer_A','A'),('dimer_AB','AB')]:
    path=R/'contexts'/f'{label}.pdb'; prot=read_pdb_to_protbb(str(path)); node,edge,tok=get_neighbor(prot,neighbor=32,noise_level=0.0,train=False)
    expected=[x for x in rows if x['chain'] in chains and x['supported']]
    assert len(expected)==len(tok)
    for i,x in enumerate(expected):
        assert int(prot.resseq[i].item())==x['pdb_resseq'] and index_to_one(int(tok[i]))==x['wild_type']
        assert int(prot.chain_num[i])==chains.index(x['chain'])
    contexts[label]={'file':str(path.relative_to(R)),'sha256':sha(path),'n':len(expected),'counts':{c:sum(x['chain']==c for x in expected) for c in chains},'node_shape':list(node.shape),'edge_shape':list(edge.shape)}
for m in 'cp':
    model=get_torch_model(str(S/f'pythia/pythia-{m}.pt'),device='cpu'); assert not model.training
source_files=['pythia/masked_ddg_scan.py','pythia/pdb_utils.py','pythia/model.py','requirements.txt','pyproject.toml','pythia/pythia-c.pt','pythia/pythia-p.pt']
manifest={'pdb_sha256':sha(P),'parent_fasta_sha256':sha(R/'parent.fasta'),'uniprot_fasta_sha256':sha(R/'evidence/Q9ZAG3.fasta'),'residue_map_sha256':sha(R/'residue_map.csv'),'missing_sha256':sha(R/'missing_positions.csv'),'source_revision_claim':'e1943402092295ae96cde0c93073ddc933ffc433 (directory name; no .git metadata, not independently verified)','source_files_sha256':{p:sha(S/p) for p in source_files},'contexts':contexts,'source_urls':['https://www.rcsb.org/structure/1NWW','https://rest.uniprot.org/uniprotkb/Q9ZAG3.fasta','https://www.ebi.ac.uk/thornton-srv/m-csa/entry/644'],'identity':'SEQRES A and B equal UniProt Q9ZAG3 exactly; all observed standard residues match same 1-based position. PDB DBREF says UniProt 0..148 but is inconsistent with exact sequence and M-CSA annotation; index by sequence alignment and PDB numbering.'}
(R/'INPUT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
plan={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assignment_id':'f5113ddd8c0f4be2aa11b9db987a22dc','mode':'fresh assisted, no other-arm or paper outcome access before seal','llm':{'provider':'boltzmann_models','model':'codex','specialists':['enzyme-method','enzyme-recovery','enzyme-evaluator']},'scientific_model':'Pythia C and P source/checkpoints in INPUT_MANIFEST.json','parent':'Q9ZAG3 exact 149-residue construct, see parent.fasta','contexts':contexts,'features':'original read_pdb_to_protbb and get_neighbor(neighbor=32,noise_level=0,train=False), 1st model, no solvent/heterogens as features, missing pseudo-Cbeta per source; no residue imputation','settings':{'device':'cpu','torch_threads':4,'precision':'float32','eval':True,'masked':True,'checkpoints_weights_only':True},'score':'-ln(p(mut)/p(wt)); sum=C+P; mean=(C+P)/2; unitless; lower is favorable','selection':'monomer_A, best nonidentity per native position by ascending sum; lexicographic amino-acid tie; keep if sum strictly < -2; global rank sum then native position then mutant; no retrospective exclusion; separate mean threshold -2 sensitivity and dimer chains separately','functional_concerns':{'positions':[53,55,99,101,132],'source':'https://www.ebi.ac.uk/thornton-srv/m-csa/entry/644','effect':'annotate only; no filtering; qualification unknown'},'coverage':'all 20 canonical residue tokens including identity; nonidentity 19 per supported residue; missing positions retained but unscored','budget_policy':{'scientific_remote_attempts':0,'compute':'local CPU only; no additional paid service','threads':4,'walltime':'bounded to available interactive session; no arbitrary extension','tokens':'actual model usage where reported; otherwise unknown','cost':'actual reported or unknown'},'historical_uncertainties':['actual published monomer/dimer choice and sum-vs-mean mapping not independently established','source revision labeled by directory rather than git metadata','torch 2.4.1, Bio 1.83 and lightning 2.4.0 differ from historical requirements; compatibility checked against current source, not equivalence to historical runtime'], 'dependency_versions':{'python':sys.version,'torch':torch.__version__,'numpy':np.__version__,'biopython':Bio.__version__,'pytorch_lightning':pytorch_lightning.__version__,'torchmetrics':torchmetrics.__version__},'submission':'local foreground inference, no remote jobs','qualification':'scores do not establish activity or stability'}
(R/'RUN_PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
print(json.dumps({'contexts':contexts,'parent_length':len(uni),'missing':[(x['chain'],x['native_position']) for x in rows if not x['supported']],'checkpoint_loads':'both success'},indent=2))
