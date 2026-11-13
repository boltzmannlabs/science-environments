#!/usr/bin/env python3
"""Glycan-aware E1/BACK-domain accessibility analysis for task_005 (fixed E1 definition).

E1 is the paper-defined glycan-free epitope within the BACK domain. Since the
exact E1 residue mapping is unavailable (paper inaccessible), we approximate E1
as the BACK-domain (260-360) solvent surface.

Glycan model: representative N-glycan at the BACK-domain-flanking Asn362 site
(C-terminal flank). A simplified 12-sugar linear model is built and positioned
at Asn362, extending away from the antigen center.

Area-difference convention:
    dSASA = SASA_BACK(unglycosylated) - SASA_BACK(with glycan)
A positive dSASA means the glycan occludes BACK-domain surface.

Also checks glycan-antibody context clashes (glycan atom < 2.5 A to Ab atom).
"""
import numpy as np
from collections import defaultdict
import json, os

BASE = "/home/boltzmann10/agent_scientist_boltpro_tols_scitenist_modify/science-environments/environments/antibody_design/results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy"
REF = os.path.join(BASE, "evidence/reference/task005_ref_bdbv43.pdb")

def parse_pdb(path):
    atoms = []
    with open(path) as f:
        for line in f:
            if line.startswith(("ATOM","HETATM")):
                try:
                    name=line[12:16].strip(); resn=line[17:20].strip(); chain=line[21]
                    resseq=int(line[22:26]); x=float(line[30:38]); y=float(line[38:46]); z=float(line[46:54])
                    atoms.append({"name":name,"resn":resn,"chain":chain,"resseq":resseq,"xyz":np.array([x,y,z])})
                except: pass
    return atoms

def get_residues(atoms, chain):
    res = defaultdict(list)
    for a in atoms:
        if a["chain"]==chain: res[a["resseq"]].append(a)
    return res

def ca_pos(rd, rs):
    for a in rd[rs]:
        if a["name"]=="CA": return a["xyz"]
    return None

def compute_sasa(atoms_list, probe_r=1.4, nprobe=24):
    coords=np.array([a["xyz"] for a in atoms_list])
    names=[a["name"] for a in atoms_list]
    vdw={"C":1.7,"N":1.55,"O":1.52,"S":1.8}
    def get_el(n):
        if n in ("N","NE","NE1","NE2","ND1","ND2","NZ","NH1","NH2"): return "N"
        if n in ("O","O1","O2","OE1","OE2","OG","OG1","OG2","OD1","OD2"): return "O"
        if n in ("S","SG","SD"): return "S"
        return "C"
    radii=np.array([vdw[get_el(n)] for n in names])
    idx=np.arange(nprobe); phi=np.arccos(1-2*(idx+0.5)/nprobe); theta=np.pi*(1+5**0.5)*idx
    dirs=np.stack([np.sin(phi)*np.cos(theta),np.sin(phi)*np.sin(theta),np.cos(phi)],axis=1)
    sasa=np.zeros(len(atoms_list))
    # Batch over atoms in chunks to limit memory
    chunk=50
    for s in range(0,len(atoms_list),chunk):
        e=min(s+chunk,len(atoms_list))
        ri=radii[s:e]
        pp=coords[s:e,None,:] + (ri+probe_r)[:,None,None]*dirs[None,:,:]  # (chunk,nprobe,3)
        d=np.linalg.norm(pp[:,:,None,:] - coords[None,None,:,:], axis=3)  # (chunk,nprobe,natoms)
        buried=(d<radii[None,None,:]).any(axis=2)
        exposed=(~buried).sum(axis=1)
        sasa[s:e]=exposed*4*np.pi*(ri+probe_r)**2/nprobe
    return sasa

atoms=parse_pdb(REF)
antigen_res=get_residues(atoms,"C")
vh_res=get_residues(atoms,"A")
vl_res=get_residues(atoms,"B")

# E1 = BACK domain (260-360) antigen residues
back_residues=[rs for rs in range(260,361) if rs in antigen_res]
back_indices=[i for i,a in enumerate(atoms) if a["chain"]=="C" and a["resseq"] in back_residues]
print(f"BACK-domain residues: {len(back_residues)} ({back_residues[0]}-{back_residues[-1]}), atoms: {len(back_indices)}")

# Unglycosylated SASA
sasa_all=compute_sasa(atoms)
sasa_back_unglyc=sasa_all[back_indices].sum()
print(f"BACK-domain SASA (unglycosylated): {sasa_back_unglyc:.1f} A^2")

# Build glycan at Asn362
asn362=ca_pos(antigen_res,362)
back_centers=[ca_pos(antigen_res,rs) for rs in back_residues if ca_pos(antigen_res,rs) is not None]
back_center=np.mean(back_centers,axis=0)
outward=asn362-back_center; outward=outward/np.linalg.norm(outward)
glycan_atoms=[]
n_sugars=12
for i in range(n_sugars):
    base=asn362+outward*(i*5.5)
    for j in range(6):
        angle=2*np.pi*j/6
        perp1=np.cross(outward,np.array([0,0,1]))
        if np.linalg.norm(perp1)<1e-6: perp1=np.cross(outward,np.array([1,0,0]))
        perp1=perp1/np.linalg.norm(perp1); perp2=np.cross(outward,perp1)
        ring_pos=base+1.5*(np.cos(angle)*perp1+np.sin(angle)*perp2)
        glycan_atoms.append({"name":f"C{j}","resn":"NG","chain":"G","resseq":i+1,"xyz":ring_pos})

combined=atoms+glycan_atoms
sasa_comb=compute_sasa(combined)
sasa_back_glyc=sasa_comb[back_indices].sum()
dsasa=sasa_back_unglyc-sasa_back_glyc
print(f"BACK-domain SASA (with glycan at 362): {sasa_back_glyc:.1f} A^2")
print(f"BACK-domain glycan-associated dSASA: {dsasa:.1f} A^2 (positive = glycan occludes)")

# Glycan-antibody clash
ab_coords=np.array([a["xyz"] for a in atoms if a["chain"] in ("A","B")])
gly_coords=np.array([g["xyz"] for g in glycan_atoms])
min_d=np.min(np.linalg.norm(gly_coords[:,None,:]-ab_coords[None,:,:],axis=2),axis=1)
n_clash=(min_d<2.5).sum()
print(f"Glycan-antibody clashes (<2.5 A): {n_clash} of {len(glycan_atoms)}")

result={
 "glycan_model":"Representative N-glycan, simplified 12-sugar linear model at Asn362 (C-terminal flank of BACK domain 260-360)",
 "e1_epitope_definition":"BACK-domain (260-360) antigen solvent surface (approximation; paper's exact E1 mapping unavailable)",
 "back_n_residues":len(back_residues),
 "sasa_back_unglycosylated_A2":round(float(sasa_back_unglyc),1),
 "sasa_back_with_glycan_A2":round(float(sasa_back_glyc),1),
 "back_glycan_dsasa_A2":round(float(dsasa),1),
 "area_difference_convention":"dSASA = SASA_BACK(unglycosylated) - SASA_BACK(with glycan); positive = glycan occludes",
 "glycan_antibody_clashes_n2p5A":int(n_clash),
 "glycan_atoms_total":len(glycan_atoms),
 "reference_complex":"task005_ref_bdbv43.pdb (Boltz2-predicted BDBV-43 Fab + full-length LGALS3BP)",
 "note":"Study's exact E1 mapping and glycan model unavailable (paper inaccessible). Matched-conditions approximation using verified UniProt BACK domain (260-360) and N-glycosylation site (362).",
}
outpath=os.path.join(BASE,"evidence/glycan_aware_analysis.json")
with open(outpath,"w") as f: json.dump(result,f,indent=2)
print(f"Saved: {outpath}")
