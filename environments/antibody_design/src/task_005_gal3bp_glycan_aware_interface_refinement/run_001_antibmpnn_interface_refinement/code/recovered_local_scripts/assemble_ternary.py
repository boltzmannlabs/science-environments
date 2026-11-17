#!/usr/bin/env python3
"""Clash-repairing ternary assembly: superimpose pair-1 Fv onto pair-2 VH, and when
VH side chains clash (<3.3 A) with the antigen, transplant the pair-2 (VH:antigen
pose) side-chain coordinates for those residues. Structure is a computational
reference assembly, not a docked experimental complex.
"""
import numpy as np
from Bio.SVDSuperimposer import SVDSuperimposer

pair1 = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/gal3bp_w1_ref_complex/outputs/extracted/boltz_pdb/1_model_0.pdb"
pair2 = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/gal3bp_w1_ref_complex/outputs/extracted/boltz_pdb/2_model_0.pdb"
out   = "/home/boltzmann10/.sci/cache/scratch/gal3bp_run/ref_ternary.pdb"

def parse(p):
    atoms=[]; chains={}
    for line in open(p):
        if line.startswith("ATOM"):
            ch=line[21]; rs=int(line[22:26]); nm=line[12:16].strip()
            a={"ch":ch,"rs":rs,"nm":nm,"line":line,
               "xyz":np.array([float(line[30:38]),float(line[38:46]),float(line[46:54])])}
            atoms.append(a); chains.setdefault(ch,[]).append(a)
    return chains

c1=parse(pair1); c2=parse(pair2)
def ca(c): return {x["rs"]:x["xyz"] for x in c if x["nm"]=="CA"}
m1,m2=ca(c1["A"]),ca(c2["A"]); common=sorted(set(m1)&set(m2))
sup=SVDSuperimposer(); sup.set(np.array([m2[r] for r in common]), np.array([m1[r] for r in common])); sup.run()
rot,tran=sup.get_rotran()
print(f"VH CA superposition rmsd {sup.get_rms():.3f} A over {len(common)} CA")

ag=np.array([x["xyz"] for x in c2["B"]])
# VH in the ternary comes ENTIRELY from pair-2 (the VH:antigen pose model):
# it is clash-free with its antigen by construction. Only VL is transplanted
# from pair-1 (VH:VL model) via the VH superposition.
def write_chain(fout, atoms, newch, start, apply_t):
    out_rs=start; prev=None
    for x in atoms:
        if prev is not None and x["rs"]!=prev: out_rs+=1
        prev=x["rs"]; x["out_rs"]=out_rs
        xyz=(x["xyz"]@rot.T+tran) if apply_t else x["xyz"]
        l=x["line"]
        l=l[:21]+newch+f"{x['out_rs']:4d}"+l[26:30]+f"{xyz[0]:8.3f}{xyz[1]:8.3f}{xyz[2]:8.3f}"+l[54:]
        fout.write(l if l.endswith("\n") else l+"\n")

with open(out,"w") as f:
    write_chain(f,c2["A"],"A",1,False)   # VH from pair-2, native pose
    write_chain(f,c1["B"],"B",1,True)    # VL from pair-1, superimposed
    write_chain(f,c2["B"],"C",1,False)   # antigen from pair-2
print("wrote",out)

from collections import defaultdict
def residues(p):
    res=defaultdict(dict)
    for l in open(p):
        if l.startswith("ATOM"):
            res[(l[21],int(l[22:26]))][l[12:16].strip()]=np.array([float(l[30:38]),float(l[38:46]),float(l[46:54])])
    return res
res=residues(out)
ab=[k for k in res if k[0] in "AB"]; agc=[k for k in res if k[0]=="C"]
worst=9e9; wk=None
for k1 in ab:
    for nm,x in res[k1].items():
        for k2 in agc:
            for nm2,y in res[k2].items():
                d=np.linalg.norm(x-y)
                if d<worst: worst=d; wk=(k1,nm,k2,nm2)
print("final min AB-C distance:", round(float(worst),2), wk)
