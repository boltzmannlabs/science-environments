import json, os, subprocess
import numpy as np
from Bio.PDB import PDBParser, PDBIO
from Bio.PDB.Atom import Atom
base="/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results"
pdb_path=base+"/1N8Z_deposited_complex.pdb"
outdir=base+"/reconstructed"
os.makedirs(outdir, exist_ok=True)
three_to_one={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
one_to_three={v:k for k,v in three_to_one.items()}
# Ideal side-chain coords relative to CA (CB along +x), no H. Approximate.
IDEAL={
 'ALA':{'CB':(1.46,0,0)},
 'ARG':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD':(3.95,0.71,0),'NE':(4.90,1.85,0),'CZ':(6.32,1.64,0),'NH1':(6.92,0.51,0),'NH2':(7.07,2.56,0)},
 'ASN':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'OD1':(2.31,2.11,0),'ND2':(3.70,0.68,0)},
 'ASP':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'OD1':(2.31,2.11,0),'OD2':(3.70,0.68,0)},
 'CYS':{'CB':(1.46,0,0),'SG':(2.80,1.0,0)},
 'GLN':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD':(3.95,0.71,0),'OE1':(4.80,1.50,0),'NE2':(4.10,-0.40,0)},
 'GLU':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD':(3.95,0.71,0),'OE1':(4.80,1.50,0),'OE2':(4.10,-0.40,0)},
 'GLY':{},
 'HIS':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'ND1':(3.80,1.20,0),'CD2':(2.40,2.10,0),'CE1':(4.90,1.90,0),'NE2':(3.70,2.80,0)},
 'ILE':{'CB':(1.46,0,0),'CG1':(2.52,-1.0,0),'CG2':(2.52,1.0,0),'CD1':(3.95,-1.29,0)},
 'LEU':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD1':(3.95,1.29,0),'CD2':(2.40,2.10,0)},
 'LYS':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD':(3.95,0.71,0),'CE':(4.90,1.85,0),'NZ':(6.32,1.64,0)},
 'MET':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'SD':(3.95,0.71,0),'CE':(5.30,1.50,0)},
 'PHE':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD1':(3.80,1.20,0),'CD2':(2.40,2.10,0),'CE1':(4.90,1.90,0),'CE2':(3.70,2.80,0),'CZ':(4.90,3.00,0)},
 'PRO':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD':(3.95,0.71,0),'NE':(4.90,1.85,0)},
 'SER':{'CB':(1.46,0,0),'OG':(2.80,1.0,0)},
 'THR':{'CB':(1.46,0,0),'OG1':(2.80,1.0,0),'CG2':(2.52,-1.0,0)},
 'TRP':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD1':(3.80,1.20,0),'CD2':(2.40,2.10,0),'NE1':(4.90,1.90,0),'CE2':(3.70,2.80,0),'CE3':(3.00,1.00,0),'CZ2':(4.90,3.60,0),'CZ3':(4.20,1.80,0),'CH2':(5.30,4.00,0)},
 'TYR':{'CB':(1.46,0,0),'CG':(2.52,1.0,0),'CD1':(3.80,1.20,0),'CD2':(2.40,2.10,0),'CE1':(4.90,1.90,0),'CE2':(3.70,2.80,0),'CZ':(4.90,3.60,0),'OH':(6.10,3.40,0)},
 'VAL':{'CB':(1.46,0,0),'CG1':(2.52,1.0,0),'CG2':(2.52,-1.0,0)}}
def rot_to_match(vf,vt):
    a=np.asarray(vf,float);b=np.asarray(vt,float);a=a/np.linalg.norm(a);b=b/np.linalg.norm(b)
    v=np.cross(a,b);c=float(np.dot(a,b));s=float(np.linalg.norm(v))
    if s<1e-8: return np.eye(3) if c>0 else np.diag([1.,-1,-1])
    vx=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+vx+vx@vx*((1-c)/(s*s))
def elem_of(an):
    if an in('OG','OD1','OD2','OE1','OE2','OH'):return 'O'
    if an in('ND1','ND2','NE','NE1','NE2','NZ','NH1','NH2'):return 'N'
    if an in('SG','SD'):return 'S'
    return 'C'
def rebuild(res,new_one):
    nt=one_to_three[new_one];ot=res.get_resname()
    if ot==nt:return False
    ca=np.asarray(res['CA'].get_coord(),float)
    cb_dir=(np.asarray(res['CB'].get_coord(),float)-ca) if 'CB' in res else np.array([1.,0,0])
    for an in list(res.get_atoms()):
        if an.get_name() not in('N','CA','C'):res.detach_child(an.get_name())
    R=rot_to_match([1,0,0],cb_dir/np.linalg.norm(cb_dir))
    for an,rel in IDEAL[nt].items():
        res.add(Atom(an,ca+R@np.asarray(rel,float),1.,1.,' ',an,0,elem_of(an)))
    res.resname=nt;return True
# reference sequences (1N8Z)
parser=PDBParser(QUIET=True)
refstruct=parser.get_structure("ref",pdb_path)
rchains={ch.get_id():ch for ch in refstruct.get_chains()}
def cseq(ch,n):
    res=[r for r in ch.get_residues() if r.get_id()[0]==' ']
    return ''.join(three_to_one[r.get_resname()] for r in res[:n])
REF_VH=cseq(rchains['B'],120);REF_VL=cseq(rchains['A'],107)
cands=json.load(open("/home/boltzmann10/.sci/cache/scratch/task001_shortlist.json"))["shortlist"]
results={}
for c in cands:
    struct=parser.get_structure(c["id"],pdb_path)
    chs={ch.get_id():ch for ch in struct.get_chains()}
    vh=chs['B'];vl=chs['A'];nh=nl=0
    for i,(ch,seq,refseq) in enumerate([(vh,c["heavy"],REF_VH),(vl,c["light"],REF_VL)]):
        sres=[r for r in ch.get_residues() if r.get_id()[0]==' ']
        for pos in range(len(seq)):
            if seq[pos]!=refseq[pos]:
                r=sres[pos]  # 1:1 mapping: position i (0-based) = standard residue i+1
                if rebuild(r,seq[pos]):
                    if ch is vh:nh+=1
                    else:nl+=1
    out=f"{outdir}/{c['id']}_reconstructed.pdb"
    io=PDBIO();io.set_structure(struct);io.save(out)
    results[c["id"]]={"out":out,"nh":nh,"nl":nl}
    print(c["id"],"rebuilt H:",nh,"L:",nl,"->",out)
# run ProDIGy on each
print("\n=== ProDIGy (Fab A,B vs HER2 C) ===")
for cid in results:
    r=subprocess.run(["/home/boltzmann10/anaconda3/bin/prodigy",results[cid]["out"],"--selection","A,B","C"],capture_output=True,text=True)
    for line in r.stdout.splitlines():
        if 'binding affinity' in line or 'dissociation' in line or 'intermolecular contacts' in line:
            print(cid,line.strip())
json.dump(results,open(outdir+"/reconstruct_results.json","w"),indent=1)
print("\nDone.")
