import os, numpy as np
from Bio.PDB import PDBParser
base="/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science_env_results/her2_results"
# van der Waals radii (Å) for clash detection
vdw={'C':1.7,'N':1.55,'O':1.52,'S':1.8,'H':1.2}
def clashes(struct, threshold=1.5):
    """Count atom pairs (non-bonded, same chain) closer than sum of vdw radii - threshold."""
    from Bio.PDB.Residue import Residue
    atoms=[]
    for ch in struct.get_chains():
        for r in ch.get_residues():
            if r.get_id()[0]!=' ':continue
            for a in r.get_atoms():
                if a.element in vdw:
                    atoms.append((ch.get_id(),r.get_id()[1],a))
    # build distance map per chain
    count=0; pairs=[]
    for i in range(len(atoms)):
        cid,rid,ai=atoms[i]; ci=atoms[i][2].coord
        for j in range(i+1,len(atoms)):
            if atoms[j][0]!=cid:continue  # same chain only
            # skip bonded (same residue or adjacent)
            if abs(atoms[j][1]-rid)<=1:continue
            aj=atoms[j][2]; d=np.linalg.norm(ci-aj.coord)
            cutoff=vdw[ai.element]+vdw[aj.element]-threshold
            if d<cutoff:
                count+=1
    return count
parser=PDBParser(QUIET=True)
ref=parser.get_structure("ref",base+"/1N8Z_deposited_complex.pdb")
print("Reference (1N8Z) clashes:",clashes(ref))
for f in sorted(os.listdir(base+"/reconstructed")):
    if f.endswith(".pdb"):
        s=parser.get_structure(f,base+"/reconstructed/"+f)
        print(f,"clashes:",clashes(s))
