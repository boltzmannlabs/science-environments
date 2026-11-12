#!/usr/bin/env python
"""Task 002: H5 reconstruction RMSD comparison (position-matched)."""
import sys, json
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared"))
import numpy as np
import metrics as m

pred_path = "/home/boltzmann10/shared_metric_tools/results/task002_boltz2_local/boltz_results_task002_h5_pdl1/predictions/task002_h5_pdl1/task002_h5_pdl1_model_0.pdb"
exp_path = "/home/boltzmann10/shared_metric_tools/prepared/35TL.pdb"
pa = m.parse_pdb(pred_path); ea = m.parse_pdb(exp_path)

def ca_chain_ordered(atoms, chain):
    """C-alpha coords in sequence order for one chain (dedup by resi)."""
    coords=[]; seen=set()
    for (c,resi,rn,an,x,y,z,het) in atoms:
        if c==chain and an=="CA" and not het and resi not in seen:
            seen.add(resi); coords.append([x,y,z])
    return np.array(coords)

# lengths must match (same sequences)
for ch in "ABC":
    lp=len(ca_chain_ordered(pa,ch)); le=len(ca_chain_ordered(ea,ch))
    assert lp==le, f"chain {ch} length mismatch {lp} vs {le}"

# Align predicted antigen (A) onto experimental antigen (A)
eA=ca_chain_ordered(ea,'A'); pA=ca_chain_ordered(pa,'A')
R,t=m.kabsch(eA,pA)
def xf(c): return c@R.T+t

# Antibody C-alpha RMSD (B+C), position-matched
pAB=np.vstack([xf(ca_chain_ordered(pa,'B')), xf(ca_chain_ordered(pa,'C'))])
eAB=np.vstack([ca_chain_ordered(ea,'B'), ca_chain_ordered(ea,'C')])
rmsd_ab=float(np.sqrt(np.mean(np.sum((eAB-pAB)**2,axis=1))))
# Whole-complex C-alpha RMSD
pAll=np.vstack([xf(ca_chain_ordered(pa,'A')),pAB])
eAll=np.vstack([eA,eAB])
rmsd_all=float(np.sqrt(np.mean(np.sum((eAll-pAll)**2,axis=1))))
# Per-antibody-chain RMSD
rmsd_B=float(np.sqrt(np.mean(np.sum((ca_chain_ordered(ea,'B')-xf(ca_chain_ordered(pa,'B')))**2,axis=1))))
rmsd_C=float(np.sqrt(np.mean(np.sum((ca_chain_ordered(ea,'C')-xf(ca_chain_ordered(pa,'C')))**2,axis=1))))

out={"protocol":"Boltz2 prediction of H5+PD-L1 (3 chains, same sequences as 35TL); Kabsch alignment on PD-L1 (chain A) C-alpha; position-matched C-alpha RMSD",
 "H5_antibody_CA_RMSD_A":round(rmsd_ab,3),"H5_VH_CA_RMSD_A":round(rmsd_B,3),"H5_VL_CA_RMSD_A":round(rmsd_C,3),
 "whole_complex_CA_RMSD_A":round(rmsd_all,3),"benchmark_published_A":1.25,
 "published_scope":"H5 predicted-vs-experimental global C-alpha RMSD (Germinal paper, different predictor)",
 "boltz2_confidence":{"ptm":0.9437,"iptm":0.9262,"complex_plddt":0.9549,"complex_pde":0.368}}
print(json.dumps(out,indent=2))
open("/home/boltzmann10/shared_metric_tools/results/task002_h5_rmsd.json","w").write(json.dumps(out,indent=2))
