#!/usr/bin/env python3
"""W4: interface sampling analysis across the 5 independent AF2-Multimer models.

Definitions (identical for reference and candidates):
- interface atoms: antibody side-chain+backbone heavy atoms of CA-CA<6 A residue pairs
- interface RMSD: models pairwise; align on antigen CA (chain C), RMSD on antibody
  interface atoms (paratope residue set of the reference, union definition)
- contact persistence: fraction of the 5 models in which each reference
  antibody-antigen residue pair (CA-CA<6 A) is present
Outputs JSON + per-model epitope/paratope sets.
"""
import glob, json, itertools
import numpy as np
from collections import defaultdict
from Bio.SVDSuperimposer import SVDSuperimposer

A = "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/gal3bp_w1_ref_complex/outputs_afm/extracted/680f678c1b1d883c92aa706c_6af879cf9de6b44b075d7f4c/MultimerStructurePrediction20261114151007Z1a2eb7_colabmult1_f3c47"
out = "/home/boltzmann10/.sci/cache/scratch/gal3bp_run/w4_interface_sampling.json"
vh="QVQLVQSGAEVKKPGSSVKVSCRASGDSFSRKYGISWVRQAPGQGFEWMGTIMPIVGLTTSAQKFQGRVTITADKSTSTAHMELNSLTSEDTAIYYCARDEIIGARPHWFDSWGQGTLVTVS"

def parse(p):
    res={}
    for l in open(p):
        if l.startswith("ATOM"):
            ch=l[21]; rs=int(l[22:26]); nm=l[12:16].strip()
            res.setdefault((ch,rs),{})[nm]=np.array([float(l[30:38]),float(l[38:46]),float(l[46:54])])
    return res

models={}
for p in sorted(glob.glob(f"{A}/*unrelaxed_rank_0*.pdb")):
    rank=p.split("rank_")[1][:3]
    models[rank]=parse(p)
print("models:", sorted(models))

def ca_pairs(res, cutoff=6.0):
    pairs=[]
    ab=[k for k in res if k[0] in "AB"]; ag=[k for k in res if k[0]=="C"]
    for k1 in ab:
        c1=res[k1].get("CA")
        if c1 is None: continue
        for k2 in ag:
            c2=res[k2].get("CA")
            if c2 is None: continue
            if np.linalg.norm(c1-c2)<cutoff:
                pairs.append((k1,k2))
    return pairs

per_model={r:ca_pairs(models[r]) for r in models}
for r in sorted(per_model):
    print(f"rank {r}: {len(per_model[r])} CA-CA<6A pairs, {len({p[0] for p in per_model[r]})} paratope res, {len({p[1] for p in per_model[r]})} epitope res")

# reference = rank_001 (iptm-best); union paratope/epitope over models for persistence
ref_pairs=set(per_model["001"])
union_pairs=set()
for r in per_model: union_pairs |= set(per_model[r])
persistence={f"{k1[0]}{k1[1]:03d}|C{k2[1]:03d}": sum(1 for r in per_model if (k1,k2) in set(per_model[r]))/len(per_model) for (k1,k2) in union_pairs}
persist_dist={"present_in_5":sum(1 for v in persistence.values() if v==1.0),
              "present_in_4":sum(1 for v in persistence.values() if v==0.8),
              "present_in_3":sum(1 for v in persistence.values() if v==0.6),
              "present_in_2_or_less":sum(1 for v in persistence.values() if v<=0.4)}
print("persistence:", persist_dist)

# pairwise interface RMSD: align each model to rank_001 on antigen CA, RMSD over
# antibody backbone+N atoms of the reference paratope residues
ref=per_model["001"]
para_res=sorted({p[0] for p in ref_pairs})
def iface_atoms(res):
    at=[]
    for k in para_res:
        for nm,x in res.get(k,{}).items():
            if not nm.startswith("H"):
                at.append(x)
    return np.array(at)

def ag_ca(res):
    return {k[1]:res[k]["CA"] for k in res if k[0]=="C" and "CA" in res[k]}

r0=models["001"]; ag0=ag_ca(r0)
pair_rmsds=[]
for r in sorted(models):
    if r=="001": continue
    m=models[r]; agm=ag_ca(m)
    common=sorted(set(ag0)&set(agm))
    sup=SVDSuperimposer()
    sup.set(np.array([ag0[c] for c in common]), np.array([agm[c] for c in common]))
    sup.run(); rot,tran=sup.get_rotran()
    a0=iface_atoms(r0); am=iface_atoms(m)
    n=min(len(a0),len(am))
    if n==0 or len(a0)!=len(am):
        pair_rmsds.append({"vs":"001","model":r,"note":f"atom count mismatch {len(a0)} vs {len(am)}; RMSD skipped"})
        continue
    am_t=am@rot.T+tran
    rmsd=float(np.sqrt(((a0-am_t)**2).sum(1).mean()))
    pair_rmsds.append({"vs":"001","model":r,"agCA_rmsd_alignment":round(float(sup.get_rms()),3),
                       "interface_atom_rmsd_A":round(rmsd,2),"n_iface_atoms":n})
    print(f"rank {r}: align agCA {sup.get_rms():.2f} -> interface RMSD {rmsd:.2f} A over {n} atoms")

result={
 "definition":"interface atoms = heavy atoms (non-H) of reference paratope residues (CA-CA<6 A pairs, rank_001); alignment on antigen CA; RMSD on antibody interface atoms",
 "reference_model":"rank_001 (iptm 0.32)",
 "per_model_pair_counts":{r:len(per_model[r]) for r in sorted(per_model)},
 "per_model_iptm":{"001":0.32,"002":0.27,"003":0.27,"004":0.27,"005":0.26},
 "persistence_distribution":persist_dist,
 "contact_persistence":persistence,
 "pairwise_interface_rmsd_to_rank001":pair_rmsds,
 "n_models":len(models),
 "caveat":"sampling = 5 independent AF2-Multimer models of one seed; NOT the study's 3 heated MD replicas; interface-RMSD-vs-5A selection boundary is protocol-incomparable (published threshold, not a reproduced measurement)",
}
json.dump(result,open(out,"w"),indent=2)
print("wrote",out)
