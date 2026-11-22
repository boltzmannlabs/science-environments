"""Compute scRMSD for predicted Fv (VH+VL multimer) against the 5NGV reference Fv.
Protocol: C-alpha atoms; Kabsch superposition of the whole Fv (VH+VL) onto the
reference Fv; then regional RMSD (HCDR1/2/3/123 from VH, Fv from all VH+VL).
"""
import numpy as np, glob, os

REF_PDB = "/home/boltzmann4/.sci/profiles/ab_task_10/workspace/igdesign_repo/examples/5ngv.pdb"
# 0-indexed VH regions
REGIONS = {
    "HCDR1": list(range(24,32)),
    "HCDR2": list(range(49,57)),
    "HCDR3": list(range(95,103)),
    "HCDR123": list(range(24,32))+list(range(49,57))+list(range(95,103)),
}
N_VH=113; N_VL=111

def ca_of_chain(pdb, chain):
    coords=[]
    seen=0
    for line in open(pdb):
        if line.startswith("ATOM") and line[21]==chain and line[12:16].strip()=="CA":
            # reference VH (chain H) has a duplicate GLU at resseq 10; skip the 2nd
            if chain=="H":
                resseq=int(line[22:26]); resname=line[17:20].strip()
                if resseq==10 and resname=="GLU":
                    seen+=1
                    if seen==2: continue
            coords.append((float(line[30:38]),float(line[38:46]),float(line[46:54])))
    return np.array(coords)

def ref_fv():
    return np.vstack([ca_of_chain(REF_PDB,"H"), ca_of_chain(REF_PDB,"L")])

def pred_fv(multimer_pdb):
    return np.vstack([ca_of_chain(multimer_pdb,"A"), ca_of_chain(multimer_pdb,"B")])

def kabsch(p,q):
    cp=p-p.mean(0); cq=q-q.mean(0)
    H=cp.T@cq; U,S,Vt=np.linalg.svd(H)
    D=np.diag([1,1,np.linalg.det(U@Vt)]); R=U@D@Vt
    tp=cp@R+q.mean(0)
    return tp, np.sqrt(np.mean(np.sum((tp-q)**2,1)))

def regional_rmsd(tp, refc):
    # tp, refc are Fv arrays (VH first, then VL)
    out={}
    for name,idx in REGIONS.items():
        d=tp[idx]-refc[idx]
        out[name]=float(np.sqrt(np.mean(np.sum(d**2,1))))
    d=tp-refc
    out["Fv_whole"]=float(np.sqrt(np.mean(np.sum(d**2,1))))
    return out

def compute(multimer_pdb):
    pf=pred_fv(multimer_pdb); rf=ref_fv()
    tp,_=kabsch(pf,rf)
    return regional_rmsd(tp,rf)

if __name__=="__main__":
    import sys
    pdb=sys.argv[1] if len(sys.argv)>1 else sorted(glob.glob('/home/boltzmann4/.sci/profiles/ab_task_10/workspace/outputs/ref_multimer/**/*rank_001*.pdb',recursive=True))[0]
    print("Published ESMFold: HCDR1=0.4362 HCDR2=0.7643 HCDR3=0.5768 HCDR123=0.6075 Fv=1.1243")
    print("AlphaFold-Multimer reference (executed):")
    for k,v in compute(pdb).items(): print(f"  {k}: {v:.4f}")
