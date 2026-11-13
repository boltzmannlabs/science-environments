#!/usr/bin/env python3
"""Analyze task002 Boltz-2 predictions: confidence + epitope engagement + clashes."""
import json, os, glob
import numpy as np
from Bio.PDB import PDBParser, MMCIFParser, PDBList
import warnings
warnings.filterwarnings("ignore")

BASE = "/home/boltzmann10/.sci/cache/scratch/boltz2_task002"
HOTSPOTS = [37, 39, 41, 96, 98]  # PD-L1 chain residue numbers (I37,Y39,E41,R96,M98)
parser = MMCIFParser(QUIET=True)

results = {}
for cid in ["rf0_d7","rf0_d0","rf0_d2","rf0_d5","rf0_d8","rf1_d2","rf1_d3","rf1_d5","rf1_d6","rf1_d9"]:
    cdir = glob.glob(f"{BASE}/pred_{cid}/boltz_results_{cid}/predictions/{cid}/*model_0.cif")
    if not cdir:
        print(cid, "NO CIF"); continue
    conf_path = cdir[0].replace(".cif","") + "_confidence.json" if False else None
    # find confidence json
    cjson = glob.glob(f"{BASE}/pred_{cid}/boltz_results_{cid}/predictions/{cid}/confidence_*.json")
    conf = json.load(open(cjson[0]))
    struct = parser.get_structure(cid, cdir[0])
    # identify chains: scfv (long, ~242) and pdl1 (~115)
    chains = {}
    for ch in struct.get_chains():
        residues = [r for r in ch if r.id[0]==' ' and r.resname not in ('WATER',)]
        chains[ch.id] = residues
    # scfv = longest chain, pdl1 = the other
    scid = max(chains, key=lambda c: len(chains[c]))
    pdid = [c for c in chains if c!=scid][0]
    scfv_atoms = [(a, r) for r in chains[scid] for a in r.get_atoms() if a.element in 'CNOS']
    pd_atoms = [(a, r) for r in chains[pdid] for a in r.get_atoms()]
    # hotspot atoms (sidechain) on pdl1
    hot_atoms = [(a,r) for (a,r) in pd_atoms if r.id[0]==' ' and int(r.id[1]) in HOTSPOTS and a.name not in ('CA','N','C','O')]
    # all-atom min distances
    def minal(dlist1, dlist2):
        best=1e9; bp=None
        for a1,r1 in dlist1:
            p1=np.asarray(a1.coord)
            for a2,r2 in dlist2:
                d=float(np.linalg.norm(p1-np.asarray(a2.coord)))
                if d<best: best=d; bp=(r1.id[1],a1.name,r2.id[1],a2.name)
        return best,bp
    # interface: scfv atoms within 6A of any pdl1 atom (residue-residue contact)
    pd_ca = {r.id[1]:a.coord for a,r in pd_atoms if a.name=='CA'}
    # contact residues
    contact_res=set()
    for a,r in scfv_atoms:
        p1=np.asarray(a.coord)
        for a2,r2 in pd_atoms:
            if float(np.linalg.norm(p1-np.asarray(a2.coord)))<6.0:
                contact_res.add(r.id[1]); break
    # hotspot contacts: any scfv atom within 4.5A of hotspot sidechain atom
    hot_contacts=set()
    for a,r in scfv_atoms:
        p1=np.asarray(a.coord)
        for a2,r2 in hot_atoms:
            if float(np.linalg.norm(p1-np.asarray(a2.coord)))<4.5:
                hot_contacts.add((r.id[1], r2.id[1])); break
    # clashes: heavy atom pairs <2.4A between chains (excluding H)
    clashes=0
    for a,r in scfv_atoms:
        p1=np.asarray(a.coord)
        for a2,r2 in pd_atoms:
            if float(np.linalg.norm(p1-np.asarray(a2.coord)))<2.4: clashes+=1
    # interface SASA (approx via contact residue count + surface)
    results[cid]={
        "pTM":round(conf["ptm"],3),"ipTM":round(conf["iptm"],3),
        "pLDDT":round(conf["complex_plddt"],3),"iPLDDT":round(conf["complex_iplddt"],3),
        "ipDE":round(conf["complex_ipde"],2),"confidence_score":round(conf["confidence_score"],3),
        "n_contact_res":len(contact_res),
        "hotspot_contact_pairs":len(hot_contacts),
        "hotspot_residues_touched":sorted(set(h for _,h in hot_contacts)),
        "min_dist":round(minal(scfv_atoms,pd_atoms)[0],2),
        "clashes":clashes,
        "scfv_chain":scid,"pdl1_chain":pdid,
        "cif":cdir[0],
    }
    print(f"{cid}: ipTM={results[cid]['ipTM']} pLDDT={results[cid]['pLDDT']} iPLDDT={results[cid]['iPLDDT']} ipDE={results[cid]['ipDE']} contact_res={results[cid]['n_contact_res']} hot_pairs={results[cid]['hotspot_contact_pairs']} hot_res={results[cid]['hotspot_residues_touched']} minD={results[cid]['min_dist']}A clashes={results[cid]['clashes']}")

json.dump(results, open(f"{BASE}/analysis.json","w"), indent=1)
print("saved analysis.json")
